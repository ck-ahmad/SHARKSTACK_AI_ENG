from typing import Dict, Any, List
from datetime import datetime

class AnalyticsEngine:
    _metrics: List[Dict[str, Any]] = []

    @classmethod
    def record_request(cls, tenant_id: str, endpoint: str, latency_ms: float, tokens_used: int):
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "endpoint": endpoint,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "estimated_cost_usd": (tokens_used / 1000.0) * 0.002 # Example cost model
        }
        cls._metrics.append(metric)
        return metric

    @classmethod
    def get_tenant_analytics(cls, tenant_id: str) -> Dict[str, Any]:
        tenant_metrics = [m for m in cls._metrics if m["tenant_id"] == tenant_id]
        total_requests = len(tenant_metrics)
        total_tokens = sum(m["tokens_used"] for m in tenant_metrics)
        total_cost = sum(m["estimated_cost_usd"] for m in tenant_metrics)
        avg_latency = sum(m["latency_ms"] for m in tenant_metrics) / total_requests if total_requests > 0 else 0.0

        return {
            "tenant_id": tenant_id,
            "total_requests": total_requests,
            "total_tokens_consumed": total_tokens,
            "total_estimated_cost_usd": round(total_cost, 4),
            "average_latency_ms": round(avg_latency, 2)
        }
