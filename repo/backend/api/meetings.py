from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from .. import models, schemas
from ..services import audio_processor, summary_generator, email_sender, experiment_recorder

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _replace_children(db: Session, meeting: models.MeetingNote, meeting_data: schemas.MeetingNoteUpdate):
    """整体替换子表记录：先删除旧行并 flush，再插入新行，避免主键冲突。"""
    if meeting_data.participants is not None:
        db.query(models.Participant).filter(
            models.Participant.meeting_id == meeting.id
        ).delete(synchronize_session=False)
        db.flush()
        for p in meeting_data.participants:
            meeting.participants.append(models.Participant(
                id=p.id,
                name=p.name,
                role=p.role,
                group=p.group,
            ))

    if meeting_data.discussions is not None:
        db.query(models.DiscussionSegment).filter(
            models.DiscussionSegment.meeting_id == meeting.id
        ).delete(synchronize_session=False)
        db.flush()
        for d in meeting_data.discussions:
            meeting.discussions.append(models.DiscussionSegment(
                id=d.id,
                speaker=d.speaker,
                group=d.group,
                content=d.content,
                timestamp=d.timestamp,
                duration=d.duration,
            ))


def _meeting_to_schema(meeting: models.MeetingNote) -> schemas.MeetingNote:
    """将数据库模型转换为Pydantic schema"""
    return schemas.MeetingNote(
        id=meeting.id,
        title=meeting.title,
        date=meeting.date,
        participants=[
            schemas.Participant(id=p.id, name=p.name, role=p.role, group=p.group)
            for p in meeting.participants
        ],
        tasteScore=schemas.TasteScore(
            juiciness=meeting.juiciness,
            tenderness=meeting.tenderness,
            elasticity=meeting.elasticity,
            flavor=meeting.flavor,
            texture=meeting.texture,
            chewiness=meeting.chewiness,
        ),
        tissueParams=schemas.TissueEngineeringParams(
            cellDensity=meeting.cell_density,
            scaffoldPorosity=meeting.scaffold_porosity,
            fiberAlignment=meeting.fiber_alignment,
            maturationRate=meeting.maturation_rate,
            extracellularMatrix=meeting.extracellular_matrix,
            vascularization=meeting.vascularization,
        ),
        discussions=[
            schemas.DiscussionSegment(
                id=d.id,
                speaker=d.speaker,
                group=d.group,
                content=d.content,
                timestamp=d.timestamp,
                duration=d.duration,
            )
            for d in meeting.discussions
        ],
        summary=meeting.summary,
        processAdjustments=meeting.process_adjustments,
        flavorOptimizations=meeting.flavor_optimizations,
        experimentRecordId=meeting.experiment_record_id,
        emailSent=meeting.email_sent,
        createdAt=meeting.created_at,
    )


@router.get("", response_model=List[schemas.MeetingNote])
def get_meetings(db: Session = Depends(get_db)):
    meetings = db.query(models.MeetingNote).order_by(models.MeetingNote.created_at.desc()).all()
    return [_meeting_to_schema(m) for m in meetings]


@router.get("/{meeting_id}", response_model=schemas.MeetingNote)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return _meeting_to_schema(meeting)


@router.post("", response_model=schemas.MeetingNote)
def create_meeting(meeting_data: schemas.MeetingNoteCreate, db: Session = Depends(get_db)):
    meeting_id = str(uuid.uuid4())

    meeting = models.MeetingNote(
        id=meeting_id,
        title=meeting_data.title,
        date=meeting_data.date,
    )

    if meeting_data.tasteScore:
        meeting.juiciness = meeting_data.tasteScore.juiciness
        meeting.tenderness = meeting_data.tasteScore.tenderness
        meeting.elasticity = meeting_data.tasteScore.elasticity
        meeting.flavor = meeting_data.tasteScore.flavor
        meeting.texture = meeting_data.tasteScore.texture
        meeting.chewiness = meeting_data.tasteScore.chewiness

    if meeting_data.tissueParams:
        meeting.cell_density = meeting_data.tissueParams.cellDensity
        meeting.scaffold_porosity = meeting_data.tissueParams.scaffoldPorosity
        meeting.fiber_alignment = meeting_data.tissueParams.fiberAlignment
        meeting.maturation_rate = meeting_data.tissueParams.maturationRate
        meeting.extracellular_matrix = meeting_data.tissueParams.extracellularMatrix
        meeting.vascularization = meeting_data.tissueParams.vascularization

    for p in meeting_data.participants:
        participant = models.Participant(
            id=p.id,
            name=p.name,
            role=p.role,
            group=p.group,
        )
        meeting.participants.append(participant)

    for d in meeting_data.discussions:
        discussion = models.DiscussionSegment(
            id=d.id,
            speaker=d.speaker,
            group=d.group,
            content=d.content,
            timestamp=d.timestamp,
            duration=d.duration,
        )
        meeting.discussions.append(discussion)

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return _meeting_to_schema(meeting)


