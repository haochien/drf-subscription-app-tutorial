# Frontend React Js Setup

## Django CORS setup

CORS (Cross-Origin Resource Sharing) is a security feature implemented by web browsers to prevent web pages from making requests to a different domain than the one that served the web page. 
This is to prevent potentially malicious websites from accessing sensitive information on other sites. 

When working with a React frontend and a Django backend, you might encounter CORS issues because your React app (served from localhost:3000) will be making API requests to your Django server (e.g., localhost:8000).

To handle CORS issues, you need to configure your Django backend to allow requests from your React frontend.

### 1. Update CORS setting in settings.py

#### a. install django-cors-headers

```sh
pip install django-cors-headers
```

#### b. settings.py configuration

```python
# settings.py


INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]


# It is suggested to be placed above CommonMiddleware
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

# To allow all origins (development):
CORS_ALLOW_ALL_ORIGINS = True

# To allow specific origins (production):
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-production-domain.com',
]

# Alternatively, you can use regex to allow origins:
# CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://\w+\.your-production-domain\.com$",]

# Allow credentials
CORS_ALLOWS_CREDENTIALS = True

```

> Tips:
>
> **1. the order of placement in MIDDLEWARE**:
>
> In Django, the order in which middleware is defined in the `MIDDLEWARE` setting is important because middleware is processed in the order it is listed for requests and in the reverse order for responses.
>
> For `CorsMiddleware`, it is generally recommended to place it above `CommonMiddleware`.
>
> * For `CorsMiddleware` Placement:
>
>   * Request Processing: Placing `CorsMiddleware` at the top ensures that CORS headers are added to the request before any other middleware processes the request. This is crucial for preflight requests (OPTIONS method) which browsers send to determine if the actual request is safe to send.
>
>   * Response Processing: Since middleware is processed in reverse order for responses, having `CorsMiddleware` at the top ensures that it is the last one to modify the response, thus adding the necessary CORS headers to the response after all other middleware have done their processing.
>
> * For `CommonMiddleware` Placement:
>
>   `CommonMiddleware` handles several tasks, such as URL normalization and adding trailing slashes to URLs. These tasks are generally not related to CORS and should be performed after the CORS checks.
>
> * Is it a Must?
>
>   While it's not strictly a must, it is a best practice to place `CorsMiddleware` above `CommonMiddleware` to ensure proper handling of CORS. If you place `CorsMiddleware` below `CommonMiddleware`, it might still work, but you could encounter issues with CORS headers not being correctly added to requests or responses, especially for preflight requests.
>
> **2. CORS_ALLOW_CREDENTIALS**:
>
> The `CORS_ALLOW_CREDENTIALS` setting in Django is used to determine whether cookies or HTTP authentication headers can be included in cross-origin requests. Whether or not you need to set `CORS_ALLOW_CREDENTIALS` to True depends on your application's requirements.
> 
> You should set `CORS_ALLOW_CREDENTIALS` to True if your frontend application needs to include credentials in its requests to the backend. This is typically necessary if:
>
> * Authentication: Your API requires the user to be authenticated and uses cookies or HTTP authentication headers to maintain the session.
>
> * Cookies: You are relying on session cookies for authentication or other purposes
