from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Listing, ListingImage, Watchlist
from .serializers import ListingSerializer, ListingImageSerializer, WatchlistSerializer
import boto3
import os
import uuid


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller_id=self.request.user.id)

    @action(detail=True, methods=['post'], url_path='images/presigned-url')
    def get_presigned_url(self, request, pk=None):
        listing = self.get_object()
        file_name = request.data.get('file_name')
        if not file_name:
            return Response({"error": "file_name required"}, status=status.HTTP_400_BAD_REQUEST)
        content_type = request.data.get('content_type', 'image/jpeg')
        file_ext = os.path.splitext(file_name)[1]
        unique_filename = f"{listing.id}/{uuid.uuid4()}{file_ext}"
        bucket_name = os.environ.get('AWS_S3_BUCKET_NAME', 'dbay-listing-images')
        s3_client = boto3.client('s3',
            endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        try:
            presigned_url = s3_client.generate_presigned_url('put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': unique_filename,
                    'ContentType': content_type
                },
                ExpiresIn=3600
            )
            return Response({
                'upload_url': presigned_url,
                's3_key': unique_filename
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='images/confirm')
    def confirm_image_upload(self, request, pk=None):
        listing = self.get_object()
        s3_key = request.data.get('s3_key')
        if not s3_key:
            return Response({"error": "s3_key required"}, status=status.HTTP_400_BAD_REQUEST)
        media_type = request.data.get('media_type', ListingImage.MEDIA_TYPE_IMAGE)
        file_size = request.data.get('file_size')
        if media_type == ListingImage.MEDIA_TYPE_VIDEO and file_size is not None:
            if file_size > ListingImage.max_video_size_bytes():
                return Response(
                    {"error": "Video must be 100MB or less"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        image = ListingImage.objects.create(
            listing=listing,
            s3_key=s3_key,
            media_type=media_type,
            file_size=file_size
        )
        serializer = ListingImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='watch')
    def watch(self, request, pk=None):
        listing = self.get_object()
        user_id = request.headers.get('X-User-ID') or 'test-user'
        
        watchlist, created = Watchlist.objects.get_or_create(user_id=user_id, listing=listing)
        if created:
            listing.watch_count += 1
            listing.save()
            
        return Response({'status': 'watched'})

    @action(detail=True, methods=['post'], url_path='unwatch')
    def unwatch(self, request, pk=None):
        listing = self.get_object()
        user_id = request.headers.get('X-User-ID') or 'test-user'
        
        deleted, _ = Watchlist.objects.filter(user_id=user_id, listing=listing).delete()
        if deleted:
            listing.watch_count = max(0, listing.watch_count - 1)
            listing.save()
            
        return Response({'status': 'unwatched'})

class WatchlistViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WatchlistSerializer
    
    def get_queryset(self):
        user_id = self.request.headers.get('X-User-ID') or 'test-user'
        return Watchlist.objects.filter(user_id=user_id)
