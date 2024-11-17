# Frontend React Js Setup

## Django CORS setup

CORS (Cross-Origin Resource Sharing) is a security feature implemented by web browsers to prevent web pages from making requests to a different domain than the one that served the web page.
This is to prevent potentially malicious websites from accessing sensitive information on other sites.

When working with a React frontend and a Django backend, you might encounter CORS issues because your React app (served from localhost:5173 or localhost:3000) will be making API requests to your Django server (e.g., localhost:8000).

To handle CORS issues, you need to configure your Django backend to allow requests from your React frontend.

### 1. Update CORS setting in settings.py

#### a. install django-cors-headers

install django-cors-headers if you did not install it in the Tutorial 1

```sh
pip install django-cors-headers==4.2.0
```

#### b. settings.py configuration

```python
# settings.py


INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]


# It is suggested to be placed above CommonMiddleware
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

# To allow all origins (development):
# CORS_ALLOW_ALL_ORIGINS = True

# To allow specific origins (production):
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://your-production-domain.com',
]

# Alternatively, you can use regex to allow origins:
# CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://\w+\.your-production-domain\.com$",]

# Allow credentials
CORS_ALLOWS_CREDENTIALS = True

```

> Tips:
>
> **1. the order of placement in MIDDLEWARE**:
>
> In Django, the order in which middleware is defined in the `MIDDLEWARE` setting is important because middleware is processed in the order it is listed for requests and in the reverse order for responses.
>
> For `CorsMiddleware`, it is generally recommended to place it above `CommonMiddleware`.
>
> * For `CorsMiddleware` Placement:
>
>   * Request Processing: Placing `CorsMiddleware` at the top ensures that CORS headers are added to the request before any other middleware processes the request. This is crucial for preflight requests (OPTIONS method) which browsers send to determine if the actual request is safe to send.
>
>   * Response Processing: Since middleware is processed in reverse order for responses, having `CorsMiddleware` at the top ensures that it is the last one to modify the response, thus adding the necessary CORS headers to the response after all other middleware have done their processing.
>
> * For `CommonMiddleware` Placement:
>
>   `CommonMiddleware` handles several tasks, such as URL normalization and adding trailing slashes to URLs. These tasks are generally not related to CORS and should be performed after the CORS checks.
>
> * Is it a Must?
>
>   While it's not strictly a must, it is a best practice to place `CorsMiddleware` above `CommonMiddleware` to ensure proper handling of CORS. If you place `CorsMiddleware` below `CommonMiddleware`, it might still work, but you could encounter issues with CORS headers not being correctly added to requests or responses, especially for preflight requests.
>
> **2. CORS_ALLOW_CREDENTIALS**:
>
> The `CORS_ALLOW_CREDENTIALS` setting in Django is used to determine whether cookies or HTTP authentication headers can be included in cross-origin requests. Whether or not you need to set `CORS_ALLOW_CREDENTIALS` to True depends on your application's requirements.
>
> You should set `CORS_ALLOW_CREDENTIALS` to True if your frontend application needs to include credentials in its requests to the backend. This is typically necessary if:
>
> * Authentication: Your API requires the user to be authenticated and uses cookies or HTTP authentication headers to maintain the session.
>
> * Cookies: You are relying on session cookies for authentication or other purposes

## Create React App via Vite

In this tutorial, we choose Vite to set up React Javascript project.

### 1. install Node Js to have access for npm

