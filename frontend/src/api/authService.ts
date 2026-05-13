/* API service for authentication endpoints. */

import { AxiosError } from 'axios';

import client from '@/api/client';
import { User } from '@/stores';

export interface LoginRequest {
  login: string;
  password: string;
  competition_id: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export const authService = {
  async judgesLogin(payload: LoginRequest): Promise<LoginResponse> {
    const response = await client.post<LoginResponse>(
      '/api/auth/judges-login',
      payload
    );
    return response.data;
  },

  async organizerLogin(payload: LoginRequest): Promise<LoginResponse> {
    const response = await client.post<LoginResponse>(
      '/api/auth/organizer-login',
      payload
    );
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await client.post('/api/auth/logout');
    } catch (error: unknown) {
      const axiosError = error as AxiosError;
      console.error('Logout error:', axiosError.message);
    }
  },
};
