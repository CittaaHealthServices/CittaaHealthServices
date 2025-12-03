"""
PDF Report Generation Service for Vocalysis
Generates clinical reports in PDF format
"""

from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any, Optional
import io


class VocalysisPDF(FPDF):
    """Custom PDF class with Vocalysis branding"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Add header to each page"""
        # Logo placeholder (using text for now)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(139, 90, 150)  # Primary color
        self.cell(0, 10, 'CITTAA Health Services', 0, 0, 'L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Vocalysis Mental Health Report', 0, 1, 'R')
        self.ln(5)
        # Line separator
        self.set_draw_color(139, 90, 150)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        """Add footer to each page"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")} | Confidential', 0, 0, 'C')


class PDFReportService:
    """Service for generating PDF reports"""
    
    def generate_analysis_report(self, prediction: Dict[str, Any], user_name: str = "Patient") -> bytes:
        """
        Generate a PDF report for voice analysis results
        
        Args:
            prediction: Dictionary containing prediction data
            user_name: Name of the patient
            
        Returns:
            PDF file as bytes
        """
        pdf = VocalysisPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 15, 'Voice Analysis Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Patient Info
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 8, f'Patient: {user_name}', 0, 1)
        pdf.cell(0, 8, f'Analysis Date: {prediction.get("predicted_at", datetime.now().isoformat())[:10]}', 0, 1)
        pdf.cell(0, 8, f'Report ID: {prediction.get("id", "N/A")}', 0, 1)
        pdf.ln(10)
        
        # Overall Score Section
        self._add_section_header(pdf, 'Overall Mental Health Assessment')
        
        mental_health_score = prediction.get('mental_health_score', 0)
        risk_level = prediction.get('overall_risk_level', 'unknown')
        confidence = prediction.get('confidence', 0)
        
        # Score box
        pdf.set_fill_color(139, 90, 150)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 24)
        pdf.cell(60, 25, f'{mental_health_score:.0f}/100', 1, 0, 'C', True)
        
        pdf.set_fill_color(123, 179, 168)
        risk_color = {'low': (39, 174, 96), 'moderate': (243, 156, 18), 'high': (231, 76, 60)}
        color = risk_color.get(risk_level, (128, 128, 128))
        pdf.set_fill_color(*color)
        pdf.cell(60, 25, f'Risk: {risk_level.upper()}', 1, 0, 'C', True)
        
        pdf.set_fill_color(100, 100, 100)
        pdf.cell(60, 25, f'Confidence: {confidence*100:.0f}%', 1, 1, 'C', True)
        pdf.ln(10)
        
        # Classification Probabilities
        self._add_section_header(pdf, 'Mental State Classification')
        pdf.set_text_color(60, 60, 60)
        pdf.set_font('Helvetica', '', 11)
        
        classifications = [
            ('Normal', prediction.get('normal_score', 0) * 100, (39, 174, 96)),
            ('Anxiety', prediction.get('anxiety_score', 0) * 100, (255, 140, 66)),
            ('Depression', prediction.get('depression_score', 0) * 100, (139, 90, 150)),
            ('Stress', prediction.get('stress_score', 0) * 100, (123, 179, 168)),
        ]
        
        for name, score, color in classifications:
            pdf.set_text_color(60, 60, 60)
            pdf.cell(40, 8, f'{name}:', 0, 0)
            # Progress bar
            pdf.set_fill_color(*color)
            bar_width = score * 1.2  # Scale to fit
            pdf.cell(bar_width, 8, '', 0, 0, 'L', True)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(120 - bar_width, 8, '', 0, 0, 'L', True)
            pdf.cell(30, 8, f'{score:.1f}%', 0, 1, 'R')
        
        pdf.ln(10)
        
        # Clinical Scale Mappings
        self._add_section_header(pdf, 'Clinical Scale Mappings (Golden Standards)')
        
        scales = [
            ('PHQ-9 (Depression)', prediction.get('phq9_score', 0), 27, prediction.get('phq9_severity', 'N/A')),
            ('GAD-7 (Anxiety)', prediction.get('gad7_score', 0), 21, prediction.get('gad7_severity', 'N/A')),
            ('PSS (Stress)', prediction.get('pss_score', 0), 40, prediction.get('pss_severity', 'N/A')),
            ('WEMWBS (Wellbeing)', prediction.get('wemwbs_score', 0), 70, prediction.get('wemwbs_severity', 'N/A')),
        ]
        
        for name, score, max_score, severity in scales:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(70, 8, name, 0, 0)
            pdf.set_font('Helvetica', '', 11)
            pdf.cell(30, 8, f'{score:.0f}/{max_score}', 0, 0, 'C')
            pdf.cell(90, 8, severity, 0, 1)
        
        pdf.ln(10)
        
        # Interpretations
        interpretations = prediction.get('interpretations', [])
        if interpretations:
            self._add_section_header(pdf, 'Clinical Interpretations')
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(60, 60, 60)
            for interp in interpretations:
                # Use bullet point (safe ASCII character)
                pdf.multi_cell(0, 7, f'- {interp}')
            pdf.ln(5)
        
        # Recommendations
        recommendations = prediction.get('recommendations', [])
        if recommendations:
            self._add_section_header(pdf, 'Recommendations')
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(60, 60, 60)
            for i, rec in enumerate(recommendations, 1):
                pdf.multi_cell(0, 7, f'{i}. {rec}')
            pdf.ln(5)
        
        # Disclaimer
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(128, 128, 128)
        pdf.multi_cell(0, 5, 
            'DISCLAIMER: This report is generated by an AI-powered voice analysis system and is intended '
            'for screening purposes only. It does not constitute a clinical diagnosis. Please consult a '
            'qualified mental health professional for proper evaluation and treatment recommendations. '
            'CITTAA Health Services Private Limited.'
        )
        
        # Output PDF as bytes
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin1')
        return bytes(pdf_bytes)
    
    def _add_section_header(self, pdf: FPDF, title: str):
        """Add a styled section header"""
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(139, 90, 150)
        pdf.cell(0, 10, title, 0, 1)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)


# Singleton instance
pdf_service = PDFReportService()
