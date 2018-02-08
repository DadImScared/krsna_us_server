
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        """Change 'next' to 'nextPage' and 'previous' to 'previousPage' in paginated response"""
        return Response({
            'nextPage': self.get_next_link(),
            'previousPage': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })
