

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { googleLogin } from '../utils/auth';

function LoginGoogleCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
      handleGoogleCallback(code);
    }

  }, []);

  const handleGoogleCallback = async (code) => {
    await googleLogin(code);
    redirectAfterLogin();

  };

  const redirectAfterLogin = () => {
    const redirectPath = sessionStorage.getItem('redirectPath') || '/';
    sessionStorage.removeItem('redirectPath');
    navigate(redirectPath, { replace: true });
  };

  return <div>Check Authorization...</div>

}

export default LoginGoogleCallback;