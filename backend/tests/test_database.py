from app.core.database import normalize_database_url


def test_normalize_database_url_supports_render_postgres_urls():
    assert (
        normalize_database_url("postgres://user:pass@example.com:5432/db")
        == "postgresql+psycopg://user:pass@example.com:5432/db"
    )


def test_normalize_database_url_supports_plain_postgresql_urls():
    assert (
        normalize_database_url("postgresql://user:pass@example.com:5432/db")
        == "postgresql+psycopg://user:pass@example.com:5432/db"
    )


def test_normalize_database_url_leaves_explicit_driver_urls_unchanged():
    assert (
        normalize_database_url("postgresql+psycopg://user:pass@example.com:5432/db")
        == "postgresql+psycopg://user:pass@example.com:5432/db"
    )
