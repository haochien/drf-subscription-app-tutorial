import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { Container } from '@mantine/core';
import { googleLogin } from '../utils/auth';


function Login() {
  const navigate = useNavigate();

  /*
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
      handleGoogleCallback(code);
    }
  }, []);
  

  const redirectAfterLogin = () => {
    const redirectPath = sessionStorage.getItem('redirectPath') || '/';
    sessionStorage.removeItem('redirectPath');
    navigate(redirectPath, { replace: true });
  };

  const handleGoogleCallback = async (code) => {
    await googleLogin(code);
    redirectAfterLogin();
  };
  */

  const handleLoginSuccess = () => {
    redirectAfterLogin();
  };

  return (
    <Container size="xs" my={40} >
      <AuthForm onLoginSuccess={handleLoginSuccess} />
    </Container>
  );
}

export default Login;