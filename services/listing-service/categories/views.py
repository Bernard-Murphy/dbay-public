from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, CategoryItem
from .serializers import CategorySerializer, CategoryWithItemsSerializer, CategoryItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []

    @action(detail=False, url_path="with-items", methods=["get"])
    def with_items(self, request):
        qs = Category.objects.prefetch_related("items").order_by("sort_order", "path")
        serializer = CategoryWithItemsSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="items", methods=["get", "post"])
    def items_list(self, request, pk=None):
        category = self.get_object()
        if request.method == "GET":
            items = category.items.all().order_by("sort_order", "name")
            return Response(CategoryItemSerializer(items, many=True).data)
        # POST
        ser = CategoryItemSerializer(data={**request.data, "category": category.id})
        ser.is_valid(raise_exception=True)
        ser.save(category=category)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @action(detail=True, url_path="items/(?P<item_pk>[^/.]+)", methods=["get", "put", "patch", "delete"])
    def item_detail(self, request, pk=None, item_pk=None):
        category = self.get_object()
        item = category.items.filter(pk=item_pk).first()
        if not item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == "GET":
            return Response(CategoryItemSerializer(item).data)
        if request.method == "DELETE":
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # PUT/PATCH
        partial = request.method == "PATCH"
        ser = CategoryItemSerializer(item, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
