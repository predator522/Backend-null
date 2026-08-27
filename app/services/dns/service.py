"""
Asynchronous DNS Reconnaissance & Inspection Service.
Uses dnspython async resolver to query A, AAAA, MX, NS, TXT, CNAME, and SOA records
concurrently without blocking the FastAPI event loop.
"""

import asyncio
import time
from typing import List
import dns.asyncresolver
import dns.exception
import dns.rdatatype
import dns.resolver

from app.config.settings import get_settings
from app.schemas.dns import DNSLookupResponse, DNSRecordsMap
from app.utils.logging import logger
from app.utils.validation import validate_domain

SUPPORTED_RECORD_TYPES: List[str] = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]


class DNSLookupService:
    """
    Dedicated DNS service executing non-blocking resource record queries.
    Never exposes raw Python tracebacks or blocks the async event loop.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = settings.DNS_RESOLVER_TIMEOUT
        self.resolver.lifetime = settings.DNS_RESOLVER_LIFETIME

    async def _query_single_record(self, domain: str, rtype: str) -> List[str]:
        """
        Safely resolve a single DNS record type for the target domain.
        Returns an empty list on NoAnswer, NXDOMAIN, or timeout.
        """
        try:
            answer = await self.resolver.resolve(domain, rtype)
            results: List[str] = []
            for rdata in answer:
                if rtype == "MX":
                    exchange = str(rdata.exchange).rstrip(".")
                    results.append(f"{rdata.preference} {exchange}")
                elif rtype == "SOA":
                    mname = str(rdata.mname).rstrip(".")
                    rname = str(rdata.rname).rstrip(".")
                    results.append(
                        f"{mname} {rname} (serial: {rdata.serial})"
                    )
                elif rtype == "TXT":
                    # Join byte strings inside TXT record
                    txt_parts = [
                        part.decode("utf-8", errors="replace")
                        for part in rdata.strings
                    ]
                    results.append("".join(txt_parts))
                else:
                    results.append(str(rdata).rstrip("."))
            return sorted(results)
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            dns.exception.DNSException,
        ):
            return []
        except Exception as exc:
            logger.debug(
                "Unexpected DNS resolver error for %s (%s): %s",
                domain,
                rtype,
                exc,
            )
            return []

    async def lookup(self, domain: str) -> DNSLookupResponse:
        """
        Execute parallel DNS queries across all 7 supported record types:
        A, AAAA, MX, NS, TXT, CNAME, SOA.
        """
        clean_domain = validate_domain(domain)
        start_time = time.perf_counter()

        # Query all 7 record types concurrently
        tasks = [
            self._query_single_record(clean_domain, rtype)
            for rtype in SUPPORTED_RECORD_TYPES
        ]
        results = await asyncio.gather(*tasks)

        records_dict = {
            rtype: records
            for rtype, records in zip(SUPPORTED_RECORD_TYPES, results)
        }

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return DNSLookupResponse(
            success=True,
            domain=clean_domain,
            records=DNSRecordsMap(**records_dict),
            query_duration_ms=duration_ms,
        )
