import React, { useState } from 'react';
import AuthForm from '../components/AuthForm';
import { Container } from '@mantine/core';


function Login() {
  return (
    <Container size="xs" my={40} >
      <AuthForm />
    </Container>
  );
}

export default Login;