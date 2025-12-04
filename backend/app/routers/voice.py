"""
Voice analysis router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
import numpy as np
import sys

from app.models.database import get_db, sync_prediction_to_mongodb
from app.models.user import User
from app.models.voice_sample import VoiceSample
from app.models.prediction import Prediction
from app.schemas.voice import VoiceUploadResponse, VoiceStatusResponse, VoiceSampleResponse, VoiceAnalysisRequest
from app.schemas.prediction import PredictionResponse, AnalysisResultResponse
from app.routers.auth import get_current_user
from app.services.voice_analysis import VoiceAnalysisService
from app.services.pdf_service import pdf_service
from app.utils.config import settings

router = APIRouter()

# Initialize voice analysis service
voice_service = VoiceAnalysisService()

@router.post("/upload", response_model=VoiceUploadResponse)
async def upload_voice_sample(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload voice recording for analysis"""
    # Validate file format
    allowed_formats = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(allowed_formats)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB"
        )
    
    # Create upload directory if not exists
    upload_dir = os.path.join(settings.UPLOAD_DIR, current_user.id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    sample_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{sample_id}{file_ext}")
    
    # Save file
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
        recorded_via="web_app"
    )
    
    db.add(voice_sample)
    db.commit()
    
    return VoiceUploadResponse(
        sample_id=sample_id,
        user_id=current_user.id,
        status="uploaded",
        message="Voice sample uploaded successfully. Processing will begin shortly.",
        estimated_processing_time=45
    )

