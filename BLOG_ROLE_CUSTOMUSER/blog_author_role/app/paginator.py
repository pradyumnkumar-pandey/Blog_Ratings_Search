from rest_framework.pagination import PageNumberPagination


class CustomPaginationClass(PageNumberPagination):
    page_size = 3
    #page_query_param='result'
