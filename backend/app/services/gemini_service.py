"""
Gemini 3 AI Service for Vocalysis Clinical Report Generation
CITTAA Health Services Private Limited

This service integrates Google's Gemini 3 Pro model to generate
detailed clinical reports from voice analysis results.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Gemini 3 model configuration
GEMINI_MODEL = "gemini-3-pro-preview"
GEMINI_FLASH_MODEL = "gemini-3-flash-preview"

# Clinical report generation prompt template
CLINICAL_REPORT_PROMPT = """You are an expert clinical psychologist AI assistant for CITTAA Health Services' Vocalysis mental health screening system. Based on the voice analysis results provided, generate a comprehensive clinical report.

## Voice Analysis Results:
- **Primary Classification**: {primary_condition}
- **Confidence Score**: {confidence:.1%}
- **Risk Level**: {risk_level}

### Probability Distribution:
- Normal: {normal_prob:.1%}
- Anxiety: {anxiety_prob:.1%}
- Depression: {depression_prob:.1%}
- Stress: {stress_prob:.1%}

### Clinical Scale Scores:
- PHQ-9 (Depression): {phq9_score}/27 - {phq9_severity}
- GAD-7 (Anxiety): {gad7_score}/21 - {gad7_severity}
- PSS (Stress): {pss_score}/40 - {pss_severity}
- WEMWBS (Wellbeing): {wemwbs_score}/70 - {wemwbs_level}

### Voice Biomarkers:
- Pitch Mean: {pitch_mean:.1f} Hz
- Pitch Variability: {pitch_std:.1f} Hz
- Speech Rate: {speech_rate:.1f} syllables/sec
- Energy Level: {energy:.2f}
- Voice Quality Index: {voice_quality:.2f}

### Personalization Status:
- Samples Collected: {samples_collected}/{target_samples}
- Baseline Established: {baseline_established}
- Deviation from Baseline: {deviation_score:.1%}

## Instructions:
Generate a professional clinical report that includes:

1. **Executive Summary**: A brief overview of the patient's mental health status based on voice analysis.

2. **Detailed Analysis**: 
   - Interpretation of the voice biomarkers
   - Correlation between voice patterns and mental health indicators
   - Comparison with established baselines (if available)

3. **Clinical Observations**:
   - Key findings from the PHQ-9, GAD-7, PSS, and WEMWBS scores
   - Risk factors identified
   - Protective factors observed

4. **Recommendations**:
   - Suggested follow-up actions
   - Lifestyle recommendations
   - Whether professional consultation is recommended

5. **Disclaimer**: Include appropriate clinical disclaimers about AI-assisted screening.

