from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .api.meetings import router as meetings_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="人造肉研发品评会议系统 API",
    description="用于管理人造肉研发项目的品评会议纪要，包含音频处理、AI摘要、邮件发送等功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings_router)


@app.get("/")
async def root():
    return {
        "message": "人造肉研发品评会议系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
