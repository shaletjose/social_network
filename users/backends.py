from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

class CaseInsensitiveEmailBackend(BaseBackend):
    """
    Custom authentication backend for case-insensitive email login.
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email__iexact=email)
        except ObjectDoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
