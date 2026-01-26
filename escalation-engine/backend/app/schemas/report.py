"""
Report schemas for CITTAA Escalation Engine
Daily, Weekly, and Monthly report formats
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime

from app.schemas.session import (
    SessionDetail, AssessmentDetail, ConsultationDetail,
    CrisisInterventionDetail, CurriculumImplementationDetail, ReferralDetail
)


# ============== DAILY ACTIVITY REPORT ==============

class DocumentationCompleted(BaseModel):
    """Schema for documentation completed section"""
    session_notes: bool = False
    assessment_reports: bool = False
    treatment_plans: bool = False
    progress_reports: bool = False
    other: Optional[str] = None


class DailyReportCreate(BaseModel):
    """
    Schema for creating a Daily Activity Report
    
    This comprehensive daily report captures all psychologist activities including:
    - Sessions conducted (individual, group, family, crisis)
    - Assessments initiated/in progress/completed
    - Teacher, parent, and admin consultations
    - Crisis interventions with action plans
    - Curriculum implementation activities
    - Referrals made
    - Documentation status
    - Priorities for next day
    """
    institution_id: UUID
    report_date: date
    
    # Section 1: Sessions Conducted
    sessions_details: List[SessionDetail] = []
    
    # Section 2: Assessments
    assessments: List[AssessmentDetail] = []
    
    # Section 3: Consultations
    consultations: List[ConsultationDetail] = []
    
    # Section 4: Crisis Interventions
    crisis_interventions: List[CrisisInterventionDetail] = []
    
    # Section 5: Curriculum Implementation
    curriculum_activities: List[CurriculumImplementationDetail] = []
    
    # Section 6: Referrals
    referrals: List[ReferralDetail] = []
    
    # Section 7: Documentation Completed
    documentation_completed: Optional[DocumentationCompleted] = None
    
    # Section 8: Priorities for Tomorrow
    priorities_for_tomorrow: List[str] = []
    
    # Summary metrics (auto-calculated)
    sessions_conducted: Optional[int] = None
    new_referrals: Optional[int] = None
    follow_ups_completed: Optional[int] = None
    
    # Additional notes
    key_highlights: Optional[str] = None
    notes_and_observations: Optional[str] = None


class DailyReportResponse(BaseModel):
    """Schema for daily report response"""
    report_id: UUID
    psychologist_id: UUID
    institution_id: UUID
    report_date: date
    sessions_conducted: int
    crisis_interventions: int
    new_referrals: int
    follow_ups_completed: int
    report_content: Optional[Dict[str, Any]] = None
    key_highlights: Optional[str] = None
    notes_and_observations: Optional[str] = None
    submitted_at: Optional[datetime] = None
    status: str
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== WEEKLY SUMMARY REPORT ==============

class ServiceDeliveryStats(BaseModel):
    """Schema for service delivery statistics"""
    service_type: str
    number_of_sessions: int = 0
    number_of_students: int = 0
    total_hours: float = 0.0


class GroupInterventionSummary(BaseModel):
    """Schema for group intervention summary"""
    group_name: str
    grades: str
    num_students: int
    sessions_this_week: int
    topics_covered: str
    progress_notes: Optional[str] = None


class CurriculumImplementationSummary(BaseModel):
    """Schema for curriculum implementation summary"""
    grade: str
    components_delivered: str
    completion_percentage: int
    successes: Optional[str] = None
    challenges: Optional[str] = None
    adaptations_made: Optional[str] = None


class CaseOfConcern(BaseModel):
    """Schema for cases of concern (initials only for privacy)"""
    student_initials: str
    grade: str
    nature_of_concern: str
    current_status: str
    plan: str
    team_members_involved: Optional[str] = None


class TeacherSupport(BaseModel):
    """Schema for teacher support and collaboration"""
    teacher_grade: str
    support_provided: str
    outcomes: Optional[str] = None
    follow_up_needed: bool = False


class ParentEngagement(BaseModel):
    """Schema for parent engagement"""
    engagement_type: str  # 'Individual Meetings', 'Phone Consultations', 'Workshops/Training', 'Written Communications'
    number: int
    themes_topics: Optional[str] = None
    success_level: int  # 1-5
    notes: Optional[str] = None


class AssessmentStatus(BaseModel):
    """Schema for assessment status"""
    assessment_type: str
    number_initiated: int = 0
    number_in_progress: int = 0
    number_completed: int = 0


class ProgramImplementationMetrics(BaseModel):
    """Schema for program implementation metrics"""
    universal_tier: Dict[str, str] = {}  # SEL Lessons, Classroom Support, Teacher Training
    selective_tier: Dict[str, str] = {}  # Small Groups, Targeted Interventions, Parent Workshops
    intensive_tier: Dict[str, str] = {}  # Individual Plans, Crisis Response, External Referrals


class ResourceUtilization(BaseModel):
    """Schema for resource utilization"""
    resource: str
    usage: str
    effectiveness: int  # 1-5
    needs: Optional[str] = None


class ProfessionalDevelopment(BaseModel):
    """Schema for professional development"""
    activity: str
    date: date
    hours: float
    key_learnings: Optional[str] = None
    application_plan: Optional[str] = None


class WeeklyReportCreate(BaseModel):
    """
    Schema for creating a Weekly Summary Report
    
    Comprehensive weekly report including:
    - Service delivery statistics
    - Group interventions summary
    - Mental health curriculum implementation
    - Cases of concern
    - Teacher support & collaboration
    - Parent engagement
    - Assessment status
    - Program implementation metrics
    - Resource utilization
    - Successes & challenges
    - Professional development
    - Goals for next week
    - Support needed
    """
    institution_id: UUID
    week_start_date: date
    week_end_date: date
    
    # Section 1: Service Delivery Statistics
    service_delivery_stats: List[ServiceDeliveryStats] = []
    
    # Section 2: Group Interventions Summary
    group_interventions: List[GroupInterventionSummary] = []
    
    # Section 3: Mental Health Curriculum Implementation
    curriculum_implementation: List[CurriculumImplementationSummary] = []
    
    # Section 4: Cases of Concern
    cases_of_concern: List[CaseOfConcern] = []
    
    # Section 5: Teacher Support & Collaboration
    teacher_support: List[TeacherSupport] = []
    
    # Section 6: Parent Engagement
    parent_engagement: List[ParentEngagement] = []
    
    # Section 7: Assessments Status
    assessments_status: List[AssessmentStatus] = []
    
    # Section 8: Program Implementation Metrics
    program_metrics: Optional[ProgramImplementationMetrics] = None
    
    # Section 9: Resource Utilization
    resource_utilization: List[ResourceUtilization] = []
    
    # Section 10: Successes & Challenges
    successes_this_week: List[str] = []
    challenges_this_week: List[str] = []
    solutions_approaches: List[str] = []
    
    # Section 11: Professional Development
    professional_development: List[ProfessionalDevelopment] = []
    
    # Section 12: Goals for Next Week
    goals_for_next_week: List[str] = []
    
    # Section 13: Support Needed
    support_needed: List[str] = []
    
    # Summary metrics
    total_sessions: Optional[int] = None
    total_students: Optional[int] = None
    new_intakes: Optional[int] = None
    no_shows: Optional[int] = None
    
    # Additional fields
    summary: Optional[str] = None
    challenges: Optional[str] = None
    recommendations: Optional[str] = None


class WeeklyReportResponse(BaseModel):
    """Schema for weekly report response"""
    report_id: UUID
    psychologist_id: UUID
    institution_id: UUID
    week_start_date: date
    week_end_date: date
    total_sessions: int
    total_students: int
    new_intakes: int
    no_shows: int
    report_content: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    challenges: Optional[str] = None
    recommendations: Optional[str] = None
    submitted_at: Optional[datetime] = None
    status: str
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== MONTHLY METRICS TRACKING ==============

class MonthlyMetric(BaseModel):
    """Schema for individual monthly metric"""
    metric_name: str
    target: Optional[float] = None
    previous_month: Optional[float] = None
    current_month: Optional[float] = None
    trend: Optional[str] = None  # 'up', 'down', 'stable'


class MonthlyReportCreate(BaseModel):
    """
    Schema for creating a Monthly Metrics Tracking Report
    
    Comprehensive monthly report including:
    - Service delivery metrics (individual sessions, group sessions, students served)
    - Implementation metrics (curriculum components, teacher training, parent engagement)
    - Outcome metrics (behavior improvement, discipline referrals, crisis interventions)
    - Feedback metrics (teachers, parents, students)
    - Executive summary
    - Clinical outcomes
    - Institutional impact
    - Recommendations
    """
    institution_id: UUID
    report_month: date  # First day of month
    
    # Service Delivery Metrics
    service_delivery_metrics: List[MonthlyMetric] = []
    
    # Implementation Metrics
    implementation_metrics: List[MonthlyMetric] = []
    
    # Outcome Metrics
    outcome_metrics: List[MonthlyMetric] = []
    
    # Quantitative Metrics (detailed breakdown)
    quantitative_metrics: Optional[Dict[str, Any]] = None
    
    # Clinical Outcomes
    clinical_outcomes: Optional[Dict[str, Any]] = None
    
    # Executive Summary
    executive_summary: Optional[str] = None
    
    # Institutional Impact
    institutional_impact: Optional[str] = None
    
    # Recommendations
    recommendations: Optional[str] = None


class MonthlyReportResponse(BaseModel):
    """Schema for monthly report response"""
    report_id: UUID
    psychologist_id: UUID
    institution_id: UUID
    report_month: date
    executive_summary: Optional[str] = None
    quantitative_metrics: Optional[Dict[str, Any]] = None
    clinical_outcomes: Optional[Dict[str, Any]] = None
    institutional_impact: Optional[str] = None
    recommendations: Optional[str] = None
    report_content: Optional[Dict[str, Any]] = None
    submitted_at: Optional[datetime] = None
    status: str
    quality_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
