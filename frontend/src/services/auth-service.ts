import { api } from './api';
import type { User } from '@/types/auth';

interface LoginResponse {
  token: string;
}

interface RegisterResponse {
  token: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<{ data: LoginResponse }>('/api/auth/login', { email, password });
  return response.data.data;
}

export async function register(email: string, password: string): Promise<RegisterResponse> {
  const response = await api.post<{ data: RegisterResponse }>('/api/auth/register', { email, password });
  return response.data.data;
}

export async function getMe(): Promise<User> {
  const response = await api.get<{ data: User }>('/api/auth/me');
  return response.data.data;
}
