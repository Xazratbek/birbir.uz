from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

class FavoritePagination(PageNumberPagination):
    page_size = 1
    page_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "favorite_count":self.page.paginator.count,
            "next":self.get_next_link(),
            "previous":self.get_previous_link(),
            "favorites": data
        })