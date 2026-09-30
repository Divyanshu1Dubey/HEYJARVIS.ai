"""
Tests for API endpoints.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    """Test health endpoints."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_demo_info(self, client):
        response = client.get("/api/v1/auth/demo")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "demo"
        assert "tenant" in data
        assert "clinic" in data


class TestPatients:
    """Test patient endpoints."""

    def test_list_patients(self, client):
        response = client.get("/api/v1/patients/")
        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        assert "total" in data

    def test_get_patient(self, client):
        response = client.get("/api/v1/patients/p1")
        assert response.status_code == 200
        data = response.json()
        assert "first_name" in data


class TestConversations:
    """Test conversation endpoints."""

    def test_list_conversations(self, client):
        response = client.get("/api/v1/conversations/")
        assert response.status_code == 200

    def test_chat(self, client):
        response = client.post(
            "/api/v1/conversations/c1/chat",
            json={"conversation_id": "c1", "message": "Hello, I'd like to book"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


class TestRecapture:
    """Test recapture endpoints."""

    def test_list_opportunities(self, client):
        response = client.get("/api/v1/recapture/opportunities")
        assert response.status_code == 200
        data = response.json()
        assert "opportunities" in data

    def test_get_summary(self, client):
        response = client.get("/api/v1/recapture/opportunities/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_patients" in data
        assert "total_potential_revenue" in data


class TestCampaigns:
    """Test campaign endpoints."""

    def test_list_campaigns(self, client):
        response = client.get("/api/v1/campaigns/")
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data

    def test_create_campaign(self, client):
        response = client.post(
            "/api/v1/campaigns/",
            json={
                "tenant_id": "demo-tenant",
                "clinic_id": "demo-clinic",
                "name": "Test Campaign",
                "recapture_type": "lead_abandoned",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Campaign"


class TestAnalytics:
    """Test analytics endpoints."""

    def test_get_summary(self, client):
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_patients" in data

    def test_get_revenue(self, client):
        response = client.get("/api/v1/analytics/revenue")
        assert response.status_code == 200

    def test_channel_performance(self, client):
        response = client.get("/api/v1/analytics/channel-performance")
        assert response.status_code == 200
