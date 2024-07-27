import React from 'react';
import { useToggle, upperFirst, useMediaQuery } from '@mantine/hooks';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import {
  TextInput,
  PasswordInput,
  Title,
  Paper,
  Group,
  Button,
  Divider,
  Checkbox,
  Anchor,
  Stack,
  useMantineTheme 
} from '@mantine/core';
import GoogleLoginButton from './GoogleLoginButton';
import classes from './AuthForm.module.css';
import { register, login } from '../utils/auth';

const AuthForm = ({ isLogin, onLoginSuccess }) => {
  const theme = useMantineTheme();
  const isLargeScreen = useMediaQuery(`(min-width: ${theme.breakpoints.sm})`);

  const [type, toggle] = useToggle(['login', 'register']);
  const form = useForm({
    initialValues: {
      email: '',
      userName: '',
      password: '',
      terms: true,
    },

    validate: {
      email: (val) => (/^\S+@\S+$/.test(val) ? null : 'Invalid email'),
      password: (val) => (val.length < 8 ? 'Password should include at least 8 characters' : null),
    },
  });

  const handleSubmit = async (data) => {
    try {
      if (type === 'register') {
        await register(data.email, data.password, { display_name: data.userName });
        
        // TODO: send validation email after registering
        toggle()
        form.values.password = ''
      } else {
        await login(data.email, data.password);
        onLoginSuccess();
      }
    } catch (error) {
      console.log(error.response?.data?.detail || `${type === 'register' ? 'Register' :  'Login'} failed. Please try again.`)
    }

    

  };

  return (
    <>
    <Title ta="center" fw={500} mb="xl" order={1} >
      {type === 'register' ? 'Get Started' : 'Welcome Back'}
    </Title>

    <Paper className={classes.form} withBorder={isLargeScreen} >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        
        <Stack>
          {type === 'register' && (
            <TextInput
              required
              label="User Name"
              placeholder="Your name"
              value={form.values.userName}
              onChange={(event) => form.setFieldValue('userName', event.currentTarget.value)}
              radius="md"
            />
          )}

          <TextInput
            required
            label="Email"
            placeholder="hello@myemail.com"
            value={form.values.email}
            onChange={(event) => form.setFieldValue('email', event.currentTarget.value)}
            error={form.errors.email}
            radius="md"
          />

          <PasswordInput
            required
            label="Password"
            placeholder="Your password"
            value={form.values.password}
            onChange={(event) => form.setFieldValue('password', event.currentTarget.value)}
            error={form.errors.password}
            radius="md"
          />

          {type === 'register' && (
            <Checkbox
              required
              label="I accept terms and conditions"
              checked={form.values.terms}
              onChange={(event) => form.setFieldValue('terms', event.currentTarget.checked)}
            />
          )}
        </Stack>

        <Group justify="space-between" mt="xl">
          <Anchor component="button" type="button" c="dimmed" onClick={() => toggle()} size="xs">
            {type === 'register'
              ? 'Already have an account? Login'
              : "Don't have an account? Register"}
          </Anchor>
          <Button type="submit" radius="xl">
            {type === 'register' ? 'Register' :  'Login'}
          </Button>
        </Group>

        <Divider label="Or" labelPosition="center" my="lg" />

        <Group grow mb="md" mt="md">
          <GoogleLoginButton />
        </Group>

      </form>
    </Paper>
    </>
  );
};

export default AuthForm;