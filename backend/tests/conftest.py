import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401


@pytest.fixture
def session(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as test_session:
        yield test_session
