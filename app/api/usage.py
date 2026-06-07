from collections import defaultdict
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud.usage import get_deployment_usage
from app.database import get_db

router = APIRouter(
    prefix="/usage",
    tags=["usage"],
)

INPUT_PRICE_PER_1000 = 0.001
OUTPUT_PRICE_PER_1000 = 0.002


def _parse_iso8601(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid 'from' or 'to' timestamp") from exc


def _round_cost(value: float) -> float:
    return round(value, 6)


@router.get("/", status_code=200)
async def get_usage(
    api_key: str = Query(..., description="API key used to identify the deployment owner"),
    from_: str = Query(..., alias="from", description="Start of the usage window"),
    to: str = Query(..., description="End of the usage window"),
    group_by: Literal["day", "model"] = Query("day", description="Grouping mode for the usage summary"),
    db: Session = Depends(get_db),
):
    """Return aggregated usage totals and estimated cost for the requested range."""
    start = _parse_iso8601(from_)
    end = _parse_iso8601(to)

    if start > end:
        raise HTTPException(status_code=400, detail="'from' must be before or equal to 'to'")

    usage_rows = await get_deployment_usage(db, api_key=api_key, start=start, end=end)

    grouped = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "estimated_cost": 0.0})

    for row in usage_rows:
        key = row.timestamp.astimezone(timezone.utc).date().isoformat() if group_by == "day" else (row.model or "unknown")
        bucket = grouped[key]
        bucket["input_tokens"] += row.input_tokens or 0
        bucket["output_tokens"] += row.output_tokens or 0
        bucket["total_tokens"] += (row.input_tokens or 0) + (row.output_tokens or 0)

    breakdown = []
    total_input_tokens = 0
    total_output_tokens = 0

    for label, bucket in grouped.items():
        input_cost = _round_cost(bucket["input_tokens"] / 1000 * INPUT_PRICE_PER_1000)
        output_cost = _round_cost(bucket["output_tokens"] / 1000 * OUTPUT_PRICE_PER_1000)
        total_cost = _round_cost(input_cost + output_cost)
        bucket["estimated_cost"] = total_cost
        total_input_tokens += bucket["input_tokens"]
        total_output_tokens += bucket["output_tokens"]

        breakdown.append({
            "group": label,
            "input_tokens": bucket["input_tokens"],
            "output_tokens": bucket["output_tokens"],
            "total_tokens": bucket["total_tokens"],
            "estimated_cost": total_cost,
            "model": label if group_by == "model" else None,
            "day": label if group_by == "day" else None,
        })

    total_tokens = total_input_tokens + total_output_tokens
    total_cost = _round_cost(total_input_tokens / 1000 * INPUT_PRICE_PER_1000 + total_output_tokens / 1000 * OUTPUT_PRICE_PER_1000)

    return {
        "api_key": api_key,
        "from": from_,
        "to": to,
        "group_by": group_by,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "breakdown": breakdown,
    }