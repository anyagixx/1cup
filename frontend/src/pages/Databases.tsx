import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Popconfirm,
  Select as ClusterSelect,
  message,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { databasesApi } from '@/api';
import type { DatabaseInfo } from '@/types';

export const Databases: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [databases, setDatabases] = useState<DatabaseInfo[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<string>('');
  const [clusters, setClusters] = useState<{ cluster_id: string }[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDb, setEditingDb] = useState<DatabaseInfo | null>(null);
  const [form] = Form.useForm();

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
      const data = await databasesApi.list(selectedCluster);
      setDatabases(data.items || []);
    } catch {
      message.error('Ошибка загрузки баз данных');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingDb(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: DatabaseInfo) => {
    setEditingDb(record);
    form.setFieldsValue({
      name: record.database_name,
      description: record.description,
      dbms: record.dbms,
      db_server: record.db_server,
      db_name: record.db_name,
      db_user: record.db_user,
    });
    setModalVisible(true);
  };

  const handleDelete = async (databaseId: string) => {
    try {
      await databasesApi.delete(databaseId, selectedCluster);
      message.success('База данных удалена');
      loadData();
    } catch {
      message.error('Ошибка удаления базы данных');
    }
  };

  const handleSubmit = async (values: Record<string, unknown>) => {
    try {
      if (editingDb) {
        await databasesApi.update(editingDb.database_id, selectedCluster, values);
        message.success('База данных обновлена');
      } else {
        await databasesApi.create(selectedCluster, values);
        message.success('База данных создана');
      }
      setModalVisible(false);
      loadData();
    } catch {
      message.error('Ошибка сохранения');
    }
  };

  const columns: ColumnsType<DatabaseInfo> = [
    {
      title: 'Имя',
      dataIndex: 'database_name',
      key: 'database_name',
    },
    {
      title: 'СУБД',
      dataIndex: 'dbms',
      key: 'dbms',
    },
    {
      title: 'Сервер БД',
      dataIndex: 'db_server',
      key: 'db_server',
    },
    {
      title: 'База данных',
      dataIndex: 'db_name',
      key: 'db_name',
    },
    {
      title: 'Сеансов',
      dataIndex: 'sessions_count',
      key: 'sessions_count',
    },
    {
      title: 'Заблокирована',
      dataIndex: 'blocked',
      key: 'blocked',
      render: (blocked: boolean) => (
        <Tag color={blocked ? 'red' : 'green'}>{blocked ? 'Да' : 'Нет'}</Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Изменить
          </Button>
          <Popconfirm
            title="Удалить базу данных?"
            onConfirm={() => handleDelete(record.database_id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Удалить
            </Button>
          </Popconfirm>
        </Space>
      ),
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
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Добавить базу
        </Button>
      </div>

      <Card title="Информационные базы">
        <Table
          columns={columns}
          dataSource={databases}
          rowKey="database_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingDb ? 'Редактировать базу' : 'Новая база данных'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="Имя базы"
            rules={[{ required: true, message: 'Введите имя базы' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="Описание">
            <Input.TextArea />
          </Form.Item>
          {!editingDb && (
            <>
              <Form.Item
                name="dbms"
                label="СУБД"
                rules={[{ required: true }]}
                initialValue="PostgreSQL"
              >
                <Select
                  options={[
                    { value: 'PostgreSQL', label: 'PostgreSQL' },
                    { value: 'MSSQL', label: 'Microsoft SQL Server' },
                    { value: 'MySQL', label: 'MySQL' },
                  ]}
                />
              </Form.Item>
              <Form.Item
                name="db_server"
                label="Сервер БД"
                rules={[{ required: true }]}
              >
                <Input placeholder="localhost:5432" />
              </Form.Item>
              <Form.Item
                name="db_name"
                label="Имя базы данных"
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item
                name="db_user"
                label="Пользователь БД"
                rules={[{ required: true }]}
              >
                <Input />
              </Form.Item>
              <Form.Item
                name="db_password"
                label="Пароль БД"
                rules={[{ required: true }]}
              >
                <Input.Password />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};
