import pytest
from django.db.utils import IntegrityError
from users.models import User, Profile

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email="test@travelbridge.test", password="securepassword123")
    assert user.email == "test@travelbridge.test"
    assert user.check_password("securepassword123")
    assert user.is_active is True
    assert user.is_email_verified is False

@pytest.mark.django_db
def test_unique_email():
    User.objects.create_user(email="test@travelbridge.test", password="pw")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="test@travelbridge.test", password="pw2")
