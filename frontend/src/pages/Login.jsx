import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { Container } from '@mantine/core';


function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const from = location.state?.from?.pathname || '/';

  const handleLoginSuccess = () => {
    navigate(from, { replace: true });
  };

  return (
    <Container size="xs" my={40} >
      <AuthForm onLoginSuccess={handleLoginSuccess} />
    </Container>
  );
}

export default Login;