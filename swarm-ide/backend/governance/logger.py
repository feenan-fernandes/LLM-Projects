"""
governance/logger.py — Phase 7: OTel additive layer
Full trajectory logging to SQLite + optional OpenTelemetry span export.
When OTEL_EXPORTER_OTLP_ENDPOINT env var is set, each action emits an OTel
child span under the task's root span. Zero breaking changes to existing API.
"""
import os
import sqlite3
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'governance.db')

# ── OTel setup (additive, fails silently if not configured) ────────────────
_otel_tracer = None

def _get_tracer():
    global _otel_tracer
    if _otel_tracer is not None:
        return _otel_tracer
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if not endpoint:
        return None
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider = TracerProvider()
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _otel_tracer = trace.get_tracer("swarm-ide")
    except Exception:
        _otel_tracer = None
    return _otel_tracer


# ── SQLite schema ──────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trajectory (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id     TEXT,
            iteration   INTEGER,
            action_type TEXT,
            content     TEXT,
            tokens      INTEGER,
            latency_ms  INTEGER,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ── Public API ─────────────────────────────────────────────────────────────

def log_action(
    task_id: str,
    iteration: int,
    action_type: str,
    content: str,
    tokens: int,
    latency_ms: int,
) -> bool:
    """
    Logs one agent action to governance.db.
    Also emits an OTel child span if OTEL_EXPORTER_OTLP_ENDPOINT is configured.
    Returns True on success.
    """
    # 1. SQLite write (always)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO trajectory (task_id, iteration, action_type, content, tokens, latency_ms) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (task_id, iteration, action_type, content[:4000], tokens, latency_ms)
    )
    conn.commit()
    conn.close()

    # 2. OTel span (additive, non-blocking)
    tracer = _get_tracer()
    if tracer:
        try:
            from opentelemetry import trace
            with tracer.start_as_current_span(
                name=f"swarm.{action_type}",
                kind=trace.SpanKind.INTERNAL,
            ) as span:
                span.set_attribute("task_id", task_id)
                span.set_attribute("iteration", iteration)
                span.set_attribute("action_type", action_type)
                span.set_attribute("tokens", tokens)
                span.set_attribute("latency_ms", latency_ms)
                span.set_attribute("content_preview", content[:200])
        except Exception:
            pass  # Never let OTel failure break the agent loop

    return True


def get_task_trajectory(task_id: str) -> list[dict]:
    """Returns all trajectory rows for a given task_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'SELECT id, iteration, action_type, content, tokens, latency_ms, timestamp '
        'FROM trajectory WHERE task_id = ? ORDER BY id',
        (task_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "iteration": r[1], "action_type": r[2],
            "content": r[3], "tokens": r[4], "latency_ms": r[5], "timestamp": r[6]
        }
        for r in rows
    ]


def get_stats() -> dict:
    """Returns aggregate stats for the governance dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT task_id) FROM trajectory')
    total_tasks = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM trajectory')
    total_actions = c.fetchone()[0]
    c.execute('SELECT SUM(tokens) FROM trajectory')
    total_tokens = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM trajectory WHERE action_type='sandbox_violation'")
    violations = c.fetchone()[0]
    c.execute('SELECT AVG(latency_ms) FROM trajectory WHERE latency_ms > 0')
    avg_latency = round(c.fetchone()[0] or 0, 1)
    conn.close()
    return {
        "total_tasks": total_tasks,
        "total_actions": total_actions,
        "total_tokens": total_tokens,
        "sandbox_violations": violations,
        "avg_latency_ms": avg_latency,
    }


# Initialise on import
init_db()
