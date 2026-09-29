import React from 'react'
import ReactECharts from 'echarts-for-react'
import type { TasteScore } from '../types'

interface Props {
  score: TasteScore
  onChange?: (score: TasteScore) => void
  readonly?: boolean
}

const labels: (keyof TasteScore)[] = ['juiciness', 'tenderness', 'elasticity', 'flavor', 'texture', 'chewiness']

const labelMap: Record<keyof TasteScore, string> = {
  juiciness: '多汁性',
  tenderness: '嫩度',
  elasticity: '弹性',
  flavor: '风味',
  texture: '质感',
  chewiness: '咀嚼性',
}

const TasteRadarChart: React.FC<Props> = ({ score, onChange, readonly = false }) => {
  const option = {
    title: {
      text: '口感评分雷达图',
      left: 'center',
      textStyle: { fontSize: 16, fontWeight: 600 },
    },
    tooltip: {
      trigger: 'item',
    },
    legend: {
      bottom: 10,
      data: ['当前样本', '对照组'],
    },
    radar: {
      indicator: labels.map(key => ({
        name: labelMap[key],
        max: 10,
      })),
      radius: '65%',
      center: ['50%', '55%'],
      splitNumber: 5,
      axisName: {
        color: '#333',
        fontSize: 13,
      },
      splitArea: {
        areaStyle: {
          color: ['#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da', '#adb5bd'],
        },
      },
    },
    series: [
      {
        name: '口感评分',
        type: 'radar',
        data: [
          {
            value: labels.map(key => score[key]),
            name: '当前样本',
            itemStyle: { color: '#667eea' },
            areaStyle: { color: 'rgba(102, 126, 234, 0.3)' },
            lineStyle: { width: 2 },
          },
          {
            value: [7.5, 7.0, 7.2, 7.8, 7.3, 7.1],
            name: '对照组',
            itemStyle: { color: '#f093fb' },
            areaStyle: { color: 'rgba(240, 147, 251, 0.2)' },
            lineStyle: { width: 2, type: 'dashed' },
          },
        ],
      },
    ],
  }

  const handleChartClick = (params: any) => {
    if (readonly || !onChange) return
    if (params.componentType === 'radar') {
      const key = labels[params.indicatorIndex]
      const currentValue = score[key]
      const newValue = Math.min(10, Math.max(0, currentValue + 0.5))
      onChange({ ...score, [key]: newValue })
    }
  }

  return (
    <div className="chart-container">
      <ReactECharts
        option={option}
        style={{ height: '450px', width: '100%' }}
        onEvents={readonly ? {} : { click: handleChartClick }}
      />
      {!readonly && (
        <div style={{ marginTop: 16, textAlign: 'center', color: '#666', fontSize: 13 }}>
          点击雷达图指标可调整评分（每次±0.5）
        </div>
      )}
    </div>
  )
}

export default TasteRadarChart
