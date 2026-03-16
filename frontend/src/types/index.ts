export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'operator' | 'viewer';
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ClusterInfo {
  cluster_id: string;
  cluster_name: string;
  host: string;
  port: number;
  cluster_status: string;
  processes_count: number;
  memory_size: number;
  selection_size: number;
  sessions_limit: number;
  sessions_count: number;
  memory_limit: number;
  security_level: number;
  load_balancing_mode: string;
  errors_count: number;
}

export interface ClusterStatus {
  cluster_id: string;
  status: string;
  servers_count: number;
  databases_count: number;
  sessions_count: number;
  processes_count: number;
  memory_used: number;
  memory_limit: number;
}

export interface ServerInfo {
  server_id: string;
  server_name: string;
  host: string;
  port: number;
  server_status: string;
  processes_count: number;
  memory_size: number;
  selection_size: number;
  sessions_count: number;
  is_main: boolean;
  cluster_peers: string[];
}

export interface ProcessInfo {
  process_id: string;
  server_id: string;
  host: string;
  port: number;
  process_status: string;
  memory_size: number;
  sessions_count: number;
  connections_count: number;
  started_at: string | null;
}

export interface DatabaseInfo {
  database_id: string;
  database_name: string;
  dbms: string;
  db_server: string;
  db_name: string;
  db_user: string;
  db_password_masked: string;
  description: string;
  security_profile_name: string;
  sessions_count: number;
  blocked: boolean;
  denied_message: string;
}

export interface SessionInfo {
  session_id: string;
  database_id: string;
  database_name: string;
  user_name: string;
  host: string;
  app_id: string;
  session_start: string | null;
  last_active_at: string | null;
  session_status: string;
  blocked_by_dbms: boolean;
  locale: string;
  process_id: string;
}

export interface LogEntry {
  log_id: string;
  datetime: string | null;
  transaction: string;
  user_name: string;
  computer_name: string;
  app_id: string;
  event: string;
  severity: string;
  database_name: string;
  session_id: string;
  transaction_id: string;
  text: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}
