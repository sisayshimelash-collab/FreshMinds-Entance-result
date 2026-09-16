"""
FreshMinds Placement Client — Asynchronous EtherNet Placement API Consumer
Directly connects to Ethiopian Ministry of Education Placement Endpoint:
https://placement.ethernet.edu.et/api/student/
"""

import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, Any, NamedTuple

logger = logging.getLogger(__name__)

PLACEMENT_ENDPOINT = "https://placement.ethernet.edu.et/api/student/"


class PlacementResult(NamedTuple):
    status: str  # 'SUCCESS', 'NOT_FOUND', 'SERVER_BUSY', 'TIMEOUT', 'ERROR'
    admission_no: str
    student_name: Optional[str] = None
    university: Optional[str] = None
    stream: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class PlacementClient:
    """Async HTTP Client for EtherNet University Placement Lookup."""

    def __init__(self, timeout_seconds: int = 12):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Origin": "https://placement.ethernet.edu.et",
            "Referer": "https://placement.ethernet.edu.et/",
            "Accept": "application/json, text/plain, */*",
        }

    async def query_placement(self, admission_no: str) -> PlacementResult:
        """
        Queries student placement by registration / admission number.
        Sends FormData as discovered in browser DevTools:
          - registration_number: <id>
          - g-recaptcha-response: ""
        """
        clean_reg = admission_no.strip()
        data = aiohttp.FormData()
        data.add_field("registration_number", clean_reg)
        data.add_field("g-recaptcha-response", "")

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers,
            ) as session:
                async with session.post(
                    PLACEMENT_ENDPOINT,
                    data=data,
                    ssl=False,  # Avoid SSL renegotiation/handshake issues on Ethiopian servers
                ) as resp:
                    status_code = resp.status

                    if status_code == 200:
                        try:
                            payload = await resp.json()
                        except Exception:
                            text = await resp.text()
                            try:
                                payload = json.loads(text)
                            except Exception:
                                payload = {"raw": text}

                        # Extract name and university from various common MoE JSON keys
                        student_name = (
                            payload.get("fullName")
                            or payload.get("full_name")
                            or payload.get("name")
                            or payload.get("studentName")
                            or payload.get("student_name")
                            or (payload.get("data", {}).get("fullName") if isinstance(payload.get("data"), dict) else None)
                            or "N/A"
                        )

                        university = (
                            payload.get("university")
                            or payload.get("institution")
                            or payload.get("assignedUniversity")
                            or payload.get("assigned_university")
                            or (payload.get("data", {}).get("university") if isinstance(payload.get("data"), dict) else None)
                            or "N/A"
                        )

                        stream = (
                            payload.get("stream")
                            or payload.get("field")
                            or payload.get("fieldOfStudy")
                            or (payload.get("data", {}).get("stream") if isinstance(payload.get("data"), dict) else None)
                            or "N/A"
                        )

                        return PlacementResult(
                            status="SUCCESS",
                            admission_no=clean_reg,
                            student_name=student_name,
                            university=university,
                            stream=stream,
                            raw_data=payload,
                        )

                    elif status_code == 404:
                        return PlacementResult(
                            status="NOT_FOUND",
                            admission_no=clean_reg,
                            error_message="Invalid Registration Number or Placement not released yet.",
                        )

                    elif status_code in (500, 502, 503, 504):
                        logger.warning(
                            f"EtherNet Placement server returned {status_code} for {clean_reg}"
                        )
                        return PlacementResult(
                            status="SERVER_BUSY",
                            admission_no=clean_reg,
                            error_message=f"Server returned HTTP {status_code}",
                        )

                    else:
                        logger.warning(
                            f"Unexpected status code {status_code} from placement endpoint"
                        )
                        return PlacementResult(
                            status="ERROR",
                            admission_no=clean_reg,
                            error_message=f"Unexpected status: {status_code}",
                        )

        except asyncio.TimeoutError:
            logger.warning(f"Timeout querying placement for {clean_reg}")
            return PlacementResult(
                status="TIMEOUT",
                admission_no=clean_reg,
                error_message="Connection timed out",
            )
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Network connection error for {clean_reg}: {e}")
            return PlacementResult(
                status="SERVER_BUSY",
                admission_no=clean_reg,
                error_message="Failed to connect to placement server",
            )
        except Exception as e:
            logger.exception(f"Unexpected error in query_placement for {clean_reg}: {e}")
            return PlacementResult(
                status="ERROR",
                admission_no=clean_reg,
                error_message=str(e),
            )


# Global placement client instance
placement_client = PlacementClient()
