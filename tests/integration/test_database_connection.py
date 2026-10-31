import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv()


@pytest.fixture(scope="module")
def test_engine():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    try:
        parsed_url = make_url(database_url)
    except Exception as exc:
        pytest.fail(f"Invalid TEST_DATABASE_URL: {exc}")

    test_db_name = parsed_url.database
    app_db_name = os.getenv("POSTGRES_DB")

    if not test_db_name:
        pytest.fail("TEST_DATABASE_URL must contain a database name")

    if app_db_name and test_db_name.lower() == app_db_name.lower():
        pytest.fail("TEST_DATABASE_URL must not point to the application database")

    if "test" not in test_db_name.lower():
        pytest.fail("Dedicated test database name must contain the word 'test'")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.mark.integration
def test_postgresql_connection(test_engine):
    with test_engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar()

    assert result == 1


@pytest.mark.integration
def test_pgvector_extension_available(test_engine):
    with test_engine.connect() as connection:
        version = connection.execute(
            text("""
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'vector'
            """)
        ).scalar()

    assert version is not None, "pgvector extension is not installed"


@pytest.mark.integration
def test_pgvector_vector_operation(test_engine):
    with test_engine.connect() as connection:
        distance = connection.execute(
            text("""
                SELECT '[1,2,3]'::vector
                <=>
                '[1,2,4]'::vector
            """)
        ).scalar()

    assert distance is not None
    assert float(distance) == pytest.approx(0.008539866, rel=1e-5)


@pytest.mark.integration
def test_pgvector_3072_dimensions(test_engine):
    vector_text = "[" + ",".join(["0"] * 3072) + "]"

    with test_engine.connect() as connection:
        dimensions = connection.execute(
            text("SELECT vector_dims(CAST(:vector AS vector))"),
            {"vector": vector_text},
        ).scalar()

    assert dimensions == 3072