Install Node Js via [official website](https://nodejs.org)

after installation, use following command to check:

```sh
npm --version
```

### 2. Create React App

There are two common ways to create React app:

#### a. create-react-app

``` sh
# Create a new React project
npx create-react-app frontend

# Navigate to the project directory
cd frontend

# Start development server
npm start
```

#### b. Vite

``` sh
# Create a new Vite project
npm create vite@latest frontend --template react

# Navigate to the project directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

> Tips:
>
> When choosing between create-react-app (CRA) and Vite to set up a React project, it's essential to consider your specific needs and preferences.
>
> This Tutorial will suggest to use Vite. Create React App was deprecated in early 2023 ([comment from maintainers](https://github.com/reactjs/react.dev/pull/5487#issuecomment-1409720741)). It is not recommended to use it for new projects.
>
> But it's still imporatant to understand the pros and cons for each of them:
>
> **Create React App (CRA)**:
>
> PRO:
>
> * CRA is the official tool for setting up React projects and is widely used in the React community. It provides a stable and consistent environment.
> * CRA offers a zero-configuration setup, which is perfect for those who want to get started quickly without worrying about build configurations.
>
> CONS:
>
> * CRA's development server can be slower compared to more modern tools like Vite, especially in large projects.
> * The build times with CRA can be slower compared to Vite, which uses modern bundling techniques.
>
> **Vite**:
>
> PRO:
>
> * Vite is designed for speed. It uses ESBuild for faster development builds and Rollup for production builds, resulting in significantly faster build times and hot module replacement (HMR).
> * Vite is highly flexible and allows for easy customization without the need to eject.
>
> CONS:
>
> * Vite’s configuration might be more complex for beginners compared to CRA’s zero-configuration approach.
>

## Test API call

### 1. Remove inessential css file

delete `App.css` and remove `import './App.css'` in ``App.jsx`

delete `index.css` and remove `import './index.css'` in ``main.jsx`

### 2. create Interceptor

#### a. create `.env` file under project folder `frontend`

The variable in .env in Vite must starts with `VITE_`

```env
# .env

VITE_API_BASE_URL=http://localhost:8000/api
```

#### b. create `constants,js` file under project folder `src/`

```js
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh"
```

#### c. create `api.js` and under `src/`

```js
// ./src/api.js

import axios from 'axios';
import { API_BASE_URL, ACCESS_TOKEN } from './constants';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// for api calls required authentication
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

export default api;
```

#### d. update `App.jsx` and under `src/`

```jsx

import React, { useState, useEffect } from 'react';
import api from './api';

function App() {
  const [data, setData] = useState('');

  useEffect(() => {
    api.get('/auth/test')
      .then(response => {
        setData(response.data);
      });
  }, []);

  return (
    <>
      <p>{JSON.stringify(data)}</p>
    </>
  )
}

export default App

```

The folder structure of your project will now be:

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
├─ frontend/
│  ├─ public
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ api.js
│  │  ├─ constant.js
│  │  ├─ main.jsx
│  ├─ .env
│  ├─ package.json
├─ local_db/
```

#### e. start server and check the results

Before starting server in front end site, make sure your backend server is up (via `python manage.py runserver`).

In addition, make sure that you have posted the data to the test api already in the previous session.

Once these are all set, simply start frontend server via `npm run dev`.

You will see an array of test data is listed in the UI.

## Start first web pages in React App

### 1. Create new pages

create a `pages` folder under `./src`.

And then create `Home.jsx` and `TestAPI.jsx` under `./src/pages`

```js
// ./src/pages/Home.jsx

import React from 'react';

const Home = () => {

  return (
    <div>
      <h1>Home Page</h1>
      <p>Welcome to my website!</p>
    </div>
  );
};

export default Home;
```

```js
// ./src/pages/TestAPI.jsx

import React, { useEffect, useState } from 'react';
import api from '../api'; 

export const TestAPI = () => {
  const [data, setData] = useState('');

  useEffect(() => {
    api.get('/auth/test')
      .then(response => {
        setData(response.data);
      });
  }, []);

  return (
    <div>
      <h1>Test API Page</h1>
      <p>My API Data:</p>
      <p>{JSON.stringify(data)}</p>
    </div>
  );
};
```

### 2. Set up Router in App.jsx

With router setup, we can then navigate to Home page and TestAPI page.
You need to install `react-router-dom` first via the following command:

```sh
npm install react-router-dom
```

```js
// ./src/App.jsx

import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Home from "./pages/Home"
import { TestAPI } from './pages/TestAPI'; 

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/test" element={<TestPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

After all set up ready, start server via `npm run dev` and navigate to `http://localhost:5173` and `http://localhost:5173/test` to see the results.

## (Optional) UI Component Library Mantine Setup

To speed up frontend development, this tutorial utilizes an open source UI component library [`Mantine`](https://ui.mantine.dev/) to build the frontend.

There are way more UI (e.g. MUI, Tailwind UI, Next UI, Shadcn UI, Chakra UI, Ant Design, etc.) you can choose. You can also use vanilla CSS to build your frontend.

Followings are the step to set up `Mantine` in the react project. You can also review the [office document](https://mantine.dev/getting-started/)

### 1. Download packages

Download required packages via `npm`.

In this tutorial, let's download all packages

```sh
npm install @mantine/core @mantine/hooks @mantine/nprogress @mantine/modals @mantine/spotlight @mantine/carousel embla-carousel-react @mantine/dropzone @mantine/tiptap @tabler/icons-react @tiptap/react @tiptap/extension-link @tiptap/starter-kit @mantine/code-highlight @mantine/notifications @mantine/dates dayjs @mantine/charts recharts@2 @mantine/form
```

### 2. PostCSS setup

Install `PostCSS` plugins and `postcss-preset-mantine`.

`PostCSS` is a tool for transforming styles with JS plugins. These plugins can lint your CSS, support variables and mixins, transpile future CSS syntax, inline images, and more.

```sh
npm install --save-dev postcss postcss-preset-mantine postcss-simple-vars
```

Create postcss.config.cjs file at the root of your application with the following content

```cjs
module.exports = {
  plugins: {
    'postcss-preset-mantine': {},
    'postcss-simple-vars': {
      variables: {
        'mantine-breakpoint-xs': '36em',
        'mantine-breakpoint-sm': '48em',
        'mantine-breakpoint-md': '62em',
        'mantine-breakpoint-lg': '75em',
        'mantine-breakpoint-xl': '88em',
      },
    },
  },
};
```

### 3. Create theme.js under src folder

Mantine theme is an object where your application's colors, fonts, spacing, border-radius and other design tokens are stored.

You can customize `theme.js` to override the default styling in Mantine and have your own global style and theme.

We can leave this fill temporarily empty.

```js
import { createTheme } from '@mantine/core';

export const theme = createTheme({

});
```

### 4. Update root component App.jsx

```js
// ./src/App.jsx

// Import styles of packages that you've installed.
// All packages except `@mantine/hooks` require styles imports
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import { theme } from './theme';

import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Home from "./pages/Home"
import { TestAPI } from './pages/TestAPI'; 

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/test" element={<TestPage />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  )
}

export default App
```

### 5. Run server

Run the server via `npm run dev` to check whether the frontend still works as expected.

The folder structure in current stage of your project will be:

```plaintext
drf-subscription-app-Tutorial/
├─ backend/
├─ frontend/
│  ├─ public
│  ├─ src
│  │  ├─ App.jsx
│  │  ├─ api.js
│  │  ├─ constant.js
│  │  ├─ main.jsx
│  │  ├─ theme.js
│  ├─ .env
│  ├─ postcss.config.cjs
│  ├─ package.json
├─ local_db/
```
