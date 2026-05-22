from rest_framework.pagination import PageNumberPagination
from .models import Listing
from rest_framework.response import Response
from rest_framework import status

class ListingPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'sahifa'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "status": status.HTTP_200_OK,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "elonlar_soni": self.page.paginator.count,
            "elonlar": data,
        })