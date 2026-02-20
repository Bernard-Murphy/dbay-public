from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Feedback
from .serializers import FeedbackSerializer
from .services import feedback_service
from users.models import SellerRating

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [] 

    def perform_create(self, serializer):
        # Validate order_id hasn't been used by this user for this target?
        # Usually one feedback per order.
        
        # Assume valid for now
        feedback = serializer.save(from_user=self.request.user)
        feedback_service.update_seller_rating(feedback.to_user.id)

    @action(detail=True, methods=['post'], url_path='reply')
    def reply(self, request, pk=None):
        feedback = self.get_object()
        if request.user != feedback.to_user:
            return Response({'error': 'Only recipient can reply'}, status=status.HTTP_403_FORBIDDEN)
            
        reply_text = request.data.get('reply')
        feedback.reply = reply_text
        feedback.replied_at = timezone.now()
        feedback.save()
        return Response(FeedbackSerializer(feedback).data)
