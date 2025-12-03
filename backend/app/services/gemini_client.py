"""
Gemini AI Client for Vocalysis Analytics
Provides AI-powered insights and recommendations for mental health analysis
"""

import os
import json
from typing import Dict, Any, Optional

class GeminiInsightsService:
    """Service for generating AI-powered insights using Google Gemini"""
    
    def __init__(self):
        """Initialize the Gemini client"""
        self.project_id = os.environ.get("GCP_PROJECT_ID", "vocalysis-production")
        self.location = os.environ.get("GCP_REGION", "us-central1")
        self.model_name = "gemini-1.5-flash"
        self._model = None
        
    def _get_model(self):
        """Get or initialize the Gemini model"""
        if self._model is None:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                
                vertexai.init(project=self.project_id, location=self.location)
                self._model = GenerativeModel(self.model_name)
            except ImportError:
                # Fallback to google-generativeai if vertexai not available
                try:
                    import google.generativeai as genai
                    api_key = os.environ.get("GEMINI_API_KEY")
                    if api_key:
                        genai.configure(api_key=api_key)
                        self._model = genai.GenerativeModel(self.model_name)
                except ImportError:
                    pass
        return self._model
    
    def generate_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered insights from voice analysis results
        
        Args:
            analysis: Dictionary containing:
                - voice_features: Extracted acoustic features
                - risk_scores: Depression, anxiety, stress scores (0-1)
                - clinical_scores: PHQ-9, GAD-7, PSS, WEMWBS scores and severities
                - risk_level: Overall risk level (low/moderate/high)
                
        Returns:
            Dictionary with:
                - summary: Plain language summary of findings
                - risk_factors: Key contributing factors
                - suggestions: Lifestyle and wellness suggestions
                - disclaimer: Medical disclaimer
        """
        model = self._get_model()
        
        if model is None:
            # Return rule-based insights if Gemini is not available
            return self._generate_fallback_insights(analysis)
        
        try:
            prompt = self._build_prompt(analysis)
            response = model.generate_content(prompt)
            
            # Parse response
            text = response.text
            try:
                # Try to parse as JSON
                return json.loads(text)
            except json.JSONDecodeError:
                # Wrap text response in structured format
                return {
                    "summary": text[:500] if len(text) > 500 else text,
                    "risk_factors": self._extract_risk_factors(analysis),
                    "suggestions": self._extract_suggestions(analysis),
                    "disclaimer": "This is an AI-generated analysis for informational purposes only. It is not a medical diagnosis. Please consult a qualified mental health professional for clinical assessment."
                }
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._generate_fallback_insights(analysis)
    
    def _build_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build the prompt for Gemini"""
        return f"""You are an analytics assistant for Vocalysis, a mental health screening platform that analyzes voice patterns to detect potential mental health indicators.

You receive structured screening results from voice analysis. Your role is to:
1. Summarize the findings in plain, compassionate language
2. Explain which voice patterns are contributing to the assessment
3. Offer general wellness suggestions (not medical advice)
4. Always include a disclaimer that this is not a diagnosis

IMPORTANT GUIDELINES:
- Do NOT claim to diagnose any condition
- Use phrases like "indicators suggest", "patterns may indicate", "screening results show"
- Be supportive and non-alarming in tone
- Focus on actionable wellness suggestions
- Acknowledge that professional consultation is recommended for any concerns

Here is the voice analysis data:

{json.dumps(analysis, indent=2)}

Respond ONLY with a JSON object containing these exact keys:
{{
    "summary": "A 2-3 sentence plain language summary of the overall findings",
    "risk_factors": "Bullet-style list of contributing factors based on voice patterns (as a single string with newlines)",
    "suggestions": "Bullet-style list of general wellness suggestions (as a single string with newlines)",
    "disclaimer": "A brief disclaimer about this being a screening tool, not a diagnosis"
}}"""

    def _generate_fallback_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based insights when Gemini is unavailable"""
        risk_level = analysis.get("risk_level", "low")
        clinical_scores = analysis.get("clinical_scores", {})
        
        # Build summary based on risk level
        if risk_level == "high":
            summary = "Your voice analysis indicates elevated stress and emotional indicators. The patterns detected suggest you may be experiencing significant mental health challenges. We recommend speaking with a mental health professional for personalized support."
        elif risk_level == "moderate":
            summary = "Your voice analysis shows some indicators of stress or emotional fluctuation. While not severe, these patterns suggest you may benefit from stress management techniques and self-care practices."
        else:
            summary = "Your voice analysis indicates generally healthy patterns. The acoustic features suggest stable emotional regulation and low stress levels. Continue maintaining your current wellness practices."
        
        return {
            "summary": summary,
            "risk_factors": self._extract_risk_factors(analysis),
            "suggestions": self._extract_suggestions(analysis),
            "disclaimer": "This screening is for informational purposes only and is not a medical diagnosis. Voice-based mental health screening is an emerging technology. Please consult a qualified mental health professional for clinical assessment and personalized care recommendations."
        }
    
    def _extract_risk_factors(self, analysis: Dict[str, Any]) -> str:
        """Extract risk factors from analysis"""
        factors = []
        
        voice_features = analysis.get("voice_features", {})
        probabilities = analysis.get("probabilities", [0.6, 0.1, 0.1, 0.1])
        
        if len(probabilities) >= 4:
            normal, anxiety, depression, stress = probabilities[:4]
            
            if depression > 0.25:
                factors.append("- Reduced pitch variability and slower speech patterns detected")
                factors.append("- Lower vocal energy levels observed")
            
            if anxiety > 0.25:
                factors.append("- Elevated pitch and increased speech rate detected")
                factors.append("- Higher vocal tension indicators present")
            
            if stress > 0.25:
                factors.append("- Irregular speech rhythm patterns observed")
                factors.append("- Elevated jitter in voice quality detected")
        
        if not factors:
            factors.append("- Voice patterns within normal ranges")
            factors.append("- Stable pitch and rhythm detected")
        
        return "\n".join(factors)
    
    def _extract_suggestions(self, analysis: Dict[str, Any]) -> str:
        """Extract wellness suggestions based on analysis"""
        suggestions = []
        risk_level = analysis.get("risk_level", "low")
        probabilities = analysis.get("probabilities", [0.6, 0.1, 0.1, 0.1])
        
        if len(probabilities) >= 4:
            normal, anxiety, depression, stress = probabilities[:4]
            
            if risk_level == "high":
                suggestions.append("- Consider scheduling a consultation with a mental health professional")
                suggestions.append("- Reach out to trusted friends or family for support")
            
            if depression > 0.25:
                suggestions.append("- Engage in activities you enjoy, even briefly")
                suggestions.append("- Maintain regular sleep and wake times")
                suggestions.append("- Consider gentle physical activity like walking")
            
            if anxiety > 0.25:
                suggestions.append("- Practice deep breathing exercises (4-7-8 technique)")
                suggestions.append("- Limit caffeine and stimulant intake")
                suggestions.append("- Try progressive muscle relaxation before bed")
            
            if stress > 0.25:
                suggestions.append("- Take regular breaks during work or study")
                suggestions.append("- Practice mindfulness or meditation for 5-10 minutes daily")
                suggestions.append("- Prioritize tasks and delegate when possible")
        
        if not suggestions or risk_level == "low":
            suggestions = [
                "- Continue your current wellness practices",
                "- Maintain regular physical activity",
                "- Ensure adequate sleep (7-9 hours)",
                "- Stay connected with supportive relationships"
            ]
        
        return "\n".join(suggestions)


# Singleton instance
gemini_service = GeminiInsightsService()
