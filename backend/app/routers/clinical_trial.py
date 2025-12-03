"""
Clinical Trial router for Vocalysis API
Handles multi-sample collection (9-12 data points, 2-5 min each) for personalized results
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import uuid
import os
import numpy as np

from app.models.database import get_db
from app.models.user import User
from app.models.voice_sample import VoiceSample
from app.models.prediction import Prediction
from app.models.clinical_trial import ClinicalTrialParticipant, VoiceSession, PersonalizedBaseline
from app.routers.auth import get_current_user, require_role
from app.services.voice_analysis import VoiceAnalysisService
from app.services.email_service import email_service
from app.utils.config import settings

router = APIRouter()
voice_service = VoiceAnalysisService()

# Constants for clinical trial
MIN_RECORDING_DURATION = 120  # 2 minutes
MAX_RECORDING_DURATION = 300  # 5 minutes
MIN_SAMPLES_REQUIRED = 9
MAX_SAMPLES_ALLOWED = 12
TARGET_SAMPLES = 10


@router.post("/enroll")
async def enroll_participant(
    age: Optional[int] = None,
    gender: Optional[str] = None,
    phone: Optional[str] = None,
    institution: Optional[str] = None,
    preferred_language: str = "english",
    medical_history: Optional[str] = None,
    current_medications: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll user as clinical trial participant"""
    # Check if already enrolled
    existing = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in clinical trial")
    
    # Create participant record
    participant = ClinicalTrialParticipant(
        user_id=current_user.id,
        age=age,
        gender=gender,
        phone=phone,
        institution=institution,
        preferred_language=preferred_language,
        medical_history=medical_history,
        current_medications=current_medications,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
        consent_given=True,
        consent_timestamp=datetime.utcnow(),
        target_samples=TARGET_SAMPLES,
        min_samples_required=MIN_SAMPLES_REQUIRED,
        max_samples_allowed=MAX_SAMPLES_ALLOWED
    )
    
    db.add(participant)
    
    # Update user record
    current_user.is_clinical_trial_participant = True
    current_user.trial_status = "pending"
    
    db.commit()
    db.refresh(participant)
    
    # Send enrollment email
    try:
        email_service.send_clinical_trial_registration(current_user.email, current_user.full_name or "Participant")
    except Exception as e:
        import logging
        logging.error(f"Failed to send enrollment email: {e}")
    
    return {
        "message": "Successfully enrolled in clinical trial",
        "participant_id": participant.id,
        "status": participant.approval_status,
        "samples_required": participant.min_samples_required,
        "target_samples": participant.target_samples
    }


