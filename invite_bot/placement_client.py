"""
FreshMinds Placement Client — Asynchronous EtherNet Placement API Consumer
Directly connects to Ethiopian Ministry of Education Placement Endpoint:
https://student.ethernet.edu.et/api/v1/portal/placement/lookup
"""

import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, Any, NamedTuple

logger = logging.getLogger(__name__)

PLACEMENT_ENDPOINT = "https://student.ethernet.edu.et/api/v1/portal/placement/lookup"


class PlacementResult(NamedTuple):
    status: str  # 'SUCCESS', 'NOT_FOUND', 'RATE_LIMIT', 'SERVER_BUSY', 'TIMEOUT', 'ERROR'
    admission_no: str
    student_name: Optional[str] = None
    university: Optional[str] = None
    stream: Optional[str] = None
    school_name: Optional[str] = None
    region_name: Optional[str] = None
    total_score: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class PlacementClient:
    """Async HTTP Client for EtherNet University Placement Lookup."""

    def __init__(self, timeout_seconds: int = 15):
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Origin": "https://student.ethernet.edu.et",
            "Referer": "https://student.ethernet.edu.et/view-placement",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }

    async def query_placement(self, admission_no: str, first_name: str) -> PlacementResult:
        """
        Queries student placement by registration / admission number and first name.
        Sends JSON body:
          - registrationNumber: <id>
          - firstName: <name>
        """
        clean_reg = admission_no.strip()
        clean_first_name = first_name.strip()
        payload_data = {
            "registrationNumber": clean_reg,
            "firstName": clean_first_name,
        }

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers,
            ) as session:
                async with session.post(
                    PLACEMENT_ENDPOINT,
                    json=payload_data,
                    ssl=False,  # Avoid SSL issues on Ministry servers
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

                        if not isinstance(payload, dict):
                            payload = {}

                        # Extract fields returned by student.ethernet.edu.et API
                        fn = payload.get("firstName") or ""
                        mn = payload.get("middleName") or ""
                        ln = payload.get("lastName") or ""
                        name_parts = [fn, mn, ln]
                        constructed_name = " ".join(p for p in name_parts if p)

                        student_name = (
                            payload.get("fullName")
                            or constructed_name
                            or payload.get("studentName")
                            or payload.get("name")
                            or "N/A"
                        )

                        uni_obj = (
                            payload.get("resultUniversity")
                            or payload.get("university")
                            or payload.get("institution")
                            or payload.get("assignedUniversity")
                        )
                        if isinstance(uni_obj, dict):
                            uni_name = uni_obj.get("name") or uni_obj.get("title") or "N/A"
                            uni_abbr = uni_obj.get("abbreviation") or uni_obj.get("code")
                            university = f"{uni_name} ({uni_abbr})" if uni_abbr else uni_name
                        elif isinstance(uni_obj, str) and uni_obj.strip():
                            university = uni_obj.strip()
                        else:
                            university = "N/A"

                        stream_obj = (
                            payload.get("resultBand")
                            or payload.get("resultField")
                            or payload.get("streamName")
                            or payload.get("stream")
                        )
                        if isinstance(stream_obj, dict):
                            stream = stream_obj.get("name") or stream_obj.get("title") or "N/A"
                        elif isinstance(stream_obj, str) and stream_obj.strip():
                            stream = stream_obj.strip()
                        else:
                            stream = "N/A"


                        school_name = payload.get("schoolName") or "N/A"
                        region_name = payload.get("regionName") or "N/A"
                        total_val = payload.get("total")
                        total_score = str(total_val) if total_val is not None else "N/A"

                        # If university is missing or "N/A" and there's a not available message
                        if university == "N/A" and not payload.get("resultUniversity"):
                            # Check if student record not found / not placed
                            if payload.get("message"):
                                return PlacementResult(
                                    status="NOT_FOUND",
                                    admission_no=clean_reg,
                                    error_message=payload.get("message"),
                                )

                        return PlacementResult(
                            status="SUCCESS",
                            admission_no=clean_reg,
                            student_name=student_name,
                            university=university,
                            stream=stream,
                            school_name=school_name,
                            region_name=region_name,
                            total_score=total_score,
                            raw_data=payload,
                        )

                    elif status_code == 404:
                        return PlacementResult(
                            status="NOT_FOUND",
                            admission_no=clean_reg,
                            error_message="ተማሪው አልተገኘም ወይም የምደባ ቁጥሩ/ስሙ ተሳስቷል።",
                        )

                    elif status_code == 429:
                        logger.warning(f"Rate limit exceeded on MoE Placement endpoint for {clean_reg}")
                        return PlacementResult(
                            status="RATE_LIMIT",
                            admission_no=clean_reg,
                            error_message="የጥያቄ ብዛት በዝቷል። እባክዎ ጥቂት ሰከንድ ቆይተው እንደገና ይሞክሩ።",
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

