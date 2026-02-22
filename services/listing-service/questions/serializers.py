from rest_framework import serializers
from .models import ListingQuestion, ListingAnswer


class ListingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingAnswer
        fields = ("id", "question", "author_id", "body", "created_at")
        read_only_fields = ("id", "created_at")


class ListingQuestionSerializer(serializers.ModelSerializer):
    answers = ListingAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ListingQuestion
        fields = ("id", "listing_id", "author_id", "body", "created_at", "answers")
        read_only_fields = ("id", "created_at")
