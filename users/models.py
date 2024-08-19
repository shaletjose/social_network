from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models, transaction
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Provides methods to create a regular user and a superuser.
    """
    def create_user(self, email, password=None, name=None, **extra_fields):
        """
        Create and return a regular user with an email, password, and optional name.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email, password, and additional permissions.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email as the username and an optional name.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional name field
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class FriendRequest(models.Model):
    """Model to manage friend requests"""
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"
