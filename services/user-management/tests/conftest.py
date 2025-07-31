import pytest
import asyncio
from typing import Generator, Any
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.api.v1.deps import get_db, get_public_db
from app.scripts.seed import seed_permissions
from app.api.v1.routers.connections import get_aadhaar_client

# This engine is created once and points to our test database
test_engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    A session-scoped fixture to create the test DB and tables before any tests run,
    and drop them after all tests are done.
    """
    # We need to import the db creation utilities here
    from sqlalchemy_utils import database_exists, create_database, drop_database

    if database_exists(test_engine.url):
        drop_database(test_engine.url)
    
    create_database(test_engine.url)
    Base.metadata.create_all(bind=test_engine)
    
    # Seed initial data like permissions
    session = TestingSessionLocal()
    asyncio.run(seed_permissions(session))
    session.close()
    
    yield # This is where all the tests will run
    
    drop_database(test_engine.url)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    """
    This is the primary fixture for providing a database session to tests.
    It creates a new transaction for a test and rolls it back at the end,
    ensuring test isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, Any, None]:
    """
    This fixture provides a TestClient. It depends on the `db_session` fixture
    and overrides the application's database dependencies to use that session.
    It also overrides the Aadhaar client with a mock.
    """
    # --- Define our Mock Aadhaar Client ---
    class MockAadhaarClient:
        def start_verification(self, aadhaar_number: str):
            if aadhaar_number.endswith("0000"): return None
            return {"transaction_id": f"mock_txn_{uuid.uuid4()}"}

        def complete_verification(self, transaction_id: str, otp: str, original_aadhaar: str):
            if otp != "123456": return None
            return {"abha_id": f"abha_for_{original_aadhaar}"}

    # --- Define the override functions ---
    def override_get_db():
        yield db_session

    def override_get_aadhaar_client():
        return MockAadhaarClient()

    # --- Apply ALL overrides to the FastAPI app ---
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_public_db] = override_get_db
    app.dependency_overrides[get_aadhaar_client] = override_get_aadhaar_client
    
    with TestClient(app) as c:
        yield c
    
    # Clean up the overrides after the test is done
    app.dependency_overrides.clear()

@pytest.fixture
def s3_mock(monkeypatch):
    """
    Fixture to mock the boto3 S3 client and its generate_presigned_url method.
    """
    class MockS3Client:
        def generate_presigned_url(self, ClientMethod, Params=None, ExpiresIn=3600, HttpMethod=None):
            # Return a predictable, fake URL for testing purposes
            bucket = Params["Bucket"]
            key = Params["Key"]
            return f"https://{bucket}.s3.amazonaws.com/{key}?mock_signature=true"

    def mock_boto3_client(*args, **kwargs):
        return MockS3Client()

    # Use monkeypatch to replace the real boto3.client with our mock version
    monkeypatch.setattr("boto3.client", mock_boto3_client)


@pytest.fixture
def aadhaar_api_mock(monkeypatch):
    """
    Fixture to mock the external Aadhaar verification API client.
    """
    class MockAadhaarVerificationResponse:
        def __init__(self, success=True, error_code=None, transaction_id=None, user_details=None):
            self._success = success
            self.error_code = error_code
            self.transaction_id = transaction_id
            self.user_details = user_details

        def is_success(self):
            return self._success

    class MockAadhaarClient:
        def start_verification(self, aadhaar_number: str):
            if aadhaar_number.endswith("0000"): # Simulate the "Mobile Not Linked" case
                return MockAadhaarVerificationResponse(success=False, error_code="AADHAAR_MOBILE_NOT_LINKED")
            # Simulate a successful OTP dispatch
            return MockAadhaarVerificationResponse(success=True, transaction_id=f"mock_txn_{uuid.uuid4()}")

        def complete_verification(self, transaction_id: str, otp: str, original_aadhaar: str):
            if otp != "123456":
                return MockAadhaarVerificationResponse(success=False, error_code="INVALID_OTP")
            
            # If OTP is correct, return mock user details
            return MockAadhaarVerificationResponse(
                success=True, 
                user_details={"abha_id": f"abha_for_{original_aadhaar}", "email": f"verified.{original_aadhaar}@email.com"}
            )

    # Replace any instance of our imaginary client with the mock version
    # Note: We need to decide where this client would live, e.g., 'app.core.aadhaar_client'
    # For now, we will mock it where it's used in the router.

    def get_mock_aadhaar_client():
        return MockAadhaarClient()

    # monkeypatch.setattr(
    #     connections_router, "get_aadhaar_client", get_mock_aadhaar_client
    # )
    