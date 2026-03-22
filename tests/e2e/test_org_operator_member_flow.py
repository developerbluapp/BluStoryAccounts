from typing import Annotated

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import text
from blustorymicroservices.BluStoryAccounts import settings
from blustorymicroservices.BluStoryAccounts.dependencies.clients import get_organisation_client
from blustorymicroservices.BluStoryAccounts.dependencies.externalclients import get_auth_provider, get_db_provider, get_pgsql_client, get_regression_db_provider
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.CreatedMemberResponse import CreatedMemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.members.MemberResponse import MemberResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorResponse import OperatorResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.OperatorSessionReponse import OperatorSessionResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.organisations.OrganisationSessionResponse import OrganisationSessionResponse
from blustorymicroservices.BluStoryAccounts.main import app
import uuid
import pytest
from blustorymicroservices.BluStoryAccounts.providers.pgsqlalchemy.SQLAlchemyDatabaseProvider import SQLAlchemyDatabaseProvider
from blustorymicroservices.BluStoryAccounts.settings.config import get_settings
from blustorymicroservices.BluStoryAccounts.tests.helpers.CleanUpDatabase import CleanUpDatabase
from blustorymicroservices.BluStoryAccounts.tests.mocks.auth_provider import MockAuthProvider
from blustorymicroservices.BluStoryAccounts.tests.mocks.organisation_client import MockOrganisationClient
from sqlalchemy.orm import Session

from blustorymicroservices.BluStoryAccounts.dependencies.externalclients import get_regression_db_provider


# Override the dependency in FastAPI app
app.dependency_overrides[get_db_provider] = get_regression_db_provider

app.dependency_overrides[get_organisation_client] = lambda: MockOrganisationClient()

@pytest.fixture(scope="function")
def supabase():
# 1. Get the session (resolving the yield)
    settings = get_settings()
    session_gen = get_pgsql_client(settings=settings) 
    session = next(session_gen)
    
    # 2. Get the provider
    provider = get_regression_db_provider(client=session)
    
    yield provider
    
    # 3. Clean up the session
    try:
        next(session_gen)
    except StopIteration:
        pass
@pytest.fixture(scope="function")
def mock_auth(supabase):
    return MockAuthProvider(db_provider=supabase)

client = TestClient(app)

@pytest.mark.e2e
def test_org_operator_member_flow(supabase, mock_auth):
    
    app.dependency_overrides[get_auth_provider] = lambda: mock_auth
 
    # -------------------------
    # Step 1: OrganisationAdmin signup
    # -------------------------

    
    org_email = f"org_{uuid.uuid4()}@test.com"
    username = f"member_{uuid.uuid4()}"
    org_name = f"Test Org {uuid.uuid4()}"
    member_name =  "John"
    

    signup_resp = client.post("/auth/organisation/signup", json={
        "email": org_email,
        "password": "password",
        "organisation_name": org_name
    })

    assert signup_resp.status_code == 201
    organisation_session = OrganisationSessionResponse(**signup_resp.json())
    organisation_admin_id = organisation_session.organisation.id
    organisation_id = organisation_session.organisation.organisation_id

    org_token = organisation_session.session.access_token

    # -------------------------
    # Step 2: OrganisationAdmin creates operator
    # -------------------------
    operator_resp = client.post(
        "/admin/operator",
        headers={"Authorization": f"Bearer {org_token}"}
    )

    assert operator_resp.status_code == 201
    created_operator_data = CreatedOperatorResponse(**operator_resp.json())
    operator_id = created_operator_data.id

    operator_session_resp = client.post(
        "/auth/operator/signin",
        json={"username":created_operator_data.username,
        "password":created_operator_data.password
        }
    )

    assert operator_session_resp.status_code == 201
    operator_session = OperatorSessionResponse(**operator_session_resp.json())

    operator_token = operator_session.session.access_token

    # -------------------------
    # Step 3: Operator creates member
    # -------------------------

    member_resp = client.post(
        "/members",
        headers={"Authorization": f"Bearer {operator_token}"},
        json={
            "username": username,
            "first_name": member_name 
        }
    )

    assert member_resp.status_code == 201
    member_data = CreatedMemberResponse(**member_resp.json())

    member_id = member_data.member.id
    assert member_data.member.username == username

    # -------------------------
    # Step 4: Get all members
    # -------------------------
    members_resp = client.get(
        "/members",
        headers={"Authorization": f"Bearer {operator_token}"}
    )

    assert members_resp.status_code == 200
    members = [MemberResponse(**m) for m in members_resp.json()]

    assert any(m.id == member_id for m in members)

    # -------------------------
    # Step 5: Get single member
    # -------------------------
    single_resp = client.get(
        f"/members/{member_id}",
        headers={"Authorization": f"Bearer {operator_token}"}
    )

    assert single_resp.status_code == 200
    single_member = MemberResponse(**single_resp.json())
    
    assert single_member.id == member_id
    assert single_member.username == username

    # 
    # Step 6: Check all records where created then remove
    #

    operator_resp = client.get(
        f"/admin/operator/{operator_id}",
        headers={"Authorization": f"Bearer {org_token}"}
    )
    print("test",operator_resp.json())
    operator_data = OperatorResponse(**operator_resp.json())
    assert operator_resp.status_code == 200
    assert operator_data.id == operator_id
    assert operator_data.username == created_operator_data.username

    CleanUpDatabase.cleanup_test_data(supabase,member_id,operator_id,organisation_admin_id,organisation_id)
    