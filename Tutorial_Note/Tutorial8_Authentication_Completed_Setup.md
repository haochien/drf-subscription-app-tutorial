# Google Oauth2 Frontend Setup

In the previous tutorial, we covered the backend setup for the Google OAuth.

In this chapter, we will integrate frontend part.

However, the workflow will be slightly different than the previous chapter.

The frontend part will mainly deal with the request handling, and the backend part will focus on processing callback respond and generate access and refresh token.

The workflow will be as followings:

1. `ProtectedRoute` component in the frontend will always check whether the users are authenticated (i.e. whether access token is valid and stored in the `local storage`) when they land to the target page required authentication. In this step, the path of target page will be stored into users' `Session Storage` for later redirection.

2. `ProtectedRoute` will refresh access token if access token is expired and the refresh token is not expired. If refresh token is expired or the user does not have access token yet, `ProtectedRoute` will navigate users to `Login` page (`<frontend_domain>/login`).

3. In the `Login` page, users can register, login with email (Simple JWT), or login via Google account (Google OAuth).

    * `registration`: A post request will be sent to the backend endpoint `<backend_domain>/api/auth/register/`. If registeration succeeds, the fontend will switch to the login form. Users can then login with registered email and password. (We don't do automatical login after registration since we can include email verification after registration in the future.)

    * `Login with email`: A POST request will be sent to the backend endpoint `<backend_domain>/api/auth/token/`. If users login successfully, the returned `access token` and `refresh token` will be stored in to users' `local storage`. Then, users will be redirect to the target page based on the path stored in the `Session Storage`

    * `Login with Google Account`: When users trigger component `GoogleLoginButton` wrapped in `Login` page, following steps will be executed:
        1. The component `GoogleLoginButton` in the frontend sends the authentication reequest to Google <https://accounts.google.com/o/oauth2/v2/auth>
        2. Users login via Google Account.
        3. After Google login succeeds, Google redirects users back to the frontend callback page `<frontend_domain>/login/google/callback` with a `code` in the redirect url.
        4. Frontend callback page will then send a GET request with `code` from Google to backend endpoint `<backend_domain>/api/auth/google/callback/?code=${code}`.
        5. The backend callback view `GoogleOAuth2CallbackView` will send the request sent to <https://oauth2.googleapis.com/token>. The function will then use the returned Google access token to send a request to <https://www.googleapis.com/oauth2/v1/userinfo> and get the user profile data. User information will then be stored in the database, and the access token and refresh from Simple JWT will then be created and returned to the frontend.
        6. After getting and storing access and refresh token in users' `local storage`, users will be redirect to the target page based on the path stored in the `Session Storage`

## Setting up Google APIs