from rest_framework.pagination import PageNumberPagination


class FoodGramPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
