"""
Voice analysis router for Vocalysis API - MongoDB Version
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from datetime import datetime
import os
import uuid
import numpy as np
import sys
from typing import Dict, Any

from app.models.mongodb import get_mongodb
from app.schemas.voice import VoiceUploadResponse, VoiceStatusResponse, VoiceSampleResponse, VoiceAnalysisRequest
from app.schemas.prediction import PredictionResponse, AnalysisResultResponse
from app.routers.auth import get_current_user_from_token
from app.services.voice_analysis import VoiceAnalysisService
from app.services.email_service import email_service
from app.utils.config import settings
from bson import ObjectId

router = APIRouter()

# Initialize voice analysis service
voice_service = VoiceAnalysisService()

def get_user_id(user: Dict[str, Any]) -> str:
    """Get user ID as string from MongoDB document"""
    user_id = user.get("_id", "")
    return str(user_id) if user_id else ""

@router.post("/upload", response_model=VoiceUploadResponse)
async def upload_voice_sample(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Upload voice recording for analysis"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
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
    upload_dir = os.path.join(settings.UPLOAD_DIR, user_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    sample_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{sample_id}{file_ext}")
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create voice sample record in MongoDB
    voice_sample_doc = {
        "_id": sample_id,
        "user_id": user_id,
        "file_path": file_path,
        "file_name": file.filename,
        "audio_format": file_ext[1:],
        "file_size": len(content),
        "processing_status": "uploaded",
        "recorded_via": "web_app",
        "recorded_at": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    db.voice_samples.insert_one(voice_sample_doc)
    
    return VoiceUploadResponse(
        sample_id=sample_id,
        user_id=user_id,
        status="uploaded",
        message="Voice sample uploaded successfully. Processing will begin shortly.",
        estimated_processing_time=45
    )

@router.post("/analyze/{sample_id}")
async def analyze_voice_sample(
    sample_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Analyze uploaded voice sample"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    # Get voice sample
    voice_sample = db.voice_samples.find_one({
        "_id": sample_id,
        "user_id": user_id
    })
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    # Update status
    db.voice_samples.update_one(
        {"_id": sample_id},
        {"$set": {"processing_status": "processing"}}
    )
    
    try:
        # Run analysis
        result = voice_service.analyze_audio(voice_sample["file_path"])
        
        if "error" in result:
            db.voice_samples.update_one(
                {"_id": sample_id},
                {"$set": {"processing_status": "failed", "validation_message": result["error"]}}
            )
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update voice sample
        db.voice_samples.update_one(
            {"_id": sample_id},
            {"$set": {
                "processing_status": "completed",
                "duration_seconds": result.get("features", {}).get("duration", 0),
                "quality_score": result.get("confidence", 0),
                "features": result.get("features", {}),
                "processed_at": datetime.utcnow()
            }}
        )
        
        # Update user's sample collection progress
        samples_collected = (current_user.get("voice_samples_collected") or 0) + 1
        target_samples = current_user.get("target_samples") or 9
        update_fields = {"voice_samples_collected": samples_collected}
        
        if samples_collected >= target_samples:
            update_fields["baseline_established"] = True
        
        db.users.update_one({"_id": current_user["_id"]}, {"$set": update_fields})
        
        # Create prediction record in MongoDB
        prediction_id = str(uuid.uuid4())
        prediction_doc = {
            "_id": prediction_id,
            "user_id": user_id,
            "voice_sample_id": sample_id,
            "model_version": "v1.0",
            "model_type": "ensemble",
            "normal_score": float(result["probabilities"][0]),
            "anxiety_score": float(result["probabilities"][1]),
            "depression_score": float(result["probabilities"][2]),
            "stress_score": float(result["probabilities"][3]),
            "overall_risk_level": result.get("risk_level", "low"),
            "mental_health_score": result.get("mental_health_score", 0),
            "confidence": result.get("confidence", 0),
            "phq9_score": result.get("scale_mappings", {}).get("PHQ-9", 0),
            "gad7_score": result.get("scale_mappings", {}).get("GAD-7", 0),
            "pss_score": result.get("scale_mappings", {}).get("PSS", 0),
            "wemwbs_score": result.get("scale_mappings", {}).get("WEMWBS", 0),
            "interpretations": result.get("interpretations", []),
            "recommendations": result.get("recommendations", []),
            "voice_features": result.get("features", {}),
            "predicted_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        db.predictions.insert_one(prediction_doc)
        
        # Send email notification with analysis results
        try:
            user_email = current_user.get("email")
            user_name = current_user.get("full_name", "there")
            
            # Send analysis results email
            email_service.send_analysis_results_email(
                to_email=user_email,
                full_name=user_name,
                risk_level=prediction_doc["overall_risk_level"],
                phq9=prediction_doc["phq9_score"],
                gad7=prediction_doc["gad7_score"],
                pss=prediction_doc["pss_score"],
                wemwbs=prediction_doc["wemwbs_score"]
            )
            
            # Check if baseline just completed (9 samples)
            if samples_collected == target_samples:
                # Send baseline completion email
                email_service.send_reminder_email(
                    to_email=user_email,
                    full_name=user_name,
                    reminder_type="baseline_complete"
                )
        except Exception as email_error:
            # Log email error but don't fail the analysis
            print(f"Failed to send analysis email: {email_error}")
        
        return {
            "id": prediction_id,
            "user_id": user_id,
            "voice_sample_id": sample_id,
            "normal_score": prediction_doc["normal_score"],
            "anxiety_score": prediction_doc["anxiety_score"],
            "depression_score": prediction_doc["depression_score"],
            "stress_score": prediction_doc["stress_score"],
            "overall_risk_level": prediction_doc["overall_risk_level"],
            "mental_health_score": prediction_doc["mental_health_score"],
            "confidence": prediction_doc["confidence"],
            "interpretations": prediction_doc["interpretations"],
            "recommendations": prediction_doc["recommendations"],
            "predicted_at": prediction_doc["predicted_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.voice_samples.update_one(
            {"_id": sample_id},
            {"$set": {"processing_status": "failed", "validation_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/sample-progress")
async def get_sample_collection_progress(
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Get user's voice sample collection progress for personalization"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    samples_collected = current_user.get("voice_samples_collected") or 0
    target_samples = current_user.get("target_samples") or 9
    baseline_established = current_user.get("baseline_established") or False
    
    # Get today's samples
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_samples = db.voice_samples.count_documents({
        "user_id": user_id,
        "recorded_at": {"$gte": today_start}
    })
    
    return {
        "samples_collected": samples_collected,
        "target_samples": target_samples,
        "progress_percentage": min(100, (samples_collected / target_samples) * 100) if target_samples > 0 else 0,
        "baseline_established": baseline_established,
        "personalization_score": current_user.get("personalization_score"),
        "today_samples": today_samples,
        "daily_target": 1,
        "streak_days": 0,
        "samples_remaining": max(0, target_samples - samples_collected),
        "message": _get_progress_message(samples_collected, target_samples, baseline_established)
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

@router.post("/demo-analyze")
async def demo_analyze(
    request: VoiceAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Generate demo analysis results"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    demo_type = request.demo_type or "normal"
    
    # Generate demo results
    result = voice_service.generate_demo_results(demo_type)
    
    # Create prediction record in MongoDB
    prediction_id = str(uuid.uuid4())
    prediction_doc = {
        "_id": prediction_id,
        "user_id": user_id,
        "model_version": "v1.0-demo",
        "model_type": "demo",
        "normal_score": float(result["probabilities"][0]),
        "anxiety_score": float(result["probabilities"][1]),
        "depression_score": float(result["probabilities"][2]),
        "stress_score": float(result["probabilities"][3]),
        "overall_risk_level": result.get("risk_level", "low"),
        "mental_health_score": result.get("mental_health_score", 0),
        "confidence": result.get("confidence", 0),
        "phq9_score": result.get("scale_mappings", {}).get("PHQ-9", 0),
        "gad7_score": result.get("scale_mappings", {}).get("GAD-7", 0),
        "pss_score": result.get("scale_mappings", {}).get("PSS", 0),
        "wemwbs_score": result.get("scale_mappings", {}).get("WEMWBS", 0),
        "interpretations": result.get("interpretations", []),
        "recommendations": result.get("recommendations", []),
        "voice_features": result.get("features", {}),
        "predicted_at": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    db.predictions.insert_one(prediction_doc)
    
    return {
        "id": prediction_id,
        "user_id": user_id,
        "normal_score": prediction_doc["normal_score"],
        "anxiety_score": prediction_doc["anxiety_score"],
        "depression_score": prediction_doc["depression_score"],
        "stress_score": prediction_doc["stress_score"],
        "overall_risk_level": prediction_doc["overall_risk_level"],
        "mental_health_score": prediction_doc["mental_health_score"],
        "confidence": prediction_doc["confidence"],
        "interpretations": prediction_doc["interpretations"],
        "recommendations": prediction_doc["recommendations"],
        "predicted_at": prediction_doc["predicted_at"]
    }

@router.get("/status/{sample_id}")
async def get_voice_status(
    sample_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Get processing status of voice sample"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    voice_sample = db.voice_samples.find_one({
        "_id": sample_id,
        "user_id": user_id
    })
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    return {
        "sample_id": voice_sample["_id"],
        "status": voice_sample.get("processing_status", "unknown"),
        "uploaded_at": voice_sample.get("recorded_at"),
        "processed_at": voice_sample.get("processed_at"),
        "message": voice_sample.get("validation_message") or f"Status: {voice_sample.get('processing_status', 'unknown')}",
        "quality_score": voice_sample.get("quality_score")
    }

@router.get("/samples")
async def get_user_samples(
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Get user's voice samples"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    samples = list(db.voice_samples.find(
        {"user_id": user_id}
    ).sort("recorded_at", -1).limit(limit))
    
    return [{
        "id": s["_id"],
        "user_id": s.get("user_id"),
        "file_name": s.get("file_name"),
        "audio_format": s.get("audio_format"),
        "file_size": s.get("file_size"),
        "duration_seconds": s.get("duration_seconds"),
        "processing_status": s.get("processing_status"),
        "quality_score": s.get("quality_score"),
        "recorded_at": s.get("recorded_at"),
        "processed_at": s.get("processed_at")
    } for s in samples]

@router.delete("/samples/{sample_id}")
async def delete_voice_sample(
    sample_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Delete a voice sample"""
    db = get_mongodb()
    user_id = get_user_id(current_user)
    
    voice_sample = db.voice_samples.find_one({
        "_id": sample_id,
        "user_id": user_id
    })
    
    if not voice_sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    # Delete file if exists
    file_path = voice_sample.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete associated prediction
    db.predictions.delete_many({"voice_sample_id": sample_id})
    
    # Delete voice sample
    db.voice_samples.delete_one({"_id": sample_id})
    
    return {"message": "Voice sample deleted successfully"}


