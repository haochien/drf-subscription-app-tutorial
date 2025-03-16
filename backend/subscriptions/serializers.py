from rest_framework import serializers
from .models import (
    SubscriptionPlan,
    Feature,
    PlanFeature
)

class FeatureSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feature
        fields = ['id', 'name', 'description', 'feature_type', 'credit_cost']


class PlanFeatureSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(read_only=True)
    
    class Meta:
        model = PlanFeature
        fields = ['feature', 'is_highlighted']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    plan_features = PlanFeatureSerializer(many=True, read_only=True)
    features = serializers.SerializerMethodField()
    highlighted_features = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'tier', 'billing_cycle', 'price', 'description', 
            'plan_features', 'features', 'highlighted_features', 'monthly_credits', 
            'trial_days', 'trial_credits', 'is_active'
        ]
    
    def get_features(self, obj):
        return [pf.feature.name for pf in obj.plan_features.all()]
    
    def get_highlighted_features(self, obj):
        return [pf.feature.name for pf in obj.plan_features.filter(is_highlighted=True)]
