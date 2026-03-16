import apiClient from './client';
import type { User, LoginRequest, TokenResponse, PasswordChange } from '@/types';

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  changePassword: async (data: PasswordChange): Promise<void> => {
    await apiClient.post('/auth/change-password', data);
  },
};

export const clusterApi = {
  list: async () => {
    const response = await apiClient.get('/cluster/list');
    return response.data;
  },

  getInfo: async (clusterId: string) => {
    const response = await apiClient.get(`/cluster/info/${clusterId}`);
    return response.data;
  },

  getStatus: async (clusterId: string) => {
    const response = await apiClient.get(`/cluster/status/${clusterId}`);
    return response.data;
  },
};

export const serversApi = {
  list: async (clusterId: string) => {
    const response = await apiClient.get('/servers', {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  getInfo: async (serverId: string, clusterId: string) => {
    const response = await apiClient.get(`/servers/${serverId}`, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  getProcesses: async (serverId: string, clusterId: string) => {
    const response = await apiClient.get(`/servers/${serverId}/processes`, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  getAllProcesses: async (clusterId: string) => {
    const response = await apiClient.get('/servers/all/processes', {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },
};

export const databasesApi = {
  list: async (clusterId: string) => {
    const response = await apiClient.get('/databases', {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  getInfo: async (databaseId: string, clusterId: string) => {
    const response = await apiClient.get(`/databases/${databaseId}`, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  create: async (clusterId: string, data: Record<string, unknown>) => {
    const response = await apiClient.post('/databases', {
      cluster_id: clusterId,
      ...data,
    });
    return response.data;
  },

  update: async (databaseId: string, clusterId: string, data: Record<string, unknown>) => {
    const response = await apiClient.put(`/databases/${databaseId}`, data, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  delete: async (databaseId: string, clusterId: string, dropDb: boolean = false) => {
    const response = await apiClient.delete(`/databases/${databaseId}`, {
      params: { cluster_id: clusterId, drop_db: dropDb },
    });
    return response.data;
  },
};

export const sessionsApi = {
  list: async (clusterId: string, databaseId?: string) => {
    const response = await apiClient.get('/sessions', {
      params: { cluster_id: clusterId, database_id: databaseId },
    });
    return response.data;
  },

  terminate: async (sessionId: string, clusterId: string) => {
    const response = await apiClient.delete(`/sessions/${sessionId}`, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },

  bulkTerminate: async (clusterId: string, databaseId?: string, sessionIds?: string[]) => {
    const response = await apiClient.post('/sessions/bulk-terminate', {
      cluster_id: clusterId,
      database_id: databaseId,
      session_ids: sessionIds,
    });
    return response.data;
  },
};

export const logsApi = {
  list: async (clusterId: string, params?: {
    database_id?: string;
    start_time?: string;
    end_time?: string;
  }) => {
    const response = await apiClient.get('/logs', {
      params: { cluster_id: clusterId, ...params },
    });
    return response.data;
  },

  export: async (clusterId: string, format: 'csv' | 'json' = 'csv', params?: {
    database_id?: string;
    start_time?: string;
    end_time?: string;
  }) => {
    const response = await apiClient.get('/logs/export', {
      params: { cluster_id: clusterId, format, ...params },
      responseType: 'blob',
    });
    return response.data;
  },
};
