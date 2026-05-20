from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from app.services.phase8_service import validate_upload
from app.utils.security import create_access_token, decode_access_token, hash_password, verify_password


REQUIRED_TABLES = {
    "users",
    "roles",
    "permissions",
    "userroles",
    "rolepermissions",
    "students",
    "employees",
    "authors",
    "publishers",
    "categories",
    "departmentcategories",
    "literaturecategories",
    "bookmasters",
    "bookauthors",
    "bookcopies",
    "issuerecords",
    "receiverecords",
    "reservations",
    "fines",
    "lostbooks",
    "damagedbooks",
    "notifications",
    "visitrecords",
    "auditrecords",
    "inventoryitems",
    "newarrivals",
    "documents",
    "importbatches",
    "importerrors",
    "settings",
    "activitylogs",
    "backups",
}


def test_app_starts_and_public_pages_render():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    login = client.get("/login")
    assert login.status_code == 200
    assert "KICSIT" in login.text


def test_model_metadata_contains_required_tables():
    assert REQUIRED_TABLES.issubset(set(Base.metadata.tables))


def test_password_hash_and_jwt_round_trip():
    password_hash = hash_password("ChangeMe@123")
    assert password_hash != "ChangeMe@123"
    assert verify_password("ChangeMe@123", password_hash)
    token = create_access_token("123")
    assert decode_access_token(token)["sub"] == "123"
    assert decode_access_token(token + "tampered") is None


def test_protected_routes_redirect_without_session():
    client = TestClient(app)
    for path in ["/dashboard", "/catalog", "/consumers/students", "/circulation/issue", "/backups"]:
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/login"


@pytest.mark.parametrize(
    ("filename", "content_type", "content", "allowed"),
    [
        ("sop.pdf", "application/pdf", b"%PDF-1.4", True),
        ("rates.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"xlsx", True),
        ("malware.exe", "application/octet-stream", b"MZ", False),
        ("empty.pdf", "application/pdf", b"", False),
        ("double.pdf.exe", "application/octet-stream", b"MZ", False),
    ],
)
def test_document_upload_validation(filename, content_type, content, allowed):
    upload = UploadFile(filename=filename, file=BytesIO(content), headers={"content-type": content_type})
    if allowed:
        assert validate_upload(upload) == len(content)
    else:
        with pytest.raises(ValueError):
            validate_upload(upload)


def test_upload_directories_are_not_committed_with_payloads():
    upload_roots = [Path("app/uploads"), Path("app/uploads/book_images"), Path("app/uploads/documents")]
    assert all(not path.exists() or path.is_dir() for path in upload_roots)
