from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from orders.models import Dispute
from orders.serializers import DisputeSerializer

class DisputeViewSet(viewsets.ModelViewSet):
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    
    def get_queryset(self):
        # Admin sees all, User sees theirs
        # For now return all
        return Dispute.objects.all()
