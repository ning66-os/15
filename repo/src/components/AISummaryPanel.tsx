import React, { useState } from 'react'
import { Button, Card, Spin, message, Typography, Tag, Space, Divider } from 'antd'
import {
  FileTextOutlined,
  SendOutlined,
  ExperimentOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { meetingApi } from '../services/api'

const { Title, Paragraph, Text } = Typography

interface Props {
  meetingId: string
}

const AISummaryPanel: React.FC<Props> = ({ meetingId }) => {
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<string>('')
  const [processAdjustments, setProcessAdjustments] = useState<string>('')
  const [flavorOptimizations, setFlavorOptimizations] = useState<string>('')
  const [emailSent, setEmailSent] = useState(false)
  const [experimentRecord, setExperimentRecord] = useState<{ recordId: string; markdown: string } | null>(null)

  const generateSummary = async () => {
    setLoading(true)
    try {
      const response = await meetingApi.generateSummary(meetingId)
      setSummary(response.data.summary)
      setProcessAdjustments(response.data.processAdjustments)
      setFlavorOptimizations(response.data.flavorOptimizations)
      message.success('AI摘要生成完成')
    } catch (error) {
      message.error('生成摘要失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const sendEmail = async () => {
    try {
      await meetingApi.sendEmail(meetingId)
      setEmailSent(true)
      message.success('邮件已发送给产品经理')
    } catch (error) {
      message.error('邮件发送失败')
      console.error(error)
    }
  }

  const createExperimentRecord = async () => {
    try {
      const response = await meetingApi.createExperimentRecord(meetingId)
      setExperimentRecord(response.data)
      message.success('实验记录已创建')
    } catch (error) {
      message.error('创建实验记录失败')
      console.error(error)
    }
  }

  const renderMarkdownContent = (content: string) => {
    return (
      <div
        style={{
          whiteSpace: 'pre-wrap',
          lineHeight: 1.8,
          fontSize: 14,
        }}
        dangerouslySetInnerHTML={{
          __html: content
            .replace(/^### (.+)$/gm, '<h3 style="color:#1890ff;margin-top:16px;margin-bottom:8px;">$1</h3>')
            .replace(/^## (.+)$/gm, '<h2 style="color:#722ed1;margin-top:20px;margin-bottom:12px;">$1</h2>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^- (.+)$/gm, '<li style="margin-left:20px;">$1</li>')
            .replace(/\n/g, '<br/>'),
        }}
      />
    )
  }

  return (
    <div>
      <div className="chart-container">
        <div className="section-title">AI智能分析</div>

        <Space wrap style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            onClick={generateSummary}
            loading={loading}
          >
            生成AI分析报告
          </Button>
          <Button
            icon={<SendOutlined />}
            onClick={sendEmail}
            disabled={!summary}
          >
            {emailSent ? '✓ 已发送邮件' : '发送邮件给PM'}
          </Button>
          <Button
            icon={<ExperimentOutlined />}
            onClick={createExperimentRecord}
            disabled={!summary}
          >
            {experimentRecord ? '✓ 已生成实验记录' : '生成实验记录'}
          </Button>
        </Space>

        {loading && (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <div style={{ marginTop: 12, color: '#666' }}>
              AI正在分析讨论内容，生成工艺调整方案和风味优化建议...
            </div>
          </div>
        )}
      </div>

      {summary && (
        <>
          <Card
            style={{ marginTop: 16 }}
            title={
              <Space>
                <FileTextOutlined />
                <span>会议摘要</span>
              </Space>
            }
            className="chart-container"
          >
            {renderMarkdownContent(summary)}
          </Card>

          <Card
            style={{ marginTop: 16 }}
            title={
              <Space>
                <ReloadOutlined />
                <span>工艺调整方案</span>
                <Tag color="orange">技术</Tag>
              </Space>
            }
            className="chart-container"
          >
            {renderMarkdownContent(processAdjustments)}
          </Card>

          <Card
            style={{ marginTop: 16 }}
            title={
              <Space>
                <ExperimentOutlined />
                <span>风味优化建议</span>
                <Tag color="green">产品</Tag>
              </Space>
            }
            className="chart-container"
          >
            {renderMarkdownContent(flavorOptimizations)}
          </Card>

          {experimentRecord && (
            <Card
              style={{ marginTop: 16 }}
              title={
                <Space>
                  <ExperimentOutlined />
                  <span>实验记录本条目</span>
                  <Tag color="purple">记录ID: {experimentRecord.recordId}</Tag>
                </Space>
              }
              className="chart-container"
            >
              <pre
                style={{
                  background: '#f6f8fa',
                  padding: 16,
                  borderRadius: 4,
                  overflowX: 'auto',
                  maxHeight: 400,
                }}
              >
                {experimentRecord.markdown}
              </pre>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

export default AISummaryPanel
