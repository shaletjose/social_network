from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, FriendRequest
from .serializers import UserSerializer, LoginSerializer, SignUpSerializer
from .pagination import UserSearchPagination
from django.core.cache import cache
from django.db.models import Q

def extract_error_messages(exception):
    """Helper function to extract error messages from exceptions."""
    error_messages = []
    if hasattr(exception, 'detail') and isinstance(exception.detail, dict):
        for field, errors in exception.detail.items():
            for error in errors:
                error_messages.append(str(error))
    else:
        error_messages.append(str(exception))
    return "; ".join(error_messages)

class SignUpView(generics.CreateAPIView):
    """API view for user signup"""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle user signup"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "status": 1,
                "message": "User created successfully",
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_message = extract_error_messages(e)
            return Response({
                "status": 0,
                "message": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = extract_error_messages(e)
            return Response({
                "status": 0,
                "message": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """API view for user login"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle user login"""
        serializer = LoginSerializer(data=request.data)
        
        try:
            # Validate the serializer
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate the user
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                # Generate or retrieve the token
                token, created = Token.objects.get_or_create(user=user)
                
                # Update the last login time
                update_last_login(None, user)
                
                return Response({
                    "status": 1,
                    "message": "Login successful",
                    "token": token.key
                }, status=status.HTTP_200_OK)
            
            return Response({"status": 0, "message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            # Handle serializer validation errors using the utility function
            return Response({
                "status": 0,
                "message": extract_error_messages(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle other exceptions using the utility function
            return Response({
                "status": 0,
                "message": extract_error_messages(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSearchView(generics.ListAPIView):
    """API view to search users by email or name"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserSearchPagination

    def get_queryset(self):
        """Return a filtered queryset based on the search keyword"""
        keyword = self.request.query_params.get('q', '').strip()
        
        if keyword:
            return User.objects.filter(
                Q(email__icontains=keyword) | Q(name__icontains=keyword)
            )
        return User.objects.none()

class SendFriendRequestView(generics.CreateAPIView):
    """API view to send a friend request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle sending a friend request"""
        sender = request.user
        receiver_id = request.data.get('receiver_id')

        if not receiver_id:
            return Response({"status": 0, "message": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            return Response({"status": 0, "message": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Rate limiting
            key = f"friend_requests_{sender.id}"
            requests = cache.get(key, 0)
            if requests >= 3:
                return Response({"status": 0, "message": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            cache.set(key, requests + 1, timeout=60)

            friend_request, created = FriendRequest.objects.get_or_create(sender=sender, receiver=receiver)
            if not created:
                return Response({"status": 0, "message": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": 1, "message": "Friend request sent"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": 0, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RespondFriendRequestView(generics.GenericAPIView):
    """API view to respond to a friend request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle accepting or rejecting a friend request"""
        user = request.user
        request_id = request.data.get('request_id')
        action = request.data.get('action')

        if action not in ['accept', 'reject']:
            return Response({"status": 0, "message": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.filter(id=request_id, receiver=user).first()
            if not friend_request:
                return Response({"status": 0, "message": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND)

            if action == 'accept':
                friend_request.status = 'accepted'
                friend_request.save()
            elif action == 'reject':
                friend_request.status = 'rejected'
                friend_request.save()

            return Response({"status": 1, "message": f"Friend request {action}ed"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": 0, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListFriendsView(generics.ListAPIView):
    """API view to list friends of the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return a list of friends of the authenticated user"""
        user = self.request.user
        friends = User.objects.filter(received_requests__sender=user, received_requests__status='accepted')
        return friends

class ListPendingRequestsView(generics.ListAPIView):
    """API view to list pending friend requests received by the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return a list of pending friend requests"""
        user = self.request.user
        pending_requests = FriendRequest.objects.filter(receiver=user, status='pending')
        sender_ids = pending_requests.values_list('sender_id', flat=True)
        return User.objects.filter(id__in=sender_ids)
