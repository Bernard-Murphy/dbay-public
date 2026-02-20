import uuid
from django.db import models
from users.models import User

class Feedback(models.Model):
    RATING_CHOICES = [
        ('POSITIVE', 'Positive'),
        ('NEUTRAL', 'Neutral'),
        ('NEGATIVE', 'Negative'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField(unique=True) # One feedback per order? Or per party? Usually buyer rates seller. Seller rates buyer? 
    # Let's assume buyer rates seller for now as per spec
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_received')
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    comment = models.TextField()
    reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating} from {self.from_user} to {self.to_user}"
