import re
import asyncio
from typing import List, Dict, Any, Optional
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from .models import ContentCategory, Language
from .database import get_database, get_redis
import json

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class ContentFilterEngine:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.inappropriate_keywords = {
            Language.ENGLISH: [
                'adult', 'porn', 'sex', 'violence', 'drugs', 'alcohol', 'gambling',
                'suicide', 'self-harm', 'hate', 'racism', 'terrorism', 'weapon'
            ],
            Language.HINDI: [
                'अश्लील', 'हिंसा', 'नशा', 'शराब', 'जुआ', 'आत्महत्या', 'नफरत'
            ],
            Language.TAMIL: [
                'வன்முறை', 'போதைப்பொருள்', 'மது', 'சூதாட்டம்', 'தற்கொலை'
            ],
            Language.TELUGU: [
                'హింస', 'మాదకద్రవ్యాలు', 'మద్యం', 'జూదం', 'ఆత్మహత్య'
            ],
            Language.BENGALI: [
                'সহিংসতা', 'মাদক', 'মদ', 'জুয়া', 'আত্মহত্যা'
            ],
            Language.MARATHI: [
                'हिंसा', 'नशा', 'दारू', 'जुगार', 'आत्महत्या'
            ]
        }
        
        self.educational_keywords = {
            Language.ENGLISH: [
                'education', 'learning', 'study', 'school', 'math', 'science',
                'history', 'geography', 'literature', 'ncert', 'cbse', 'icse'
            ],
            Language.HINDI: [
                'शिक्षा', 'अध्ययन', 'स्कूल', 'गणित', 'विज्ञान', 'इतिहास',
                'भूगोल', 'साहित्य', 'एनसीईआरटी'
            ]
        }
        
        self.vpn_indicators = [
            'vpn', 'proxy', 'tunnel', 'tor', 'anonymizer', 'hide ip',
            'bypass', 'unblock', 'circumvent', 'mask location'
        ]

    async def analyze_content(self, url: str, content: Optional[str] = None, language: Language = Language.ENGLISH) -> Dict[str, Any]:
        """Analyze content and determine if it should be blocked"""
        
        redis_client = get_redis()
        cache_key = f"content_filter:{url}"
        
        if redis_client:
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
        
        analysis_result = {
            'url': url,
            'category': ContentCategory.ENTERTAINMENT,
            'is_blocked': False,
            'confidence_score': 0.0,
            'reason': '',
            'language': language,
            'alternative_content': []
        }
        
        url_analysis = self._analyze_url(url, language)
        analysis_result.update(url_analysis)
        
        if content:
            content_analysis = self._analyze_text_content(content, language)
            if content_analysis['confidence_score'] > analysis_result['confidence_score']:
                analysis_result.update(content_analysis)
        
        if redis_client:
            await redis_client.setex(cache_key, 3600, json.dumps(analysis_result))
        
        return analysis_result

    def _analyze_url(self, url: str, language: Language) -> Dict[str, Any]:
        """Analyze URL for inappropriate content indicators"""
        url_lower = url.lower()
        
        for indicator in self.vpn_indicators:
            if indicator in url_lower:
                return {
                    'category': ContentCategory.INAPPROPRIATE,
                    'is_blocked': True,
                    'confidence_score': 0.95,
                    'reason': f'VPN/Proxy service detected: {indicator}',
                    'alternative_content': self._get_educational_alternatives()
                }
        
        inappropriate_words = self.inappropriate_keywords.get(language, self.inappropriate_keywords[Language.ENGLISH])
        for word in inappropriate_words:
            if word in url_lower:
                return {
                    'category': ContentCategory.ADULT_CONTENT,
                    'is_blocked': True,
                    'confidence_score': 0.9,
                    'reason': f'Inappropriate content detected: {word}',
                    'alternative_content': self._get_educational_alternatives()
                }
        
        educational_words = self.educational_keywords.get(language, self.educational_keywords[Language.ENGLISH])
        for word in educational_words:
            if word in url_lower:
                return {
                    'category': ContentCategory.EDUCATIONAL,
                    'is_blocked': False,
                    'confidence_score': 0.8,
                    'reason': f'Educational content detected: {word}',
                    'alternative_content': []
                }
        
        return {
            'category': ContentCategory.ENTERTAINMENT,
            'is_blocked': False,
            'confidence_score': 0.5,
            'reason': 'General content - no specific indicators found',
            'alternative_content': []
        }

    def _analyze_text_content(self, content: str, language: Language) -> Dict[str, Any]:
        """Analyze text content for inappropriate material"""
        content_lower = content.lower()
        
        sentiment_scores = self.sia.polarity_scores(content)
        
        inappropriate_words = self.inappropriate_keywords.get(language, self.inappropriate_keywords[Language.ENGLISH])
        inappropriate_count = sum(1 for word in inappropriate_words if word in content_lower)
        
        if inappropriate_count > 0:
            confidence = min(0.9, 0.5 + (inappropriate_count * 0.1))
            return {
                'category': ContentCategory.INAPPROPRIATE,
                'is_blocked': True,
                'confidence_score': confidence,
                'reason': f'Inappropriate language detected ({inappropriate_count} instances)',
                'alternative_content': self._get_educational_alternatives()
            }
        
        educational_words = self.educational_keywords.get(language, self.educational_keywords[Language.ENGLISH])
        educational_count = sum(1 for word in educational_words if word in content_lower)
        
        if educational_count > 2:
            return {
                'category': ContentCategory.EDUCATIONAL,
                'is_blocked': False,
                'confidence_score': 0.8,
                'reason': f'Educational content detected ({educational_count} educational terms)',
                'alternative_content': []
            }
        
        if sentiment_scores['compound'] < -0.5:
            return {
                'category': ContentCategory.INAPPROPRIATE,
                'is_blocked': True,
                'confidence_score': 0.7,
                'reason': 'Negative sentiment detected - potentially harmful content',
                'alternative_content': self._get_educational_alternatives()
            }
        
        return {
            'category': ContentCategory.ENTERTAINMENT,
            'is_blocked': False,
            'confidence_score': 0.6,
            'reason': 'Content appears safe for viewing',
            'alternative_content': []
        }

    def _get_educational_alternatives(self) -> List[str]:
        """Get list of educational content alternatives"""
        return [
            "https://ncert.nic.in/",
            "https://www.khanacademy.org/",
            "https://byjus.com/",
            "https://unacademy.com/",
            "https://vedantu.com/"
        ]

    async def detect_vpn_usage(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect VPN usage based on device data"""
        vpn_detected = False
        detection_methods = []
        confidence_score = 0.0
        
        if 'installed_apps' in device_data:
            vpn_apps = ['vpn', 'proxy', 'tunnel', 'tor', 'hotspot shield', 'nordvpn', 'expressvpn']
            for app in device_data['installed_apps']:
                app_lower = app.lower()
                for vpn_app in vpn_apps:
                    if vpn_app in app_lower:
                        vpn_detected = True
                        detection_methods.append(f"VPN app detected: {app}")
                        confidence_score = max(confidence_score, 0.9)
        
        if 'network_info' in device_data:
            network = device_data['network_info']
            
            if 'dns_servers' in network:
                suspicious_dns = ['1.1.1.1', '8.8.8.8', '9.9.9.9']  # Common VPN DNS
                for dns in network['dns_servers']:
                    if dns in suspicious_dns:
                        detection_methods.append(f"Suspicious DNS server: {dns}")
                        confidence_score = max(confidence_score, 0.6)
            
            if 'ip_location' in network and 'device_location' in device_data:
                pass
        
        return {
            'vpn_detected': vpn_detected,
            'detection_methods': detection_methods,
            'confidence_score': confidence_score,
            'recommended_action': 'block' if vpn_detected else 'allow'
        }

content_filter = ContentFilterEngine()
