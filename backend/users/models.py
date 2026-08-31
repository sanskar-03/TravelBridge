from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from common.models import BaseModel

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True, db_index=True)
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(BaseModel):
    class RoleChoice(models.TextChoices):
        TRAVELER = 'TRAVELER', 'Traveler'
        REQUESTER = 'REQUESTER', 'Requester'
        BOTH = 'BOTH', 'Both'

    class VerificationState(models.TextChoices):
        UNVERIFIED = 'UNVERIFIED', 'Unverified'
        PENDING = 'PENDING', 'Pending'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    role = models.CharField(max_length=20, choices=RoleChoice.choices, default=RoleChoice.BOTH, db_index=True)
    verification_status = models.CharField(max_length=20, choices=VerificationState.choices, default=VerificationState.UNVERIFIED, db_index=True)
    phone_number = models.CharField(max_length=30, blank=True)
    phone_verified = models.BooleanField(default=False)
    profile_visibility = models.CharField(max_length=20, default='public')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en')

    def __str__(self):
        return f"Profile for {self.user.email} ({self.role})"

    @property
    def completion_percentage(self):
        fields = [
            bool(self.display_name),
            bool(self.bio),
            bool(self.user.is_email_verified),
            bool(self.role)
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)
