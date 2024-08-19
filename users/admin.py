from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FriendRequest
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating new users."""
    class Meta:
        model = User
        fields = ('email', 'name')  # Include 'name' if it's a field in User

class CustomUserChangeForm(UserChangeForm):
    """Custom form for changing user details."""
    class Meta:
        model = User
        fields = ('email', 'name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.
    """
    model = User
    ordering = ['email']
    list_display = ('email', 'name', 'is_staff', 'is_active')  # Display fields in the list view

    fieldsets = (
        (None, {'fields': ('email', 'password', 'name')}),  # Fields to display on the user edit page
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')  # Allow searching by email and name
    filter_horizontal = ('groups', 'user_permissions',)  # Add horizontal filters for group and user permissions

    def delete_model(self, request, obj):
        """
        Simplified delete_model to just call super.
        """
        super().delete_model(request, obj)

# Register the User model with the custom admin interface
admin.site.register(User, CustomUserAdmin)

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    """Admin configuration for FriendRequest model"""
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
