import React, { useState } from 'react'
import { Upload, Button, Progress, message, List, Tag, Typography } from 'antd'
import { UploadOutlined, AudioOutlined, UserOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import { meetingApi } from '../services/api'
import type { AudioProcessingResult } from '../types'

const { Text, Paragraph } = Typography

interface Props {
  meetingId: string
  onProcessingComplete?: (result: AudioProcessingResult) => void
}

const AudioUploadProcessor: React.FC<Props> = ({ meetingId, onProcessingComplete }) => {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<AudioProcessingResult | null>(null)

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择音频文件')
      return
    }

    const file = fileList[0]
    setUploading(true)
    setProgress(0)

    try {
      const interval = setInterval(() => {
        setProgress(p => Math.min(p + 5, 90))
      }, 200)

      setProcessing(true)
      const response = await meetingApi.uploadAudio(meetingId, file as File)

      clearInterval(interval)
      setProgress(100)
      setResult(response.data)
      message.success('音频处理完成')
      onProcessingComplete?.(response.data)
    } catch (error) {
      message.error('音频处理失败')
      console.error(error)
    } finally {
      setUploading(false)
      setProcessing(false)
    }
  }

  const props = {
    fileList,
    maxCount: 1,
    accept: 'audio/*',
    beforeUpload: (file: UploadFile) => {
      setFileList([file])
      return false
    },
    onRemove: () => {
      setFileList([])
      setResult(null)
    },
  }

  const getGroupTag = (group: string) => {
    if (group === 'rd') {
      return <Tag color="blue">研发组</Tag>
    } else if (group === 'sensory') {
      return <Tag color="green">感官评价组</Tag>
    }
    return <Tag>未知</Tag>
  }

  return (
    <div className="chart-container">
      <div className="section-title">会议音频处理</div>

      <div style={{ marginBottom: 16 }}>
        <Upload {...props}>
          <Button icon={<UploadOutlined />}>选择会议录音</Button>
        </Upload>
      </div>

      {fileList.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            onClick={handleUpload}
            loading={uploading}
            icon={<AudioOutlined />}
            disabled={processing}
          >
            {processing ? '处理中...' : '开始处理'}
          </Button>
          {(uploading || processing) && (
            <Progress
              percent={progress}
              status={progress === 100 ? 'success' : 'active'}
              style={{ marginTop: 12 }}
            />
          )}
        </div>
      )}

      {processing && (
        <div style={{ padding: 16, background: '#f5f5f5', borderRadius: 4, marginBottom: 16 }}>
          <Paragraph>
            <Text strong>正在执行以下处理步骤：</Text>
          </Paragraph>
          <List
            size="small"
            dataSource={[
              { step: 1, text: '使用 librosa 去除实验室离心机噪声', done: progress > 30 },
              { step: 2, text: '使用 Whisper 识别生物学术语转录', done: progress > 60 },
              { step: 3, text: '使用 pyannote 分离研发组与感官评价组', done: progress > 90 },
            ]}
            renderItem={item => (
              <List.Item>
                <Text type={item.done ? 'success' : 'secondary'}>
                  {item.done ? '✓' : '○'} 步骤 {item.step}: {item.text}
                </Text>
              </List.Item>
            )}
          />
        </div>
      )}

      {result && (
        <div>
          <div style={{ marginBottom: 12 }}>
            <Text strong>处理完成 - 识别到 {result.speakerSegments.length} 个发言片段</Text>
          </div>
          <div
            style={{
              maxHeight: 300,
              overflowY: 'auto',
              background: '#fafafa',
              padding: 12,
              borderRadius: 4,
            }}
          >
            {result.speakerSegments.map((segment, index) => (
              <div
                key={index}
                style={{
                  marginBottom: 12,
                  padding: 8,
                  background: segment.group === 'rd' ? '#e6f7ff' : '#f6ffed',
                  borderRadius: 4,
                }}
              >
                <div style={{ marginBottom: 4 }}>
                  <UserOutlined style={{ marginRight: 4 }} />
                  <Text strong>{segment.speaker}</Text>
                  {getGroupTag(segment.group)}
                  <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                    {segment.start.toFixed(1)}s - {segment.end.toFixed(1)}s
                  </Text>
                </div>
                <Paragraph style={{ margin: 0 }}>{segment.text}</Paragraph>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AudioUploadProcessor
