"""
Email Service for CITTAA Escalation Engine
SendGrid integration for escalation notifications
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import sendgrid, but allow graceful fallback
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (
        Mail, Email, To, Content, Attachment, FileContent,
        FileName, FileType, Disposition
    )
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not available. Email functionality will be limited.")

import base64


class EscalationEmailService:
    """
    Email service for sending escalation notifications
    
    Features:
    - Different templates for each escalation level
    - PDF attachment support
    - Multi-recipient support
    - Delivery tracking
    """
    
    # CITTAA Brand Colors for HTML emails
    CITTAA_PURPLE = "#8B5A96"
    CITTAA_TEAL = "#7BB3A8"
    WARM_GRAY = "#6B7280"
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "escalations@cittaa.in")
        self.client = None
        
        if SENDGRID_AVAILABLE and self.api_key:
            self.client = SendGridAPIClient(self.api_key)
    
    def _get_escalation_color(self, level: str) -> str:
        """Get color for escalation level"""
        colors = {
            "level_4_emergency": "#DC2626",  # Red
            "level_3_high": "#EA580C",       # Orange
            "level_2_moderate": "#CA8A04",   # Yellow
            "level_1_low": "#059669"         # Green
        }
        return colors.get(level, self.CITTAA_TEAL)
    
    def _get_escalation_title(self, level: str) -> str:
        """Get title for escalation level"""
        titles = {
            "level_4_emergency": "EMERGENCY ESCALATION - IMMEDIATE ACTION REQUIRED",
            "level_3_high": "HIGH RISK ESCALATION - ACTION NEEDED WITHIN 24 HOURS",
            "level_2_moderate": "MODERATE CONCERN - INCREASED MONITORING RECOMMENDED",
            "level_1_low": "LOW RISK NOTIFICATION - STANDARD FOLLOW-UP"
        }
        return titles.get(level, "ESCALATION NOTIFICATION")
    
    def _build_email_template(self, case_data: Dict[str, Any]) -> str:
        """Build HTML email template with CITTAA branding"""
        level = case_data.get("escalation_level", "level_1_low")
        level_color = self._get_escalation_color(level)
        level_title = self._get_escalation_title(level)
        
        # Format keywords
        keywords = case_data.get("keywords_detected", [])
        keywords_html = ", ".join(keywords) if keywords else "None detected"
        
        # Format recommended actions
        actions = case_data.get("recommended_actions", [])
        actions_html = ""
        for i, action in enumerate(actions, 1):
            actions_html += f"<li>{action}</li>"
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CITTAA Escalation Alert</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; background-color: #F9FAFB;">
            <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF;">
                <!-- Header -->
                <tr>
                    <td style="background-color: {self.CITTAA_PURPLE}; padding: 20px; text-align: center;">
                        <h1 style="color: #FFFFFF; margin: 0; font-size: 24px; font-family: 'Open Sans', Arial, sans-serif;">
                            CITTAA HEALTH SERVICES
                        </h1>
                        <p style="color: #E5E7EB; margin: 5px 0 0 0; font-size: 12px;">
                            Bridging Mental Health Gaps Through Intelligent Wellness Solutions
                        </p>
                    </td>
                </tr>
                
                <!-- Alert Banner -->
                <tr>
                    <td style="background-color: {level_color}; padding: 15px; text-align: center;">
                        <h2 style="color: #FFFFFF; margin: 0; font-size: 18px; font-weight: bold;">
                            {level_title}
                        </h2>
                    </td>
                </tr>
                
                <!-- Content -->
                <tr>
                    <td style="padding: 30px;">
                        <!-- Case Details -->
                        <table width="100%" style="margin-bottom: 20px;">
                            <tr>
                                <td style="padding: 10px; background-color: #F3F4F6; border-radius: 8px;">
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Case ID:</strong> {case_data.get('case_id', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Date/Time:</strong> {case_data.get('escalated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Student Code:</strong> {case_data.get('student_code', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Institution:</strong> {case_data.get('institution_name', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Psychologist:</strong> {case_data.get('psychologist_name', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>Risk Category:</strong> {case_data.get('risk_category', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; color: {self.WARM_GRAY}; font-size: 14px;">
                                        <strong>AI Confidence:</strong> {case_data.get('ai_confidence_score', 0):.1%}
                                    </p>
                                </td>
                            </tr>
                        </table>
                        
                        <!-- Situation -->
                        <h3 style="color: {self.CITTAA_PURPLE}; margin: 20px 0 10px 0; font-size: 16px;">
                            Situation
                        </h3>
                        <p style="color: #374151; font-size: 14px; line-height: 1.6;">
                            {case_data.get('escalation_reason', 'No details provided.')}
                        </p>
                        
                        <!-- Risk Indicators -->
                        <h3 style="color: {self.CITTAA_PURPLE}; margin: 20px 0 10px 0; font-size: 16px;">
                            Risk Indicators Detected
                        </h3>
                        <p style="color: {level_color}; font-size: 14px; font-weight: bold;">
                            {keywords_html}
                        </p>
                        
                        <!-- Recommended Actions -->
                        <h3 style="color: {self.CITTAA_PURPLE}; margin: 20px 0 10px 0; font-size: 16px;">
                            Recommended Actions
                        </h3>
                        <ol style="color: #374151; font-size: 14px; line-height: 1.8; padding-left: 20px;">
                            {actions_html}
                        </ol>
                        
                        <!-- Immediate Actions Taken -->
                        {f'''
                        <h3 style="color: {self.CITTAA_PURPLE}; margin: 20px 0 10px 0; font-size: 16px;">
                            Immediate Actions Taken
                        </h3>
                        <p style="color: #374151; font-size: 14px; line-height: 1.6;">
                            {case_data.get('immediate_actions_taken', 'None recorded.')}
                        </p>
                        ''' if case_data.get('immediate_actions_taken') else ''}
                        
                        <!-- Contact Information -->
                        <table width="100%" style="margin-top: 30px; background-color: {self.CITTAA_TEAL}; border-radius: 8px;">
                            <tr>
                                <td style="padding: 20px; color: #FFFFFF;">
                                    <h3 style="margin: 0 0 10px 0; font-size: 16px;">Contact Information</h3>
                                    <p style="margin: 5px 0; font-size: 14px;">
                                        <strong>Psychologist:</strong> {case_data.get('psychologist_name', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; font-size: 14px;">
                                        <strong>Phone:</strong> {case_data.get('psychologist_phone', 'N/A')}
                                    </p>
                                    <p style="margin: 5px 0; font-size: 14px;">
                                        <strong>Email:</strong> {case_data.get('psychologist_email', 'N/A')}
                                    </p>
                                    <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.3); margin: 15px 0;">
                                    <p style="margin: 5px 0; font-size: 14px;">
                                        <strong>24/7 CITTAA Crisis Hotline:</strong> +91-XXX-XXX-XXXX
                                    </p>
                                    <p style="margin: 5px 0; font-size: 14px;">
                                        <strong>CITTAA Support:</strong> support@cittaa.in
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <!-- Footer -->
                <tr>
                    <td style="background-color: #F3F4F6; padding: 20px; text-align: center;">
                        <p style="color: {self.WARM_GRAY}; font-size: 12px; margin: 0;">
                            This is an automated escalation notification from CITTAA's AI-powered monitoring system.
                        </p>
                        <p style="color: {self.WARM_GRAY}; font-size: 12px; margin: 10px 0 0 0;">
                            &copy; {datetime.now().year} Cittaa Health Services Private Limited. All rights reserved.
                        </p>
                        <p style="color: {self.WARM_GRAY}; font-size: 11px; margin: 10px 0 0 0;">
                            www.cittaa.in | info@cittaa.in
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return template
    
    def send_escalation_notification(
        self,
        case_data: Dict[str, Any],
        recipients: List[str],
        pdf_attachment: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Send escalation notification email
        
        Args:
            case_data: Escalation case details
            recipients: List of email addresses
            pdf_attachment: Optional PDF report bytes
            
        Returns:
            Dictionary with send status and details
        """
        if not self.client:
            logger.warning("SendGrid client not configured. Email not sent.")
            return {
                "success": False,
                "error": "SendGrid not configured",
                "recipients": recipients
            }
        
        level = case_data.get("escalation_level", "level_1_low")
        subject = f"[CITTAA] {self._get_escalation_title(level)}"
        
        # Build HTML content
        html_content = self._build_email_template(case_data)
        
        results = []
        
        for recipient in recipients:
            try:
                message = Mail(
                    from_email=Email(self.from_email, "CITTAA Escalation System"),
                    to_emails=To(recipient),
                    subject=subject,
                    html_content=Content("text/html", html_content)
                )
                
                # Add PDF attachment if provided
                if pdf_attachment:
                    encoded_pdf = base64.b64encode(pdf_attachment).decode()
                    attachment = Attachment(
                        FileContent(encoded_pdf),
                        FileName(f"escalation_report_{case_data.get('case_id', 'unknown')}.pdf"),
                        FileType("application/pdf"),
                        Disposition("attachment")
                    )
                    message.attachment = attachment
                
                response = self.client.send(message)
                
                results.append({
                    "recipient": recipient,
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code
                })
                
                logger.info(f"Escalation email sent to {recipient}: {response.status_code}")
                
            except Exception as e:
                logger.error(f"Failed to send email to {recipient}: {str(e)}")
                results.append({
                    "recipient": recipient,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "results": results,
            "total_sent": sum(1 for r in results if r["success"]),
            "total_failed": sum(1 for r in results if not r["success"])
        }
    
    def send_daily_report_notification(
        self,
        report_data: Dict[str, Any],
        recipients: List[str],
        pdf_attachment: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Send daily report notification email"""
        if not self.client:
            return {"success": False, "error": "SendGrid not configured"}
        
        subject = f"[CITTAA] Daily Activity Report - {report_data.get('report_date', 'N/A')}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CITTAA Daily Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #F9FAFB; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden;">
                <div style="background-color: {self.CITTAA_PURPLE}; padding: 20px; text-align: center;">
                    <h1 style="color: #FFFFFF; margin: 0;">CITTAA Daily Activity Report</h1>
                </div>
                <div style="padding: 30px;">
                    <p style="color: #374151; font-size: 14px;">
                        <strong>Date:</strong> {report_data.get('report_date', 'N/A')}<br>
                        <strong>Psychologist:</strong> {report_data.get('psychologist_name', 'N/A')}<br>
                        <strong>Institution:</strong> {report_data.get('institution_name', 'N/A')}
                    </p>
                    <h3 style="color: {self.CITTAA_PURPLE};">Summary</h3>
                    <ul style="color: #374151; font-size: 14px;">
                        <li>Sessions Conducted: {report_data.get('sessions_conducted', 0)}</li>
                        <li>Crisis Interventions: {report_data.get('crisis_interventions', 0)}</li>
                        <li>New Referrals: {report_data.get('new_referrals', 0)}</li>
                        <li>Follow-ups Completed: {report_data.get('follow_ups_completed', 0)}</li>
                    </ul>
                    <p style="color: #374151; font-size: 14px;">
                        Please find the detailed report attached.
                    </p>
                </div>
                <div style="background-color: #F3F4F6; padding: 15px; text-align: center;">
                    <p style="color: {self.WARM_GRAY}; font-size: 12px; margin: 0;">
                        &copy; {datetime.now().year} Cittaa Health Services Private Limited
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        results = []
        for recipient in recipients:
            try:
                message = Mail(
                    from_email=Email(self.from_email, "CITTAA Reports"),
                    to_emails=To(recipient),
                    subject=subject,
                    html_content=Content("text/html", html_content)
                )
                
                if pdf_attachment:
                    encoded_pdf = base64.b64encode(pdf_attachment).decode()
                    attachment = Attachment(
                        FileContent(encoded_pdf),
                        FileName(f"daily_report_{report_data.get('report_date', 'unknown')}.pdf"),
                        FileType("application/pdf"),
                        Disposition("attachment")
                    )
                    message.attachment = attachment
                
                response = self.client.send(message)
                results.append({
                    "recipient": recipient,
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code
                })
            except Exception as e:
                logger.error(f"Failed to send daily report to {recipient}: {str(e)}")
                results.append({"recipient": recipient, "success": False, "error": str(e)})
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
    
    def send_weekly_report_notification(
        self,
        report_data: Dict[str, Any],
        recipients: List[str],
        pdf_attachment: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Send weekly report notification email"""
        if not self.client:
            return {"success": False, "error": "SendGrid not configured"}
        
        week_range = f"{report_data.get('week_start_date', '')} to {report_data.get('week_end_date', '')}"
        subject = f"[CITTAA] Weekly Summary Report - {week_range}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CITTAA Weekly Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #F9FAFB; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden;">
                <div style="background-color: {self.CITTAA_PURPLE}; padding: 20px; text-align: center;">
                    <h1 style="color: #FFFFFF; margin: 0;">CITTAA Weekly Summary Report</h1>
                </div>
                <div style="padding: 30px;">
                    <p style="color: #374151; font-size: 14px;">
                        <strong>Week:</strong> {week_range}<br>
                        <strong>Psychologist:</strong> {report_data.get('psychologist_name', 'N/A')}<br>
                        <strong>Institution:</strong> {report_data.get('institution_name', 'N/A')}
                    </p>
                    <h3 style="color: {self.CITTAA_PURPLE};">Weekly Summary</h3>
                    <ul style="color: #374151; font-size: 14px;">
                        <li>Total Sessions: {report_data.get('total_sessions', 0)}</li>
                        <li>Total Students Served: {report_data.get('total_students', 0)}</li>
                        <li>New Intakes: {report_data.get('new_intakes', 0)}</li>
                        <li>No Shows: {report_data.get('no_shows', 0)}</li>
                    </ul>
                    <p style="color: #374151; font-size: 14px;">
                        Please find the detailed weekly report attached.
                    </p>
                </div>
                <div style="background-color: #F3F4F6; padding: 15px; text-align: center;">
                    <p style="color: {self.WARM_GRAY}; font-size: 12px; margin: 0;">
                        &copy; {datetime.now().year} Cittaa Health Services Private Limited
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        results = []
        for recipient in recipients:
            try:
                message = Mail(
                    from_email=Email(self.from_email, "CITTAA Reports"),
                    to_emails=To(recipient),
                    subject=subject,
                    html_content=Content("text/html", html_content)
                )
                
                if pdf_attachment:
                    encoded_pdf = base64.b64encode(pdf_attachment).decode()
                    attachment = Attachment(
                        FileContent(encoded_pdf),
                        FileName(f"weekly_report_{report_data.get('week_start_date', 'unknown')}.pdf"),
                        FileType("application/pdf"),
                        Disposition("attachment")
                    )
                    message.attachment = attachment
                
                response = self.client.send(message)
                results.append({
                    "recipient": recipient,
                    "success": response.status_code in [200, 201, 202],
                    "status_code": response.status_code
                })
            except Exception as e:
                logger.error(f"Failed to send weekly report to {recipient}: {str(e)}")
                results.append({"recipient": recipient, "success": False, "error": str(e)})
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }


# Singleton instance
email_service = EscalationEmailService()
