from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import redis
import httpx
import os
import logging
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analytics Service", version="1.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")
TICKETS_SERVICE_URL = os.getenv("TICKETS_SERVICE_URL", "http://localhost:8124")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class TicketStats(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    avg_resolution_time: float


class UserActivity(BaseModel):
    user_id: int
    tickets_created: int
    tickets_assigned: int
    tickets_resolved: int


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "analytics-service"}


@app.get("/ready")
def readiness_check():
    try:
        redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis not ready: {str(e)}")


@app.get("/api/analytics/tickets/stats", response_model=TicketStats)
async def get_ticket_stats():
    cache_key = "analytics:tickets:stats"

    cached = redis_client.get(cache_key)
    if cached:
        logger.info("Returning cached ticket stats")
        return json.loads(cached)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TICKETS_SERVICE_URL}/api/tickets?limit=1000", timeout=10.0)
            response.raise_for_status()
            tickets = response.json()

        total = len(tickets)
        by_status = {}
        by_priority = {}

        for ticket in tickets:
            status = ticket.get("status", "unknown")
            priority = str(ticket.get("priority", 3))

            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        resolved_tickets = [t for t in tickets if t.get("status") == "resolved"]
        avg_resolution_time = 0.0

        if resolved_tickets:
            total_time = 0
            for ticket in resolved_tickets:
                created = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
                updated = datetime.fromisoformat(ticket["updated_at"].replace("Z", "+00:00"))
                total_time += (updated - created).total_seconds()

            avg_resolution_time = total_time / len(resolved_tickets) / 3600

        stats = TicketStats(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            avg_resolution_time=round(avg_resolution_time, 2)
        )

        redis_client.setex(cache_key, 300, stats.model_dump_json())

        return stats

    except httpx.HTTPError as e:
        logger.error(f"Error fetching tickets: {e}")
        raise HTTPException(status_code=503, detail="Could not fetch ticket data")


@app.get("/api/analytics/users/activity")
async def get_user_activity(user_id: int):
    cache_key = f"analytics:user:{user_id}:activity"

    cached = redis_client.get(cache_key)
    if cached:
        logger.info(f"Returning cached activity for user {user_id}")
        return json.loads(cached)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TICKETS_SERVICE_URL}/api/tickets?limit=1000", timeout=10.0)
            response.raise_for_status()
            tickets = response.json()

        tickets_created = sum(1 for t in tickets if t.get("reporter_id") == user_id)
        tickets_assigned = sum(1 for t in tickets if t.get("assignee_id") == user_id)
        tickets_resolved = sum(
            1 for t in tickets
            if t.get("assignee_id") == user_id and t.get("status") == "resolved"
        )

        activity = {
            "user_id": user_id,
            "tickets_created": tickets_created,
            "tickets_assigned": tickets_assigned,
            "tickets_resolved": tickets_resolved
        }

        redis_client.setex(cache_key, 300, json.dumps(activity))

        return activity

    except httpx.HTTPError as e:
        logger.error(f"Error fetching tickets: {e}")
        raise HTTPException(status_code=503, detail="Could not fetch ticket data")


@app.get("/api/analytics/performance")
def get_performance_metrics():
    return {
        "service": "analytics-service",
        "uptime": "99.9%",
        "cache_hit_rate": "85%",
        "avg_response_time_ms": 45,
        "requests_per_minute": 120
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8126)
