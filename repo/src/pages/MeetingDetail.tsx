import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  Space,
  Row,
  Col,
  Divider,
  Typography,
  message,
  Tag,
} from 'antd'
import {
  ArrowLeftOutlined,
  SaveOutlined,
  UserAddOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'
import dayjs from 'dayjs'
import TasteRadarChart from '../components/TasteRadarChart'
import TissueEngineeringCard from '../components/TissueEngineeringCard'
import AudioUploadProcessor from '../components/AudioUploadProcessor'
import AISummaryPanel from '../components/AISummaryPanel'
import { meetingApi } from '../services/api'
import type {
  MeetingNote,
  TasteScore,
  TissueEngineeringParams,
  Participant,
  DiscussionSegment,
  AudioProcessingResult,
} from '../types'

const { Title } = Typography
const { TextArea } = Input
const { Option } = Select

const defaultTasteScore: TasteScore = {
  juiciness: 7.0,
  tenderness: 6.5,
  elasticity: 7.2,
  flavor: 6.8,
  texture: 7.0,
  chewiness: 6.5,
}

const defaultTissueParams: TissueEngineeringParams = {
  cellDensity: 1500000,
  scaffoldPorosity: 85,
  fiberAlignment: 78,
  maturationRate: 72,
  extracellularMatrix: 85,
  vascularization: 45,
}

const MeetingDetail: React.FC = () => {
  const navigate = useNavigate()
  const { id } = useParams()
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)
  const [tasteScore, setTasteScore] = useState<TasteScore>(defaultTasteScore)
  const [tissueParams, setTissueParams] = useState<TissueEngineeringParams>(defaultTissueParams)
  const [participants, setParticipants] = useState<Participant[]>([])
  const [discussions, setDiscussions] = useState<DiscussionSegment[]>([])
  const [meetingId, setMeetingId] = useState<string | null>(id || null)
  const [loading, setLoading] = useState(false)
  const [newParticipant, setNewParticipant] = useState({
    name: '',
    role: 'scientist' as Participant['role'],
    group: 'rd' as Participant['group'],
  })

  const isNew = !id || id === 'new'

  useEffect(() => {
    if (!isNew && id) {
      fetchMeeting(id)
    }
  }, [id, isNew])

  const fetchMeeting = async (meetingId: string) => {
    setLoading(true)
    try {
      const response = await meetingApi.getMeeting(meetingId)
      const meeting = response.data
      form.setFieldsValue({
        title: meeting.title,
        date: meeting.date,
      })
      setTasteScore(meeting.tasteScore)
      setTissueParams(meeting.tissueParams)
      setParticipants(meeting.participants)
      setDiscussions(meeting.discussions)
    } catch (error) {
      message.error('加载会议详情失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    const values = await form.validateFields()
    setSaving(true)

    try {
      const meetingData: Partial<MeetingNote> = {
        title: values.title,
        date: values.date || dayjs().format('YYYY-MM-DDTHH:mm:ss'),
        participants,
        tasteScore,
        tissueParams,
        discussions,
      }

      let response
      if (isNew || !meetingId) {
        response = await meetingApi.createMeeting(meetingData)
        setMeetingId(response.data.id)
        message.success('会议创建成功')
      } else {
        response = await meetingApi.updateMeeting(meetingId, meetingData)
        message.success('保存成功')
      }

      if (isNew) {
        navigate(`/meetings/${response.data.id}`, { replace: true })
      }
    } catch (error) {
      message.error('保存失败')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  const addParticipant = () => {
    if (!newParticipant.name.trim()) {
      message.warning('请输入姓名')
      return
    }
    const participant: Participant = {
      id: Date.now().toString(),
      name: newParticipant.name,
      role: newParticipant.role,
      group: newParticipant.group,
    }
    setParticipants([...participants, participant])
    setNewParticipant({ name: '', role: 'scientist', group: 'rd' })
  }

  const removeParticipant = (id: string) => {
    setParticipants(participants.filter(p => p.id !== id))
  }

  const handleAudioProcessed = (result: AudioProcessingResult) => {
    const segments: DiscussionSegment[] = result.speakerSegments.map((seg, index) => ({
      id: `disc-${Date.now()}-${index}`,
      speaker: seg.speaker,
      group: seg.group,
      content: seg.text,
      timestamp: seg.start,
      duration: seg.end - seg.start,
    }))
    setDiscussions(segments)
    message.success(`已识别 ${segments.length} 条讨论内容`)
  }

  const handleTasteScoreSave = async () => {
    if (!meetingId) return
    try {
      await meetingApi.updateTasteScore(meetingId, tasteScore)
      message.success('口感评分已保存')
    } catch (error) {
      message.error('保存失败')
    }
  }

  const handleTissueParamsSave = async () => {
    if (!meetingId) return
    try {
      await meetingApi.updateTissueParams(meetingId, tissueParams)
      message.success('组织工程参数已保存')
    } catch (error) {
      message.error('保存失败')
    }
  }

  const roleOptions = [
    { value: 'scientist', label: '科学家' },
    { value: 'chef', label: '厨师' },
    { value: 'sensory', label: '感官评价员' },
    { value: 'pm', label: '产品经理' },
  ]

  const groupOptions = [
    { value: 'rd', label: '研发组' },
    { value: 'sensory', label: '感官评价组' },
  ]

  return (
    <div className="page-container">
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/meetings')}>
            返回列表
          </Button>
          <Title level={3} style={{ margin: 0 }}>
            {isNew ? '新建品评会议' : '会议详情'}
          </Title>
        </Space>

        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                label="会议标题"
                name="title"
                rules={[{ required: true, message: '请输入会议标题' }]}
                initialValue={isNew ? `品评会议 - ${dayjs().format('YYYY-MM-DD')}` : ''}
              >
                <Input placeholder="例如：第5批人造肉样本品评会议" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                label="会议时间"
                name="date"
                initialValue={dayjs().format('YYYY-MM-DDTHH:mm:ss')}
              >
                <Input type="datetime-local" />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">参与人员</Divider>

          <div style={{ marginBottom: 16 }}>
            <Space wrap>
              <Input
                placeholder="姓名"
                value={newParticipant.name}
                onChange={e => setNewParticipant({ ...newParticipant, name: e.target.value })}
                style={{ width: 150 }}
              />
              <Select
                value={newParticipant.role}
                onChange={value => setNewParticipant({ ...newParticipant, role: value })}
                style={{ width: 120 }}
                options={roleOptions}
              />
              <Select
                value={newParticipant.group}
                onChange={value => setNewParticipant({ ...newParticipant, group: value })}
                style={{ width: 120 }}
                options={groupOptions}
              />
              <Button type="primary" icon={<UserAddOutlined />} onClick={addParticipant}>
                添加
              </Button>
            </Space>
          </div>

          <div style={{ marginBottom: 16 }}>
            {participants.length === 0 ? (
              <Tag>暂无参与人员</Tag>
            ) : (
              <Space wrap>
                {participants.map(p => (
                  <Tag
                    key={p.id}
                    color={p.group === 'rd' ? 'blue' : 'green'}
                    closable
                    onClose={() => removeParticipant(p.id)}
                  >
                    {p.name} ({roleOptions.find(r => r.value === p.role)?.label})
                  </Tag>
                ))}
              </Space>
            )}
          </div>

          <Divider />

          <Space>
            <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={saving}>
              保存会议
            </Button>
          </Space>
        </Form>
      </Card>

      {meetingId && !isNew && (
        <>
          <div style={{ marginTop: 24 }}>
            <Row gutter={16}>
              <Col xs={24} lg={12}>
                <TasteRadarChart
                  score={tasteScore}
                  onChange={setTasteScore}
                />
                <div style={{ textAlign: 'right', marginTop: 8 }}>
                  <Button size="small" onClick={handleTasteScoreSave}>
                    保存评分
                  </Button>
                </div>
              </Col>
              <Col xs={24} lg={12}>
                <TissueEngineeringCard
                  params={tissueParams}
                  onChange={setTissueParams}
                />
                <div style={{ textAlign: 'right', marginTop: 8 }}>
                  <Button size="small" onClick={handleTissueParamsSave}>
                    保存参数
                  </Button>
                </div>
              </Col>
            </Row>
          </div>

          <div style={{ marginTop: 24 }}>
            <AudioUploadProcessor
              meetingId={meetingId}
              onProcessingComplete={handleAudioProcessed}
            />
          </div>

          {discussions.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <AISummaryPanel meetingId={meetingId} />
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default MeetingDetail
