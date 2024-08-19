from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'email']



class SignUpSerializer(serializers.ModelSerializer):
    """Serializer for user signup"""
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=False, allow_blank=True)  # Optional name field

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True}
        }

    def validate(self, data):
        """Validate password and confirmation match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords must match."})
        return data

    def create(self, validated_data):
        """Create a new user"""
        validated_data.pop('password_confirm')  # Remove password confirmation field
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')  # Handle optional name
        )
        return user

  

class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """Validate user credentials"""
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        return data



