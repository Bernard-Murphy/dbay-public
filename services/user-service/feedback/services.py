from django.db import transaction
from django.db.models import Count, Q
from .models import Feedback
from users.models import SellerRating, User

class FeedbackService:
    @transaction.atomic
    def create_feedback(self, from_user_id, to_user_id, order_id, rating, comment):
        feedback = Feedback.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            order_id=order_id,
            rating=rating,
            comment=comment
        )
        self.update_seller_rating(to_user_id)
        return feedback

    def update_seller_rating(self, user_id):
        # Calculate scores
        stats = Feedback.objects.filter(to_user_id=user_id).aggregate(
            positive=Count('id', filter=Q(rating='POSITIVE')),
            neutral=Count('id', filter=Q(rating='NEUTRAL')),
            negative=Count('id', filter=Q(rating='NEGATIVE')),
        )
        
        pos = stats['positive']
        neu = stats['neutral']
        neg = stats['negative']
        total = pos + neu + neg
        
        # Simple score calculation: (Positive / Total) * 100? Or just count?
        # eBay style: Positive percentage.
        # But let's just store counts and calculate percentage on frontend or here.
        
        score = 0
        if total > 0:
            score = (pos / total) * 100
            
        rating, created = SellerRating.objects.get_or_create(user_id=user_id)
        rating.positive_count = pos
        rating.neutral_count = neu
        rating.negative_count = neg
        rating.score = score
        rating.save()

feedback_service = FeedbackService()
