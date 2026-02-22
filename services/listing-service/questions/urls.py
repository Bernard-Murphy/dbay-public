from django.urls import path
from .views import ListingQuestionViewSet, ListingAnswerViewSet

urlpatterns = [
    path(
        "listings/<uuid:listing_id>/questions/",
        ListingQuestionViewSet.as_view({"get": "list", "post": "create"}),
        name="listing-questions",
    ),
    path(
        "questions/<uuid:question_id>/answers/",
        ListingAnswerViewSet.as_view({"get": "list", "post": "create"}),
        name="question-answers",
    ),
]
