from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer, CategoryWithItemsSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []

    @action(detail=False, url_path="with-items", methods=["get"])
    def with_items(self, request):
        qs = Category.objects.prefetch_related("items").order_by("sort_order", "path")
        serializer = CategoryWithItemsSerializer(qs, many=True)
        return Response(serializer.data)
