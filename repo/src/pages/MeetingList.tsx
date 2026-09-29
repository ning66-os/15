import React, { useState, useEffect } from 'react'
import { Table, Button, Tag, Space, Typography, Card, Empty, message } from 'antd'
import {
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  CalendarOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import { meetingApi } from '../services/api'
import type { MeetingNote } from '../types'

const { Title, Text } = Typography

const MeetingList: React.FC = () => {
  const navigate = useNavigate()
  const [meetings, setMeetings] = useState<MeetingNote[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchMeetings()
  }, [])

  const fetchMeetings = async () => {
    setLoading(true)
    try {
      const response = await meetingApi.getMeetings()
      setMeetings(response.data)
    } catch (error) {
      console.error('获取会议列表失败', error)
      message.error('获取会议列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await meetingApi.deleteMeeting(id)
      message.success('删除成功')
      fetchMeetings()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '会议标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: MeetingNote) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <CalendarOutlined style={{ marginRight: 4 }} />
            {dayjs(record.date).format('YYYY-MM-DD HH:mm')}
          </Text>
        </Space>
      ),
    },
    {
      title: '参与人员',
      dataIndex: 'participants',
      key: 'participants',
      render: (participants: MeetingNote['participants']) => (
        <Space wrap>
          {participants.map(p => (
            <Tag key={p.id} color={p.group === 'rd' ? 'blue' : 'green'}>
              <UserOutlined style={{ marginRight: 2 }} />
              {p.name}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '综合评分',
      key: 'score',
      render: (_: any, record: MeetingNote) => {
        const scores = Object.values(record.tasteScore)
        const avg = scores.reduce((a, b) => a + b, 0) / scores.length
        return (
          <Tag color={avg >= 7 ? 'green' : avg >= 5 ? 'orange' : 'red'}>
            {avg.toFixed(1)} / 10
          </Tag>
        )
      },
    },
    {
      title: '状态',
      key: 'status',
      render: (_: any, record: MeetingNote) => (
        <Space>
          {record.summary && <Tag color="blue">已分析</Tag>}
          {record.emailSent && <Tag color="green">已发邮件</Tag>}
          {record.experimentRecordId && <Tag color="purple">已归档</Tag>}
          {!record.summary && <Tag>待处理</Tag>}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: MeetingNote) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/meetings/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div className="page-container">
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={3} style={{ margin: 0 }}>
            品评会议列表
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/meetings/new')}
          >
            新建会议
          </Button>
        </div>

        {meetings.length === 0 ? (
          <Empty description="暂无会议记录，点击上方按钮创建第一个品评会议" />
        ) : (
          <Table
            columns={columns}
            dataSource={meetings}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        )}
      </Card>
    </div>
  )
}

export default MeetingList
