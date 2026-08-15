from sqlalchemy import text, create_engine
from .config import settings


def main() -> None:
    engine = create_engine(settings.database_url, future=True)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO fees(program, level, year, campus, amount, currency, updated_at, source_url)
                VALUES (:program, :level, :year, :campus, :amount, :currency, now(), :url)
                ON CONFLICT DO NOTHING
                """
            ),
            dict(
                program="B.Tech CSE",
                level="UG",
                year="2025-26",
                campus="KTR",
                amount=250000,
                currency="INR",
                url="https://example.edu/fees",
            ),
        )
        conn.execute(
            text(
                """
                INSERT INTO deadlines(category, name, date, campus, program, updated_at, source_url)
                VALUES (:category, :name, CURRENT_DATE + INTERVAL '30 days', :campus, :program, now(), :url)
                """
            ),
            dict(
                category="admissions",
                name="Application Deadline",
                campus="KTR",
                program="B.Tech CSE",
                url="https://example.edu/deadlines",
            ),
        )
        conn.execute(
            text(
                """
                INSERT INTO contacts(role, name, email, phone, campus, updated_at, source_url)
                VALUES (:role, :name, :email, :phone, :campus, now(), :url)
                """
            ),
            dict(
                role="Admissions Office",
                name="SRM KTR Admissions",
                email="admissions@ktr.srm.edu",
                phone="+91-44-9999-0000",
                campus="KTR",
                url="https://example.edu/contacts",
            ),
        )


if __name__ == "__main__":
    main()


