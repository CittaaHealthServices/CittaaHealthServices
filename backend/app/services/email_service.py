"""
Email service for Vocalysis - handles sending notification emails
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "info@cittaa.in")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "info@cittaa.in")
        self.from_name = os.getenv("FROM_NAME", "CITTAA Vocalysis")
        self.enabled = bool(self.smtp_user and self.smtp_password)
        
        # Debug logging for email service initialization
        print(f"[EMAIL SERVICE] Initialized: enabled={self.enabled}, smtp_user={self.smtp_user}, smtp_host={self.smtp_host}, password_set={bool(self.smtp_password)}")
        
        if not self.enabled:
            print(f"[EMAIL SERVICE] WARNING: Email service not configured - SMTP_PASSWORD not set")
            logger.warning("Email service not configured - SMTP_PASSWORD not set for info@cittaa.in")
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an email using SMTP"""
        print(f"[EMAIL SERVICE] _send_email called: to={to_email}, subject={subject[:50]}..., enabled={self.enabled}")
        
        if not self.enabled:
            print(f"[EMAIL SERVICE] Email service disabled - would have sent email to {to_email}")
            logger.info(f"Email service disabled - would have sent email to {to_email}: {subject}")
            return False
        
        try:
            print(f"[EMAIL SERVICE] Preparing email message...")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            print(f"[EMAIL SERVICE] Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                print(f"[EMAIL SERVICE] Starting TLS...")
                server.starttls()
                print(f"[EMAIL SERVICE] Logging in as {self.smtp_user}...")
                server.login(self.smtp_user, self.smtp_password)
                print(f"[EMAIL SERVICE] Sending email...")
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"[EMAIL SERVICE] Email sent successfully to {to_email}")
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL SERVICE] FAILED to send email to {to_email}: {str(e)}")
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_registration_welcome(self, to_email: str, full_name: str) -> bool:
        """Send welcome email after registration"""
        subject = "Welcome to CITTAA Vocalysis - Your Mental Health Journey Begins"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Vocalysis</h1>
                    <p>by CITTAA Health Services</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <p>Thank you for registering with CITTAA Vocalysis - your AI-powered mental health companion.</p>
                    <p>With Vocalysis, you can:</p>
                    <ul>
                        <li>Record voice samples for mental health analysis</li>
                        <li>Get AI-powered insights based on clinical standards (PHQ-9, GAD-7, PSS, WEMWBS)</li>
                        <li>Track your mental wellness journey over time</li>
                        <li>Connect with qualified psychologists for personalized support</li>
                    </ul>
                    <p>Your privacy and data security are our top priorities. All voice recordings are processed securely and in compliance with healthcare data protection standards.</p>
                    <a href="https://vocalysis-frontend-1081764900204.us-central1.run.app/login" class="button">Login to Your Account</a>
                    <p>If you have any questions, please don't hesitate to reach out to our support team.</p>
                    <p>Best regards,<br>The CITTAA Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                    <p>This email was sent to {to_email} because you registered for a Vocalysis account.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to CITTAA Vocalysis!
        
        Hello {full_name},
        
        Thank you for registering with CITTAA Vocalysis - your AI-powered mental health companion.
        
        With Vocalysis, you can:
        - Record voice samples for mental health analysis
        - Get AI-powered insights based on clinical standards (PHQ-9, GAD-7, PSS, WEMWBS)
        - Track your mental wellness journey over time
        - Connect with qualified psychologists for personalized support
        
        Login to your account: https://vocalysis-frontend-1081764900204.us-central1.run.app/login
        
        Best regards,
        The CITTAA Team
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_clinical_trial_registration(self, to_email: str, full_name: str) -> bool:
        """Send email when user registers for clinical trial"""
        subject = "Clinical Trial Registration Received - CITTAA Vocalysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Clinical Trial Registration</h1>
                    <p>CITTAA Vocalysis Research Program</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <p>Thank you for your interest in participating in the CITTAA Vocalysis clinical trial.</p>
                    <div class="status">
                        <strong>Status: Pending Approval</strong>
                        <p>Your registration is currently under review by our clinical team. You will receive another email once your participation has been approved.</p>
                    </div>
                    <p>What happens next:</p>
                    <ul>
                        <li>Our clinical team will review your registration</li>
                        <li>You will be assigned to a qualified psychologist</li>
                        <li>You will receive access to the clinical trial features</li>
                        <li>Regular voice analysis sessions will be scheduled</li>
                    </ul>
                    <p>If you have any questions about the clinical trial, please contact our research team.</p>
                    <p>Best regards,<br>The CITTAA Clinical Research Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                    <p>This email was sent to {to_email} regarding your clinical trial registration.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Clinical Trial Registration - CITTAA Vocalysis
        
        Hello {full_name},
        
        Thank you for your interest in participating in the CITTAA Vocalysis clinical trial.
        
        Status: Pending Approval
        Your registration is currently under review by our clinical team. You will receive another email once your participation has been approved.
        
        What happens next:
        - Our clinical team will review your registration
        - You will be assigned to a qualified psychologist
        - You will receive access to the clinical trial features
        - Regular voice analysis sessions will be scheduled
        
        Best regards,
        The CITTAA Clinical Research Team
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_clinical_trial_approved(self, to_email: str, full_name: str, psychologist_name: Optional[str] = None) -> bool:
        """Send email when clinical trial participation is approved"""
        subject = "Clinical Trial Approved - Welcome to CITTAA Vocalysis Research"
        
        psychologist_info = ""
        if psychologist_name:
            psychologist_info = f"<p><strong>Assigned Psychologist:</strong> {psychologist_name}</p>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #059669; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>You're Approved!</h1>
                    <p>CITTAA Vocalysis Clinical Trial</p>
                </div>
                <div class="content">
                    <h2>Congratulations {full_name}!</h2>
                    <div class="status">
                        <strong>Status: Approved</strong>
                        <p>Your participation in the CITTAA Vocalysis clinical trial has been approved.</p>
                        {psychologist_info}
                    </div>
                    <p>You now have access to:</p>
                    <ul>
                        <li>Advanced voice analysis features</li>
                        <li>Detailed clinical reports with PHQ-9, GAD-7, PSS, and WEMWBS scores</li>
                        <li>AI-powered mental health insights</li>
                        <li>Direct communication with your assigned psychologist</li>
                    </ul>
                    <a href="https://vocalysis-frontend-1081764900204.us-central1.run.app/login" class="button">Start Your First Session</a>
                    <p>Best regards,<br>The CITTAA Clinical Research Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_clinical_trial_rejected(self, to_email: str, full_name: str, reason: Optional[str] = None) -> bool:
        """Send email when clinical trial participation is rejected"""
        subject = "Clinical Trial Application Update - CITTAA Vocalysis"
        
        reason_text = ""
        if reason:
            reason_text = f"<p><strong>Reason:</strong> {reason}</p>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status {{ background: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Application Update</h1>
                    <p>CITTAA Vocalysis Clinical Trial</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <p>Thank you for your interest in the CITTAA Vocalysis clinical trial.</p>
                    <div class="status">
                        <strong>Status: Not Selected</strong>
                        <p>Unfortunately, we are unable to include you in the current clinical trial at this time.</p>
                        {reason_text}
                    </div>
                    <p>You can still use the standard Vocalysis features to track your mental wellness. We encourage you to continue using the platform for your personal mental health journey.</p>
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>Best regards,<br>The CITTAA Clinical Research Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)


    def send_password_reset(self, to_email: str, full_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request - CITTAA Vocalysis"
        
        reset_link = f"https://vocalysis-frontend-1081764900204.us-central1.run.app/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #6366f1; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                    <p>CITTAA Vocalysis</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <p>We received a request to reset your password for your CITTAA Vocalysis account.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_link}" class="button">Reset Password</a>
                    <div class="warning">
                        <strong>Important:</strong>
                        <p>This link will expire in 1 hour. If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                    </div>
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #6366f1;">{reset_link}</p>
                    <p>Best regards,<br>The CITTAA Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                    <p>This email was sent to {to_email} because a password reset was requested.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset - CITTAA Vocalysis
        
        Hello {full_name},
        
        We received a request to reset your password for your CITTAA Vocalysis account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The CITTAA Team
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_password_changed_confirmation(self, to_email: str, full_name: str) -> bool:
        """Send confirmation email after password change"""
        subject = "Password Changed Successfully - CITTAA Vocalysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .success {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #059669; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Changed</h1>
                    <p>CITTAA Vocalysis</p>
                </div>
                <div class="content">
                    <h2>Hello {full_name},</h2>
                    <div class="success">
                        <strong>Your password has been successfully changed.</strong>
                    </div>
                    <p>You can now log in to your account with your new password.</p>
                    <a href="https://vocalysis-frontend-1081764900204.us-central1.run.app/login" class="button">Login to Your Account</a>
                    <p>If you did not make this change, please contact our support team immediately.</p>
                    <p>Best regards,<br>The CITTAA Team</p>
                </div>
                <div class="footer">
                    <p>CITTAA Health Services Pvt. Ltd.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
