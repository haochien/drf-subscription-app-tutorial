from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    SubscriptionPlan
)

from .serializers import (
    SubscriptionPlanSerializer
)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view subscription plans"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    
    def list(self, request):
        """List subscription plans, grouped by tier"""
        plans = self.get_queryset()
        
        # Group by tier
        grouped_plans = {}
        for plan in plans:
            if plan.tier not in grouped_plans:
                grouped_plans[plan.tier] = []
            grouped_plans[plan.tier].append(self.get_serializer(plan).data)
        
        return Response(grouped_plans)

