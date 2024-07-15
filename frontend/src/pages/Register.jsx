import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextInput, PasswordInput, Button, Group, Box } from '@mantine/core';
import { register } from '../utils/auth';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await register(email, password, { display_name: displayName });
      navigate('/login');
    } catch (error) {
      console.error('Registration failed:', error);
      // Handle error (e.g., show error message)
    }
  };

  return (
    <Box mx="auto">
      <form onSubmit={handleSubmit}>
        <TextInput
          required
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <PasswordInput
          required
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <TextInput
          required
          label="Display Name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
        />
        <Group position="right" mt="md">
          <Button type="submit">Register</Button>
        </Group>
      </form>
    </Box>
  );
};

export default Register;