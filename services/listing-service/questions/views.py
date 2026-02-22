from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from .models import ListingQuestion, ListingAnswer
from .serializers import ListingQuestionSerializer, ListingAnswerSerializer


class ListingQuestionViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = ListingQuestionSerializer

    def get_queryset(self):
        listing_id = self.kwargs.get("listing_id")
        return ListingQuestion.objects.filter(listing_id=listing_id).prefetch_related("answers")

    def list(self, request, listing_id=None):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, listing_id=None):
        author_id = request.headers.get("X-User-ID") or "test-user-id"
        data = {**request.data, "listing_id": listing_id, "author_id": author_id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListingAnswerViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    serializer_class = ListingAnswerSerializer

    def get_queryset(self):
        question_id = self.kwargs.get("question_id")
        return ListingAnswer.objects.filter(question_id=question_id)

    def list(self, request, question_id=None):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, question_id=None):
        author_id = request.headers.get("X-User-ID") or "test-user-id"
        data = {**request.data, "question": question_id, "author_id": author_id}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
