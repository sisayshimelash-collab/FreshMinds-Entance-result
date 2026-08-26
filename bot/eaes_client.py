"""
FreshMinds Result Bot — High-Throughput EAES API Client

Features:
- Global "Not Released" stampede cache (shielding EAES from 1,000s of redundant hits)
- In-memory result cache (5 min TTL) for duplicate queries
- Outbound concurrency limiter (asyncio.Semaphore) to avoid socket exhaustion
- Connection pool optimization (httpx.Limits with keepalive)
- Automatic retry on transient network & 5xx server errors
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import httpx

from config import EAES_BOT_ENDPOINT, REQUEST_TIMEOUT
from rate_limiter import TTLCache

logger = logging.getLogger(__name__)


# ── Result Types ─────────────────────────────────────────────────────────────

class ResultStatus(Enum):
    SUCCESS = "success"
    NOT_RELEASED = "not_released"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    SERVICE_ERROR = "service_error"


@dataclass
class SubjectResult:
    subject: str
    result: str


@dataclass
class StudentInfo:
    full_name: str
    admission_no: str
    sex: Optional[str] = None
    age: Optional[str] = None
    school: Optional[str] = None
    stream: Optional[str] = None


@dataclass
class EAESResult:
    status: ResultStatus
    student: Optional[StudentInfo] = None
    results: list[SubjectResult] = field(default_factory=list)
    message: str = ""
    from_cache: bool = False


# ── High-Performance Client ──────────────────────────────────────────────────

class EAESClient:
    """
    High-throughput async client for the EAES result bot endpoint.
    Includes connection pooling, stampede caching, and concurrency limiting.
    """

    def __init__(
        self,
        max_concurrent_requests: int = 50,
        result_cache_ttl: float = 600.0,      # 10 minutes for student results
        not_released_cache_ttl: float = 30.0, # 30 seconds global stampede shield
    ):
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._result_cache = TTLCache(default_ttl=result_cache_ttl, max_size=20000)
        self._not_released_cache_ttl = not_released_cache_ttl

        # Global flag for "Results Not Released" status to avoid hammering EAES
        self._global_not_released_until: float = 0.0
        self._global_not_released_msg: str = ""

    async def start(self):
        """Initialize the HTTP client with optimized connection pool."""
        limits = httpx.Limits(
            max_connections=300,
            max_keepalive_connections=100,
            keepalive_expiry=30.0,
        )
        self._client = httpx.AsyncClient(
            limits=limits,
            timeout=httpx.Timeout(REQUEST_TIMEOUT, connect=5.0),
            follow_redirects=True,
            headers={
                "User-Agent": "FreshMindsResultBot/2.0 (+https://t.me/FreshMindsResultBot)",
                "Accept": "application/json",
            },
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def check_result(self, admission_no: str, first_name: str) -> EAESResult:
        """
        Check a student's result with multi-layer caching and concurrency management.
        """
        # 1. Normalize input for cache key
        norm_adm = admission_no.strip()
        norm_name = first_name.strip().lower()
        cache_key = f"res:{norm_adm}:{norm_name}"

        # 2. Check local student result cache
        cached_result = self._result_cache.get(cache_key)
        if cached_result is not None:
            cached_result.from_cache = True
            return cached_result

        # 3. Check global stampede shield ("Results not released" state)
        now = time.monotonic()
        if now < self._global_not_released_until:
            return EAESResult(
                status=ResultStatus.NOT_RELEASED,
                message=self._global_not_released_msg,
                from_cache=True,
            )

        if not self._client:
            await self.start()

        # 4. Outbound call under concurrency semaphore with retries
        return await self._fetch_with_retry(norm_adm, first_name.strip(), cache_key)

    async def _fetch_with_retry(
        self,
        admission_no: str,
        first_name: str,
        cache_key: str,
        max_retries: int = 2,
    ) -> EAESResult:
        """Execute request with concurrency limiting and exponential backoff retry."""
        import re
        from config import EAES_SMS_ENDPOINT

        for attempt in range(max_retries + 1):
            try:
                async with self._semaphore:
                    # 1. Primary: Query the active, high-speed SMS result endpoint
                    response = await self._client.get(
                        EAES_SMS_ENDPOINT,
                        params={
                            "admission_no": admission_no,
                            "first_name": first_name,
                        },
                    )

                # 200 — Result successfully found
                if response.status_code == 200:
                    text_body = response.text
                    if "{SMS:TEXT}" in text_body or "Name:" in text_body:
                        parsed = self._parse_sms_success(text_body, admission_no, first_name)
                    else:
                        try:
                            parsed = self._parse_success(response.json())
                        except Exception:
                            parsed = self._parse_sms_success(text_body, admission_no, first_name)

                    if parsed.status == ResultStatus.SUCCESS:
                        self._result_cache.set(cache_key, parsed)
                    return parsed

                # 404 — Student Not Found
                if response.status_code == 404:
                    detail = self._extract_detail(response)
                    return EAESResult(
                        status=ResultStatus.NOT_FOUND,
                        message=detail or "Student not found with the provided details.",
                    )

                # 423 — Results Not Released (Activate Stampede Shield)
                if response.status_code == 423:
                    detail = self._extract_detail(response)
                    msg = detail or "Results have not been released yet."
                    self._global_not_released_until = time.monotonic() + self._not_released_cache_ttl
                    self._global_not_released_msg = msg
                    return EAESResult(status=ResultStatus.NOT_RELEASED, message=msg)

                # 422 — Validation Error
                if response.status_code == 422:
                    return EAESResult(
                        status=ResultStatus.VALIDATION_ERROR,
                        message="Invalid admission number or name format.",
                    )

                # Transient server error (500, 502, 503, 504) -> retry if attempts remain
                if response.status_code in (500, 502, 503, 504) and attempt < max_retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue

                return EAESResult(
                    status=ResultStatus.SERVICE_ERROR,
                    message=f"Service responded with status {response.status_code}.",
                )

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < max_retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
                break
            except Exception as e:
                logger.error(f"Unexpected error in check_result: {e}")
                return EAESResult(
                    status=ResultStatus.SERVICE_ERROR,
                    message="An unexpected error occurred while communicating with the result service.",
                )

        return EAESResult(
            status=ResultStatus.SERVICE_ERROR,
            message="The result service is temporarily busy. Please try again in a moment.",
        )

    def _parse_sms_success(self, text: str, admission_no: str, first_name: str) -> EAESResult:
        """Parse the active EAES SMS result format."""
        import re
        try:
            name_match = re.search(r'Name:\s*([^;]+);', text)
            full_name = name_match.group(1).strip() if name_match else first_name

            adm_match = re.search(r'Admission\s*No:\s*([^;]+);', text)
            parsed_adm = adm_match.group(1).strip() if adm_match else admission_no

            res_match = re.search(r'Results:\s*([^;]+);', text)
            results = []
            if res_match:
                subject_entries = res_match.group(1).split(',')
                for entry in subject_entries:
                    entry = entry.strip()
                    if entry:
                        parts = entry.rsplit(' ', 1)
                        if len(parts) == 2:
                            results.append(SubjectResult(subject=parts[0].strip(), result=parts[1].strip()))
                        else:
                            results.append(SubjectResult(subject=entry, result="-"))

            total_match = re.search(r'Total\s*([\d.]+)', text)
            if total_match:
                results.append(SubjectResult(subject="Total", result=total_match.group(1).strip().rstrip('.')))

            avg_match = re.search(r'Average\s*([\d.]+)', text)
            if avg_match:
                results.append(SubjectResult(subject="Average", result=avg_match.group(1).strip().rstrip('.')))

            student = StudentInfo(
                full_name=full_name,
                admission_no=parsed_adm,
            )

            return EAESResult(
                status=ResultStatus.SUCCESS,
                student=student,
                results=results,
            )
        except Exception as e:
            logger.error(f"Failed to parse SMS result text: {e}")
            return EAESResult(
                status=ResultStatus.SERVICE_ERROR,
                message="Failed to parse the result record.",
            )

    def _parse_success(self, data: dict) -> EAESResult:
        """Parse a successful result response safely with null guards."""
        try:
            student_data = data.get("studentInfo") or {}
            student = StudentInfo(
                full_name=str(student_data.get("FullName") or "Student"),
                admission_no=str(student_data.get("Admission_No") or ""),
                sex=student_data.get("Sex"),
                age=str(student_data.get("Age")) if student_data.get("Age") is not None else None,
                school=student_data.get("School"),
                stream=student_data.get("Stream"),
            )

            raw_results = data.get("results") or []
            results = []
            for item in raw_results:
                if isinstance(item, dict):
                    results.append(SubjectResult(
                        subject=str(item.get("Subject") or "Subject"),
                        result=str(item.get("Result") or "-"),
                    ))

            return EAESResult(
                status=ResultStatus.SUCCESS,
                student=student,
                results=results,
            )
        except Exception as e:
            logger.error(f"Failed to parse result payload: {e}")
            return EAESResult(
                status=ResultStatus.SERVICE_ERROR,
                message="Failed to parse the result record.",
            )

    @staticmethod
    def _extract_detail(response: httpx.Response) -> str:
        """Extract the 'detail' field from a JSON error response."""
        try:
            return response.json().get("detail", "")
        except Exception:
            return ""
