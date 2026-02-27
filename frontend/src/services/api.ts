import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000';

export const TOKEN_KEY = 'auth_token';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30_000,
});

// Attach the JWT from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// On 401, clear token and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = '/login';
      }

      const message =
        (error.response?.data as { error?: { message?: string } } | undefined)
          ?.error?.message ?? error.message;
      return Promise.reject(new Error(message));
    }
    return Promise.reject(error);
  },
);
