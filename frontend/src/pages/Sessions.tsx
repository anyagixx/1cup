import React, { useEffect, useState } from 'react';
import { Table, Card, Tag, Button, Select, Space, Popconfirm, message, Input } from 'antd';
import { ReloadOutlined, DeleteOutlined, StopOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { sessionsApi } from '@/api';
import type { SessionInfo } from '@/types';

export const Sessions: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [clusters, setClusters] = useState<{ cluster_id: string }[]>([]);
  const [selectedDb, setSelectedDb] = useState<string | undefined>();
  const [databases, setDatabases] = useState<{ database_id: string; database_name: string }[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  useEffect(() => {
    loadClusters();
  }, []);

  useEffect(() => {
    if (selectedCluster) {
      loadData();
      loadDatabases();
    }
  }, [selectedCluster, selectedDb]);

  const loadClusters = async () => {
    try {
      const { clusterApi } = await import('@/api');
      const data = await clusterApi.list();
      setClusters(data);
      if (data.length > 0) {
        setSelectedCluster(data[0].cluster_id);
      }
    } catch {
      message.error('Ошибка загрузки списка кластеров');
    }
  };

  const loadDatabases = async () => {
    try {
      const { databasesApi } = await import('@/api');
      const data = await databasesApi.list(selectedCluster);
      setDatabases(
        (data.items || []).map((db: { database_id: string; database_name: string }) => ({
          database_id: db.database_id,
          database_name: db.database_name,
        }))
      );
    } catch {
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await sessionsApi.list(selectedCluster, selectedDb);
      setSessions(data.items || []);
    } catch {
      message.error('Ошибка загрузки сеансов');
    } finally {
      setLoading(false);
    }
  };

  const handleTerminate = async (sessionId: string) => {
    try {
      await sessionsApi.terminate(sessionId, selectedCluster);
      message.success('Сеанс завершен');
      loadData();
    } catch {
      message.error('Ошибка завершения сеанса');
    }
  };

  const handleBulkTerminate = async () => {
    try {
      await sessionsApi.bulkTerminate(
        selectedCluster,
        selectedDb,
        selectedRowKeys as string[]
      );
      message.success('Сеансы завершены');
      setSelectedRowKeys([]);
      loadData();
    } catch {
      message.error('Ошибка завершения сеансов');
    }
  };

  const columns: ColumnsType<SessionInfo> = [
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
      title: 'Приложение',
      dataIndex: 'app_id',
      key: 'app_id',
      ellipsis: true,
    },
    {
      title: 'Статус',
      dataIndex: 'session_status',
      key: 'session_status',
      render: (status: string) => (
        <Tag color={status === 'ACTIVE' ? 'green' : 'default'}>{status}</Tag>
      ),
    },
    {
      title: 'Начало',
      dataIndex: 'session_start',
      key: 'session_start',
      render: (date: string) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Popconfirm
          title="Завершить сеанс?"
          onConfirm={() => handleTerminate(record.session_id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            Завершить
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <Select
          style={{ width: 300 }}
          value={selectedCluster}
          onChange={setSelectedCluster}
          options={clusters.map((c) => ({ value: c.cluster_id, label: c.cluster_id }))}
          placeholder="Выберите кластер"
        />
        <Select
          style={{ width: 250 }}
          value={selectedDb}
          onChange={setSelectedDb}
          allowClear
          placeholder="Все базы данных"
          options={databases.map((db) => ({
            value: db.database_id,
            label: db.database_name,
          }))}
        />
        <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
          Обновить
        </Button>
        {selectedRowKeys.length > 0 && (
          <Popconfirm
            title={`Завершить ${selectedRowKeys.length} сеансов?`}
            onConfirm={handleBulkTerminate}
          >
            <Button danger icon={<StopOutlined />}>
              Завершить выбранные ({selectedRowKeys.length})
            </Button>
          </Popconfirm>
        )}
      </div>

      <Card title="Активные сеансы">
        <Table
          columns={columns}
          dataSource={sessions}
          rowKey="session_id"
          loading={loading}
          pagination={{ pageSize: 20 }}
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
          }}
        />
      </Card>
    </div>
  );
};
