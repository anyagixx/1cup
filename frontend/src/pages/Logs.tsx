import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Button,
  Select,
  DatePicker,
  Space,
  Dropdown,
  message,
} from 'antd';
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { logsApi } from '@/api';
import type { LogEntry } from '@/types';

const { RangePicker } = DatePicker;

export const Logs: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [clusters, setClusters] = useState<{ cluster_id: string }[]>([]);
  const [selectedDb, setSelectedDb] = useState<string | undefined>();
  const [databases, setDatabases] = useState<{ database_id: string; database_name: string }[]>([]);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null);

  useEffect(() => {
    loadClusters();
  }, []);

  useEffect(() => {
    if (selectedCluster) {
      loadData();
      loadDatabases();
    }
  }, [selectedCluster, selectedDb, dateRange]);

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
      const params: Record<string, string | undefined> = {};
      if (dateRange?.[0]) params.start_time = dateRange[0].format('YYYY-MM-DD HH:mm:ss');
      if (dateRange?.[1]) params.end_time = dateRange[1].format('YYYY-MM-DD HH:mm:ss');

      const data = await logsApi.list(selectedCluster, {
        database_id: selectedDb,
        ...params,
      });
      setLogs(data.items || []);
    } catch {
      message.error('Ошибка загрузки логов');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const params: Record<string, string | undefined> = {};
      if (dateRange?.[0]) params.start_time = dateRange[0].format('YYYY-MM-DD HH:mm:ss');
      if (dateRange?.[1]) params.end_time = dateRange[1].format('YYYY-MM-DD HH:mm:ss');

      const blob = await logsApi.export(selectedCluster, format, {
        database_id: selectedDb,
        ...params,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logs_${dayjs().format('YYYYMMDD_HHmmss')}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      message.error('Ошибка экспорта');
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      ERROR: 'red',
      WARNING: 'orange',
      INFO: 'blue',
      DEBUG: 'default',
    };
    return colors[severity] || 'default';
  };

  const columns: ColumnsType<LogEntry> = [
    {
      title: 'Дата/Время',
      dataIndex: 'datetime',
      key: 'datetime',
      width: 180,
      render: (date: string) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: 'Событие',
      dataIndex: 'event',
      key: 'event',
      width: 150,
    },
    {
      title: 'Уровень',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>{severity}</Tag>
      ),
    },
    {
      title: 'Пользователь',
      dataIndex: 'user_name',
      key: 'user_name',
      width: 150,
    },
    {
      title: 'База данных',
      dataIndex: 'database_name',
      key: 'database_name',
      width: 150,
    },
    {
      title: 'Текст',
      dataIndex: 'text',
      key: 'text',
      ellipsis: true,
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
        <RangePicker
          showTime
          value={dateRange}
          onChange={(dates) => setDateRange(dates)}
          placeholder={['Начало', 'Конец']}
        />
        <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
          Обновить
        </Button>
        <Dropdown
          menu={{
            items: [
              { key: 'csv', label: 'CSV' },
              { key: 'json', label: 'JSON' },
            ],
            onClick: ({ key }) => handleExport(key as 'csv' | 'json'),
          }}
        >
          <Button icon={<DownloadOutlined />}>Экспорт</Button>
        </Dropdown>
      </div>

      <Card title="Журнал событий">
        <Table
          columns={columns}
          dataSource={logs}
          rowKey="log_id"
          loading={loading}
          pagination={{ pageSize: 50 }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};
