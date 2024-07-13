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
    > For dev environment, Please input your dev local domain and port (e.g. for React Vite, you would need to enter <http://localhost:5173>).
    >
    > For future production environment, you would need to add your production domain here.
    >
    > Authorised redirect URIs:
    >
    > In the testing stage (this chapter), we will test on our OAuth redirect API without any frontend setup.
    >
    > Thus, we will set up an endpoint in Django <http://localhost:8000/api/auth/google/callback> and input this as redirect URI in Google OAuth.
    >
    > In the next chapter, we will change this part to an frontend url after the frontend login page is set up.
    >
    > More details will be covered later.

4. Get and copy Client ID and Client Secret

    ![image14](./Tutorial_Images/Google_OAuth/image14.png)

## Create Google OAuth Endpoint

Followings are the workflow to authenticate users by Google OAuth:

### 1. Send an Authentication Request to Google

The first step is to send a GET request with the appropriate URI parameters to Google <https://accounts.google.com/o/oauth2/v2/auth>.

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

After users finish the google login, they will be redirect to the redirect uri you provided in the request (i.e. `http://localhost:8000/api/auth/google/callback/`) with `code` attached.

`localhost:8000/api/auth/google/callback/?code=4%2F0ATx3LY6o4aM1fmw4aSE9Gxw4kPFgJZ1_Mbc8xj2OFrdroVxZxS5xmxdbiJ48XyFcAzcBNw&scope=email+profile+openid+`

We would need to use this code (the text between `?code=` and `&scope=`) to further fetch the user Google profile.

Please note that this redirect uri must be registered in Google (see step 3 in above [Setting up Google APIs](#setting-up-google-apis))

### 2. Create Google Callback Endpoint

We will now create a callback endpoint in our backend, so that we can process the request from Google redirection after the user login

In this endpoint, we include the `code` from previous step with our `client id` and `client secret` in the request sent to `https://oauth2.googleapis.com/token`.

If there is no error, the response will contain `access token`.

We will then use this `access token` to send a request to `https://www.googleapis.com/oauth2/v1/userinfo` and get the user profile data (e.g. email, name,...etc.)

Once we get the user profile data, we check whether this user is in our `User` table. If not, then we create the user and his/her profile.

In final, we generate an `access token` and `refresh token` via our Simple JWT mechanism for this user.

The way to use and refresh JWT access token here will be exactly same as [previous tutorial](./Tutorial6_DRF_JWT_Authentication_Setup.md)

The only difference is that the user need to login again via Google (instead of email login in Simple JWT case) once the refresh token we issued is expired.

```python
# ./backend/api_auth/views.py

class GoogleOAuth2CallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': env('GOOGL_CLIENT_ID'),
            'client_secret': env('GOOGL_SECRET'),
            'redirect_uri': env('GOOGLE_OAUTH2_REDIRECT_URI'),
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()

        if 'error' in token_data:
            return Response(token_data, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')

        # Retrieve user info
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        user_info_response = requests.get(user_info_url, params={'access_token': access_token})
        if not response.ok:
            raise ValidationError('Failed to obtain user info from Google.')
        
        user_info = user_info_response.json()
        email = user_info.get('email')
        user_name = user_info.get('name')
        first_name = user_info.get('given_name')

        # Create or get user
        user, created = User.objects.get_or_create(email=email)
        user.last_login = timezone.now()
        if created:
            user.register_method = "google"
            user.save()
        
        # Update profile
        Profile.objects.update_or_create(
            user=user,
            defaults={'display_name': user_name, 'first_name': first_name}
        )

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
```

```python
# ./backend/api_auth/urls.py

urlpatterns = [

    ...
    path('google/login/', views.GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', views.GoogleOAuth2CallbackView.as_view(), name='google_callback'),
]

```

If above steps are set up correctly, the callback function will correctly process the google request and you will receive a set of `access token` and `refresh token` in the response:

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyMDc2NTg4NywiaWF0IjoxNzIwNTA2Njg3LCJqdGkiOiI0M2ViMDRkNWU2OGY0MjQyODc0MDM3M2ZlNzllZWM5MiIsInVzZXJfaWQiOjF9.FgdwtMMMQ86OC76_YfrGzC3jxXgGv6K_0fTR7PTZfeg",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIwNTA3NTg3LCJpYXQiOjE3MjA1MDY2ODcsImp0aSI6ImZiODRlNGRhYjdlZDRmZDY4ODExZWMzMjdmYmQzMzllIiwidXNlcl9pZCI6MX0.5kTwTRsGneo8Oj7U4yJ2FWR_0QM3BhcHEnz7Fzfi_JA"
}
```

You can also check in the database whether the user data is successfully created in User table `auth_user` and profile table `profile`.

If you would like to understand Google OAuth more, you can check the Google [official document](https://developers.google.com/identity/openid-connect/openid-connect#python)
