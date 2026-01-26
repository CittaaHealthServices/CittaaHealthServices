"""
AI Escalation Engine for CITTAA
Multi-stage risk assessment with multilingual keyword detection
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Multilingual keyword detection across Hindi, English, Telugu, Tamil, Kannada
RISK_KEYWORDS = {
    "level_4_emergency": {
        "suicide_intent": [
            # English
            "want to die", "kill myself", "end my life", "suicide plan",
            "better off dead", "can't go on", "prepared to die", "no reason to live",
            "goodbye forever", "final goodbye", "ending it all", "take my life",
            # Hindi
            "मरना चाहता हूँ", "आत्महत्या", "जीना नहीं चाहता", "मौत", "खुद को मार",
            "जीवन समाप्त", "मर जाना चाहता",
            # Telugu
            "చావాలని", "ఆత్మహత్య", "బతకడం ఇష్టం లేదు", "చనిపోవాలని",
            # Tamil
            "சாக வேண்டும்", "தற்கொலை", "வாழ விரும்பவில்லை", "உயிரை மாய்த்துக்கொள்ள",
            # Kannada
            "ಸಾಯಬೇಕು", "ಆತ್ಮಹತ್ಯೆ", "ಬದುಕಲು ಇಷ್ಟವಿಲ್ಲ"
        ],
        "active_attempt": [
            "I have the pills", "wrote suicide note", "saying goodbye",
            "today is the day", "cutting myself now", "jumping from",
            "hanging myself", "overdose", "slit my wrists"
        ],
        "abuse_indicators": [
            "uncle touches me", "forced to", "hurts me there", "secret touch",
            "don't tell anyone", "threatened if I tell", "inappropriate touch",
            "bad touch", "sexual abuse", "molested", "raped",
            # Hindi
            "छूता है", "जबरदस्ती", "गलत तरीके से छुआ",
            # Telugu
            "తాకుతున్నాడు", "బలవంతంగా",
            # Tamil
            "தொடுகிறார்", "கட்டாயப்படுத்துகிறார்"
        ]
    },
    "level_3_high": {
        "suicide_ideation": [
            "thoughts of dying", "wish I was dead", "life is pointless",
            "everyone would be better", "thinking about ending", "hopeless",
            "no point in living", "want to disappear", "burden to everyone",
            # Hindi
            "जीवन व्यर्थ है", "कोई अर्थ नहीं", "मरने के बारे में सोचता",
            # Telugu
            "నిరాశగా ఉంది", "జీవితం వ్యర్థం",
            # Tamil
            "வாழ்வு அர்த்தமற்றது", "நம்பிக்கையில்லை",
            # Kannada
            "ಜೀವನ ನಿರರ್ಥಕ", "ಆಶಾಹೀನ"
        ],
        "severe_depression": [
            "can't get out of bed", "nothing matters", "constant crying",
            "stopped eating", "can't sleep for days", "extreme sadness",
            "completely numb", "empty inside", "lost all interest"
        ],
        "self_harm": [
            "cutting", "burning myself", "hurting myself", "self-injury",
            "scars on arms", "blood", "razor blade", "scratching myself",
            "hitting myself", "punching walls"
        ],
        "psychosis_indicators": [
            "hearing voices", "seeing things", "people following me",
            "controlling my thoughts", "not real", "hallucinations",
            "paranoid", "conspiracy against me"
        ]
    },
    "level_2_moderate": {
        "significant_distress": [
            "very anxious", "panic attacks", "severe stress", "can't cope",
            "overwhelming", "breaking down", "too much pressure",
            # Hindi
            "बहुत तनाव", "चिंता", "सहन नहीं होता",
            # Telugu
            "కష్టంగా ఉంది", "చాలా ఒత్తిడి",
            # Tamil
            "மன அழுத்தம்", "தாங்க முடியவில்லை",
            # Kannada
            "ತುಂಬಾ ಒತ್ತಡ"
        ],
        "behavioral_concerns": [
            "aggressive", "violent thoughts", "want to hurt", "anger issues",
            "can't control", "lashing out", "fighting", "disruptive",
            "explosive anger", "rage"
        ],
        "family_crisis": [
            "parents divorcing", "family violence", "financial crisis",
            "homeless", "abusive home", "unsafe environment", "domestic violence",
            "parents fighting", "kicked out of home"
        ],
        "persistent_issues": [
            "ongoing depression", "chronic anxiety", "not improving",
            "getting worse", "declining grades", "withdrawal from friends",
            "isolation", "refusing to go to school"
        ]
    },
    "level_1_low": {
        "mild_concerns": [
            "feeling sad", "bit anxious", "exam stress", "friend issues",
            "temporary sadness", "minor conflicts", "adjustment difficulties",
            "nervous about test", "worried about grades"
        ],
        "developmental_issues": [
            "peer pressure", "social anxiety", "academic stress",
            "identity confusion", "relationship issues", "body image concerns",
            "fitting in", "making friends"
        ]
    }
}

# Contextual modifiers that increase risk
RISK_AMPLIFIERS = [
    "specific plan", "access to means", "previous attempt", "recent loss",
    "isolated", "substance use", "giving away possessions", "final arrangements",
    "saying goodbye", "sudden calm after depression", "reckless behavior",
    "no support system", "history of trauma", "family history of suicide"
]

# Protective factors that may reduce risk
PROTECTIVE_FACTORS = [
    "supportive family", "good friends", "religious beliefs", "future plans",
    "seeking help", "therapy engagement", "willing to safety plan",
    "reasons for living", "hope for future", "connected to others",
    "engaged in activities", "positive coping skills"
]


@dataclass
class RiskAssessmentResult:
    """Result of risk assessment"""
    escalation_level: str
    confidence: float
    risk_category: str
    keywords_detected: List[str]
    reasoning: str
    recommended_actions: List[str]
    amplifiers_found: List[str]
    protective_factors_found: List[str]
    language_detected: str


class RuleBasedClassifier:
    """Rule-based keyword detection classifier"""
    
    def detect_keywords(self, text: str) -> Dict[str, Any]:
        """Detect risk keywords in text"""
        text_lower = text.lower()
        detected = {
            "level_4_emergency": [],
            "level_3_high": [],
            "level_2_moderate": [],
            "level_1_low": [],
            "categories": {}
        }
        
        for level, categories in RISK_KEYWORDS.items():
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        detected[level].append(keyword)
                        if category not in detected["categories"]:
                            detected["categories"][category] = []
                        detected["categories"][category].append(keyword)
        
        return detected


class ContextualRiskScorer:
    """Contextual risk scoring based on amplifiers and protective factors"""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze contextual factors"""
        text_lower = text.lower()
        
        amplifiers = [amp for amp in RISK_AMPLIFIERS if amp.lower() in text_lower]
        protectives = [pf for pf in PROTECTIVE_FACTORS if pf.lower() in text_lower]
        
        # Calculate risk modifier
        risk_modifier = len(amplifiers) * 0.1 - len(protectives) * 0.05
        
        return {
            "amplifiers": amplifiers,
            "protective_factors": protectives,
            "risk_modifier": risk_modifier
        }