@router.get("/status")
async def get_participant_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current participant's clinical trial status"""
    participant = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        return {
            "enrolled": False,
            "message": "Not enrolled in clinical trial"
        }
    
    # Get voice sessions
    sessions = db.query(VoiceSession).filter(
        VoiceSession.participant_id == participant.id
    ).order_by(VoiceSession.session_number).all()
    
    return {
        "enrolled": True,
        "participant_id": participant.id,
        "approval_status": participant.approval_status,
        "trial_status": participant.trial_status,
        "samples_collected": participant.voice_samples_collected,
        "samples_required": participant.min_samples_required,
        "target_samples": participant.target_samples,
        "max_samples": participant.max_samples_allowed,
        "baseline_established": participant.baseline_established,
        "assigned_psychologist_id": participant.assigned_psychologist_id,
        "sessions": [
            {
                "session_number": s.session_number,
                "status": s.status,
                "duration_seconds": s.actual_duration_seconds,
                "is_valid": s.is_valid,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in sessions
        ]
    }


@router.post("/session/start")
async def start_voice_session(
    session_type: str = "baseline",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new voice recording session (2-5 min required)"""
    participant = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=400, detail="Not enrolled in clinical trial")
    
    if participant.approval_status != "approved":
        raise HTTPException(status_code=403, detail="Clinical trial participation not yet approved")
    
    if participant.voice_samples_collected >= participant.max_samples_allowed:
        raise HTTPException(status_code=400, detail="Maximum samples already collected")
    
    # Get next session number
    session_number = participant.voice_samples_collected + 1
    
    # Create voice session
    session = VoiceSession(
        participant_id=participant.id,
        user_id=current_user.id,
        session_number=session_number,
        session_type=session_type,
        min_duration_seconds=MIN_RECORDING_DURATION,
        max_duration_seconds=MAX_RECORDING_DURATION,
        status="recording",
        recording_started_at=datetime.utcnow()
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "session_number": session_number,
        "min_duration_seconds": MIN_RECORDING_DURATION,
        "max_duration_seconds": MAX_RECORDING_DURATION,
        "message": f"Session {session_number} started. Please record for 2-5 minutes."
    }


@router.post("/session/{session_id}/upload")
async def upload_session_recording(
    session_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload voice recording for a session (must be 2-5 min)"""
    # Get session
    session = db.query(VoiceSession).filter(
        VoiceSession.id == session_id,
        VoiceSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")
    
    # Validate file format
    allowed_formats = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )
    
    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, current_user.id, "clinical_trial")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    sample_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{sample_id}{file_ext}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create voice sample record
    voice_sample = VoiceSample(
        id=sample_id,
        user_id=current_user.id,
        file_path=file_path,
        file_name=file.filename,
        audio_format=file_ext[1:],
        file_size=len(content),
        processing_status="uploaded",
        recorded_via="clinical_trial"
    )
    
    db.add(voice_sample)
    db.commit()
    
    # Analyze the audio
    try:
        result = voice_service.analyze_audio(file_path)
        
        if "error" in result:
            session.status = "failed"
            session.validation_message = result["error"]
            db.commit()
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Check duration (must be 2-5 min)
        duration = result.get("features", {}).get("duration", 0)
        
        if duration < MIN_RECORDING_DURATION:
            session.status = "failed"
            session.is_valid = False
            session.validation_message = f"Recording too short. Minimum {MIN_RECORDING_DURATION} seconds (2 min) required. Got {duration:.1f} seconds."
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Recording too short. Minimum 2 minutes required. Got {duration:.1f} seconds."
            )
        
        if duration > MAX_RECORDING_DURATION:
            session.validation_message = f"Recording longer than recommended ({duration:.1f}s > {MAX_RECORDING_DURATION}s). Using first 5 minutes."
        
        # Update voice sample
        voice_sample.processing_status = "completed"
        voice_sample.duration_seconds = duration
        voice_sample.quality_score = result.get("confidence", 0)
        voice_sample.features = result.get("features", {})
        voice_sample.processed_at = datetime.utcnow()
        
        # Create prediction record
        prediction = Prediction(
            user_id=current_user.id,
            voice_sample_id=sample_id,
            model_version="v1.0-clinical",
            model_type="clinical_trial",
            normal_score=float(result["probabilities"][0]),
            anxiety_score=float(result["probabilities"][1]),
            depression_score=float(result["probabilities"][2]),
            stress_score=float(result["probabilities"][3]),
            overall_risk_level=result.get("risk_level", "low"),
            mental_health_score=result.get("mental_health_score", 0),
            confidence=result.get("confidence", 0),
            phq9_score=result.get("scale_mappings", {}).get("PHQ-9", 0),
            phq9_severity=result.get("scale_mappings", {}).get("interpretations", {}).get("PHQ-9", ""),
            gad7_score=result.get("scale_mappings", {}).get("GAD-7", 0),
            gad7_severity=result.get("scale_mappings", {}).get("interpretations", {}).get("GAD-7", ""),
            pss_score=result.get("scale_mappings", {}).get("PSS", 0),
            pss_severity=result.get("scale_mappings", {}).get("interpretations", {}).get("PSS", ""),
            wemwbs_score=result.get("scale_mappings", {}).get("WEMWBS", 0),
            wemwbs_severity=result.get("scale_mappings", {}).get("interpretations", {}).get("WEMWBS", ""),
            interpretations=result.get("interpretations", []),
            recommendations=result.get("recommendations", []),
            voice_features=result.get("features", {})
        )
        
        db.add(prediction)
        
        # Update session
        session.voice_sample_id = sample_id
        session.prediction_id = prediction.id
        session.actual_duration_seconds = duration
        session.audio_quality_score = result.get("confidence", 0)
        session.session_features = result.get("features", {})
        session.status = "completed"
        session.is_valid = True
        session.recording_completed_at = datetime.utcnow()
        
        # Update participant
        participant = db.query(ClinicalTrialParticipant).filter(
            ClinicalTrialParticipant.id == session.participant_id
        ).first()
        
        participant.voice_samples_collected += 1
        
        # Check if baseline can be established (after 9 samples)
        if participant.voice_samples_collected >= MIN_SAMPLES_REQUIRED and not participant.baseline_established:
            # Calculate personalized baseline
            await _establish_baseline(participant.id, current_user.id, db)
        
        db.commit()
        db.refresh(session)
        db.refresh(prediction)
        
        return {
            "message": "Recording uploaded and analyzed successfully",
            "session_id": session.id,
            "session_number": session.session_number,
            "duration_seconds": duration,
            "prediction_id": prediction.id,
            "samples_collected": participant.voice_samples_collected,
            "samples_remaining": max(0, participant.min_samples_required - participant.voice_samples_collected),
            "baseline_established": participant.baseline_established,
            "analysis": {
                "mental_health_score": prediction.mental_health_score,
                "risk_level": prediction.overall_risk_level,
                "phq9_score": prediction.phq9_score,
                "gad7_score": prediction.gad7_score,
                "pss_score": prediction.pss_score,
                "wemwbs_score": prediction.wemwbs_score
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.status = "failed"
        session.validation_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def _establish_baseline(participant_id: str, user_id: str, db: Session):
    """Establish personalized baseline from collected samples"""
    # Get all completed sessions
    sessions = db.query(VoiceSession).filter(
        VoiceSession.participant_id == participant_id,
        VoiceSession.status == "completed",
        VoiceSession.is_valid == True
    ).all()
    
    if len(sessions) < MIN_SAMPLES_REQUIRED:
        return
    
    # Collect features from all sessions
    all_features = [s.session_features for s in sessions if s.session_features]
    
    if not all_features:
        return
    
    # Calculate baseline averages
    baseline_features = {}
    feature_keys = all_features[0].keys() if all_features else []
    
    for key in feature_keys:
        values = [f.get(key) for f in all_features if f.get(key) is not None and isinstance(f.get(key), (int, float))]
        if values:
            baseline_features[key] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values))
            }
    
    # Create or update personalized baseline
    existing_baseline = db.query(PersonalizedBaseline).filter(
        PersonalizedBaseline.user_id == user_id
    ).first()
    
    if existing_baseline:
        existing_baseline.samples_used = len(sessions)
        existing_baseline.baseline_features = baseline_features
        existing_baseline.baseline_pitch_mean = baseline_features.get("pitch_mean", {}).get("mean")
        existing_baseline.baseline_pitch_std = baseline_features.get("pitch_std", {}).get("mean")
        existing_baseline.baseline_pitch_cv = baseline_features.get("pitch_cv", {}).get("mean")
        existing_baseline.baseline_rms_mean = baseline_features.get("rms_mean", {}).get("mean")
        existing_baseline.baseline_rms_std = baseline_features.get("rms_std", {}).get("mean")
        existing_baseline.baseline_speech_rate = baseline_features.get("speech_rate", {}).get("mean")
        existing_baseline.baseline_jitter = baseline_features.get("jitter_rel", {}).get("mean")
        existing_baseline.baseline_shimmer = baseline_features.get("shimmer_rel", {}).get("mean")
        existing_baseline.baseline_hnr = baseline_features.get("hnr_mean", {}).get("mean")
        existing_baseline.baseline_mfcc_mean = baseline_features.get("mfcc_mean", {}).get("mean")
        existing_baseline.baseline_mfcc_std = baseline_features.get("mfcc_std", {}).get("mean")
        existing_baseline.baseline_confidence = 0.8 + (len(sessions) - MIN_SAMPLES_REQUIRED) * 0.02
        existing_baseline.last_updated_at = datetime.utcnow()
    else:
        baseline = PersonalizedBaseline(
            user_id=user_id,
            participant_id=participant_id,
            samples_used=len(sessions),
            baseline_features=baseline_features,
            baseline_pitch_mean=baseline_features.get("pitch_mean", {}).get("mean"),
            baseline_pitch_std=baseline_features.get("pitch_std", {}).get("mean"),
            baseline_pitch_cv=baseline_features.get("pitch_cv", {}).get("mean"),
            baseline_rms_mean=baseline_features.get("rms_mean", {}).get("mean"),
            baseline_rms_std=baseline_features.get("rms_std", {}).get("mean"),
            baseline_speech_rate=baseline_features.get("speech_rate", {}).get("mean"),
            baseline_jitter=baseline_features.get("jitter_rel", {}).get("mean"),
            baseline_shimmer=baseline_features.get("shimmer_rel", {}).get("mean"),
            baseline_hnr=baseline_features.get("hnr_mean", {}).get("mean"),
            baseline_mfcc_mean=baseline_features.get("mfcc_mean", {}).get("mean"),
            baseline_mfcc_std=baseline_features.get("mfcc_std", {}).get("mean"),
            baseline_confidence=0.8
        )
        db.add(baseline)
    
    # Update participant
    participant = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.id == participant_id
    ).first()
    
    participant.baseline_established = True
    participant.baseline_data = baseline_features
    participant.baseline_established_at = datetime.utcnow()
    participant.trial_status = "active"


