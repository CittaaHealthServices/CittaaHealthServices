"""
Psychologist router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.models.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample
from app.models.clinical_assessment import ClinicalAssessment
from app.routers.auth import get_current_user, require_role

router = APIRouter()

class ClinicalAssessmentCreate(BaseModel):
    """Schema for creating clinical assessment"""
    patient_id: str
    phq9_score: Optional[int] = None
    gad7_score: Optional[int] = None
    pss_score: Optional[int] = None
    clinician_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    ground_truth_label: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    session_duration_minutes: Optional[int] = None

class ClinicalAssessmentResponse(BaseModel):
    """Schema for clinical assessment response"""
    id: str
    user_id: str
    psychologist_id: Optional[str] = None
    assessment_date: datetime
    phq9_score: Optional[int] = None
    gad7_score: Optional[int] = None
    pss_score: Optional[int] = None
    clinician_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    ground_truth_label: Optional[str] = None
    session_number: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/patients")
async def get_assigned_patients(
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to the psychologist"""
    patients = db.query(User).filter(
        User.assigned_psychologist_id == current_user.id,
        User.role == "patient"
    ).all()
    
    result = []
    for patient in patients:
        # Get latest prediction
        latest_pred = db.query(Prediction).filter(
            Prediction.user_id == patient.id
        ).order_by(Prediction.predicted_at.desc()).first()
        
        # Get total sessions
        total_sessions = db.query(ClinicalAssessment).filter(
            ClinicalAssessment.user_id == patient.id,
            ClinicalAssessment.psychologist_id == current_user.id
        ).count()
        
        result.append({
            "id": patient.id,
            "email": patient.email,
            "full_name": patient.full_name,
            "phone": patient.phone,
            "age_range": patient.age_range,
            "gender": patient.gender,
            "assignment_date": patient.assignment_date.isoformat() if patient.assignment_date else None,
            "latest_risk_level": latest_pred.overall_risk_level if latest_pred else "unknown",
            "latest_mental_health_score": latest_pred.mental_health_score if latest_pred else None,
            "total_sessions": total_sessions
        })
    
    return {"patients": result, "total": len(result)}

