from django.urls import path
from .views import SignUpView,LoginView,UserSearchView, SendFriendRequestView, RespondFriendRequestView, ListFriendsView, ListPendingRequestsView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/respond/', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('friends/', ListFriendsView.as_view(), name='list-friends'),
    path('pending-requests/', ListPendingRequestsView.as_view(), name='list-pending-requests'),
]
