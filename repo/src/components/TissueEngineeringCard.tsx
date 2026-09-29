import React from 'react'
import { Row, Col, Card, Progress, Tooltip } from 'antd'
import type { TissueEngineeringParams } from '../types'

interface Props {
  params: TissueEngineeringParams
  onChange?: (params: TissueEngineeringParams) => void
  readonly?: boolean
}

const paramConfig: {
  key: keyof TissueEngineeringParams
  label: string
  unit: string
  color: string
  description: string
}[] = [
  {
    key: 'cellDensity',
    label: '细胞密度',
    unit: 'cells/cm²',
    color: '#1890ff',
    description: '支架上的肌肉细胞接种密度',
  },
  {
    key: 'scaffoldPorosity',
    label: '支架孔隙率',
    unit: '%',
    color: '#52c41a',
    description: '多孔支架的孔隙体积百分比',
  },
  {
    key: 'fiberAlignment',
    label: '纤维取向度',
    unit: '%',
    color: '#faad14',
    description: '电纺纤维的排列整齐程度',
  },
  {
    key: 'maturationRate',
    label: '成熟度',
    unit: '%',
    color: '#722ed1',
    description: '细胞分化为成熟肌管的比例',
  },
  {
    key: 'extracellularMatrix',
    label: 'ECM分泌量',
    unit: 'μg/mg',
    color: '#eb2f96',
    description: '细胞外基质胶原蛋白含量',
  },
  {
    key: 'vascularization',
    label: '血管化程度',
    unit: '%',
    color: '#13c2c2',
    description: '微血管网络形成程度',
  },
]

const TissueEngineeringCard: React.FC<Props> = ({ params, onChange, readonly = false }) => {
  const handleProgressClick = (key: keyof TissueEngineeringParams, delta: number) => {
    if (readonly || !onChange) return
    const maxValue = key === 'cellDensity' ? 2000000 : 100
    const current = params[key]
    const step = key === 'cellDensity' ? 50000 : 2
    const newValue = Math.min(maxValue, Math.max(0, current + delta * step))
    onChange({ ...params, [key]: newValue })
  }

  const formatValue = (key: keyof TissueEngineeringParams, value: number) => {
    if (key === 'cellDensity') {
      return (value / 1000000).toFixed(2) + 'M'
    }
    return value.toFixed(1)
  }

  const getPercent = (key: keyof TissueEngineeringParams, value: number) => {
    if (key === 'cellDensity') {
      return (value / 2000000) * 100
    }
    return value
  }

  return (
    <div className="chart-container">
      <div className="section-title">组织工程学参数</div>
      <Row gutter={[16, 16]}>
        {paramConfig.map(({ key, label, unit, color, description }) => (
          <Col xs={24} sm={12} md={8} key={key}>
            <Card
              size="small"
              hoverable={!readonly}
              onClick={() => handleProgressClick(key, 1)}
              onContextMenu={(e) => {
                e.preventDefault()
                handleProgressClick(key, -1)
              }}
              style={{ cursor: readonly ? 'default' : 'pointer' }}
            >
              <div style={{ marginBottom: 8 }}>
                <Tooltip title={description}>
                  <span style={{ fontWeight: 500, color: '#333' }}>{label}</span>
                </Tooltip>
                <span style={{ float: 'right', color: '#999', fontSize: 12 }}>{unit}</span>
              </div>
              <div className="param-value" style={{ color, marginBottom: 8 }}>
                {formatValue(key, params[key])}
              </div>
              <Progress
                percent={getPercent(key, params[key])}
                showInfo={false}
                strokeColor={color}
                size="small"
              />
            </Card>
          </Col>
        ))}
      </Row>
      {!readonly && (
        <div style={{ marginTop: 16, textAlign: 'center', color: '#666', fontSize: 13 }}>
          左键点击增加参数，右键点击减少参数
        </div>
      )}
    </div>
  )
}

export default TissueEngineeringCard
