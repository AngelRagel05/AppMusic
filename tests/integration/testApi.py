from __future__ import annotations

from time import sleep

from app.api import createApi
from app.config.settings import Settings
from app.infrastructure.persistence.database.base import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def createClient() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def enableForeignKeys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )
    application = createApi(
        settings=Settings(database_url="sqlite://"),
        database_engine=engine,
        session_factory=session_factory,
    )
    return TestClient(application)


def test_health_uses_stable_camel_case_contract() -> None:
    with createClient() as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "appName": "SoundShelf",
        "environment": "development",
    }


def test_library_crud_and_empty_scan_task(tmp_path) -> None:
    library_path = tmp_path / "library"
    library_path.mkdir()

    with createClient() as client:
        created = client.post(
            "/api/libraries",
            json={
                "path": str(library_path),
                "displayName": "Pruebas",
            },
        )
        scan = client.post(
            f"/api/libraries/{created.json()['id']}/scan"
        )
        task_id = scan.json()["id"]

        for _ in range(100):
            task = client.get(f"/api/tasks/{task_id}").json()
            if task["status"] not in {"queued", "running", "cancelling"}:
                break
            sleep(0.01)

    assert created.status_code == 201
    assert created.json()["isActive"] is True
    assert scan.status_code == 200
    assert task["status"] == "completed"
    assert task["result"]["scanned_file_count"] == 0


def test_validation_errors_use_structured_error_contract() -> None:
    with createClient() as client:
        response = client.post(
            "/api/downloads",
            json={"localFolderId": 1, "sourceUrls": []},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_production_frontend_serves_assets_and_spa_routes(tmp_path) -> None:
    frontend_directory = tmp_path / "frontend"
    assets_directory = frontend_directory / "assets"
    assets_directory.mkdir(parents=True)
    (frontend_directory / "index.html").write_text(
        "<html><body>SoundShelf desktop</body></html>",
        encoding="utf-8",
    )
    (assets_directory / "app.js").write_text(
        "window.soundShelf = true;",
        encoding="utf-8",
    )

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    session_factory = sessionmaker(
        bind=engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )
    application = createApi(
        settings=Settings(
            database_url="sqlite://",
            frontend_directory=str(frontend_directory),
        ),
        database_engine=engine,
        session_factory=session_factory,
        bootstrap_database=False,
    )

    with TestClient(application) as client:
        index_response = client.get("/")
        route_response = client.get("/comparison")
        asset_response = client.get("/assets/app.js")
        missing_api_response = client.get("/api/not-found")

    assert index_response.status_code == 200
    assert route_response.text == index_response.text
    assert asset_response.text == "window.soundShelf = true;"
    assert missing_api_response.status_code == 404