@router.get("/patients/{patient_id}")
async def get_patient_details(
    patient_id: str,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get detailed patient information"""
    patient = db.query(User).filter(
        User.id == patient_id,
        User.assigned_psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not assigned to you")
    
    # Get all predictions
    predictions = db.query(Prediction).filter(
        Prediction.user_id == patient_id
    ).order_by(Prediction.predicted_at.desc()).limit(20).all()
    
    # Get all clinical assessments
    assessments = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.user_id == patient_id
    ).order_by(ClinicalAssessment.assessment_date.desc()).all()
    
    # Get voice samples count
    voice_samples_count = db.query(VoiceSample).filter(
        VoiceSample.user_id == patient_id
    ).count()
    
    return {
        "patient": {
            "id": patient.id,
            "email": patient.email,
            "full_name": patient.full_name,
            "phone": patient.phone,
            "age_range": patient.age_range,
            "gender": patient.gender,
            "language_preference": patient.language_preference,
            "consent_given": patient.consent_given,
            "assignment_date": patient.assignment_date.isoformat() if patient.assignment_date else None,
            "created_at": patient.created_at.isoformat() if patient.created_at else None
        },
        "predictions": [
            {
                "id": p.id,
                "predicted_at": p.predicted_at.isoformat(),
                "overall_risk_level": p.overall_risk_level,
                "mental_health_score": p.mental_health_score,
                "depression_score": p.depression_score,
                "anxiety_score": p.anxiety_score,
                "stress_score": p.stress_score,
                "phq9_score": p.phq9_score,
                "gad7_score": p.gad7_score,
                "pss_score": p.pss_score,
                "confidence": p.confidence
            }
            for p in predictions
        ],
        "clinical_assessments": [
            ClinicalAssessmentResponse.model_validate(a) for a in assessments
        ],
        "voice_samples_count": voice_samples_count
    }

@router.post("/assessments", response_model=ClinicalAssessmentResponse)
async def create_clinical_assessment(
    assessment_data: ClinicalAssessmentCreate,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Create a new clinical assessment for a patient"""
    # Verify patient is assigned to this psychologist
    patient = db.query(User).filter(
        User.id == assessment_data.patient_id,
        User.assigned_psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not assigned to you")
    
    # Get session number
    existing_sessions = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.user_id == assessment_data.patient_id,
        ClinicalAssessment.psychologist_id == current_user.id
    ).count()
    
    assessment = ClinicalAssessment(
        user_id=assessment_data.patient_id,
        psychologist_id=current_user.id,
        phq9_score=assessment_data.phq9_score,
        gad7_score=assessment_data.gad7_score,
        pss_score=assessment_data.pss_score,
        clinician_notes=assessment_data.clinician_notes,
        diagnosis=assessment_data.diagnosis,
        treatment_plan=assessment_data.treatment_plan,
        ground_truth_label=assessment_data.ground_truth_label,
        follow_up_date=assessment_data.follow_up_date,
        session_duration_minutes=assessment_data.session_duration_minutes,
        session_number=existing_sessions + 1
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return ClinicalAssessmentResponse.model_validate(assessment)

@router.get("/assessments/{patient_id}", response_model=List[ClinicalAssessmentResponse])
async def get_patient_assessments(
    patient_id: str,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get all clinical assessments for a patient"""
    # Verify patient is assigned to this psychologist
    patient = db.query(User).filter(
        User.id == patient_id,
        User.assigned_psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not assigned to you")
    
    assessments = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.user_id == patient_id
    ).order_by(ClinicalAssessment.assessment_date.desc()).all()
    
    return [ClinicalAssessmentResponse.model_validate(a) for a in assessments]

@router.put("/assessments/{assessment_id}")
async def update_clinical_assessment(
    assessment_id: str,
    update_data: ClinicalAssessmentCreate,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Update a clinical assessment"""
    assessment = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.id == assessment_id,
        ClinicalAssessment.psychologist_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if update_data.phq9_score is not None:
        assessment.phq9_score = update_data.phq9_score
    if update_data.gad7_score is not None:
        assessment.gad7_score = update_data.gad7_score
    if update_data.pss_score is not None:
        assessment.pss_score = update_data.pss_score
    if update_data.clinician_notes is not None:
        assessment.clinician_notes = update_data.clinician_notes
    if update_data.diagnosis is not None:
        assessment.diagnosis = update_data.diagnosis
    if update_data.treatment_plan is not None:
        assessment.treatment_plan = update_data.treatment_plan
    if update_data.ground_truth_label is not None:
        assessment.ground_truth_label = update_data.ground_truth_label
    if update_data.follow_up_date is not None:
        assessment.follow_up_date = update_data.follow_up_date
    
    db.commit()
    db.refresh(assessment)
    
    return ClinicalAssessmentResponse.model_validate(assessment)

@router.get("/high-risk-patients")
async def get_high_risk_patients(
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get patients with high risk levels"""
    # Get assigned patients
    patients = db.query(User).filter(
        User.assigned_psychologist_id == current_user.id,
        User.role == "patient"
    ).all()
    
    high_risk = []
    for patient in patients:
        latest_pred = db.query(Prediction).filter(
            Prediction.user_id == patient.id
        ).order_by(Prediction.predicted_at.desc()).first()
        
        if latest_pred and latest_pred.overall_risk_level == "high":
            high_risk.append({
                "patient_id": patient.id,
                "email": patient.email,
                "full_name": patient.full_name,
                "phone": patient.phone,
                "risk_level": latest_pred.overall_risk_level,
                "mental_health_score": latest_pred.mental_health_score,
                "depression_score": latest_pred.depression_score,
                "anxiety_score": latest_pred.anxiety_score,
                "stress_score": latest_pred.stress_score,
                "last_assessment": latest_pred.predicted_at.isoformat()
            })
    
    return {"high_risk_patients": high_risk, "count": len(high_risk)}

@router.get("/patients/{patient_id}/voice-samples")
async def get_patient_voice_samples(
    patient_id: str,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get all voice samples for a patient"""
    patient = db.query(User).filter(
        User.id == patient_id,
        User.assigned_psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not assigned to you")
    
    samples = db.query(VoiceSample).filter(
        VoiceSample.user_id == patient_id
    ).order_by(VoiceSample.recorded_at.desc()).all()
    
    return {
        "samples": [
            {
                "id": s.id,
                "file_name": s.file_name,
                "duration_seconds": s.duration_seconds,
                "quality_score": s.quality_score,
                "processing_status": s.processing_status,
                "recorded_at": s.recorded_at.isoformat() if s.recorded_at else None,
                "processed_at": s.processed_at.isoformat() if s.processed_at else None
            }
            for s in samples
        ],
        "total": len(samples)
    }

@router.post("/patients/{patient_id}/analyze")
async def analyze_patient_voice(
    patient_id: str,
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Perform voice analysis on a patient's voice samples (psychologist-initiated)"""
    from app.services.voice_analysis import VoiceAnalysisService
    
    patient = db.query(User).filter(
        User.id == patient_id,
        User.assigned_psychologist_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or not assigned to you")
    
    voice_service = VoiceAnalysisService()
    
    latest_sample = db.query(VoiceSample).filter(
        VoiceSample.user_id == patient_id,
        VoiceSample.processing_status == "completed"
    ).order_by(VoiceSample.recorded_at.desc()).first()
    
    if latest_sample:
        result = voice_service.analyze_audio(latest_sample.file_path)
    else:
        result = voice_service.generate_demo_results("normal")
    
    prediction = Prediction(
        user_id=patient_id,
        voice_sample_id=latest_sample.id if latest_sample else None,
        model_version="v1.0",
        model_type="psychologist_analysis",
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
        voice_features=result.get("features", {}),
        analyzed_by_psychologist_id=current_user.id
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return {
        "prediction_id": prediction.id,
        "patient_id": patient_id,
        "risk_level": prediction.overall_risk_level,
        "mental_health_score": prediction.mental_health_score,
        "phq9_score": prediction.phq9_score,
        "gad7_score": prediction.gad7_score,
        "pss_score": prediction.pss_score,
        "wemwbs_score": prediction.wemwbs_score,
        "confidence": prediction.confidence,
        "interpretations": prediction.interpretations,
        "recommendations": prediction.recommendations,
        "analyzed_at": prediction.predicted_at.isoformat()
    }

@router.get("/dashboard")
async def get_psychologist_dashboard(
    current_user: User = Depends(require_role(["psychologist"])),
    db: Session = Depends(get_db)
):
    """Get psychologist dashboard summary"""
    # Get assigned patients count
    total_patients = db.query(User).filter(
        User.assigned_psychologist_id == current_user.id,
        User.role == "patient"
    ).count()
    
    # Get patients by risk level
    patients = db.query(User).filter(
        User.assigned_psychologist_id == current_user.id,
        User.role == "patient"
    ).all()
    
    risk_counts = {"low": 0, "moderate": 0, "high": 0, "unknown": 0}
    for patient in patients:
        latest_pred = db.query(Prediction).filter(
            Prediction.user_id == patient.id
        ).order_by(Prediction.predicted_at.desc()).first()
        
        if latest_pred:
            level = latest_pred.overall_risk_level or "unknown"
            if level in risk_counts:
                risk_counts[level] += 1
            else:
                risk_counts["unknown"] += 1
        else:
            risk_counts["unknown"] += 1
    
    # Get total sessions
    total_sessions = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.psychologist_id == current_user.id
    ).count()
    
    # Get upcoming follow-ups
    upcoming_followups = db.query(ClinicalAssessment).filter(
        ClinicalAssessment.psychologist_id == current_user.id,
        ClinicalAssessment.follow_up_date >= datetime.utcnow()
    ).order_by(ClinicalAssessment.follow_up_date.asc()).limit(5).all()
    
    return {
        "total_patients": total_patients,
        "risk_distribution": risk_counts,
        "total_sessions": total_sessions,
        "upcoming_followups": [
            {
                "assessment_id": f.id,
                "patient_id": f.user_id,
                "follow_up_date": f.follow_up_date.isoformat() if f.follow_up_date else None
            }
            for f in upcoming_followups
        ]
    }
