from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text


def lookup_fees(db: Session, filters: Dict[str, Any]) -> List[dict]:
    sql = text(
        "SELECT program, level, year, campus, amount, currency, updated_at, source_url FROM fees WHERE program=:program AND campus=:campus AND year=:year"
    )
    rows = db.execute(sql, filters).mappings().all()
    return [dict(r) for r in rows]


def lookup_deadlines(db: Session, filters: Dict[str, Any]) -> List[dict]:
    sql = text(
        "SELECT category, name, date, campus, program, updated_at, source_url FROM deadlines WHERE campus=:campus AND program=:program"
    )
    rows = db.execute(sql, filters).mappings().all()
    return [dict(r) for r in rows]


def lookup_contacts(db: Session, filters: Dict[str, Any]) -> List[dict]:
    sql = text(
        "SELECT role, name, email, phone, campus, updated_at, source_url FROM contacts WHERE campus=:campus"
    )
    rows = db.execute(sql, filters).mappings().all()
    return [dict(r) for r in rows]


