import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_health_check_endpoint():
    client = Client()
    response = client.get(reverse('health-check'))
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    # Ensure no secrets or connection strings are leaked
    for key, value in data.items():
        assert "password" not in str(value).lower()
        assert "secret" not in str(value).lower()
