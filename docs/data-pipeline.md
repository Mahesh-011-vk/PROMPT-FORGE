# PromptForge AI - Data Engineering & Analytics Pipeline

> **Module:** `app.analytics`  
> **Role:** Telemetry Collection, High-Performance Aggregations, and Predictive Cost Modeling

---

## 1. Event Telemetry Data Model

Every platform operation (generation, optimization, evaluation, agent synthesis) emits structured telemetry into the `UsageEvent` table:

```python
class UsageEvent(Base, UUIDMixin):
    event_name: str          # e.g., "prompt.generate", "prompt.optimize"
    user_id: str | None      # Correlation user identifier
    modality: str | None     # "text", "image", "video", "code"
    model_used: str | None   # "gpt-4o", "midjourney-v6", "claude-3-5-sonnet"
    latency_ms: int          # End-to-end execution time in milliseconds
    tokens: int              # Token consumption count
    cost: float              # Estimated dollar expenditure
    status: str              # "SUCCESS" or "ERROR"
    metadata: dict           # Quality score and contextual tags
    timestamp: datetime      # UTC timestamp (indexed)
```

---

## 2. Analytics Processing Engine (Pandas & NumPy)

The analytical aggregation pipeline transforms raw database rows into an analytical DataFrame using Pandas:

1. **Volume & Success Rates:**
   Calculates total event throughput and computes successful request percentages.
2. **Modality & Model Grouping:**
   Groups records by `modality` and `model_used`, aggregating:
   - Request counts and volume shares (%).
   - Total tokens consumed and token throughput per request.
   - Cumulative dollar expenditure.
   - Mean execution latency.
3. **Latency Distribution Percentiles:**
   Uses NumPy to compute empirical percentile distributions:
   - **p50 (Median):** Typical user experience latency.
   - **p90 / p95:** Tail latency for complex multi-agent calls.
   - **p99:** Outlier latency indicating upstream API throttling or retries.

---

## 3. Predictive Cost Burn Modeling

PromptForge AI projects organizational spending velocity based on rolling observation windows:
- **Daily Run Rate:** Computes observed daily expenditure:
  $$\text{Daily Burn} = \frac{\sum \text{Cost}}{\text{Observation Days}}$$
- **7-Day & 30-Day Projections:** Incorporates a conservative compounding growth coefficient ($5\%$ weekly, $15\%$ monthly) to anticipate budget requirements as usage scales.
- **Top Cost Contributors:** Identifies which modality (e.g. video rendering vs text reasoning) accounts for the largest fraction of expenditure.

---

## 4. Telemetry Export & Reporting

The system supports automated data export to CSV via `GET /api/v1/analytics/export`, enabling seamless ingestion into data lakes, Snowflake, or BigQuery for enterprise BI visualization.