# ============== PSYCHOLOGIST CALIBRATION ENDPOINTS ==============

@router.post("/calibrate/{patient_id}")
async def calibrate_patient_model(
    patient_id: str,
    clinical_assessment: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Psychologist calibration endpoint - allows psychologists to validate and adjust
    model predictions based on their clinical assessment.
    
    This creates a calibration factor that adjusts future predictions for this patient.
    
    Required clinical_assessment fields:
    - phq9_score: PHQ-9 depression score (0-27)
    - gad7_score: GAD-7 anxiety score (0-21)
    - pss_score: PSS stress score (0-40)
    - prediction_id: The prediction ID being calibrated (optional)
    - notes: Clinical notes (optional)
    """
    db = get_mongodb()
    psychologist_id = get_user_id(current_user)
    
    # Verify user is a psychologist or admin
    user_role = current_user.get("role", "")
    if user_role not in ["psychologist", "admin", "super_admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Only psychologists can calibrate patient models"
        )
    
    # Validate clinical scores
    phq9 = clinical_assessment.get("phq9_score", 0)
    gad7 = clinical_assessment.get("gad7_score", 0)
    pss = clinical_assessment.get("pss_score", 0)
    
    if not (0 <= phq9 <= 27):
        raise HTTPException(status_code=400, detail="PHQ-9 score must be between 0-27")
    if not (0 <= gad7 <= 21):
        raise HTTPException(status_code=400, detail="GAD-7 score must be between 0-21")
    if not (0 <= pss <= 40):
        raise HTTPException(status_code=400, detail="PSS score must be between 0-40")
    
    # Get the most recent prediction for this patient
    prediction_id = clinical_assessment.get("prediction_id")
    if prediction_id:
        prediction = db.predictions.find_one({"_id": prediction_id, "user_id": patient_id})
    else:
        prediction = db.predictions.find_one(
            {"user_id": patient_id},
            sort=[("predicted_at", -1)]
        )
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction found for this patient")
    
    # Get original model prediction
    model_prediction = [
        prediction.get("normal_score", 0.25),
        prediction.get("anxiety_score", 0.25),
        prediction.get("depression_score", 0.25),
        prediction.get("stress_score", 0.25)
    ]
    
    # Add psychologist ID to clinical assessment
    clinical_assessment["psychologist_id"] = psychologist_id
    
    # Set calibration in voice service
    calibration = voice_service.set_calibration(patient_id, clinical_assessment, model_prediction)
    
    # Store calibration in MongoDB for persistence
    calibration_doc = {
        "_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "psychologist_id": psychologist_id,
        "prediction_id": prediction.get("_id"),
        "original_prediction": {
            "normal": model_prediction[0],
            "anxiety": model_prediction[1],
            "depression": model_prediction[2],
            "stress": model_prediction[3]
        },
        "clinical_assessment": {
            "phq9_score": phq9,
            "gad7_score": gad7,
            "pss_score": pss,
            "notes": clinical_assessment.get("notes", "")
        },
        "calibration_factors": calibration,
        "calibrated_at": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    db.calibrations.insert_one(calibration_doc)
    
    # Update the prediction with calibration info
    db.predictions.update_one(
        {"_id": prediction.get("_id")},
        {"$set": {
            "calibrated": True,
            "calibration_id": calibration_doc["_id"],
            "clinical_phq9": phq9,
            "clinical_gad7": gad7,
            "clinical_pss": pss,
            "calibrated_by": psychologist_id,
            "calibrated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Calibration successful",
        "calibration_id": calibration_doc["_id"],
        "patient_id": patient_id,
        "original_prediction": calibration_doc["original_prediction"],
        "clinical_assessment": calibration_doc["clinical_assessment"],
        "calibration_factors": {
            "normal": calibration.get("factor_0", 1.0),
            "anxiety": calibration.get("factor_1", 1.0),
            "depression": calibration.get("factor_2", 1.0),
            "stress": calibration.get("factor_3", 1.0)
        }
    }


@router.get("/calibration/{patient_id}")
async def get_patient_calibration(
    patient_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Get calibration history for a patient.
    Only accessible by psychologists, admins, or the patient themselves.
    """
    db = get_mongodb()
    user_id = get_user_id(current_user)
    user_role = current_user.get("role", "")
    
    # Check access permissions
    if user_role not in ["psychologist", "admin", "super_admin"] and user_id != patient_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this patient's calibration"
        )
    
    # Get calibration history
    calibrations = list(db.calibrations.find(
        {"patient_id": patient_id}
    ).sort("calibrated_at", -1).limit(10))
    
    # Get current in-memory calibration
    current_calibration = voice_service.get_calibration(patient_id)
    
    return {
        "patient_id": patient_id,
        "has_calibration": current_calibration is not None,
        "current_calibration": current_calibration,
        "calibration_history": [{
            "id": c["_id"],
            "psychologist_id": c.get("psychologist_id"),
            "clinical_assessment": c.get("clinical_assessment"),
            "calibrated_at": c.get("calibrated_at")
        } for c in calibrations]
    }


@router.delete("/calibration/{patient_id}")
async def reset_patient_calibration(
    patient_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    Reset calibration for a patient (use raw model predictions).
    Only accessible by psychologists or admins.
    """
    db = get_mongodb()
    user_role = current_user.get("role", "")
    
    if user_role not in ["psychologist", "admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only psychologists can reset patient calibration"
        )
    
    # Remove from in-memory cache
    if hasattr(voice_service, 'calibration_factors') and patient_id in voice_service.calibration_factors:
        del voice_service.calibration_factors[patient_id]
    
    # Mark calibrations as inactive in database
    db.calibrations.update_many(
        {"patient_id": patient_id},
        {"$set": {"active": False, "deactivated_at": datetime.utcnow()}}
    )
    
    return {
        "message": "Calibration reset successful",
        "patient_id": patient_id
    }
