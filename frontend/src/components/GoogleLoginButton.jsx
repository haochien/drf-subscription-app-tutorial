import React from 'react';
import { Button } from '@mantine/core';

const GoogleLoginButton = () => {
  const handleGoogleLogin = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    const redirectUri = `${window.location.origin}/google/callback`;
    const scope = 'openid email profile';
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&prompt=consent`;

    window.location.href = authUrl;
  };

  return (
    <Button onClick={handleGoogleLogin} variant="outline" color="red" fullWidth>
      Login with Google
    </Button>
  );
};

export default GoogleLoginButton;