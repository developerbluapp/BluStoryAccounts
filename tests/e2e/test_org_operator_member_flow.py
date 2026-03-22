from typing import Annotated
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from blustorymicroservices.BluStoryAccounts.main import app
from blustorymicroservices.BluStoryAccounts.dependencies.clients import get_organisation_client
from blustorymicroservices.BluStoryAccounts.dependencies.externalclients import (
    get_auth_provider, 
    get_db_provider, 
    get_pgsql_client, 
    get_regression_db_provider
)
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.CreatedMemberResponse import CreatedMemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberResponse import MemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorSessionReponse import OperatorSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationSessionResponse import OrganisationSessionResponse
from blustorymicroservices.BluStoryAccounts.settings.config import get_settings
from blustorymicroservices.BluStoryAccounts.tests.helpers.CleanUpDatabase import CleanUpDatabase
from blustorymicroservices.BluStoryAccounts.tests.mocks.auth_provider import MockAuthProvider
from blustorymicroservices.BluStoryAccounts.tests.mocks.organisation_client import MockOrganisationClient

# -------------------------
# Dependency Overrides
# -------------------------
app.dependency_overrides[get_db_provider] = get_regression_db_provider
app.dependency_overrides[get_organisation_client] = lambda: MockOrganisationClient()

@pytest.fixture(scope="function")
def supabase():
    """Provides the SQLAlchemy provider and handles session lifecycle."""
    settings = get_settings()
    session_gen = get_pgsql_client(settings=settings) 
    session = next(session_gen)
    provider = get_regression_db_provider(client=session)
    
    yield provider
    
    try:
        next(session_gen)
    except StopIteration:
        pass

@pytest.fixture(scope="function")
def mock_auth(supabase):
    """Provides the stateful mock auth provider."""
    return MockAuthProvider(db_provider=supabase)

client = TestClient(app)

@pytest.mark.e2e
def test_org_operator_member_flow(supabase, mock_auth):
    # Inject the specific mock instance into the FastAPI app
    app.dependency_overrides[get_auth_provider] = lambda: mock_auth
 
    # -------------------------
    # Step 1: Organisation Admin Signup
    # -------------------------
    org_email = f"org_{uuid.uuid4()}@test.com"
    org_name = f"Test Org {uuid.uuid4()}"

    signup_resp = client.post("/auth/organisation/signup", json={
        "email": org_email,
        "password": "password",
        "organisation_name": org_name
    })

    assert signup_resp.status_code == 201
    org_session_data = OrganisationSessionResponse(**signup_resp.json())
    
    # 📍 DATABASE IDs
    organisation_admin_id = org_session_data.organisation.id
    organisation_id = org_session_data.organisation.organisation_id
    org_token = org_session_data.session.access_token

    # 📍 CRITICAL SYNC: 
    # Tell the mock to associate this token with the REAL ID created in Postgres.
    # This prevents the 'operators_organisation_id_fkey' violation.
    mock_auth.users_registry[org_token].app_metadata["organisation_id"] = str(organisation_id)

    # -------------------------
    # Step 2: Organisation Admin creates operator
    # -------------------------
    operator_resp = client.post(
        "/admin/operator",
        headers={"Authorization": f"Bearer {org_token}"}
    )

    assert operator_resp.status_code == 201
    created_operator_data = CreatedOperatorResponse(**operator_resp.json())
    operator_id = created_operator_data.id

    # Sign in as the operator to get an Operator Token
    op_signin_resp = client.post(
        "/auth/operator/signin",
        json={
            "username": created_operator_data.username,
            "password": created_operator_data.password
        }
    )

    assert op_signin_resp.status_code == 201
    op_session_data = OperatorSessionResponse(**op_signin_resp.json())
    operator_token = op_session_data.session.access_token

    # 📍 CRITICAL SYNC:
    # Ensure the operator token also carries the correct org_id for member creation.
    mock_auth.users_registry[operator_token].app_metadata["organisation_id"] = str(organisation_id)

    # -------------------------
    # Step 3: Operator creates member
    # -------------------------
    member_username = f"member_{uuid.uuid4()}"
    member_name = "John"

    member_resp = client.post(
        "/members",
        headers={"Authorization": f"Bearer {operator_token}"},
        json={
            "username": member_username,
            "first_name": member_name 
        }
    )

    assert member_resp.status_code == 201
    member_data = CreatedMemberResponse(**member_resp.json())
    member_id = member_data.member.id

    # -------------------------
    # Step 4: Verification & Cleanup
    # -------------------------
    
    # Get all members
    members_resp = client.get(
        "/members",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert members_resp.status_code == 200
    
    # Get single operator to verify admin access
    admin_get_op_resp = client.get(
        f"/admin/operator/{operator_id}",
        headers={"Authorization": f"Bearer {org_token}"}
    )
    assert admin_get_op_resp.status_code == 200
    
    # Final Cleanup
    #CleanUpDatabase.cleanup_test_data(
    #    supabase, 
    #    member_id, 
    #    operator_id, 
    #    organisation_admin_id, 
    #    organisation_id
    #)