import os
from pathlib import Path

# --- 1. DIRECTORY STRUCTURE ---
DIRECTORIES = [
    "backend/common",
    "backend/users",
    "backend/travel",
    "backend/packages",
    "backend/users/tests",
    "backend/travel/tests",
    "backend/packages/tests",
]

# --- 2. FILE DEFINITIONS ---
FILES = {
    # ==========================================
    # COMMON APP (Shared Architecture)
    # ==========================================
    "backend/common/__init__.py": "",
    "backend/common/apps.py": """from django.apps import AppConfig

class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
""",
    "backend/common/models.py": """import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    \"\"\"
    Abstract base model providing UUID primary key and timestamps.
    \"\"\"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
""",

    # ==========================================
    # USERS APP
    # ==========================================
    "backend/users/__init__.py": "",
    "backend/users/apps.py": """from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
""",
    "backend/users/models.py": """from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
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
    \"\"\"
    Core user model using email as the primary identity.
    \"\"\"
    email = models.EmailField(unique=True, db_index=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Trust/Verification Status
    is_email_verified = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(BaseModel):
    \"\"\"
    Extended user profile for marketplace display.
    \"\"\"
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=1000)
    
    def __str__(self):
        return f"Profile for {self.user.email}"
""",

    # ==========================================
    # TRAVEL APP
    # ==========================================
    "backend/travel/__init__.py": "",
    "backend/travel/apps.py": """from django.apps import AppConfig

class TravelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'travel'
""",
    "backend/travel/models.py": """from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models import BaseModel

class Location(BaseModel):
    \"\"\"
    Reusable structured location data.
    Privacy Note: Should represent cities, airports, or stations—NOT exact residential addresses.
    \"\"\"
    city = models.CharField(max_length=100, db_index=True)
    state_province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2) # ISO 3166-1 alpha-2

    class Meta:
        unique_together = ('city', 'state_province', 'country_code')
        indexes = [
            models.Index(fields=['country_code', 'city']),
        ]

    def __str__(self):
        return f"{self.city}, {self.country_code}"

class TravelPost(BaseModel):
    \"\"\"
    Represents a journey published by a traveler.
    \"\"\"
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        PAUSED = 'PAUSED', 'Paused'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    traveler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='travel_posts')
    
    origin = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='travels_from')
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='travels_to')
    
    departure_date = models.DateTimeField(db_index=True)
    arrival_date = models.DateTimeField(null=True, blank=True)
    
    # Baggage Info
    capacity_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(capacity_kg__gt=0), name='capacity_must_be_positive'),
        ]
        indexes = [
            models.Index(fields=['status', 'departure_date']),
            models.Index(fields=['origin', 'destination']),
        ]

    def __str__(self):
        return f"{self.traveler} | {self.origin} -> {self.destination}"
""",

    # ==========================================
    # PACKAGES APP
    # ==========================================
    "backend/packages/__init__.py": "",
    "backend/packages/apps.py": """from django.apps import AppConfig

class PackagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packages'
""",
    "backend/packages/models.py": """from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from common.models import BaseModel
from travel.models import Location

class PackageRequest(BaseModel):
    \"\"\"
    Represents a requester's need to transport an item.
    \"\"\"
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        MATCHING = 'MATCHING', 'Matching'
        MATCHED = 'MATCHED', 'Matched'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        DISPUTED = 'DISPUTED', 'Disputed'

    class ItemCategory(models.TextChoices):
        DOCUMENTS = 'DOC', 'Documents'
        CLOTHING = 'CLO', 'Clothing'
        ELECTRONICS = 'ELE', 'Electronics'
        PERSONAL = 'PER', 'Personal Items'
        GIFTS = 'GFT', 'Gifts'
        OTHER = 'OTH', 'Other'

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='package_requests')
    
    origin = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='packages_from')
    destination = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='packages_to')
    
    requested_pickup_date = models.DateTimeField()
    required_delivery_date = models.DateTimeField(db_index=True)
    
    weight_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.1'))]
    )
    
    # Structured dimensions: Length x Width x Height in cm
    length_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    width_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    category = models.CharField(max_length=3, choices=ItemCategory.choices, default=ItemCategory.OTHER)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(weight_kg__gt=0), name='weight_must_be_positive'),
        ]
        indexes = [
            models.Index(fields=['status', 'required_delivery_date']),
            models.Index(fields=['origin', 'destination']),
        ]

    def __str__(self):
        return f"Package {self.id} | {self.origin} -> {self.destination}"
""",

    # ==========================================
    # TESTS
    # ==========================================
    "backend/users/tests/test_models.py": """import pytest
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
""",

    # ==========================================
    # SETTINGS UPDATE INJECTION
    # ==========================================
    # (The script below will inject the new apps and AUTH_USER_MODEL into settings.py)
}

