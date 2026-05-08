from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
import pymysql

from .models import DataSourceInstance, DataSourceType


@dataclass(frozen=True)
class TableColumn:
    name: str
    data_type: str
    comment: str | None = None


def _strip_schema(schema: str) -> str:
    return (schema or "").strip()


def connect(instance: DataSourceInstance):
    if instance.db_type == DataSourceType.POSTGRES:
        return psycopg.connect(
            host=instance.host,
            port=instance.port,
            dbname=instance.database,
            user=instance.username,
            password=instance.password,
            connect_timeout=5,
        )
    if instance.db_type == DataSourceType.MYSQL:
        return pymysql.connect(
            host=instance.host,
            port=instance.port,
            db=instance.database,
            user=instance.username,
            password=instance.password,
            connect_timeout=5,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    raise ValueError("Unsupported db_type")


def list_tables_and_views(instance: DataSourceInstance) -> dict[str, Any]:
    if instance.db_type == DataSourceType.POSTGRES:
        schema = _strip_schema(instance.schema) or "public"
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select table_schema, table_name, table_type
                    from information_schema.tables
                    where table_schema = %s
                      and table_type in ('BASE TABLE','VIEW')
                    order by table_type, table_name
                    """,
                    (schema,),
                )
                rows = cur.fetchall()
        items = [{"schema": r[0], "name": r[1], "type": "view" if r[2] == "VIEW" else "table"} for r in rows]
        return {"schema": schema, "items": items}

    if instance.db_type == DataSourceType.MYSQL:
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select table_name, table_type
                    from information_schema.tables
                    where table_schema = %s
                    order by table_type, table_name
                    """,
                    (instance.database,),
                )
                rows = cur.fetchall()
        items = [{"schema": instance.database, "name": r["table_name"], "type": "view" if r["table_type"] == "VIEW" else "table"} for r in rows]
        return {"schema": instance.database, "items": items}

    raise ValueError("Unsupported db_type")


def get_table_columns(instance: DataSourceInstance, table_name: str, schema: str | None = None) -> list[TableColumn]:
    if instance.db_type == DataSourceType.POSTGRES:
        schema = _strip_schema(schema) or _strip_schema(instance.schema) or "public"
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                      c.column_name,
                      c.data_type,
                      pgd.description as comment
                    from information_schema.columns c
                    left join pg_catalog.pg_statio_all_tables st
                      on st.schemaname = c.table_schema and st.relname = c.table_name
                    left join pg_catalog.pg_description pgd
                      on pgd.objoid = st.relid and pgd.objsubid = c.ordinal_position
                    where c.table_schema = %s and c.table_name = %s
                    order by c.ordinal_position
                    """,
                    (schema, table_name),
                )
                rows = cur.fetchall()
        return [TableColumn(name=r[0], data_type=r[1], comment=r[2]) for r in rows]

    if instance.db_type == DataSourceType.MYSQL:
        with connect(instance) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select column_name, data_type, column_comment as comment
                    from information_schema.columns
                    where table_schema = %s and table_name = %s
                    order by ordinal_position
                    """,
                    (instance.database, table_name),
                )
                rows = cur.fetchall()
        return [TableColumn(name=r["column_name"], data_type=r["data_type"], comment=r.get("comment") or None) for r in rows]

    raise ValueError("Unsupported db_type")