@router.put("/{meeting_id}", response_model=schemas.MeetingNote)
def update_meeting(meeting_id: str, meeting_data: schemas.MeetingNoteUpdate, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting_data.title is not None:
        meeting.title = meeting_data.title
    if meeting_data.date is not None:
        meeting.date = meeting_data.date

    if meeting_data.tasteScore is not None:
        meeting.juiciness = meeting_data.tasteScore.juiciness
        meeting.tenderness = meeting_data.tasteScore.tenderness
        meeting.elasticity = meeting_data.tasteScore.elasticity
        meeting.flavor = meeting_data.tasteScore.flavor
        meeting.texture = meeting_data.tasteScore.texture
        meeting.chewiness = meeting_data.tasteScore.chewiness

    if meeting_data.tissueParams is not None:
        meeting.cell_density = meeting_data.tissueParams.cellDensity
        meeting.scaffold_porosity = meeting_data.tissueParams.scaffoldPorosity
        meeting.fiber_alignment = meeting_data.tissueParams.fiberAlignment
        meeting.maturation_rate = meeting_data.tissueParams.maturationRate
        meeting.extracellular_matrix = meeting_data.tissueParams.extracellularMatrix
        meeting.vascularization = meeting_data.tissueParams.vascularization

    _replace_children(db, meeting, meeting_data)

    # 摘要类字段：显式传 null 表示清空，未传则保持不变
    if "summary" in meeting_data.model_fields_set:
        meeting.summary = meeting_data.summary
    if "processAdjustments" in meeting_data.model_fields_set:
        meeting.process_adjustments = meeting_data.processAdjustments
    if "flavorOptimizations" in meeting_data.model_fields_set:
        meeting.flavor_optimizations = meeting_data.flavorOptimizations

    db.commit()
    db.refresh(meeting)

    return _meeting_to_schema(meeting)


@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()

    return {"message": "Meeting deleted successfully"}


@router.put("/{meeting_id}/taste-score", response_model=schemas.MeetingNote)
def update_taste_score(meeting_id: str, score: schemas.TasteScore, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.juiciness = score.juiciness
    meeting.tenderness = score.tenderness
    meeting.elasticity = score.elasticity
    meeting.flavor = score.flavor
    meeting.texture = score.texture
    meeting.chewiness = score.chewiness

    db.commit()
    db.refresh(meeting)

    return _meeting_to_schema(meeting)


@router.put("/{meeting_id}/tissue-params", response_model=schemas.MeetingNote)
def update_tissue_params(meeting_id: str, params: schemas.TissueEngineeringParams, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.cell_density = params.cellDensity
    meeting.scaffold_porosity = params.scaffoldPorosity
    meeting.fiber_alignment = params.fiberAlignment
    meeting.maturation_rate = params.maturationRate
    meeting.extracellular_matrix = params.extracellularMatrix
    meeting.vascularization = params.vascularization

    db.commit()
    db.refresh(meeting)

    return _meeting_to_schema(meeting)


@router.post("/{meeting_id}/audio", response_model=schemas.AudioProcessingResult)
async def process_audio(meeting_id: str, audio: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    audio_content = await audio.read()
    result = audio_processor.process_audio(audio_content, meeting_id=meeting_id)

    db.query(models.DiscussionSegment).filter(
        models.DiscussionSegment.meeting_id == meeting.id
    ).delete(synchronize_session=False)
    db.flush()
    for idx, seg in enumerate(result["speakerSegments"]):
        discussion = models.DiscussionSegment(
            id=f"disc-{meeting_id}-{idx}",
            speaker=seg.speaker,
            group=seg.group,
            content=seg.text,
            timestamp=seg.start,
            duration=seg.end - seg.start,
        )
        meeting.discussions.append(discussion)

    db.commit()

    return result


@router.post("/{meeting_id}/summary", response_model=schemas.SummaryResponse)
def generate_summary(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    taste_score = schemas.TasteScore(
        juiciness=meeting.juiciness,
        tenderness=meeting.tenderness,
        elasticity=meeting.elasticity,
        flavor=meeting.flavor,
        texture=meeting.texture,
        chewiness=meeting.chewiness,
    )

    tissue_params = schemas.TissueEngineeringParams(
        cellDensity=meeting.cell_density,
        scaffoldPorosity=meeting.scaffold_porosity,
        fiberAlignment=meeting.fiber_alignment,
        maturationRate=meeting.maturation_rate,
        extracellularMatrix=meeting.extracellular_matrix,
        vascularization=meeting.vascularization,
    )

    discussions = [
        schemas.DiscussionSegment(
            id=d.id,
            speaker=d.speaker,
            group=d.group,
            content=d.content,
            timestamp=d.timestamp,
            duration=d.duration,
        )
        for d in meeting.discussions
    ]

    participants = [
        schemas.Participant(id=p.id, name=p.name, role=p.role, group=p.group)
        for p in meeting.participants
    ]

    result = summary_generator.generate_summary(
        discussions=discussions,
        taste_score=taste_score,
        tissue_params=tissue_params,
        participants=participants,
    )

    meeting.summary = result["summary"]
    meeting.process_adjustments = result["processAdjustments"]
    meeting.flavor_optimizations = result["flavorOptimizations"]
    db.commit()

    return result


@router.post("/{meeting_id}/email", response_model=schemas.EmailResponse)
def send_email(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    success = email_sender.send_meeting_email(meeting)

    if success:
        meeting.email_sent = True
        db.commit()

    return {
        "success": success,
        "message": "Email sent successfully" if success else "Failed to send email"
    }


@router.post("/{meeting_id}/experiment-record", response_model=schemas.ExperimentRecordResponse)
def create_experiment_record(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingNote).filter(models.MeetingNote.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    result = experiment_recorder.create_record(meeting)

    meeting.experiment_record_id = result["recordId"]
    db.commit()

    return result