class HistoricalPatternAnalyzer:
    """Analyze historical patterns for a student"""
    
    def analyze(self, student_history: List[Dict]) -> Dict[str, Any]:
        """Analyze student's historical patterns"""
        if not student_history:
            return {"pattern_risk": 0.0, "escalating_trend": False}
        
        # Check for escalating patterns
        risk_levels = []
        for session in student_history:
            level = session.get("risk_level", "low")
            level_score = {"low": 1, "moderate": 2, "high": 3, "imminent": 4}.get(level, 1)
            risk_levels.append(level_score)
        
        # Check if trend is escalating
        if len(risk_levels) >= 3:
            recent = risk_levels[-3:]
            escalating = recent[-1] > recent[0]
        else:
            escalating = False
        
        avg_risk = sum(risk_levels) / len(risk_levels) if risk_levels else 0
        
        return {
            "pattern_risk": avg_risk / 4,  # Normalize to 0-1
            "escalating_trend": escalating,
            "session_count": len(student_history)
        }


class EscalationAIEngine:
    """
    Multi-Model Ensemble Approach for Risk Assessment
    
    Combines:
    1. Rule-based keyword detection (fast, deterministic)
    2. Contextual risk scoring
    3. Historical pattern analysis
    4. Ensemble scoring for final assessment
    """
    
    def __init__(self):
        self.rule_engine = RuleBasedClassifier()
        self.risk_scorer = ContextualRiskScorer()
        self.pattern_analyzer = HistoricalPatternAnalyzer()
    
    def detect_language(self, text: str) -> str:
        """Detect primary language of text"""
        # Simple heuristic based on character ranges
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
        kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
        
        if hindi_pattern.search(text):
            return "hindi"
        elif telugu_pattern.search(text):
            return "telugu"
        elif tamil_pattern.search(text):
            return "tamil"
        elif kannada_pattern.search(text):
            return "kannada"
        return "english"
    
    def assess_escalation(self, session_data: Dict, student_history: Optional[List[Dict]] = None) -> RiskAssessmentResult:
        """
        Multi-stage assessment pipeline:
        1. Keyword detection (fast, rule-based)
        2. Contextual analysis
        3. Historical context analysis
        4. Final risk scoring with confidence
        """
        # Extract session text
        presenting_issue = session_data.get("presenting_issue", "")
        session_notes = session_data.get("session_notes", "")
        combined_text = f"{presenting_issue} {session_notes}"
        
        # Detect language
        language = self.detect_language(combined_text)
        
        # Stage 1: Rule-based keyword detection
        keyword_results = self.rule_engine.detect_keywords(combined_text)
        
        # Stage 2: Contextual analysis
        context_results = self.risk_scorer.analyze(combined_text)
        
        # Stage 3: Historical pattern analysis
        pattern_results = self.pattern_analyzer.analyze(student_history or [])
        
        # Stage 4: Ensemble scoring
        return self._ensemble_scoring(
            keyword_results,
            context_results,
            pattern_results,
            language
        )
    
    def _ensemble_scoring(
        self,
        keyword_results: Dict,
        context_results: Dict,
        pattern_results: Dict,
        language: str
    ) -> RiskAssessmentResult:
        """Combine all signals for final assessment"""
        
        # Determine escalation level based on keywords found
        if keyword_results["level_4_emergency"]:
            level = "level_4_emergency"
            base_confidence = 0.85
        elif keyword_results["level_3_high"]:
            level = "level_3_high"
            base_confidence = 0.75
        elif keyword_results["level_2_moderate"]:
            level = "level_2_moderate"
            base_confidence = 0.70
        elif keyword_results["level_1_low"]:
            level = "level_1_low"
            base_confidence = 0.65
        else:
            level = "level_1_low"
            base_confidence = 0.50
        
        # Adjust confidence based on context
        confidence = base_confidence + context_results["risk_modifier"]
        
        # Adjust for historical patterns
        if pattern_results["escalating_trend"]:
            confidence += 0.1
            # Potentially upgrade level if escalating
            if level == "level_2_moderate" and confidence > 0.8:
                level = "level_3_high"
        
        # Cap confidence
        confidence = min(max(confidence, 0.0), 1.0)
        
        # Determine primary risk category
        categories = keyword_results.get("categories", {})
        if categories:
            risk_category = max(categories.keys(), key=lambda k: len(categories[k]))
        else:
            risk_category = "general_concern"
        
        # Collect all detected keywords
        all_keywords = []
        for level_keywords in [keyword_results["level_4_emergency"], 
                               keyword_results["level_3_high"],
                               keyword_results["level_2_moderate"],
                               keyword_results["level_1_low"]]:
            all_keywords.extend(level_keywords)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            level, all_keywords, context_results, pattern_results
        )
        
        # Get recommended actions
        recommended_actions = self._get_recommended_actions(level, risk_category)
        
        return RiskAssessmentResult(
            escalation_level=level,
            confidence=round(confidence, 4),
            risk_category=risk_category,
            keywords_detected=all_keywords,
            reasoning=reasoning,
            recommended_actions=recommended_actions,
            amplifiers_found=context_results["amplifiers"],
            protective_factors_found=context_results["protective_factors"],
            language_detected=language
        )
    
    def _generate_reasoning(
        self,
        level: str,
        keywords: List[str],
        context: Dict,
        patterns: Dict
    ) -> str:
        """Generate human-readable reasoning for the assessment"""
        parts = []
        
        if keywords:
            parts.append(f"Detected {len(keywords)} risk indicator(s): {', '.join(keywords[:5])}")
        
        if context["amplifiers"]:
            parts.append(f"Risk amplifiers present: {', '.join(context['amplifiers'])}")
        
        if context["protective_factors"]:
            parts.append(f"Protective factors noted: {', '.join(context['protective_factors'])}")
        
        if patterns.get("escalating_trend"):
            parts.append("Historical pattern shows escalating risk trend")
        
        level_descriptions = {
            "level_4_emergency": "EMERGENCY - Immediate intervention required",
            "level_3_high": "HIGH RISK - Action needed within 24 hours",
            "level_2_moderate": "MODERATE - Increased monitoring recommended",
            "level_1_low": "LOW - Standard follow-up appropriate"
        }
        
        parts.append(f"Assessment: {level_descriptions.get(level, 'Unknown')}")
        
        return ". ".join(parts)
    
    def _get_recommended_actions(self, level: str, category: str) -> List[str]:
        """Get recommended actions based on escalation level and category"""
        actions = {
            "level_4_emergency": [
                "Contact student's parent/guardian immediately",
                "Ensure continuous supervision of student",
                "Consider emergency services if needed (112/108)",
                "Coordinate with CITTAA clinical team",
                "Document all actions taken",
                "Do not leave student alone",
                "Remove access to means if applicable"
            ],
            "level_3_high": [
                "Schedule parent meeting within 24 hours",
                "Increase monitoring frequency",
                "Develop safety plan with student",
                "Consider referral to psychiatrist/specialist",
                "Coordinate with school administration",
                "Document intervention plan"
            ],
            "level_2_moderate": [
                "Schedule follow-up session within 1 week",
                "Inform relevant teachers for classroom support",
                "Consider group intervention if appropriate",
                "Monitor for any escalation",
                "Document observations and plan"
            ],
            "level_1_low": [
                "Continue regular counseling schedule",
                "Monitor progress in subsequent sessions",
                "Provide psychoeducation resources",
                "Document session notes"
            ]
        }
        
        # Add category-specific actions
        category_actions = {
            "abuse_indicators": [
                "Follow POCSO Act mandatory reporting requirements",
                "Contact Child Welfare Committee if required",
                "Ensure child safety is prioritized"
            ],
            "suicide_intent": [
                "Conduct thorough suicide risk assessment",
                "Create no-harm contract if appropriate",
                "Provide crisis helpline numbers"
            ],
            "self_harm": [
                "Assess wound severity and medical needs",
                "Discuss alternative coping strategies",
                "Consider DBT skills training"
            ]
        }
        
        base_actions = actions.get(level, actions["level_1_low"])
        extra_actions = category_actions.get(category, [])
        
        return base_actions + extra_actions


# Singleton instance
escalation_engine = EscalationAIEngine()