@router.get("/baseline")
async def get_personalized_baseline(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's personalized baseline"""
    baseline = db.query(PersonalizedBaseline).filter(
        PersonalizedBaseline.user_id == current_user.id
    ).first()
    
    if not baseline:
        return {
            "established": False,
            "message": "Baseline not yet established. Complete at least 9 voice sessions."
        }
    
    return {
        "established": True,
        "samples_used": baseline.samples_used,
        "confidence": baseline.baseline_confidence,
        "baseline": {
            "pitch_mean": baseline.baseline_pitch_mean,
            "pitch_std": baseline.baseline_pitch_std,
            "pitch_cv": baseline.baseline_pitch_cv,
            "rms_mean": baseline.baseline_rms_mean,
            "rms_std": baseline.baseline_rms_std,
            "speech_rate": baseline.baseline_speech_rate,
            "jitter": baseline.baseline_jitter,
            "shimmer": baseline.baseline_shimmer,
            "hnr": baseline.baseline_hnr,
            "mfcc_mean": baseline.baseline_mfcc_mean,
            "mfcc_std": baseline.baseline_mfcc_std
        },
        "thresholds": {
            "anxiety": baseline.anxiety_threshold,
            "depression": baseline.depression_threshold,
            "stress": baseline.stress_threshold
        },
        "last_updated": baseline.last_updated_at.isoformat() if baseline.last_updated_at else None
    }


@router.post("/analyze-personalized")
async def analyze_with_personalization(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze voice with personalized baseline comparison"""
    # Get baseline
    baseline = db.query(PersonalizedBaseline).filter(
        PersonalizedBaseline.user_id == current_user.id
    ).first()
    
    if not baseline:
        raise HTTPException(
            status_code=400,
            detail="Personalized baseline not established. Complete at least 9 voice sessions first."
        )
    
    # Validate file
    allowed_formats = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_formats:
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # Read and save file
    content = await file.read()
    upload_dir = os.path.join(settings.UPLOAD_DIR, current_user.id, "personalized")
    os.makedirs(upload_dir, exist_ok=True)
    
    sample_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{sample_id}{file_ext}")
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Analyze
    result = voice_service.analyze_audio(file_path)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    features = result.get("features", {})
    
    # Compare with baseline
    deviations = {}
    baseline_features = baseline.baseline_features or {}
    
    for key, value in features.items():
        if isinstance(value, (int, float)) and key in baseline_features:
            baseline_data = baseline_features[key]
            if isinstance(baseline_data, dict) and "mean" in baseline_data and "std" in baseline_data:
                baseline_mean = baseline_data["mean"]
                baseline_std = baseline_data["std"]
                if baseline_std > 0:
                    z_score = (value - baseline_mean) / baseline_std
                    deviations[key] = {
                        "current": value,
                        "baseline_mean": baseline_mean,
                        "baseline_std": baseline_std,
                        "z_score": z_score,
                        "deviation_percent": ((value - baseline_mean) / baseline_mean * 100) if baseline_mean != 0 else 0
                    }
    
    # Calculate personalized risk indicators
    personalized_risk = {
        "anxiety": False,
        "depression": False,
        "stress": False
    }
    
    # Check for anxiety indicators (deviation from baseline)
    pitch_cv_dev = deviations.get("pitch_cv", {}).get("z_score", 0)
    speech_rate_dev = deviations.get("speech_rate", {}).get("z_score", 0)
    if pitch_cv_dev > 1.5 or speech_rate_dev > 1.5:
        personalized_risk["anxiety"] = True
    
    # Check for depression indicators
    rms_dev = deviations.get("rms_mean", {}).get("z_score", 0)
    if pitch_cv_dev < -1.5 or rms_dev < -1.5 or speech_rate_dev < -1.5:
        personalized_risk["depression"] = True
    
    # Check for stress indicators
    jitter_dev = deviations.get("jitter_rel", {}).get("z_score", 0)
    hnr_dev = deviations.get("hnr_mean", {}).get("z_score", 0)
    if jitter_dev > 1.5 or hnr_dev < -1.5:
        personalized_risk["stress"] = True
    
    return {
        "analysis": result,
        "personalization": {
            "baseline_samples": baseline.samples_used,
            "baseline_confidence": baseline.baseline_confidence,
            "deviations": deviations,
            "personalized_risk": personalized_risk,
            "interpretation": _generate_personalized_interpretation(deviations, personalized_risk)
        }
    }


def _generate_personalized_interpretation(deviations: dict, risk: dict) -> str:
    """Generate personalized interpretation based on baseline comparison"""
    interpretations = []
    
    if risk["anxiety"]:
        interpretations.append("Your voice patterns show elevated anxiety indicators compared to your baseline.")
    
    if risk["depression"]:
        interpretations.append("Your voice patterns show reduced energy and variability compared to your baseline, which may indicate low mood.")
    
    if risk["stress"]:
        interpretations.append("Your voice quality metrics indicate elevated stress compared to your baseline.")
    
    if not any(risk.values()):
        interpretations.append("Your voice patterns are within normal range compared to your personalized baseline.")
    
    return " ".join(interpretations)


# Admin endpoints for clinical trial management
@router.get("/admin/participants")
async def get_all_participants(
    status: Optional[str] = None,
    current_user: User = Depends(require_role(["admin", "super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get all clinical trial participants (admin only)"""
    query = db.query(ClinicalTrialParticipant)
    
    if status:
        query = query.filter(ClinicalTrialParticipant.approval_status == status)
    
    participants = query.all()
    
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "age": p.age,
            "gender": p.gender,
            "institution": p.institution,
            "approval_status": p.approval_status,
            "trial_status": p.trial_status,
            "samples_collected": p.voice_samples_collected,
            "target_samples": p.target_samples,
            "baseline_established": p.baseline_established,
            "assigned_psychologist_id": p.assigned_psychologist_id,
            "enrollment_date": p.enrollment_date.isoformat() if p.enrollment_date else None
        }
        for p in participants
    ]


