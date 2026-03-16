import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Spin, Select, message } from 'antd';
import {
  ServerOutlined,
  DatabaseOutlined,
  UserOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { clusterApi, serversApi, databasesApi, sessionsApi } from '@/api';
import type { ClusterStatus, ServerInfo, SessionInfo } from '@/types';

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [clusters, setClusters] = useState<{ cluster_id: string }[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [clusterStatus, setClusterStatus] = useState<ClusterStatus | null>(null);
  const [servers, setServers] = useState<ServerInfo[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);

  useEffect(() => {
    loadClusters();
  }, []);

  useEffect(() => {
    if (selectedCluster) {
      loadDashboardData();
      const interval = setInterval(loadDashboardData, 30000);
      return () => clearInterval(interval);
    }
  }, [selectedCluster]);

  const loadClusters = async () => {
    try {
      const data = await clusterApi.list();
      setClusters(data);
      if (data.length > 0) {
        setSelectedCluster(data[0].cluster_id);
      }
    } catch {
      message.error('Ошибка загрузки списка кластеров');
    }
  };

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [status, serversData, sessionsData] = await Promise.all([
        clusterApi.getStatus(selectedCluster),
        serversApi.list(selectedCluster),
        sessionsApi.list(selectedCluster),
      ]);
      setClusterStatus(status);
      setServers(serversData.items || []);
      setSessions(sessionsData.items || []);
    } catch {
      message.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const serverColumns: ColumnsType<ServerInfo> = [
    {
      title: 'Сервер',
      dataIndex: 'server_name',
      key: 'server_name',
    },
    {
      title: 'Хост',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'Статус',
      dataIndex: 'server_status',
      key: 'server_status',
      render: (status: string) => (
        <Tag color={status === 'RUNNING' ? 'green' : 'red'}>
          {status === 'RUNNING' ? 'Активен' : 'Остановлен'}
        </Tag>
      ),
    },
    {
      title: 'Процессы',
      dataIndex: 'processes_count',
      key: 'processes_count',
    },
    {
      title: 'Сеансы',
      dataIndex: 'sessions_count',
      key: 'sessions_count',
    },
  ];

  const sessionColumns: ColumnsType<SessionInfo> = [
    {
      title: 'Пользователь',
      dataIndex: 'user_name',
      key: 'user_name',
    },
    {
      title: 'База данных',
      dataIndex: 'database_name',
      key: 'database_name',
    },
    {
      title: 'Хост',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'Статус',
      dataIndex: 'session_status',
      key: 'session_status',
      render: (status: string) => (
        <Tag color={status === 'ACTIVE' ? 'green' : 'default'}>
          {status === 'ACTIVE' ? 'Активен' : status}
        </Tag>
      ),
    },
  ];

  if (loading && !clusterStatus) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Select
          style={{ width: 300 }}
          value={selectedCluster}
          onChange={setSelectedCluster}
          options={clusters.map((c) => ({ value: c.cluster_id, label: c.cluster_id }))}
          placeholder="Выберите кластер"
        />
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Серверы"
              value={clusterStatus?.servers_count || 0}
              prefix={<ServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Базы данных"
              value={clusterStatus?.databases_count || 0}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Активные сеансы"
              value={clusterStatus?.sessions_count || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Статус кластера"
              value={clusterStatus?.status || 'Unknown'}
              prefix={
                clusterStatus?.status === 'RUNNING' ? (
                  <CheckCircleOutlined />
                ) : (
                  <ExclamationCircleOutlined />
                )
              }
              valueStyle={{
                color: clusterStatus?.status === 'RUNNING' ? '#52c41a' : '#ff4d4f',
              }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Серверы кластера">
            <Table
              columns={serverColumns}
              dataSource={servers}
              rowKey="server_id"
              pagination={false}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Последние сеансы">
            <Table
              columns={sessionColumns}
              dataSource={sessions.slice(0, 10)}
              rowKey="session_id"
              pagination={false}
              size="small"
              loading={loading}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
