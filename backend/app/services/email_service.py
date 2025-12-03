"""
Email Service for Vocalysis
Handles sending emails for registration, password reset, and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.utils.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.frontend_url = settings.FRONTEND_URL
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        """Send an email using SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, full_name: Optional[str] = None) -> bool:
        """Send welcome email after registration"""
        name = full_name or "there"
        subject = "Welcome to Cittaa Vocalysis - Your Mental Health Journey Begins"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #2C3E50; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #8B5A96, #7BB3A8); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #8B5A96, #7BB3A8); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
                .feature {{ display: flex; align-items: center; margin: 15px 0; }}
                .feature-icon {{ width: 40px; height: 40px; background: #f3e8ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Cittaa Vocalysis</h1>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Thank you for joining Cittaa Vocalysis, your AI-powered mental health companion. We're excited to have you on board!</p>
                    
                    <h3>What you can do:</h3>
                    <ul>
                        <li><strong>Voice Analysis:</strong> Record voice samples to get instant mental health insights</li>
                        <li><strong>Clinical Assessments:</strong> Track your PHQ-9, GAD-7, PSS, and WEMWBS scores</li>
                        <li><strong>Personalized Insights:</strong> Build your baseline with 9+ recordings for personalized analysis</li>
                        <li><strong>Progress Tracking:</strong> Monitor your mental wellness journey over time</li>
                    </ul>
                    
                    <center>
                        <a href="{self.frontend_url}/login" class="button">Get Started</a>
                    </center>
                    
                    <p>If you have any questions, our support team is here to help.</p>
                    
                    <p>Best regards,<br>The Cittaa Health Team</p>
                </div>
                <div class="footer">
                    <p>Cittaa Health Services Private Limited</p>
                    <p>This email was sent to {to_email}</p>
                    <p>&copy; 2024 Cittaa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Cittaa Vocalysis!
        
        Hello {name}!
        
        Thank you for joining Cittaa Vocalysis, your AI-powered mental health companion.
        
        What you can do:
        - Voice Analysis: Record voice samples to get instant mental health insights
        - Clinical Assessments: Track your PHQ-9, GAD-7, PSS, and WEMWBS scores
        - Personalized Insights: Build your baseline with 9+ recordings
        - Progress Tracking: Monitor your mental wellness journey
        
        Get started: {self.frontend_url}/login
        
        Best regards,
        The Cittaa Health Team
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def send_clinical_trial_registration_email(self, to_email: str, full_name: Optional[str] = None) -> bool:
        """Send email when user registers for clinical trial"""
        name = full_name or "there"
        subject = "Clinical Trial Registration Received - Cittaa Vocalysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #2C3E50; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #8B5A96, #7BB3A8); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .status-box {{ background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Clinical Trial Registration</h1>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Thank you for registering for our clinical trial program. Your application has been received and is pending review.</p>
                    
                    <div class="status-box">
                        <strong>Status: Pending Approval</strong>
                        <p>Our admin team will review your registration and you'll receive an email once your participation is approved.</p>
                    </div>
                    
                    <h3>What happens next:</h3>
                    <ol>
                        <li>Our team reviews your registration (typically within 24-48 hours)</li>
                        <li>You'll receive an approval email</li>
                        <li>A psychologist will be assigned to monitor your progress</li>
                        <li>You can start recording voice samples to build your baseline</li>
                    </ol>
                    
                    <p>If you have any questions about the clinical trial, please contact our support team.</p>
                    
                    <p>Best regards,<br>The Cittaa Clinical Team</p>
                </div>
                <div class="footer">
                    <p>Cittaa Health Services Private Limited</p>
                    <p>&copy; 2024 Cittaa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_trial_approval_email(self, to_email: str, full_name: Optional[str] = None, psychologist_name: Optional[str] = None) -> bool:
        """Send email when clinical trial participation is approved"""
        name = full_name or "there"
        subject = "Clinical Trial Approved - Welcome to Cittaa Vocalysis"
        
        psychologist_section = ""
        if psychologist_name:
            psychologist_section = f"""
            <div style="background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <strong>Your Assigned Psychologist:</strong> {psychologist_name}
                <p>Your psychologist will be monitoring your progress and providing clinical support.</p>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #2C3E50; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #27AE60, #7BB3A8); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #8B5A96, #7BB3A8); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>You're Approved!</h1>
                </div>
                <div class="content">
                    <h2>Congratulations {name}!</h2>
                    <p>Your clinical trial participation has been approved. You can now start your mental health monitoring journey with Vocalysis.</p>
                    
                    {psychologist_section}
                    
                    <h3>Getting Started:</h3>
                    <ol>
                        <li><strong>Record 9 voice samples</strong> to establish your personalized baseline</li>
                        <li><strong>Daily recordings</strong> help us track your mental health trends</li>
                        <li><strong>View your reports</strong> to see PHQ-9, GAD-7, PSS, and WEMWBS scores</li>
                    </ol>
                    
                    <center>
                        <a href="{self.frontend_url}/record" class="button">Start Recording</a>
                    </center>
                    
                    <p>Best regards,<br>The Cittaa Clinical Team</p>
                </div>
                <div class="footer">
                    <p>Cittaa Health Services Private Limited</p>
                    <p>&copy; 2024 Cittaa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str, full_name: Optional[str] = None) -> bool:
        """Send password reset email"""
        name = full_name or "there"
        reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
        subject = "Password Reset Request - Cittaa Vocalysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #2C3E50; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #8B5A96, #7BB3A8); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #8B5A96, #7BB3A8); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>We received a request to reset your password for your Cittaa Vocalysis account.</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </center>
                    
                    <div class="warning">
                        <strong>Important:</strong> This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
                    </div>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #8B5A96;">{reset_link}</p>
                    
                    <p>Best regards,<br>The Cittaa Health Team</p>
                </div>
                <div class="footer">
                    <p>Cittaa Health Services Private Limited</p>
                    <p>&copy; 2024 Cittaa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_high_risk_alert_email(self, to_email: str, patient_name: str, risk_level: str) -> bool:
        """Send alert email to psychologist when patient shows high risk"""
        subject = f"High Risk Alert - Patient {patient_name} - Cittaa Vocalysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #2C3E50; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #E74C3C, #c0392b); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
                .alert-box {{ background: #fee2e2; border: 2px solid #E74C3C; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center; }}
                .button {{ display: inline-block; background: #E74C3C; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>High Risk Alert</h1>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <h2 style="color: #E74C3C; margin: 0;">Patient Requires Attention</h2>
                        <p><strong>Patient:</strong> {patient_name}</p>
                        <p><strong>Risk Level:</strong> {risk_level.upper()}</p>
                    </div>
                    
                    <p>A patient assigned to you has shown elevated risk indicators in their recent voice analysis. Please review their clinical reports and consider scheduling a follow-up session.</p>
                    
                    <center>
                        <a href="{self.frontend_url}/psychologist/patients" class="button">View Patient Details</a>
                    </center>
                    
                    <p>Best regards,<br>Cittaa Clinical Alert System</p>
                </div>
                <div class="footer">
                    <p>Cittaa Health Services Private Limited</p>
                    <p>This is an automated clinical alert.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