@router.post("/admin/approve/{participant_id}")
async def approve_participant(
    participant_id: str,
    psychologist_id: Optional[str] = None,
    current_user: User = Depends(require_role(["admin", "super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Approve clinical trial participant (admin only)"""
    participant = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    participant.approval_status = "approved"
    participant.approved_by = current_user.id
    participant.approval_date = datetime.utcnow()
    participant.trial_status = "enrolled"
    
    if psychologist_id:
        participant.assigned_psychologist_id = psychologist_id
        participant.assignment_date = datetime.utcnow()
    
    # Update user record
    user = db.query(User).filter(User.id == participant.user_id).first()
    if user:
        user.trial_status = "approved"
        user.approved_by = current_user.id
        user.approval_date = datetime.utcnow()
        if psychologist_id:
            user.assigned_psychologist_id = psychologist_id
            user.assignment_date = datetime.utcnow()
    
    db.commit()
    
    # Send approval email
    try:
        psychologist_name = None
        if psychologist_id:
            psychologist = db.query(User).filter(User.id == psychologist_id).first()
            if psychologist:
                psychologist_name = psychologist.full_name
        
        email_service.send_clinical_trial_approved(user.email, user.full_name or "Participant", psychologist_name)
    except Exception as e:
        import logging
        logging.error(f"Failed to send approval email: {e}")
    
    return {"message": "Participant approved successfully"}


@router.post("/admin/reject/{participant_id}")
async def reject_participant(
    participant_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role(["admin", "super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Reject clinical trial participant (admin only)"""
    participant = db.query(ClinicalTrialParticipant).filter(
        ClinicalTrialParticipant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    participant.approval_status = "rejected"
    participant.rejection_reason = reason
    participant.approved_by = current_user.id
    participant.approval_date = datetime.utcnow()
    
    # Update user record
    user = db.query(User).filter(User.id == participant.user_id).first()
    if user:
        user.trial_status = "rejected"
    
    db.commit()
    
    # Send rejection email
    try:
        email_service.send_clinical_trial_rejected(user.email, user.full_name or "Participant", reason)
    except Exception as e:
        import logging
        logging.error(f"Failed to send rejection email: {e}")
    
    return {"message": "Participant rejected"}
