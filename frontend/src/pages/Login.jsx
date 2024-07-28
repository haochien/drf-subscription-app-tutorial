import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { Container } from '@mantine/core';
import { redirectAfterLogin } from '../utils/auth';


function Login() {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    redirectAfterLogin(navigate);
  };

  return (
    <Container size="xs" my={40} >
      <AuthForm onLoginSuccess={handleLoginSuccess} />
    </Container>
  );
}

export default Login;