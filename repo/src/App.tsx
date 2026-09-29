import React, { useState } from 'react'
import { Layout, Menu, Typography } from 'antd'
import {
  FileTextOutlined,
  PlusOutlined,
  ExperimentOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import MeetingList from './pages/MeetingList'
import MeetingDetail from './pages/MeetingDetail'

const { Header, Sider, Content } = Layout
const { Title } = Typography

const App: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    {
      key: '/meetings',
      icon: <FileTextOutlined />,
      label: '会议列表',
      onClick: () => navigate('/meetings'),
    },
    {
      key: '/meetings/new',
      icon: <PlusOutlined />,
      label: '新建会议',
      onClick: () => navigate('/meetings/new'),
    },
  ]

  return (
    <Layout className="app-container" style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 12 : 16,
            fontWeight: 600,
            background: 'rgba(255,255,255,0.1)',
          }}
        >
          {collapsed ? '🥩' : '🥩 人造肉研发平台'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            boxShadow: '0 1px 4px rgba(0,21,41,0.08)',
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            品评会议纪要系统
          </Title>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
            <ExperimentOutlined style={{ fontSize: 18, color: '#667eea' }} />
            <span style={{ color: '#666' }}>研发组</span>
            <UserOutlined style={{ fontSize: 18, color: '#52c41a', marginLeft: 16 }} />
            <span style={{ color: '#666' }}>感官评价组</span>
          </div>
        </Header>
        <Content style={{ padding: '24px', background: '#f0f2f5', minHeight: 'calc(100vh - 64px)' }}>
          <Routes>
            <Route path="/" element={<MeetingList />} />
            <Route path="/meetings" element={<MeetingList />} />
            <Route path="/meetings/new" element={<MeetingDetail />} />
            <Route path="/meetings/:id" element={<MeetingDetail />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
