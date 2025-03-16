from django.db import models

class SubscriptionPlan(models.Model):
    """Defines available subscription plans"""
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    TIER_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='free')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    monthly_credits = models.PositiveIntegerField(default=0)
    trial_days = models.PositiveIntegerField(default=0)
    trial_credits = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    paypal_plan_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.tier} - {self.billing_cycle})"

    class Meta:
        unique_together = ('tier', 'billing_cycle')
        ordering = ['price']


class Feature(models.Model):
    """Defines features that can be included in subscription plans"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    FEATURE_TYPE_CHOICES = [
        ('standard', 'Standard Feature'),  # Unlimited use based on tier
        ('credit', 'Credit-Based Feature')  # Requires credits per use
    ]
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES, default='standard')

    credit_cost = models.PositiveIntegerField(default=0)  # Only relevant for credit-based features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({'Credit-Based' if self.feature_type == 'credit' else 'Standard'})"
    
    class Meta:
        ordering = ['display_order', 'name']


class PlanFeature(models.Model):
    """Maps features to subscription plans"""
    plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE, related_name='plan_features')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    is_highlighted = models.BooleanField(default=False)  # For marketing emphasis
    
    class Meta:
        unique_together = ('plan', 'feature')
    
    def __str__(self):
        return f"{self.plan.name} - {self.feature.name}"
