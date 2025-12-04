"""
Personalization Service for Vocalysis
Implements personalized baseline learning and outcome prediction
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample


class PersonalizationService:
    """
    Service for personalized mental health analysis
    - Learns individual baselines from 9+ voice samples
    - Detects deviations from personal baseline
    - Predicts outcome/deterioration trends
    """
    
    # Minimum samples required for baseline establishment
    MIN_BASELINE_SAMPLES = 9
    TARGET_BASELINE_SAMPLES = 12
    
    # Feature weights for baseline comparison
    FEATURE_WEIGHTS = {
        "pitch_mean": 0.15,
        "pitch_std": 0.10,
        "speech_rate": 0.15,
        "rms_mean": 0.10,
        "jitter_mean": 0.10,
        "hnr": 0.10,
        "mfcc_mean": 0.10,
        "spectral_centroid_mean": 0.10,
        "zcr_mean": 0.10
    }
    
    # Risk thresholds for deterioration prediction
    DETERIORATION_THRESHOLDS = {
        "mild": 0.15,      # 15% increase in risk scores
        "moderate": 0.25,  # 25% increase
        "significant": 0.40  # 40% increase
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_baseline(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get or compute the user's personalized baseline from their voice samples
        
        Args:
            user_id: User ID to get baseline for
            
        Returns:
            Dictionary containing baseline features and metadata, or None if insufficient samples
        """
        # Get all predictions for this user with voice features
        predictions = self.db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.voice_features.isnot(None)
        ).order_by(Prediction.created_at).all()
        
        if len(predictions) < self.MIN_BASELINE_SAMPLES:
            return None
        
        # Use first N samples for baseline (established baseline)
        baseline_predictions = predictions[:self.TARGET_BASELINE_SAMPLES]
        
        # Extract features from baseline samples
        baseline_features = self._compute_baseline_features(baseline_predictions)
        
        # Compute baseline clinical scores
        baseline_scores = self._compute_baseline_scores(baseline_predictions)
        
        return {
            "user_id": user_id,
            "sample_count": len(baseline_predictions),
            "baseline_established": True,
            "established_at": baseline_predictions[-1].created_at.isoformat() if baseline_predictions else None,
            "features": baseline_features,
            "scores": baseline_scores,
            "total_samples": len(predictions)
        }
    
    def _compute_baseline_features(self, predictions: List[Prediction]) -> Dict[str, Dict[str, float]]:
        """Compute mean and std for each feature across baseline samples"""
        feature_values = {}
        
        for pred in predictions:
            if pred.voice_features:
                features = pred.voice_features if isinstance(pred.voice_features, dict) else {}
                for key, value in features.items():
                    if isinstance(value, (int, float)) and key in self.FEATURE_WEIGHTS:
                        if key not in feature_values:
                            feature_values[key] = []
                        feature_values[key].append(float(value))
        
        baseline = {}
        for key, values in feature_values.items():
            if len(values) >= 3:  # Need at least 3 samples for meaningful stats
                baseline[key] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        
        return baseline
    
    def _compute_baseline_scores(self, predictions: List[Prediction]) -> Dict[str, Dict[str, float]]:
        """Compute baseline clinical scores"""
        scores = {
            "phq9": [],
            "gad7": [],
            "pss": [],
            "wemwbs": [],
            "mental_health_score": [],
            "normal_score": [],
            "anxiety_score": [],
            "depression_score": [],
            "stress_score": []
        }
        
        for pred in predictions:
            if pred.phq9_score is not None:
                scores["phq9"].append(pred.phq9_score)
            if pred.gad7_score is not None:
                scores["gad7"].append(pred.gad7_score)
            if pred.pss_score is not None:
                scores["pss"].append(pred.pss_score)
            if pred.wemwbs_score is not None:
                scores["wemwbs"].append(pred.wemwbs_score)
            if pred.mental_health_score is not None:
                scores["mental_health_score"].append(pred.mental_health_score)
            if pred.normal_score is not None:
                scores["normal_score"].append(pred.normal_score)
            if pred.anxiety_score is not None:
                scores["anxiety_score"].append(pred.anxiety_score)
            if pred.depression_score is not None:
                scores["depression_score"].append(pred.depression_score)
            if pred.stress_score is not None:
                scores["stress_score"].append(pred.stress_score)
        
        baseline_scores = {}
        for key, values in scores.items():
            if len(values) >= 3:
                baseline_scores[key] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        
        return baseline_scores
    
    def analyze_with_personalization(
        self, 
        user_id: str, 
        current_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance analysis with personalized baseline comparison
        
        Args:
            user_id: User ID
            current_analysis: Current analysis results from voice analysis service
            
        Returns:
            Enhanced analysis with personalization data
        """
        baseline = self.get_user_baseline(user_id)
        
        # Get sample progress
        sample_count = self._get_sample_count(user_id)
        
        personalization = {
            "baseline_established": baseline is not None,
            "samples_collected": sample_count,
            "samples_required": self.MIN_BASELINE_SAMPLES,
            "samples_target": self.TARGET_BASELINE_SAMPLES,
            "progress_percentage": min(100, int((sample_count / self.MIN_BASELINE_SAMPLES) * 100))
        }
        
        if baseline:
            # Compare current analysis to baseline
            deviation = self._compute_deviation(current_analysis, baseline)
            personalization["deviation_from_baseline"] = deviation
            personalization["personalization_applied"] = True
            
            # Adjust risk level based on personal baseline
            adjusted_risk = self._adjust_risk_for_baseline(
                current_analysis.get("risk_level", "low"),
                deviation
            )
            personalization["adjusted_risk_level"] = adjusted_risk
            
            # Add baseline comparison insights
            personalization["baseline_comparison"] = self._generate_baseline_insights(
                current_analysis, baseline, deviation
            )
        else:
            personalization["personalization_applied"] = False
            personalization["message"] = f"Collect {self.MIN_BASELINE_SAMPLES - sample_count} more samples to establish your personal baseline"
        
        # Add personalization to analysis
        enhanced_analysis = current_analysis.copy()
        enhanced_analysis["personalization"] = personalization
        
        return enhanced_analysis
    
    def _get_sample_count(self, user_id: str) -> int:
        """Get total sample count for user"""
        return self.db.query(Prediction).filter(
            Prediction.user_id == user_id
        ).count()
    
    def _compute_deviation(
        self, 
        current: Dict[str, Any], 
        baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute deviation of current analysis from baseline"""
        deviation = {
            "feature_deviations": {},
            "score_deviations": {},
            "overall_deviation": 0.0
        }
        
        # Feature deviations
        current_features = current.get("features", {})
        baseline_features = baseline.get("features", {})
        
        total_weighted_deviation = 0.0
        total_weight = 0.0
        
        for feature, weight in self.FEATURE_WEIGHTS.items():
            if feature in current_features and feature in baseline_features:
                current_val = current_features[feature]
                baseline_mean = baseline_features[feature]["mean"]
                baseline_std = baseline_features[feature]["std"]
                
                if baseline_std > 0:
                    # Z-score deviation
                    z_score = (current_val - baseline_mean) / baseline_std
                    deviation["feature_deviations"][feature] = {
                        "current": current_val,
                        "baseline_mean": baseline_mean,
                        "z_score": round(z_score, 2),
                        "interpretation": self._interpret_z_score(z_score)
                    }
                    total_weighted_deviation += abs(z_score) * weight
                    total_weight += weight
        
        # Score deviations
        baseline_scores = baseline.get("scores", {})
        score_mappings = {
            "phq9_score": "phq9",
            "gad7_score": "gad7",
            "pss_score": "pss",
            "wemwbs_score": "wemwbs",
            "mental_health_score": "mental_health_score"
        }
        
        scale_mappings = current.get("scale_mappings", {})
        
        for current_key, baseline_key in score_mappings.items():
            current_val = None
            if current_key == "phq9_score":
                current_val = scale_mappings.get("PHQ-9")
            elif current_key == "gad7_score":
                current_val = scale_mappings.get("GAD-7")
            elif current_key == "pss_score":
                current_val = scale_mappings.get("PSS")
            elif current_key == "wemwbs_score":
                current_val = scale_mappings.get("WEMWBS")
            elif current_key == "mental_health_score":
                current_val = current.get("mental_health_score")
            
            if current_val is not None and baseline_key in baseline_scores:
                baseline_mean = baseline_scores[baseline_key]["mean"]
                baseline_std = baseline_scores[baseline_key]["std"]
                
                if baseline_std > 0:
                    z_score = (current_val - baseline_mean) / baseline_std
                    deviation["score_deviations"][baseline_key] = {
                        "current": current_val,
                        "baseline_mean": round(baseline_mean, 1),
                        "z_score": round(z_score, 2),
                        "change_direction": "increased" if z_score > 0 else "decreased",
                        "interpretation": self._interpret_score_deviation(baseline_key, z_score)
                    }
        
        # Overall deviation score
        if total_weight > 0:
            deviation["overall_deviation"] = round(total_weighted_deviation / total_weight, 2)
        
        return deviation
    
    def _interpret_z_score(self, z_score: float) -> str:
        """Interpret z-score deviation"""
        abs_z = abs(z_score)
        if abs_z < 1:
            return "within normal range"
        elif abs_z < 2:
            return "slightly outside normal range"
        elif abs_z < 3:
            return "moderately outside normal range"
        else:
            return "significantly outside normal range"
    
    def _interpret_score_deviation(self, score_type: str, z_score: float) -> str:
        """Interpret clinical score deviation"""
        direction = "higher" if z_score > 0 else "lower"
        abs_z = abs(z_score)
        
        # For WEMWBS and mental_health_score, higher is better
        positive_scores = ["wemwbs", "mental_health_score", "normal_score"]
        
        if score_type in positive_scores:
            if z_score > 1:
                return "Better than your baseline - positive trend"
            elif z_score < -1:
                return "Below your baseline - may need attention"
            else:
                return "Consistent with your baseline"
        else:
            # For PHQ-9, GAD-7, PSS, anxiety, depression, stress - lower is better
            if z_score > 1:
                return "Higher than your baseline - may need attention"
            elif z_score < -1:
                return "Lower than your baseline - positive trend"
            else:
                return "Consistent with your baseline"
    
    def _adjust_risk_for_baseline(self, current_risk: str, deviation: Dict) -> str:
        """Adjust risk level based on personal baseline deviation"""
        overall_deviation = deviation.get("overall_deviation", 0)
        
        risk_levels = ["low", "moderate", "high"]
        current_idx = risk_levels.index(current_risk) if current_risk in risk_levels else 0
        
        # If significant deviation from baseline, consider elevating risk
        if overall_deviation > 2.5:
            # Significant deviation - elevate risk by one level
            adjusted_idx = min(current_idx + 1, 2)
        elif overall_deviation > 1.5:
            # Moderate deviation - keep or slightly elevate
            adjusted_idx = current_idx
        else:
            # Within normal deviation - trust the current assessment
            adjusted_idx = current_idx
        
        return risk_levels[adjusted_idx]
    
    def _generate_baseline_insights(
        self, 
        current: Dict, 
        baseline: Dict, 
        deviation: Dict
    ) -> List[str]:
        """Generate insights comparing current to baseline"""
        insights = []
        
        overall_dev = deviation.get("overall_deviation", 0)
        
        if overall_dev < 1:
            insights.append("Your voice patterns are consistent with your established baseline.")
        elif overall_dev < 2:
            insights.append("Some variation from your baseline detected, but within expected range.")
        else:
            insights.append("Significant variation from your baseline detected. Consider monitoring closely.")
        
        # Score-specific insights
        score_devs = deviation.get("score_deviations", {})
        
        for score, data in score_devs.items():
            z = data.get("z_score", 0)
            if abs(z) > 1.5:
                direction = "increased" if z > 0 else "decreased"
                if score in ["phq9", "gad7", "pss", "anxiety_score", "depression_score", "stress_score"]:
                    if z > 1.5:
                        insights.append(f"Your {score.upper()} score has {direction} compared to your baseline.")
                elif score in ["wemwbs", "mental_health_score"]:
                    if z < -1.5:
                        insights.append(f"Your wellbeing score has {direction} compared to your baseline.")
        
        return insights
    
    def predict_outcome(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Predict mental health outcome/deterioration risk based on trends
        
        Args:
            user_id: User ID
            days: Number of days to look back for trend analysis
            
        Returns:
            Outcome prediction with trend analysis
        """
        # Get recent predictions
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_predictions = self.db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= cutoff_date
        ).order_by(Prediction.created_at).all()
        
        if len(recent_predictions) < 2:
            return {
                "prediction_available": False,
                "message": "Need at least 2 recent samples for trend analysis",
                "samples_in_period": len(recent_predictions)
            }
        
        # Analyze trends
        trends = self._analyze_trends(recent_predictions)
        
        # Predict deterioration risk
        deterioration_risk = self._calculate_deterioration_risk(trends)
        
        # Generate outcome prediction
        outcome = {
            "prediction_available": True,
            "analysis_period_days": days,
            "samples_analyzed": len(recent_predictions),
            "trends": trends,
            "deterioration_risk": deterioration_risk,
            "predicted_trajectory": self._predict_trajectory(trends),
            "recommendations": self._generate_trend_recommendations(trends, deterioration_risk)
        }
        
        return outcome
    
    def _analyze_trends(self, predictions: List[Prediction]) -> Dict[str, Any]:
        """Analyze trends in recent predictions"""
        if len(predictions) < 2:
            return {}
        
        # Extract time series for each metric
        metrics = {
            "mental_health_score": [],
            "phq9": [],
            "gad7": [],
            "pss": [],
            "wemwbs": [],
            "depression": [],
            "anxiety": [],
            "stress": []
        }
        
        timestamps = []
        
        for pred in predictions:
            timestamps.append(pred.created_at)
            if pred.mental_health_score is not None:
                metrics["mental_health_score"].append(pred.mental_health_score)
            if pred.phq9_score is not None:
                metrics["phq9"].append(pred.phq9_score)
            if pred.gad7_score is not None:
                metrics["gad7"].append(pred.gad7_score)
            if pred.pss_score is not None:
                metrics["pss"].append(pred.pss_score)
            if pred.wemwbs_score is not None:
                metrics["wemwbs"].append(pred.wemwbs_score)
            if pred.depression_score is not None:
                metrics["depression"].append(pred.depression_score)
            if pred.anxiety_score is not None:
                metrics["anxiety"].append(pred.anxiety_score)
            if pred.stress_score is not None:
                metrics["stress"].append(pred.stress_score)
        
        trends = {}
        
        for metric, values in metrics.items():
            if len(values) >= 2:
                trend = self._calculate_trend(values)
                trends[metric] = {
                    "values": values,
                    "first": values[0],
                    "last": values[-1],
                    "mean": round(np.mean(values), 2),
                    "std": round(np.std(values), 2),
                    "trend_direction": trend["direction"],
                    "trend_slope": trend["slope"],
                    "trend_strength": trend["strength"],
                    "change_percentage": trend["change_percentage"]
                }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend statistics for a series of values"""
        if len(values) < 2:
            return {"direction": "stable", "slope": 0, "strength": "none", "change_percentage": 0}
        
        # Simple linear regression
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Calculate change percentage
        if values[0] != 0:
            change_pct = ((values[-1] - values[0]) / abs(values[0])) * 100
        else:
            change_pct = 0
        
        # Determine direction and strength
        if abs(slope) < 0.01:
            direction = "stable"
            strength = "none"
        elif slope > 0:
            direction = "increasing"
            strength = "strong" if abs(slope) > 0.1 else "moderate" if abs(slope) > 0.05 else "mild"
        else:
            direction = "decreasing"
            strength = "strong" if abs(slope) > 0.1 else "moderate" if abs(slope) > 0.05 else "mild"
        
        return {
            "direction": direction,
            "slope": round(slope, 4),
            "strength": strength,
            "change_percentage": round(change_pct, 1)
        }
    
    def _calculate_deterioration_risk(self, trends: Dict) -> Dict[str, Any]:
        """Calculate overall deterioration risk from trends"""
        risk_factors = []
        risk_score = 0.0
        
        # Check negative indicators (higher is worse)
        negative_metrics = ["phq9", "gad7", "pss", "depression", "anxiety", "stress"]
        for metric in negative_metrics:
            if metric in trends:
                trend = trends[metric]
                if trend["trend_direction"] == "increasing":
                    change = abs(trend["change_percentage"])
                    if change > 40:
                        risk_factors.append(f"Significant increase in {metric.upper()}")
                        risk_score += 0.3
                    elif change > 25:
                        risk_factors.append(f"Moderate increase in {metric.upper()}")
                        risk_score += 0.2
                    elif change > 15:
                        risk_factors.append(f"Mild increase in {metric.upper()}")
                        risk_score += 0.1
        
        # Check positive indicators (higher is better)
        positive_metrics = ["mental_health_score", "wemwbs"]
        for metric in positive_metrics:
            if metric in trends:
                trend = trends[metric]
                if trend["trend_direction"] == "decreasing":
                    change = abs(trend["change_percentage"])
                    if change > 20:
                        risk_factors.append(f"Decline in {metric.replace('_', ' ')}")
                        risk_score += 0.25
                    elif change > 10:
                        risk_factors.append(f"Slight decline in {metric.replace('_', ' ')}")
                        risk_score += 0.15
        
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        # Determine risk level
        if risk_score < 0.2:
            risk_level = "low"
            interpretation = "No significant deterioration detected"
        elif risk_score < 0.4:
            risk_level = "mild"
            interpretation = "Some concerning trends detected"
        elif risk_score < 0.6:
            risk_level = "moderate"
            interpretation = "Multiple concerning trends - monitoring recommended"
        else:
            risk_level = "high"
            interpretation = "Significant deterioration risk - professional consultation recommended"
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "interpretation": interpretation,
            "risk_factors": risk_factors
        }
    
    def _predict_trajectory(self, trends: Dict) -> Dict[str, Any]:
        """Predict future trajectory based on current trends"""
        # Use mental health score as primary indicator
        if "mental_health_score" in trends:
            mh_trend = trends["mental_health_score"]
            current = mh_trend["last"]
            slope = mh_trend["trend_slope"]
            
            # Project 7 days ahead (assuming daily samples)
            projected = current + (slope * 7)
            projected = max(0, min(100, projected))  # Clamp to valid range
            
            if slope > 0.5:
                trajectory = "improving"
                confidence = "high" if mh_trend["trend_strength"] == "strong" else "moderate"
            elif slope < -0.5:
                trajectory = "declining"
                confidence = "high" if mh_trend["trend_strength"] == "strong" else "moderate"
            else:
                trajectory = "stable"
                confidence = "high"
            
            return {
                "current_score": round(current, 1),
                "projected_score_7d": round(projected, 1),
                "trajectory": trajectory,
                "confidence": confidence,
                "trend_strength": mh_trend["trend_strength"]
            }
        
        return {
            "trajectory": "unknown",
            "confidence": "low",
            "message": "Insufficient data for trajectory prediction"
        }
    
    def _generate_trend_recommendations(
        self, 
        trends: Dict, 
        deterioration_risk: Dict
    ) -> List[str]:
        """Generate recommendations based on trends and risk"""
        recommendations = []
        
        risk_level = deterioration_risk.get("risk_level", "low")
        
        if risk_level == "high":
            recommendations.append("Consider scheduling a consultation with a mental health professional soon.")
            recommendations.append("Increase frequency of voice recordings to daily for closer monitoring.")
        elif risk_level == "moderate":
            recommendations.append("Continue regular voice recordings to monitor trends.")
            recommendations.append("Practice stress management techniques and maintain healthy routines.")
        elif risk_level == "mild":
            recommendations.append("Some fluctuation detected - maintain your wellness practices.")
            recommendations.append("Consider journaling to track factors affecting your mental state.")
        else:
            recommendations.append("Your mental health appears stable. Continue your current wellness practices.")
        
        # Specific recommendations based on trends
        if "anxiety" in trends and trends["anxiety"]["trend_direction"] == "increasing":
            recommendations.append("Try relaxation exercises like deep breathing or meditation.")
        
        if "depression" in trends and trends["depression"]["trend_direction"] == "increasing":
            recommendations.append("Engage in activities you enjoy and maintain social connections.")
        
        if "stress" in trends and trends["stress"]["trend_direction"] == "increasing":
            recommendations.append("Take regular breaks and practice time management techniques.")
        
        return recommendations
    
    def get_personalization_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a complete personalization summary for a user"""
        baseline = self.get_user_baseline(user_id)
        sample_count = self._get_sample_count(user_id)
        outcome = self.predict_outcome(user_id)
        
        return {
            "user_id": user_id,
            "total_samples": sample_count,
            "baseline_established": baseline is not None,
            "baseline_sample_count": baseline["sample_count"] if baseline else 0,
            "samples_to_baseline": max(0, self.MIN_BASELINE_SAMPLES - sample_count),
            "progress_percentage": min(100, int((sample_count / self.MIN_BASELINE_SAMPLES) * 100)),
            "baseline": baseline,
            "outcome_prediction": outcome
        }
