from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ParticipantBase(BaseModel):
    name: str
    role: str
    group: str


class ParticipantCreate(ParticipantBase):
    id: str


class Participant(ParticipantBase):
    id: str

    class Config:
        from_attributes = True


class DiscussionSegmentBase(BaseModel):
    speaker: str
    group: str
    content: str
    timestamp: float
    duration: float


class DiscussionSegmentCreate(DiscussionSegmentBase):
    id: str


class DiscussionSegment(DiscussionSegmentBase):
    id: str

    class Config:
        from_attributes = True


class TasteScore(BaseModel):
    juiciness: float
    tenderness: float
    elasticity: float
    flavor: float
    texture: float
    chewiness: float


class TissueEngineeringParams(BaseModel):
    cellDensity: float
    scaffoldPorosity: float
    fiberAlignment: float
    maturationRate: float
    extracellularMatrix: float
    vascularization: float


class MeetingNoteBase(BaseModel):
    title: str
    date: str


class MeetingNoteCreate(MeetingNoteBase):
    participants: List[ParticipantCreate] = []
    tasteScore: Optional[TasteScore] = None
    tissueParams: Optional[TissueEngineeringParams] = None
    discussions: List[DiscussionSegmentCreate] = []


class MeetingNoteUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    participants: Optional[List[ParticipantCreate]] = None
    tasteScore: Optional[TasteScore] = None
    tissueParams: Optional[TissueEngineeringParams] = None
    discussions: Optional[List[DiscussionSegmentCreate]] = None
    summary: Optional[str] = None
    processAdjustments: Optional[str] = None
    flavorOptimizations: Optional[str] = None


class MeetingNote(MeetingNoteBase):
    id: str
    participants: List[Participant] = []
    tasteScore: TasteScore
    tissueParams: TissueEngineeringParams
    discussions: List[DiscussionSegment] = []
    summary: Optional[str] = None
    processAdjustments: Optional[str] = None
    flavorOptimizations: Optional[str] = None
    experimentRecordId: Optional[str] = None
    emailSent: bool = False
    createdAt: datetime

    class Config:
        from_attributes = True


class SpeakerSegment(BaseModel):
    speaker: str
    start: float
    end: float
    text: str
    group: str


class AudioProcessingResult(BaseModel):
    denoisedAudioPath: str
    transcript: str
    speakerSegments: List[SpeakerSegment]


class SummaryResponse(BaseModel):
    summary: str
    processAdjustments: str
    flavorOptimizations: str


class EmailResponse(BaseModel):
    success: bool
    message: str


class ExperimentRecordResponse(BaseModel):
    recordId: str
    markdown: str
