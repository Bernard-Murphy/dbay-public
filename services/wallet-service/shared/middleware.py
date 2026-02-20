import uuid
import logging
import time

logger = logging.getLogger('dbay.request')

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.path} ID: {getattr(request, 'request_id', 'unknown')}")
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {response.status_code} Duration: {duration:.4f}s ID: {getattr(request, 'request_id', 'unknown')}")
        
        return response
