# Mantine UI

1. `defaultColorScheme` prop, possible values are `light`, `dark` and `auto`

## TODO:

### rate limiting in DRF (per url and per auth group)

pip install djangorestframework django-ratelimit

requirements.txt
```
django-ratelimit>=4.0.0
```

settings.py

```python
# Rate limiting settings
REST_FRAMEWORK = {
    # Your existing settings...
    
    'DEFAULT_THROTTLE_CLASSES': [],  # We'll apply throttling at the view level
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',              # Unauthenticated users
        'user': '60/minute',              # Standard authenticated users
        'premium_user': '200/minute',     # Premium users
        'auth_attempts': '5/minute',      # Authentication attempts
        'sensitive_operations': '10/hour' # Password changes, deletion, etc.
    },
}
```

api_auth/throttling.py
```python
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AnonymousRateThrottle(AnonRateThrottle):
    scope = 'anon'

class UserRateThrottle(UserRateThrottle):
    scope = 'user'

class PremiumUserRateThrottle(UserRateThrottle):
    scope = 'premium_user'
    
    def get_cache_key(self, request, view):
        # Only apply this throttle to premium users
        user = request.user
        if user.is_authenticated and hasattr(user, 'profile') and getattr(user.profile, 'is_premium', False):
            return self.cache_format % {
                'scope': self.scope,
                'ident': user.pk
            }
        return None  # Skip this throttle for non-premium users

class AuthAttemptRateThrottle(AnonRateThrottle):
    scope = 'auth_attempts'

class SensitiveOperationRateThrottle(UserRateThrottle):
    scope = 'sensitive_operations'
```

In views
```python
# In api_auth/views.py
from .throttling import AnonymousRateThrottle, UserRateThrottle, PremiumUserRateThrottle, AuthAttemptRateThrottle, SensitiveOperationRateThrottle

# Example: standard API view with different throttles for auth/unauth users
class TestModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer
    throttle_classes = [AnonymousRateThrottle, UserRateThrottle, PremiumUserRateThrottle]

# Example: Login/token endpoint with strict throttling
class TokenObtainPairView(TokenObtainPairView):
    throttle_classes = [AuthAttemptRateThrottle]

# Example: Password reset with very strict throttling
class PasswordResetView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [SensitiveOperationRateThrottle]
    
    # Your view implementation...
```


```python

```


```python

```



### put cloudflare in front of Droplet

How to Set Up Cloudflare for Both Domains

Create a Cloudflare account if you don't have one already
Add both domains to Cloudflare:

Log into your Cloudflare dashboard
Click "Add a Site"
Enter "haodevelop.com" (your root domain)
Follow the steps to verify domain ownership and update nameservers

Configure DNS records:

Create an A record for "ui.haodevelop.com" pointing to your frontend server IP
Create an A record for "api.haodevelop.com" pointing to your DigitalOcean Droplet IP
Ensure the orange cloud icon is enabled for both (this means traffic is proxied through Cloudflare)

Configure SSL/TLS settings:

Go to SSL/TLS tab
Set encryption mode to "Full" or "Full (strict)"
Enable "Always Use HTTPS"

Set up security settings:

Configure security level (I recommend starting with "Medium")
Enable "Browser Integrity Check"
Consider enabling "WAF" (Web Application Firewall) for additional protection

Create specific rules for your API:

Go to "Security" → "WAF" → "Rate limiting rules"
Create a rate limiting rule specifically for API endpoints
Example: Limit requests to /api/* to 100 requests per minute per IP

Update Nginx Configuration
You'll need to update your Nginx configuration to work with Cloudflare:

```nginx
# In your nginx.digitalocean.ssl.conf

# Get real visitor IP (Cloudflare provides this in a header)
real_ip_header CF-Connecting-IP;
# Cloudflare IP ranges (keep updated)
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
# Add more Cloudflare IP ranges as needed

server {
    listen 443 ssl;
    server_name api.haodevelop.com;
    
    # Rest of your configuration...
}
```


Benefits of This Approach

Complete DDoS protection: Cloudflare absorbs attack traffic before it reaches either your frontend or backend servers.
Cost control: Your DigitalOcean Droplet will only see legitimate traffic that passes through Cloudflare's filters.
Performance improvements: Cloudflare's global CDN will cache static content and optimize connections.
Security in depth: Cloudflare's WAF adds another security layer beyond your rate limiting.ss