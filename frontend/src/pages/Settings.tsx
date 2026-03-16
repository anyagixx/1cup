import React from 'react';
import { Card, Typography, Descriptions } from 'antd';
import { useAuth } from '@/auth';

const { Title } = Typography;

export const Settings: React.FC = () => {
  const { user } = useAuth();

  return (
    <div>
      <Title level={4}>Настройки системы</Title>

      <Card title="Информация о пользователе" style={{ maxWidth: 600 }}>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="Имя пользователя">
            {user?.username}
          </Descriptions.Item>
          <Descriptions.Item label="Email">{user?.email}</Descriptions.Item>
          <Descriptions.Item label="Полное имя">
            {user?.full_name || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Роль">{user?.role}</Descriptions.Item>
          <Descriptions.Item label="Статус">
            {user?.is_active ? 'Активен' : 'Неактивен'}
          </Descriptions.Item>
          <Descriptions.Item label="Последний вход">
            {user?.last_login
              ? new Date(user.last_login).toLocaleString()
              : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};
