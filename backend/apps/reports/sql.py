import re


_leading_comments = re.compile(r"^\s*(?:--[^\n]*\n|\s*/\*[\s\S]*?\*/\s*)*", re.IGNORECASE)


def is_safe_select_sql(sql: str) -> bool:
    if not sql:
        return False
    s = _leading_comments.sub("", sql).lstrip()
    head = s[:20].lower()
    return head.startswith("select") or head.startswith("with")

