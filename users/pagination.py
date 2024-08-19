from rest_framework.pagination import PageNumberPagination

class UserSearchPagination(PageNumberPagination):
    """Pagination class for user search results"""
    page_size = 10
