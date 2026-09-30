"""
Tests for demo data generation.
"""

from __future__ import annotations

import pytest
from packages.shared.demo_data import (
    get_demo_tenant,
    get_demo_clinic,
    get_demo_admin,
    get_demo_staff,
    seed_demo_data,
    get_demo_summary,
    _make_patients,
    _make_consents,
    _make_comm_prefs,
    _make_appointments,
    _make_campaigns,
)


class TestDemoData:
    """Test demo data generation."""

    def test_demo_tenant(self):
        tenant = get_demo_tenant()
        assert tenant["name"] == "Bright Smile Dental Group"
        assert tenant["slug"] == "bright-smile"
        assert tenant["status"] == "active"

    def test_demo_clinic(self):
        clinic = get_demo_clinic()
        assert clinic["name"] == "Bright Smile Dental"
        assert clinic["city"] == "Austin"
        assert clinic["state"] == "TX"
        assert "business_hours" in clinic

    def test_demo_admin(self):
        admin = get_demo_admin()
        assert admin["role"] == "owner"
        assert "@brightsmile.example.com" in admin["email"]

    def test_patients_generated(self):
        patients = _make_patients()
        assert len(patients) > 0
        assert all("id" in p for p in patients)
        assert all("first_name" in p for p in patients)
        assert all("state" in p for p in patients)

    def test_patient_categories(self):
        patients = _make_patients()
        states = set(p["state"] for p in patients)
        # Should have variety of patient states
        assert len(states) > 1

    def test_consents_generated(self):
        consents = _make_consents()
        assert len(consents) > 0
        assert all("patient_id" in c for c in consents)
        assert all("consent_type" in c for c in consents)

    def test_comm_prefs_generated(self):
        prefs = _make_comm_prefs()
        assert len(prefs) > 0
        assert all("patient_id" in p for p in prefs)
        assert all("channel" in p for p in prefs)

    def test_campaigns_generated(self):
        campaigns = _make_campaigns()
        assert len(campaigns) > 0
        assert all("name" in c for c in campaigns)
        assert all("recapture_type" in c for c in campaigns)

    def test_demo_summary(self):
        summary = get_demo_summary()
        assert summary["clinic"] == "Bright Smile Dental"
        assert summary["total_patients"] > 0
        assert summary["total_potential_revenue"] > 0

    def test_seed_demo_data(self):
        data = seed_demo_data()
        assert "tenants" in data
        assert "clinics" in data
        assert "patients" in data
        assert "campaigns" in data
        assert len(data["patients"]) > 0
