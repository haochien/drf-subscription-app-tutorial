import React, { useState } from 'react';
import { TextInput, PasswordInput, Button, Box, Alert } from '@mantine/core';

const AuthForm = ({ handleSubmit, isLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      await handleSubmit({ email, password, firstName, lastName });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box maw={300} mx="auto">
      <form onSubmit={onSubmit}>
        <TextInput
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <PasswordInput
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {!isLogin && (
          <>
            <TextInput
              label="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
            />
            <TextInput
              label="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
            />
          </>
        )}
        {error && <Alert color="red">{error}</Alert>}
        <Button type="submit" mt="md">{isLogin ? 'Login' : 'Register'}</Button>
      </form>
    </Box>
  );
};

export default AuthForm;