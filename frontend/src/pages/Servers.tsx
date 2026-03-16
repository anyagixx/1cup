import React, { useEffect, useState } from 'react';
import { Table, Card, Tag, Button, Modal, Descriptions, Select, message, Spin } from 'antd';
import { ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { serversApi } from '@/api';
import type { ServerInfo, ProcessInfo } from '@/types';

export const Servers: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [servers, setServers] = useState<ServerInfo[]>([]);
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [clusters, setClusters] = useState<{ cluster_id: string }[]>([]);
  const [detailsModal, setDetailsModal] = useState<{
    visible: boolean;
    server: ServerInfo | null;
    processes: ProcessInfo[];
  }>({ visible: false, server: null, processes: [] });

  useEffect(() => {
    loadClusters();
  }, []);

  useEffect(() => {
    if (selectedCluster) {
      loadData();
    }
  }, [selectedCluster]);

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

  const loadData = async () => {
    setLoading(true);
    try {
      const [serversData, processesData] = await Promise.all([
        serversApi.list(selectedCluster),
        serversApi.getAllProcesses(selectedCluster),
      ]);
      setServers(serversData.items || []);
      setProcesses(processesData.items || []);
    } catch {
      message.error('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const showDetails = async (server: ServerInfo) => {
    try {
      const processData = await serversApi.getProcesses(server.server_id, selectedCluster);
      setDetailsModal({
        visible: true,
        server,
        processes: processData.items || [],
      });
    } catch {
      message.error('Ошибка загрузки процессов');
    }
  };

  const serverColumns: ColumnsType<ServerInfo> = [
    {
      title: 'Имя сервера',
      dataIndex: 'server_name',
      key: 'server_name',
    },
    {
      title: 'Хост:Порт',
      key: 'host_port',
      render: (_, record) => `${record.host}:${record.port}`,
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
      title: 'Главный',
      dataIndex: 'is_main',
      key: 'is_main',
      render: (isMain: boolean) => (
        <Tag color={isMain ? 'blue' : 'default'}>{isMain ? 'Да' : 'Нет'}</Tag>
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
    {
      title: 'Память (МБ)',
      dataIndex: 'memory_size',
      key: 'memory_size',
      render: (size: number) => Math.round(size / 1024 / 1024),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => showDetails(record)}
        >
          Детали
        </Button>
      ),
    },
  ];

  const processColumns: ColumnsType<ProcessInfo> = [
    {
      title: 'ID процесса',
      dataIndex: 'process_id',
      key: 'process_id',
      width: 280,
      ellipsis: true,
    },
    {
      title: 'Хост:Порт',
      key: 'host_port',
      render: (_, record) => `${record.host}:${record.port}`,
    },
    {
      title: 'Статус',
      dataIndex: 'process_status',
      key: 'process_status',
      render: (status: string) => (
        <Tag color={status === 'RUNNING' ? 'green' : 'default'}>{status}</Tag>
      ),
    },
    {
      title: 'Сеансы',
      dataIndex: 'sessions_count',
      key: 'sessions_count',
    },
    {
      title: 'Соединения',
      dataIndex: 'connections_count',
      key: 'connections_count',
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
        <Select
          style={{ width: 300 }}
          value={selectedCluster}
          onChange={setSelectedCluster}
          options={clusters.map((c) => ({ value: c.cluster_id, label: c.cluster_id }))}
          placeholder="Выберите кластер"
        />
        <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
          Обновить
        </Button>
      </div>

      <Card title="Серверы кластера">
        <Table
          columns={serverColumns}
          dataSource={servers}
          rowKey="server_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Card title="Рабочие процессы" style={{ marginTop: 16 }}>
        <Table
          columns={processColumns}
          dataSource={processes}
          rowKey="process_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          size="small"
        />
      </Card>

      <Modal
        title={`Сервер: ${detailsModal.server?.server_name}`}
        open={detailsModal.visible}
        onCancel={() => setDetailsModal({ visible: false, server: null, processes: [] })}
        footer={null}
        width={800}
      >
        {detailsModal.server && (
          <>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="ID">{detailsModal.server.server_id}</Descriptions.Item>
              <Descriptions.Item label="Хост">{detailsModal.server.host}</Descriptions.Item>
              <Descriptions.Item label="Порт">{detailsModal.server.port}</Descriptions.Item>
              <Descriptions.Item label="Статус">
                <Tag color={detailsModal.server.server_status === 'RUNNING' ? 'green' : 'red'}>
                  {detailsModal.server.server_status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Процессов">
                {detailsModal.server.processes_count}
              </Descriptions.Item>
              <Descriptions.Item label="Сеансов">
                {detailsModal.server.sessions_count}
              </Descriptions.Item>
            </Descriptions>
            <h4 style={{ marginTop: 16 }}>Процессы сервера</h4>
            <Table
              columns={processColumns}
              dataSource={detailsModal.processes}
              rowKey="process_id"
              pagination={false}
              size="small"
            />
          </>
        )}
      </Modal>
    </div>
  );
};
