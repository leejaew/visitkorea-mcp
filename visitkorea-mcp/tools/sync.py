"""
Sync tool handler — delta sync list for incremental data updates.

Schema definition lives in schemas/sync_schema.py.
"""
from __future__ import annotations

from typing import Optional

from schemas.sync_schema import TOOLS
from utils.api_client import call_api

__all__ = ["TOOLS", "handle"]


async def handle(name: str, args: dict) -> Optional[dict]:
    if name == "get_sync_list":
        return await call_api("areaBasedSyncList2", {
            "numOfRows": args.get("numOfRows", 10),
            "pageNo": args.get("pageNo", 1),
            "modifiedtime": args.get("modifiedtime"),
            "showflag": args.get("showflag"),
            "arrange": args.get("arrange"),
            "contentTypeId": args.get("contentTypeId"),
            "oldContentid": args.get("oldContentid"),
            "lDongRegnCd": args.get("lDongRegnCd"),
            "lDongSignguCd": args.get("lDongSignguCd"),
            "lclsSystm1": args.get("lclsSystm1"),
            "lclsSystm2": args.get("lclsSystm2"),
            "lclsSystm3": args.get("lclsSystm3"),
        })

    return None
