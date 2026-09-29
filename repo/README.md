# 人造肉研发品评会议系统

## 项目简介

这是一个针对人造肉研发项目的品评会议纪要全栈应用，集成了音频处理、AI智能分析和实验记录管理功能。

## 功能特性

### 前端
- 🍖 **口感评分雷达图** - 六维口感评分可视化（多汁性、嫩度、弹性、风味、质感、咀嚼性）
- 🔬 **组织工程学参数展示** - 细胞密度、支架孔隙率、纤维取向度等关键参数
- 🎙️ **音频上传与处理** - 会议录音自动处理
- 🤖 **AI智能分析面板** - 工艺调整方案与风味优化建议
- 📝 **会议管理** - 创建、查看、编辑、删除会议记录

### 后端
- 🎵 **librosa噪声去除** - 去除实验室离心机等低频噪声
- 🗣️ **Whisper语音识别** - 支持生物学术语的精准转录
- 👥 **pyannote声纹分离** - 自动分离研发组与感官评价组发言
- 🧠 **OpenAI智能摘要** - 生成会议摘要、工艺调整方案、风味优化建议
- 📧 **Markdown邮件发送** - 自动发送会议纪要给产品经理
- 📒 **实验记录本集成** - 生成标准化的实验记录文档

## 技术栈

### 前端
- React 18 + TypeScript
- Vite
- ECharts (雷达图)
- Ant Design
- Axios

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- librosa (音频处理)
- OpenAI Whisper (语音识别)
- pyannote.audio (声纹分离)
- OpenAI API (智能摘要)

## 快速开始

### 后端启动

```bash
cd backend
pip install -r ../requirements.txt
cp ../.env.example .env
# 编辑 .env 文件，配置 API keys
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API文档将在 http://localhost:8000/docs 可用

### 前端启动

```bash
npm install
npm run dev
```

前端将在 http://localhost:3000 启动

## 项目结构

```
.
├── backend/
│   ├── main.py                 # FastAPI 主应用
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models.py               # SQLAlchemy 模型
│   ├── schemas.py              # Pydantic 模式
│   ├── api/
│   │   └── meetings.py         # 会议相关 API
│   └── services/
│       ├── audio_processor.py  # 音频处理服务
│       ├── summary_generator.py # AI摘要生成服务
│       ├── email_sender.py     # 邮件发送服务
│       └── experiment_recorder.py # 实验记录服务
├── src/
│   ├── components/
│   │   ├── TasteRadarChart.tsx      # 口感评分雷达图
│   │   ├── TissueEngineeringCard.tsx # 组织工程参数卡片
│   │   ├── AudioUploadProcessor.tsx # 音频上传处理器
│   │   └── AISummaryPanel.tsx       # AI摘要面板
│   ├── pages/
│   │   ├── MeetingList.tsx     # 会议列表页
│   │   └── MeetingDetail.tsx   # 会议详情页
│   ├── services/
│   │   └── api.ts              # API 服务
│   ├── types.ts                # TypeScript 类型定义
│   ├── App.tsx                 # 主应用组件
│   └── main.tsx                # 入口文件
├── requirements.txt            # Python 依赖
├── package.json                # Node 依赖
└── .env.example                # 环境变量示例
```

## 使用说明

1. **创建会议**: 点击"新建会议"，填写会议基本信息，添加参与人员
2. **录入评分**: 在会议详情页调整口感评分雷达图和组织工程学参数
3. **上传音频**: 上传会议录音，系统将自动进行降噪、转录和声纹分离
4. **AI分析**: 点击"生成AI分析报告"，获取智能摘要和优化建议
5. **发送邮件**: 一键发送Markdown格式的会议纪要给产品经理
6. **生成记录**: 自动生成标准化的实验记录本条目

## 注意事项

- 首次使用需要配置 `.env` 文件中的 API keys
- 音频处理可能需要较长时间，请耐心等待
- 系统提供mock数据，即使没有配置真实API也可以体验完整流程