@router.post("/analyze/{sample_id}", response_model=PredictionResponse)
async def analyze_voice_sample(
    sample_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze uploaded voice sample"""
    # Get voice sample
    voice_sample = db.query(VoiceSample).filter(
        VoiceSample.id == sample_id,
        VoiceSample.user_id == current_user.id
    ).first()
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    # Update status
    voice_sample.processing_status = "processing"
    db.commit()
    
    try:
        # Run analysis
        result = voice_service.analyze_audio(voice_sample.file_path)
        
        if "error" in result:
            voice_sample.processing_status = "failed"
            voice_sample.validation_message = result["error"]
            db.commit()
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update voice sample
        voice_sample.processing_status = "completed"
        voice_sample.duration_seconds = result.get("features", {}).get("duration", 0)
        voice_sample.quality_score = result.get("confidence", 0)
        voice_sample.features = result.get("features", {})
        voice_sample.processed_at = datetime.utcnow()
        
        # Update user's sample collection progress
        current_user.voice_samples_collected = (current_user.voice_samples_collected or 0) + 1
        
        # Check if baseline is established (9+ samples)
        if current_user.voice_samples_collected >= current_user.target_samples:
            current_user.baseline_established = True
            # Calculate personalization score based on sample quality
            all_samples = db.query(VoiceSample).filter(
                VoiceSample.user_id == current_user.id,
                VoiceSample.processing_status == "completed"
            ).all()
            if all_samples:
                avg_quality = sum(s.quality_score or 0 for s in all_samples) / len(all_samples)
                current_user.personalization_score = min(1.0, avg_quality)
        
        # Create prediction record
        prediction = Prediction(
            user_id=current_user.id,
            voice_sample_id=sample_id,
            model_version="v1.0",
            model_type="ensemble",
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
        db.commit()
        db.refresh(prediction)
        
        # Sync prediction to MongoDB for permanent storage
        sync_prediction_to_mongodb({
            "id": prediction.id,
            "user_id": prediction.user_id,
            "voice_sample_id": prediction.voice_sample_id,
            "model_version": prediction.model_version,
            "model_type": prediction.model_type,
            "normal_score": prediction.normal_score,
            "anxiety_score": prediction.anxiety_score,
            "depression_score": prediction.depression_score,
            "stress_score": prediction.stress_score,
            "overall_risk_level": prediction.overall_risk_level,
            "mental_health_score": prediction.mental_health_score,
            "confidence": prediction.confidence,
            "phq9_score": prediction.phq9_score,
            "phq9_severity": prediction.phq9_severity,
            "gad7_score": prediction.gad7_score,
            "gad7_severity": prediction.gad7_severity,
            "pss_score": prediction.pss_score,
            "pss_severity": prediction.pss_severity,
            "wemwbs_score": prediction.wemwbs_score,
            "wemwbs_severity": prediction.wemwbs_severity,
            "interpretations": prediction.interpretations,
            "recommendations": prediction.recommendations,
            "voice_features": prediction.voice_features,
            "predicted_at": prediction.predicted_at,
            "created_at": prediction.created_at
        })
        
        return PredictionResponse.model_validate(prediction)
        
    except Exception as e:
        voice_sample.processing_status = "failed"
        voice_sample.validation_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/sample-progress")
async def get_sample_collection_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's voice sample collection progress for personalization"""
    samples_collected = current_user.voice_samples_collected or 0
    target_samples = current_user.target_samples or 9
    
    # Get today's samples
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_samples = db.query(VoiceSample).filter(
        VoiceSample.user_id == current_user.id,
        VoiceSample.recorded_at >= today_start
    ).count()
    
    # Calculate streak (consecutive days with recordings)
    from sqlalchemy import func
    daily_recordings = db.query(
        func.date(VoiceSample.recorded_at).label('date')
    ).filter(
        VoiceSample.user_id == current_user.id
    ).group_by(func.date(VoiceSample.recorded_at)).order_by(
        func.date(VoiceSample.recorded_at).desc()
    ).limit(30).all()
    
    streak = 0
    if daily_recordings:
        from datetime import timedelta
        current_date = date.today()
        for record in daily_recordings:
            if record.date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif record.date == current_date - timedelta(days=1):
                streak += 1
                current_date = record.date - timedelta(days=1)
            else:
                break
    
    return {
        "samples_collected": samples_collected,
        "target_samples": target_samples,
        "progress_percentage": min(100, (samples_collected / target_samples) * 100),
        "baseline_established": current_user.baseline_established or False,
        "personalization_score": current_user.personalization_score,
        "today_samples": today_samples,
        "daily_target": 1,  # Recommended 1 sample per day
        "streak_days": streak,
        "samples_remaining": max(0, target_samples - samples_collected),
        "message": _get_progress_message(samples_collected, target_samples, current_user.baseline_established)
    }

def _get_progress_message(collected: int, target: int, baseline: bool) -> str:
    """Generate encouraging progress message"""
    if baseline:
        return "Baseline established! Your personalized analysis is now active."
    elif collected == 0:
        return f"Start your journey! Record {target} voice samples to unlock personalized analysis."
    elif collected < target // 3:
        return f"Great start! {target - collected} more samples to establish your baseline."
    elif collected < target * 2 // 3:
        return f"You're making progress! {target - collected} samples to go."
    else:
        return f"Almost there! Just {target - collected} more samples for personalized insights."

@router.post("/demo-analyze", response_model=PredictionResponse)
async def demo_analyze(
    request: VoiceAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate demo analysis results"""
    demo_type = request.demo_type or "normal"
    
    # Generate demo results
    result = voice_service.generate_demo_results(demo_type)
    
    # Create prediction record
    prediction = Prediction(
        user_id=current_user.id,
        model_version="v1.0-demo",
        model_type="demo",
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
    db.commit()
    db.refresh(prediction)
    
    # Sync prediction to MongoDB for permanent storage
    sync_prediction_to_mongodb({
        "id": prediction.id,
        "user_id": prediction.user_id,
        "voice_sample_id": prediction.voice_sample_id,
        "model_version": prediction.model_version,
        "model_type": prediction.model_type,
        "normal_score": prediction.normal_score,
        "anxiety_score": prediction.anxiety_score,
        "depression_score": prediction.depression_score,
        "stress_score": prediction.stress_score,
        "overall_risk_level": prediction.overall_risk_level,
        "mental_health_score": prediction.mental_health_score,
        "confidence": prediction.confidence,
        "phq9_score": prediction.phq9_score,
        "phq9_severity": prediction.phq9_severity,
        "gad7_score": prediction.gad7_score,
        "gad7_severity": prediction.gad7_severity,
        "pss_score": prediction.pss_score,
        "pss_severity": prediction.pss_severity,
        "wemwbs_score": prediction.wemwbs_score,
        "wemwbs_severity": prediction.wemwbs_severity,
        "interpretations": prediction.interpretations,
        "recommendations": prediction.recommendations,
        "voice_features": prediction.voice_features,
        "predicted_at": prediction.predicted_at,
        "created_at": prediction.created_at
    })
    
    return PredictionResponse.model_validate(prediction)

@router.get("/status/{sample_id}", response_model=VoiceStatusResponse)
async def get_voice_status(
    sample_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get processing status of voice sample"""
    voice_sample = db.query(VoiceSample).filter(
        VoiceSample.id == sample_id,
        VoiceSample.user_id == current_user.id
    ).first()
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    return VoiceStatusResponse(
        sample_id=voice_sample.id,
        status=voice_sample.processing_status,
        uploaded_at=voice_sample.recorded_at,
        processed_at=voice_sample.processed_at,
        message=voice_sample.validation_message or f"Status: {voice_sample.processing_status}",
        quality_score=voice_sample.quality_score
    )

@router.get("/samples", response_model=list[VoiceSampleResponse])
async def get_user_samples(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's voice samples"""
    samples = db.query(VoiceSample).filter(
        VoiceSample.user_id == current_user.id
    ).order_by(VoiceSample.recorded_at.desc()).limit(limit).all()
    
    return [VoiceSampleResponse.model_validate(s) for s in samples]

@router.delete("/samples/{sample_id}")
async def delete_voice_sample(
    sample_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a voice sample"""
    voice_sample = db.query(VoiceSample).filter(
        VoiceSample.id == sample_id,
        VoiceSample.user_id == current_user.id
    ).first()
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    # Delete file if exists
    if voice_sample.file_path and os.path.exists(voice_sample.file_path):
        os.remove(voice_sample.file_path)
    
    # Delete associated prediction
    db.query(Prediction).filter(Prediction.voice_sample_id == sample_id).delete()
    
    # Delete voice sample
    db.delete(voice_sample)
    db.commit()
    
    return {"message": "Voice sample deleted successfully"}


@router.get("/report/{prediction_id}/pdf")
async def download_report_pdf(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download analysis report as PDF"""
    # Get prediction
    prediction = db.query(Prediction).filter(
        Prediction.id == prediction_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Check access - user can only download their own reports
    # (or admin/psychologist can download their patients' reports)
    if prediction.user_id != current_user.id and current_user.role not in ['admin', 'super_admin', 'hr_admin', 'psychologist']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get user name for the report
    patient = db.query(User).filter(User.id == prediction.user_id).first()
    user_name = patient.full_name if patient and patient.full_name else "Patient"
    
    # Convert prediction to dict for PDF generation
    prediction_data = {
        "id": prediction.id,
        "predicted_at": prediction.predicted_at.isoformat() if prediction.predicted_at else None,
        "mental_health_score": prediction.mental_health_score,
        "overall_risk_level": prediction.overall_risk_level,
        "confidence": prediction.confidence,
        "normal_score": prediction.normal_score,
        "anxiety_score": prediction.anxiety_score,
        "depression_score": prediction.depression_score,
        "stress_score": prediction.stress_score,
        "phq9_score": prediction.phq9_score,
        "phq9_severity": prediction.phq9_severity,
        "gad7_score": prediction.gad7_score,
        "gad7_severity": prediction.gad7_severity,
        "pss_score": prediction.pss_score,
        "pss_severity": prediction.pss_severity,
        "wemwbs_score": prediction.wemwbs_score,
        "wemwbs_severity": prediction.wemwbs_severity,
        "interpretations": prediction.interpretations or [],
        "recommendations": prediction.recommendations or [],
    }
    
    # Generate PDF
    try:
        pdf_bytes = pdf_service.generate_analysis_report(prediction_data, user_name)
        
        # Return PDF as downloadable file
        filename = f"vocalysis_report_{prediction_id[:8]}_{prediction.predicted_at.strftime('%Y%m%d') if prediction.predicted_at else 'report'}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
