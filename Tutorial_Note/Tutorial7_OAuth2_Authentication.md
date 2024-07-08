# Google Oauth2 Setup

Becides Simple JWT, we will also allow user to use google OAuth2 as an alternative login approach.

## Setting up Google APIs

To use Google login, you need to first register your application in [Google Developers Console](https://console.developers.google.com/). Please follow the steps below:

1. Create a New APIs project:

    ![image1](./Tutorial_Images/Google_OAuth/image1.png)
    ![image2](./Tutorial_Images/Google_OAuth/image2.png)
    ![image3](./Tutorial_Images/Google_OAuth/image3.png)

2. Update the OAuth Consent Screen:

    ![image4](./Tutorial_Images/Google_OAuth/image4.png)
    ![image5](./Tutorial_Images/Google_OAuth/image5.png)
    ![image6](./Tutorial_Images/Google_OAuth/image6.png)
    ![image8](./Tutorial_Images/Google_OAuth/image8.png)
    ![image9](./Tutorial_Images/Google_OAuth/image9.png)
    ![image10](./Tutorial_Images/Google_OAuth/image10.png)

3. Create New API Credentials

    ![image11](./Tutorial_Images/Google_OAuth/image11.png)

    ![image12](./Tutorial_Images/Google_OAuth/image12.png)

    ![image13](./Tutorial_Images/Google_OAuth/image13.png)

    >Hint:
    >
    > Authorised JavaScript origins:
    >
    > For dev environment, Please input your dev local domain and port (e.g. for React Vite, you would need to enter http://localhost:5173).
    >
    > For future production environment, you would need to add your production domain here.
    >
    > Authorised redirect URIs:
    >
    > In the testing stage (this chapter), we will test on our OAuth redirect API without any frontend setup.
    >
    > Thus, we will set up an endpoint in Django (http://localhost:8000/api/auth/google/callback) and input this as redirect URI in Google OAuth.
    >
    > In the next chapter, we will change this part to an frontend url after the frontend login page is set up.
    >
    > More details will be covered later.

4. Get and copy Client ID and Client Secret

    ![image14](./Tutorial_Images/Google_OAuth/image14.png)

## Create Google OAuth Endpoint

Followings are the workflow to authenticate users by Google OAuth:

### 1. Send an Authentication Request to Google

The first step is to send a GET request with the appropriate URI parameters to Google (https://accounts.google.com/o/oauth2/v2/auth).

You can send the request via postman or any approach. For easier testing, we could create a Google Login endpoint in our backend `http://localhost:8000/api/auth/google/login`.

```env
# ./backend/.env

...
GOOGL_CLIENT_ID=your_client_id_from_google
GOOGL_SECRET=your_client_secret_from_google
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/
```

```python
# ./backend/api_auth/views.py

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth?'
            'redirect_uri={redirect_uri}&'
            'prompt=consent&'
            'response_type=code&'
            'client_id={client_id}&'
            'scope=openid%20email%20profile'
        ).format(
            redirect_uri=env('GOOGLE_OAUTH2_REDIRECT_URI'),
            client_id=env('GOOGL_CLIENT_ID'),
        )
        return redirect(auth_url)
```

```python
# ./backend/api_auth/urls.py

urlpatterns = [
    ...
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
]
```

Once request is sent, we will be redirect to the Google login page. 

![image15](./Tutorial_Images/Google_OAuth/image15.png)

After users finish the google login, they will be redirect to the redirect uri you provided in the request (i.e. `http://localhost:8000/api/auth/google/callback/`).

Please note that this redirect uri must be registered in Google (see step 3 in above [Setting up Google APIs](#setting-up-google-apis))

### 2. Create Google Callback Endpoint

We will now create a callback endpoint in our backend, so that we can process the request from Google redirection after the user login

```python

```