Format the report in a professional, clinical style suitable for healthcare documentation.
"""

class GeminiService:
    """Service for generating clinical reports using Gemini 3 AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini service.
        
        Args:
            api_key: Google API key for Gemini. If not provided, reads from environment.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model = GEMINI_MODEL
        self._initialized = False
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client."""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self._initialized = True
            logger.info(f"Gemini 3 client initialized with model: {self.model}")
        except ImportError:
            logger.warning("google-generativeai package not installed. Using fallback report generation.")
            self._initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if Gemini service is available."""
        return self._initialized and self.client is not None
    
    async def generate_clinical_report(
        self,
        analysis_result: Dict[str, Any],
        voice_features: Dict[str, Any],
        personalization_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a clinical report from voice analysis results using Gemini 3.
        
        Args:
            analysis_result: The voice analysis prediction results
            voice_features: Extracted voice biomarkers
            personalization_data: User's personalization/baseline data
            
        Returns:
            Dictionary containing the generated clinical report
        """
        # Prepare data for the prompt
        probabilities = analysis_result.get("probabilities", {})
        clinical_scores = analysis_result.get("clinical_scores", {})
        
        # Determine primary condition and risk level
        primary_condition = max(probabilities, key=probabilities.get) if probabilities else "Unknown"
        confidence = max(probabilities.values()) if probabilities else 0.0
        
        # Determine risk level based on probabilities
        risk_score = (
            probabilities.get("anxiety", 0) * 0.3 +
            probabilities.get("depression", 0) * 0.4 +
            probabilities.get("stress", 0) * 0.3
        )
        if risk_score > 0.6:
            risk_level = "High"
        elif risk_score > 0.3:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
        
        # Get clinical scale interpretations
        phq9 = clinical_scores.get("phq9", {})
        gad7 = clinical_scores.get("gad7", {})
        pss = clinical_scores.get("pss", {})
        wemwbs = clinical_scores.get("wemwbs", {})
        
        # Personalization data
        if personalization_data is None:
            personalization_data = {}
        
        # Format the prompt
        prompt_data = {
            "primary_condition": primary_condition.capitalize(),
            "confidence": confidence,
            "risk_level": risk_level,
            "normal_prob": probabilities.get("normal", 0),
            "anxiety_prob": probabilities.get("anxiety", 0),
            "depression_prob": probabilities.get("depression", 0),
            "stress_prob": probabilities.get("stress", 0),
            "phq9_score": phq9.get("score", 0),
            "phq9_severity": phq9.get("severity", "Not assessed"),
            "gad7_score": gad7.get("score", 0),
            "gad7_severity": gad7.get("severity", "Not assessed"),
            "pss_score": pss.get("score", 0),
            "pss_severity": pss.get("level", "Not assessed"),
            "wemwbs_score": wemwbs.get("score", 0),
            "wemwbs_level": wemwbs.get("level", "Not assessed"),
            "pitch_mean": voice_features.get("pitch_mean", 0),
            "pitch_std": voice_features.get("pitch_std", 0),
            "speech_rate": voice_features.get("speech_rate", 0),
            "energy": voice_features.get("energy", 0),
            "voice_quality": voice_features.get("voice_quality", 0),
            "samples_collected": personalization_data.get("samples_collected", 0),
            "target_samples": personalization_data.get("target_samples", 9),
            "baseline_established": "Yes" if personalization_data.get("baseline_established", False) else "No",
            "deviation_score": personalization_data.get("deviation_score", 0),
        }
        
        formatted_prompt = CLINICAL_REPORT_PROMPT.format(**prompt_data)
        
        # Generate report using Gemini 3
        if self.is_available():
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=formatted_prompt,
                )
                report_text = response.text
                generation_method = "gemini-3-pro"
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}")
                report_text = self._generate_fallback_report(prompt_data)
                generation_method = "fallback"
        else:
            report_text = self._generate_fallback_report(prompt_data)
            generation_method = "fallback"
        
        return {
            "report": report_text,
            "generated_at": datetime.utcnow().isoformat(),
            "model": self.model if generation_method == "gemini-3-pro" else "fallback",
            "generation_method": generation_method,
            "risk_level": risk_level,
            "primary_condition": primary_condition,
            "confidence": confidence,
        }
    
    def _generate_fallback_report(self, data: Dict[str, Any]) -> str:
        """
        Generate a basic clinical report without Gemini AI.
        Used as fallback when Gemini is not available.
        """
        report = f"""
# Vocalysis Clinical Screening Report
## CITTAA Health Services Private Limited

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

---

## Executive Summary

Based on voice biomarker analysis, the primary classification is **{data['primary_condition']}** with a confidence of **{data['confidence']:.1%}**. The overall risk level is assessed as **{data['risk_level']}**.

---

## Voice Analysis Results

### Probability Distribution
| Condition | Probability |
|-----------|-------------|
| Normal | {data['normal_prob']:.1%} |
| Anxiety | {data['anxiety_prob']:.1%} |
| Depression | {data['depression_prob']:.1%} |
| Stress | {data['stress_prob']:.1%} |

### Clinical Scale Scores
- **PHQ-9 (Depression):** {data['phq9_score']}/27 - {data['phq9_severity']}
- **GAD-7 (Anxiety):** {data['gad7_score']}/21 - {data['gad7_severity']}
- **PSS (Stress):** {data['pss_score']}/40 - {data['pss_severity']}
- **WEMWBS (Wellbeing):** {data['wemwbs_score']}/70 - {data['wemwbs_level']}

### Voice Biomarkers
- Pitch Mean: {data['pitch_mean']:.1f} Hz
- Pitch Variability: {data['pitch_std']:.1f} Hz
- Speech Rate: {data['speech_rate']:.1f} syllables/sec
- Energy Level: {data['energy']:.2f}

---

## Personalization Status

- Samples Collected: {data['samples_collected']}/{data['target_samples']}
- Baseline Established: {data['baseline_established']}

---

## Recommendations

Based on the analysis results:

1. {"Consider consulting a mental health professional for further evaluation." if data['risk_level'] == "High" else "Continue regular self-monitoring and maintain healthy lifestyle practices."}

2. {"Regular follow-up voice screenings are recommended to track changes over time." if data['samples_collected'] < data['target_samples'] else "Baseline established - future analyses will be compared against your personal baseline."}

---

## Disclaimer

This report is generated by an AI-assisted voice analysis system and is intended for screening purposes only. It does not constitute a clinical diagnosis. Please consult a qualified healthcare professional for proper evaluation and treatment recommendations.

---

*CITTAA Health Services Private Limited - Vocalysis Mental Health Screening System*
"""
        return report.strip()


# Global service instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the global Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