def inject_django_settings():
    settings_path = Path("backend/travelbridge/settings.py")
    if not settings_path.exists():
        print("❌ Cannot find settings.py. Ensure you are running this in the root directory.")
        return

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Append INSTALLED_APPS
    if "'common'" not in content:
        # Simple injection right before rest_framework
        content = content.replace(
            "'rest_framework',",
            "'common',\n    'users',\n    'travel',\n    'packages',\n    'rest_framework',"
        )
    
    # Append AUTH_USER_MODEL
    if "AUTH_USER_MODEL" not in content:
        content += "\n# ==========================================\n"
        content += "# CUSTOM USER MODEL\n"
        content += "# ==========================================\n"
        content += "AUTH_USER_MODEL = 'users.User'\n"

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Injected apps and AUTH_USER_MODEL into settings.py")

def append_handoff():
    handoff_path = Path("HANDOFF_STATE.md")
    part5_handoff = """
# Part 05 Handoff

## Django Apps
* `common`: Provides `BaseModel` for UUID primary keys and auditing timestamps.
* `users`: Houses the Custom User model (`AbstractBaseUser`) and marketplace `Profile`.
* `travel`: Houses `Location` and `TravelPost` models.
* `packages`: Houses `PackageRequest` and item categorization.

## User Architecture
Implemented a custom user model mapping identity primarily to `email` instead of `username`. Stripped all unnecessary personal identifiable information (PII). Passwords remain managed strictly by Django internals.

## Core Models & Database Constraints
* Primary Keys: Migrated to secure `UUIDField` globally to prevent sequential scraping.
* `capacity_kg` / `weight_kg`: Use `DecimalField` bounded by PostgreSQL `CheckConstraint` (> 0).
* Deletion behavior: Users cascade to Profiles. However, Users `PROTECT` Locations to prevent breaking historical route data.

## Indexes
Added composite and individual indexes optimizing for exact origin/destination matches, and status-based date queries (`status` + `departure_date`).

## API Foundation Status
Models are architected to support future DRF ViewSets. `AUTH_USER_MODEL` has been formally registered.

## Next Part
PART 06 — Authentication, Firebase Integration & Account Security
"""
    if handoff_path.exists():
        with open(handoff_path, 'a', encoding='utf-8') as f:
            f.write(part5_handoff)
        print("✅ Appended Part 05 to HANDOFF_STATE.md")

def create_scaffold():
    print("🚀 Initializing Part 05 (Database Architecture & Core Models)...\n")

    for directory in DIRECTORIES:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}/")

    for filename, content in FILES.items():
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if content:  # Don't write empty __init__.py if we just created them
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Created/Updated file: {filename}")
        else:
            filepath.touch(exist_ok=True)

    inject_django_settings()
    append_handoff()

    print("\n✅ Part 05 Setup complete!")
    print("\n👉 REQUIRED NEXT STEPS:")
    print("1. Start your backend Docker container (or keep it running).")
    print("2. Run the migrations to map these new models to PostgreSQL:")
    print("   docker-compose exec backend python manage.py makemigrations common users travel packages")
    print("   docker-compose exec backend python manage.py migrate")
    print("3. Verify tests:")
    print("   docker-compose exec backend pytest")

if __name__ == "__main__":
    create_scaffold()