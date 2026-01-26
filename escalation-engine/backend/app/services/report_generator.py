"""
PDF Report Generator for CITTAA Escalation Engine
Generates branded PDF reports with CITTAA styling
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class CITTAAReportGenerator:
    """
    Generate branded PDF reports for CITTAA Escalation Engine
    
    Supports:
    - Daily Activity Reports
    - Weekly Summary Reports
    - Monthly Metrics Reports
    - Escalation Case Reports
    """
    
    # CITTAA Brand Colors
    CITTAA_PURPLE = colors.HexColor('#8B5A96')
    CITTAA_TEAL = colors.HexColor('#7BB3A8')
    WARM_GRAY = colors.HexColor('#6B7280')
    DARK_TEXT = colors.HexColor('#1F2937')
    LIGHT_BG = colors.HexColor('#F9FAFB')
    
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Define CITTAA brand typography"""
        self.styles = getSampleStyleSheet()
        
        # Main title style (Open Sans Bold equivalent)
        self.title_style = ParagraphStyle(
            'CITTAATitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=self.CITTAA_PURPLE,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Header style
        self.header_style = ParagraphStyle(
            'CITTAAHeader',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=self.CITTAA_PURPLE,
            spaceAfter=12,
            spaceBefore=16
        )
        
        # Subheader style (Open Sans Semi-Bold)
        self.subheader_style = ParagraphStyle(
            'CITTAASubHeader',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.CITTAA_TEAL,
            spaceAfter=8,
            spaceBefore=12
        )
        
        # Body text style (Roboto Regular)
        self.body_style = ParagraphStyle(
            'CITTAABody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=self.DARK_TEXT,
            spaceAfter=8,
            leading=14
        )
        
        # Small text style
        self.small_style = ParagraphStyle(
            'CITTAASmall',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=self.WARM_GRAY,
            spaceAfter=4
        )
        
        # Footer style
        self.footer_style = ParagraphStyle(
            'CITTAAFooter',
            parent=self.styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=self.WARM_GRAY,
            alignment=TA_CENTER
        )
        
        # Alert styles for different escalation levels
        self.emergency_style = ParagraphStyle(
            'Emergency',
            parent=self.body_style,
            textColor=colors.HexColor('#DC2626'),
            fontName='Helvetica-Bold'
        )
        
        self.high_risk_style = ParagraphStyle(
            'HighRisk',
            parent=self.body_style,
            textColor=colors.HexColor('#EA580C'),
            fontName='Helvetica-Bold'
        )
    
    def _create_header(self, title: str, subtitle: Optional[str] = None) -> List:
        """Create report header with CITTAA branding"""
        elements = []
        
        # Company name
        elements.append(Paragraph(
            "CITTAA HEALTH SERVICES",
            ParagraphStyle(
                'CompanyName',
                parent=self.styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=self.CITTAA_PURPLE,
                alignment=TA_CENTER
            )
        ))
        
        # Tagline
        elements.append(Paragraph(
            "Bridging Mental Health Gaps Through Intelligent Wellness Solutions",
            ParagraphStyle(
                'Tagline',
                parent=self.styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=9,
                textColor=self.WARM_GRAY,
                alignment=TA_CENTER,
                spaceAfter=20
            )
        ))
        
        # Main title
        elements.append(Paragraph(title, self.title_style))
        
        if subtitle:
            elements.append(Paragraph(subtitle, self.subheader_style))
        
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _create_footer_text(self) -> str:
        """Create footer text"""
        return f"""
        <br/><br/>
        <b>CITTAA HEALTH SERVICES PRIVATE LIMITED</b><br/>
        Professional Mental Health Services for Schools and Hospitals in India<br/>
        <b>www.cittaa.in</b> | info@cittaa.in<br/>
        <br/>
        &copy; {datetime.now().year} Cittaa Health Services Private Limited. All rights reserved.
        """
    
    def _create_table(self, data: List[List], col_widths: Optional[List] = None) -> Table:
        """Create a styled table"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.CITTAA_TEAL),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, self.WARM_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.LIGHT_BG]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return table
    
    def generate_daily_report(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate branded Daily Activity Report PDF
        
        Sections:
        1. Sessions Conducted
        2. Assessments
        3. Consultations
        4. Crisis Interventions
        5. Curriculum Implementation
        6. Referrals
        7. Documentation Completed
        8. Priorities for Tomorrow
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )
        
        story = []
        
        # Header
        story.extend(self._create_header("DAILY ACTIVITY REPORT"))
        
        # Report metadata
        metadata = f"""
        <b>Date:</b> {report_data.get('report_date', 'N/A')}<br/>
        <b>Psychologist:</b> {report_data.get('psychologist_name', 'N/A')}<br/>
        <b>Institution:</b> {report_data.get('institution_name', 'N/A')}<br/>
        <b>Submitted:</b> {report_data.get('submitted_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}
        """
        story.append(Paragraph(metadata, self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 1: Sessions Conducted
        story.append(Paragraph("1. SESSIONS CONDUCTED", self.header_style))
        sessions = report_data.get('sessions_details', [])
        if sessions:
            session_data = [['Session Type', 'Student Code', 'Grade', 'Duration', 'Focus Area', 'Risk Level']]
            for s in sessions:
                session_data.append([
                    s.get('session_type', ''),
                    s.get('student_code', ''),
                    s.get('grade', ''),
                    f"{s.get('duration', 0)} min",
                    s.get('focus_area', ''),
                    s.get('risk_level', 'low')
                ])
            story.append(self._create_table(session_data, [1.2*inch, 1*inch, 0.6*inch, 0.7*inch, 1.5*inch, 0.8*inch]))
        else:
            story.append(Paragraph("No sessions conducted today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 2: Assessments
        story.append(Paragraph("2. ASSESSMENTS", self.header_style))
        assessments = report_data.get('assessments', [])
        if assessments:
            assess_data = [['Assessment Type', 'Student Code', 'Grade', 'Status', 'Notes']]
            for a in assessments:
                assess_data.append([
                    a.get('assessment_type', ''),
                    a.get('student_code', ''),
                    a.get('grade', ''),
                    a.get('status', ''),
                    a.get('notes', '')[:50] if a.get('notes') else ''
                ])
            story.append(self._create_table(assess_data, [1.3*inch, 1*inch, 0.6*inch, 1*inch, 2*inch]))
        else:
            story.append(Paragraph("No assessments conducted today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 3: Consultations
        story.append(Paragraph("3. CONSULTATIONS", self.header_style))
        consultations = report_data.get('consultations', [])
        if consultations:
            consult_data = [['Type', 'With', 'Regarding', 'Duration', 'Follow-up']]
            for c in consultations:
                consult_data.append([
                    c.get('consultation_type', ''),
                    c.get('with_person', ''),
                    c.get('regarding', '')[:30] if c.get('regarding') else '',
                    f"{c.get('duration', 0)} min",
                    'Yes' if c.get('follow_up_needed') else 'No'
                ])
            story.append(self._create_table(consult_data, [1*inch, 1.2*inch, 2*inch, 0.8*inch, 0.8*inch]))
        else:
            story.append(Paragraph("No consultations today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 4: Crisis Interventions
        story.append(Paragraph("4. CRISIS INTERVENTIONS", self.header_style))
        crisis = report_data.get('crisis_interventions', [])
        if crisis:
            crisis_data = [['Student Code', 'Grade', 'Nature of Crisis', 'Action Taken', 'Parent Notified']]
            for cr in crisis:
                crisis_data.append([
                    cr.get('student_code', ''),
                    cr.get('grade', ''),
                    cr.get('nature_of_crisis', '')[:30] if cr.get('nature_of_crisis') else '',
                    cr.get('action_taken', '')[:30] if cr.get('action_taken') else '',
                    'Yes' if cr.get('parent_notified') else 'No'
                ])
            story.append(self._create_table(crisis_data, [1*inch, 0.6*inch, 1.8*inch, 1.8*inch, 0.8*inch]))
        else:
            story.append(Paragraph("No crisis interventions today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 5: Curriculum Implementation
        story.append(Paragraph("5. CURRICULUM IMPLEMENTATION", self.header_style))
        curriculum = report_data.get('curriculum_activities', [])
        if curriculum:
            curr_data = [['Activity', 'Grade/Class', 'Topic', 'Engagement (1-5)']]
            for cu in curriculum:
                curr_data.append([
                    cu.get('activity', ''),
                    cu.get('grade_class', ''),
                    cu.get('topic', '')[:30] if cu.get('topic') else '',
                    str(cu.get('student_engagement', ''))
                ])
            story.append(self._create_table(curr_data, [1.5*inch, 1*inch, 2.5*inch, 1*inch]))
        else:
            story.append(Paragraph("No curriculum activities today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 6: Referrals
        story.append(Paragraph("6. REFERRALS", self.header_style))
        referrals = report_data.get('referrals', [])
        if referrals:
            ref_data = [['Student Code', 'Grade', 'Reason', 'Referred To', 'Status']]
            for r in referrals:
                ref_data.append([
                    r.get('student_code', ''),
                    r.get('grade', ''),
                    r.get('reason', '')[:25] if r.get('reason') else '',
                    r.get('referred_to', ''),
                    r.get('status', '')
                ])
            story.append(self._create_table(ref_data, [1*inch, 0.6*inch, 1.8*inch, 1.5*inch, 1*inch]))
        else:
            story.append(Paragraph("No referrals made today.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 7: Documentation Completed
        story.append(Paragraph("7. DOCUMENTATION COMPLETED", self.header_style))
        docs = report_data.get('documentation_completed', {})
        doc_items = []
        if docs.get('session_notes'):
            doc_items.append("Session notes")
        if docs.get('assessment_reports'):
            doc_items.append("Assessment reports")
        if docs.get('treatment_plans'):
            doc_items.append("Treatment plans")
        if docs.get('progress_reports'):
            doc_items.append("Progress reports")
        if docs.get('other'):
            doc_items.append(f"Other: {docs.get('other')}")
        
        if doc_items:
            story.append(Paragraph(", ".join(doc_items), self.body_style))
        else:
            story.append(Paragraph("No documentation completed.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 8: Priorities for Tomorrow
        story.append(Paragraph("8. PRIORITIES FOR TOMORROW", self.header_style))
        priorities = report_data.get('priorities_for_tomorrow', [])
        if priorities:
            for i, p in enumerate(priorities, 1):
                story.append(Paragraph(f"{i}. {p}", self.body_style))
        else:
            story.append(Paragraph("No priorities listed.", self.body_style))
        
        # Key Highlights
        if report_data.get('key_highlights'):
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("KEY HIGHLIGHTS", self.header_style))
            story.append(Paragraph(report_data['key_highlights'], self.body_style))
        
        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(self._create_footer_text(), self.footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_weekly_report(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate branded Weekly Summary Report PDF
        
        Sections:
        1. Service Delivery Statistics
        2. Group Interventions Summary
        3. Mental Health Curriculum Implementation
        4. Cases of Concern
        5. Teacher Support & Collaboration
        6. Parent Engagement
        7. Assessments Status
        8. Program Implementation Metrics
        9. Resource Utilization
        10. Successes & Challenges
        11. Professional Development
        12. Goals for Next Week
        13. Support Needed
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch
        )
        
        story = []
        
        # Header
        week_range = f"{report_data.get('week_start_date', '')} to {report_data.get('week_end_date', '')}"
        story.extend(self._create_header("WEEKLY SUMMARY REPORT", f"Week of: {week_range}"))
        
        # Report metadata
        metadata = f"""
        <b>Psychologist:</b> {report_data.get('psychologist_name', 'N/A')}<br/>
        <b>Institution:</b> {report_data.get('institution_name', 'N/A')}
        """
        story.append(Paragraph(metadata, self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 1: Service Delivery Statistics
        story.append(Paragraph("1. SERVICE DELIVERY STATISTICS", self.header_style))
        stats = report_data.get('service_delivery_stats', [])
        if stats:
            stats_data = [['Service Type', 'Sessions', 'Students', 'Hours']]
            for s in stats:
                stats_data.append([
                    s.get('service_type', ''),
                    str(s.get('number_of_sessions', 0)),
                    str(s.get('number_of_students', 0)),
                    f"{s.get('total_hours', 0):.1f}"
                ])
            story.append(self._create_table(stats_data, [2.5*inch, 1*inch, 1*inch, 1*inch]))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 2: Group Interventions Summary
        story.append(Paragraph("2. GROUP INTERVENTIONS SUMMARY", self.header_style))
        groups = report_data.get('group_interventions', [])
        if groups:
            group_data = [['Group Name', 'Grade(s)', 'Students', 'Sessions', 'Topics']]
            for g in groups:
                group_data.append([
                    g.get('group_name', ''),
                    g.get('grades', ''),
                    str(g.get('num_students', 0)),
                    str(g.get('sessions_this_week', 0)),
                    g.get('topics_covered', '')[:30] if g.get('topics_covered') else ''
                ])
            story.append(self._create_table(group_data, [1.3*inch, 0.8*inch, 0.8*inch, 0.8*inch, 2*inch]))
        else:
            story.append(Paragraph("No group interventions this week.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 3: Curriculum Implementation
        story.append(Paragraph("3. MENTAL HEALTH CURRICULUM IMPLEMENTATION", self.header_style))
        curriculum = report_data.get('curriculum_implementation', [])
        if curriculum:
            curr_data = [['Grade', 'Components', 'Completion %', 'Successes', 'Challenges']]
            for c in curriculum:
                curr_data.append([
                    c.get('grade', ''),
                    c.get('components_delivered', '')[:20] if c.get('components_delivered') else '',
                    f"{c.get('completion_percentage', 0)}%",
                    c.get('successes', '')[:20] if c.get('successes') else '',
                    c.get('challenges', '')[:20] if c.get('challenges') else ''
                ])
            story.append(self._create_table(curr_data, [0.8*inch, 1.5*inch, 1*inch, 1.3*inch, 1.3*inch]))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 4: Cases of Concern
        story.append(Paragraph("4. CASES OF CONCERN", self.header_style))
        cases = report_data.get('cases_of_concern', [])
        if cases:
            case_data = [['Student (Initials)', 'Grade', 'Concern', 'Status', 'Plan']]
            for c in cases:
                case_data.append([
                    c.get('student_initials', ''),
                    c.get('grade', ''),
                    c.get('nature_of_concern', '')[:25] if c.get('nature_of_concern') else '',
                    c.get('current_status', ''),
                    c.get('plan', '')[:25] if c.get('plan') else ''
                ])
            story.append(self._create_table(case_data, [1*inch, 0.6*inch, 1.8*inch, 1*inch, 1.5*inch]))
        else:
            story.append(Paragraph("No cases of concern this week.", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 5: Teacher Support
        story.append(Paragraph("5. TEACHER SUPPORT & COLLABORATION", self.header_style))
        teachers = report_data.get('teacher_support', [])
        if teachers:
            teacher_data = [['Teacher/Grade', 'Support Provided', 'Outcomes', 'Follow-up']]
            for t in teachers:
                teacher_data.append([
                    t.get('teacher_grade', ''),
                    t.get('support_provided', '')[:30] if t.get('support_provided') else '',
                    t.get('outcomes', '')[:25] if t.get('outcomes') else '',
                    'Yes' if t.get('follow_up_needed') else 'No'
                ])
            story.append(self._create_table(teacher_data, [1.2*inch, 2*inch, 1.8*inch, 0.8*inch]))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 6: Parent Engagement
        story.append(Paragraph("6. PARENT ENGAGEMENT", self.header_style))
        parents = report_data.get('parent_engagement', [])
        if parents:
            parent_data = [['Type', 'Number', 'Themes/Topics', 'Success (1-5)']]
            for p in parents:
                parent_data.append([
                    p.get('engagement_type', ''),
                    str(p.get('number', 0)),
                    p.get('themes_topics', '')[:30] if p.get('themes_topics') else '',
                    str(p.get('success_level', ''))
                ])
            story.append(self._create_table(parent_data, [1.5*inch, 0.8*inch, 2.5*inch, 1*inch]))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 7: Assessments Status
        story.append(Paragraph("7. ASSESSMENTS STATUS", self.header_style))
        assessments = report_data.get('assessments_status', [])
        if assessments:
            assess_data = [['Assessment Type', 'Initiated', 'In Progress', 'Completed']]
            for a in assessments:
                assess_data.append([
                    a.get('assessment_type', ''),
                    str(a.get('number_initiated', 0)),
                    str(a.get('number_in_progress', 0)),
                    str(a.get('number_completed', 0))
                ])
            story.append(self._create_table(assess_data, [2*inch, 1.2*inch, 1.2*inch, 1.2*inch]))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 10: Successes & Challenges
        story.append(Paragraph("8. SUCCESSES & CHALLENGES", self.header_style))
        
        successes = report_data.get('successes_this_week', [])
        if successes:
            story.append(Paragraph("<b>Successes This Week:</b>", self.body_style))
            for i, s in enumerate(successes, 1):
                story.append(Paragraph(f"{i}. {s}", self.body_style))
        
        challenges = report_data.get('challenges_this_week', [])
        if challenges:
            story.append(Paragraph("<b>Challenges This Week:</b>", self.body_style))
            for i, c in enumerate(challenges, 1):
                story.append(Paragraph(f"{i}. {c}", self.body_style))
        
        solutions = report_data.get('solutions_approaches', [])
        if solutions:
            story.append(Paragraph("<b>Solutions/Approaches:</b>", self.body_style))
            for i, sol in enumerate(solutions, 1):
                story.append(Paragraph(f"{i}. {sol}", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 12: Goals for Next Week
        story.append(Paragraph("9. GOALS FOR NEXT WEEK", self.header_style))
        goals = report_data.get('goals_for_next_week', [])
        if goals:
            for i, g in enumerate(goals, 1):
                story.append(Paragraph(f"{i}. {g}", self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Section 13: Support Needed
        story.append(Paragraph("10. SUPPORT NEEDED", self.header_style))
        support = report_data.get('support_needed', [])
        if support:
            for i, s in enumerate(support, 1):
                story.append(Paragraph(f"{i}. {s}", self.body_style))
        
        # Signature section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("_" * 50, self.body_style))
        story.append(Paragraph("School Psychologist Signature", self.small_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("_" * 50, self.body_style))
        story.append(Paragraph("Principal's Review", self.small_style))
        
        # Footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(self._create_footer_text(), self.footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_monthly_report(self, report_data: Dict[str, Any]) -> bytes:
        """Generate branded Monthly Metrics Tracking Report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch
        )
        
        story = []
        
        # Header
        month_str = report_data.get('report_month', '')
        story.extend(self._create_header("MONTHLY METRICS TRACKING", f"Report Month: {month_str}"))
        
        # Metadata
        metadata = f"""
        <b>Psychologist:</b> {report_data.get('psychologist_name', 'N/A')}<br/>
        <b>Institution:</b> {report_data.get('institution_name', 'N/A')}
        """
        story.append(Paragraph(metadata, self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Executive Summary
        if report_data.get('executive_summary'):
            story.append(Paragraph("EXECUTIVE SUMMARY", self.header_style))
            story.append(Paragraph(report_data['executive_summary'], self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Metrics Table
        story.append(Paragraph("MONTHLY METRICS", self.header_style))
        
        # Service Delivery Metrics
        service_metrics = report_data.get('service_delivery_metrics', [])
        if service_metrics:
            story.append(Paragraph("Service Delivery", self.subheader_style))
            metrics_data = [['Metric', 'Target', 'Previous', 'Current', 'Trend']]
            for m in service_metrics:
                metrics_data.append([
                    m.get('metric_name', ''),
                    str(m.get('target', '-')),
                    str(m.get('previous_month', '-')),
                    str(m.get('current_month', '-')),
                    m.get('trend', '-')
                ])
            story.append(self._create_table(metrics_data, [2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch]))
            story.append(Spacer(1, 0.1 * inch))
        
        # Implementation Metrics
        impl_metrics = report_data.get('implementation_metrics', [])
        if impl_metrics:
            story.append(Paragraph("Implementation", self.subheader_style))
            metrics_data = [['Metric', 'Target', 'Previous', 'Current', 'Trend']]
            for m in impl_metrics:
                metrics_data.append([
                    m.get('metric_name', ''),
                    str(m.get('target', '-')),
                    str(m.get('previous_month', '-')),
                    str(m.get('current_month', '-')),
                    m.get('trend', '-')
                ])
            story.append(self._create_table(metrics_data, [2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch]))
            story.append(Spacer(1, 0.1 * inch))
        
        # Outcome Metrics
        outcome_metrics = report_data.get('outcome_metrics', [])
        if outcome_metrics:
            story.append(Paragraph("Outcomes", self.subheader_style))
            metrics_data = [['Metric', 'Target', 'Previous', 'Current', 'Trend']]
            for m in outcome_metrics:
                metrics_data.append([
                    m.get('metric_name', ''),
                    str(m.get('target', '-')),
                    str(m.get('previous_month', '-')),
                    str(m.get('current_month', '-')),
                    m.get('trend', '-')
                ])
            story.append(self._create_table(metrics_data, [2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch]))
            story.append(Spacer(1, 0.15 * inch))
        
        # Clinical Outcomes
        if report_data.get('clinical_outcomes'):
            story.append(Paragraph("CLINICAL OUTCOMES", self.header_style))
            outcomes = report_data['clinical_outcomes']
            if isinstance(outcomes, dict):
                for key, value in outcomes.items():
                    story.append(Paragraph(f"<b>{key}:</b> {value}", self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Institutional Impact
        if report_data.get('institutional_impact'):
            story.append(Paragraph("INSTITUTIONAL IMPACT", self.header_style))
            story.append(Paragraph(report_data['institutional_impact'], self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Recommendations
        if report_data.get('recommendations'):
            story.append(Paragraph("RECOMMENDATIONS", self.header_style))
            story.append(Paragraph(report_data['recommendations'], self.body_style))
        
        # Signature section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("_" * 50, self.body_style))
        story.append(Paragraph("School Psychologist Signature                    Date: ___________", self.small_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("_" * 50, self.body_style))
        story.append(Paragraph("Principal's Review                               Date: ___________", self.small_style))
        
        # Footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(self._create_footer_text(), self.footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_escalation_report(self, case_data: Dict[str, Any]) -> bytes:
        """Generate branded Escalation Case Report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )
        
        story = []
        
        # Determine alert level styling
        level = case_data.get('escalation_level', 'level_1_low')
        if level == 'level_4_emergency':
            alert_color = colors.HexColor('#DC2626')
            alert_text = "EMERGENCY - IMMEDIATE ACTION REQUIRED"
        elif level == 'level_3_high':
            alert_color = colors.HexColor('#EA580C')
            alert_text = "HIGH RISK - ACTION NEEDED WITHIN 24 HOURS"
        elif level == 'level_2_moderate':
            alert_color = colors.HexColor('#CA8A04')
            alert_text = "MODERATE CONCERN - INCREASED MONITORING"
        else:
            alert_color = self.CITTAA_TEAL
            alert_text = "LOW RISK - STANDARD FOLLOW-UP"
        
        # Header
        story.extend(self._create_header("ESCALATION CASE REPORT"))
        
        # Alert banner
        alert_style = ParagraphStyle(
            'Alert',
            parent=self.body_style,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=TA_CENTER
        )
        
        alert_table = Table([[Paragraph(alert_text, alert_style)]], colWidths=[6*inch])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), alert_color),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(alert_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Case details
        details = f"""
        <b>Case ID:</b> {case_data.get('case_id', 'N/A')}<br/>
        <b>Date:</b> {case_data.get('escalated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}<br/>
        <b>Student Code:</b> {case_data.get('student_code', 'N/A')}<br/>
        <b>Institution:</b> {case_data.get('institution_name', 'N/A')}<br/>
        <b>Psychologist:</b> {case_data.get('psychologist_name', 'N/A')}<br/>
        <b>Risk Category:</b> {case_data.get('risk_category', 'N/A')}<br/>
        <b>AI Confidence:</b> {case_data.get('ai_confidence_score', 0):.1%}
        """
        story.append(Paragraph(details, self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Situation
        story.append(Paragraph("SITUATION", self.header_style))
        story.append(Paragraph(case_data.get('escalation_reason', 'No details provided.'), self.body_style))
        story.append(Spacer(1, 0.15 * inch))
        
        # Keywords Detected
        keywords = case_data.get('keywords_detected', [])
        if keywords:
            story.append(Paragraph("RISK INDICATORS DETECTED", self.header_style))
            story.append(Paragraph(", ".join(keywords), self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Immediate Actions Taken
        if case_data.get('immediate_actions_taken'):
            story.append(Paragraph("IMMEDIATE ACTIONS TAKEN", self.header_style))
            story.append(Paragraph(case_data['immediate_actions_taken'], self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Recommended Actions
        actions = case_data.get('recommended_actions', [])
        if actions:
            story.append(Paragraph("RECOMMENDED ACTIONS", self.header_style))
            for i, action in enumerate(actions, 1):
                story.append(Paragraph(f"{i}. {action}", self.body_style))
            story.append(Spacer(1, 0.15 * inch))
        
        # Contact Information
        story.append(Paragraph("CONTACT INFORMATION", self.header_style))
        contact = f"""
        <b>Psychologist:</b> {case_data.get('psychologist_name', 'N/A')}<br/>
        <b>Phone:</b> {case_data.get('psychologist_phone', 'N/A')}<br/>
        <b>Email:</b> {case_data.get('psychologist_email', 'N/A')}<br/>
        <br/>
        <b>24/7 CITTAA Crisis Hotline:</b> +91-XXX-XXX-XXXX<br/>
        <b>CITTAA Support:</b> support@cittaa.in
        """
        story.append(Paragraph(contact, self.body_style))
        
        # Footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(
            "This is an automated escalation report generated by CITTAA's AI-powered monitoring system.",
            self.small_style
        ))
        story.append(Paragraph(self._create_footer_text(), self.footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Singleton instance
report_generator = CITTAAReportGenerator()
