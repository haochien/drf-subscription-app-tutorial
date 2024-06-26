# Frontend React Js Setup

## Django CORS setup

CORS (Cross-Origin Resource Sharing) is a security feature implemented by web browsers to prevent web pages from making requests to a different domain than the one that served the web page. 
This is to prevent potentially malicious websites from accessing sensitive information on other sites. 

When working with a React frontend and a Django backend, you might encounter CORS issues because your React app (served from localhost:5173 or localhost:3000) will be making API requests to your Django server (e.g., localhost:8000).

To handle CORS issues, you need to configure your Django backend to allow requests from your React frontend.

### 1. Update CORS setting in settings.py

#### a. install django-cors-headers

```sh
pip install django-cors-headers
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

#### b. create `api.js` and under `src/`

```js
// ./src/api.js

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export default api;

```

#### c. update `App.jsx` and under `src/`

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
├─ local_db/
│  ├─ docker-compose.yml
├─ backend/
├─ .gitignore
├─ frontend/
│  ├─ public
│  ├─ src
│  │  ├─ api.js
│  │  ├─ App.jsx
│  │  ├─ main.jsx
│  ├─ .env
│  ├─ package.json
│  ├─ ...
```

#### d. start server and check the results

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

const TestPage = () => {

  return (
    <div>
      <h1>Home Page</h1>
      <p>Welecome to my website!</p>
    </div>
  );
};

export default TestPage;
```

```js
// ./src/pages/TestAPI.jsx

import React, { useEffect, useState } from 'react';
import api from '../api'; 

const TestPage = () => {
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

export default TestPage;
```

### 2. Set up Router in App.jsx

With router setup, we can then navigate to Home page and TestAPI page.

```js
import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Home from "./pages/Home"
import TestPage from './pages/TestAPI'; 

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

After all set up ready, start server and navigate to `http://localhost:5173/test` and `http://localhost:5173/test` to see the results.
