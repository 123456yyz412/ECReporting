from __future__ import annotations

from typing import Any

from apps.datasources.models import DataSourceType
from apps.datasources.services import connect


def run_query(
    *,
    db_type: str,
    instance,
    sql: str,
    params: dict[str, Any] | None = None,
    statement_timeout_ms: int = 30000,
    max_rows: int = 5000,
) -> dict[str, Any]:
    params = params or {}

    if db_type == DataSourceType.POSTGRES:
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute("begin")
                cur.execute("set transaction read only")
                # PostgreSQL does not accept bind parameters in SET statements with psycopg.
                cur.execute(f"set local statement_timeout = {int(statement_timeout_ms)}")
                cur.execute(sql, params)
                cols = [d.name for d in cur.description] if cur.description else []
                rows = cur.fetchmany(size=max_rows + 1)
                truncated = len(rows) > max_rows
                rows = rows[:max_rows]
                conn.rollback()
        data = [dict(zip(cols, r)) for r in rows]
        return {"columns": cols, "rows": data, "truncated": truncated}

    if db_type == DataSourceType.MYSQL:
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute(f"set session max_execution_time={int(statement_timeout_ms)}")
                cur.execute(sql, params)
                cols = [d[0] for d in cur.description] if cur.description else []
                rows = cur.fetchmany(size=max_rows + 1)
                truncated = len(rows) > max_rows
                rows = rows[:max_rows]
        if rows and isinstance(rows[0], dict):
            data = rows
        else:
            data = [dict(zip(cols, r)) for r in rows]
        return {"columns": cols, "rows": data, "truncated": truncated}

    raise ValueError("Unsupported db_type")
