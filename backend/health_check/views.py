from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import logging
import time

logger = logging.getLogger(__name__)


def health_check_basic(request):
    """
    Basic health check - just confirms the application is responding
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'api',
        'timestamp': time.time()
    })


def health_check_db(request):
    """
    Checks database connectivity
    """
    start_time = time.time()
    try:
        # Try to connect to each database and execute a simple query
        for name in connections:
            cursor = connections[name].cursor()
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row is None:
                return JsonResponse({
                    'status': 'error',
                    'service': 'api',
                    'database': name,
                    'message': 'Database query returned no results',
                    'timestamp': time.time()
                }, status=500)
        
        response_time = time.time() - start_time
        return JsonResponse({
            'status': 'ok',
            'service': 'api',
            'database_response_time': response_time,
            'timestamp': time.time()
        })
    
    except OperationalError as e:
        logger.error(f"Database health check failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'service': 'api',
            'message': f'Database error: {str(e)}',
            'timestamp': time.time()
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error during database health check: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'service': 'api',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': time.time()
        }, status=500)
