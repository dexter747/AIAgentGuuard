"""
Email Service for OverseeX
Handles all transactional emails using SMTP (compatible with any SMTP provider)
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.from_email = os.getenv("FROM_EMAIL", "noreply@overseex.com").strip()
        self.from_name = os.getenv("FROM_NAME", "OverseeX")
        self.app_url = os.getenv("APP_URL", "http://localhost:3000").strip()
        self.development_mode = os.getenv("ENVIRONMENT", "development") == "development"
        self.smtp_configured = bool(self.smtp_user and self.smtp_password)
        
    def _get_smtp_connection(self):
        """Create SMTP connection with TLS"""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            if self.smtp_user and self.smtp_password:
                # Remove any whitespace from password
                password = self.smtp_password.strip()
                server.login(self.smtp_user, password)
            return server
        except Exception as e:
            logger.error(f"SMTP connection failed: {str(e)}")
            raise
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using SMTP"""
        
        # In development mode without SMTP, just log the email
        if not self.smtp_configured:
            if self.development_mode:
                print("\n" + "="*80)
                print(f"📧 EMAIL (Development Mode - SMTP not configured)")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print("-"*80)
                if text_content:
                    print(text_content)
                print("="*80 + "\n")
                # Return True in development mode so registration succeeds
                return True
            else:
                logger.error(f"SMTP not configured - Cannot send email to {to_email}")
                return False
            
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.sendmail(
                    self.from_email,
                    to_email,
                    message.as_string()
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _get_base_template(self, content: str) -> str:
        """Base email template with styling"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverseeX</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0a0f; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse;">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <a href="{self.app_url}" style="text-decoration: none;">
                                <img src="{self.app_url}/logo.jpeg" alt="OverseeX" style="width: 150px; height: auto;" />
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(168, 85, 247, 0.05)); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 40px;">
                            {content}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center;">
                            <p style="color: #6b7280; font-size: 14px; margin: 0 0 10px 0;">
                                © {datetime.now().year} OverseeX. All rights reserved.
                            </p>
                            <p style="color: #6b7280; font-size: 12px; margin: 0;">
                                <a href="{self.app_url}/privacy" style="color: #8b5cf6; text-decoration: none;">Privacy Policy</a>
                                &nbsp;•&nbsp;
                                <a href="{self.app_url}/terms" style="color: #8b5cf6; text-decoration: none;">Terms of Service</a>
                                &nbsp;•&nbsp;
                                <a href="{self.app_url}/unsubscribe" style="color: #8b5cf6; text-decoration: none;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    # ============================================
    # EMAIL TEMPLATES
    # ============================================
    
    def send_confirmation_email(
        self,
        to_email: str,
        user_name: str,
        confirmation_token: str
    ) -> bool:
        """Send email confirmation/verification email"""
        confirmation_url = f"{self.app_url}/verify-email?token={confirmation_token}"
        
        content = f"""
            <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                Verify Your Email
            </h1>
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6;">
                Hi {user_name}, thanks for signing up for OverseeX! Please verify your email address to get started.
            </p>
            
            <a href="{confirmation_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                Verify Email Address
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin: 30px 0 0 0;">
                Or copy and paste this link into your browser:<br>
                <a href="{confirmation_url}" style="color: #8b5cf6; word-break: break-all;">{confirmation_url}</a>
            </p>
            
            <p style="color: #6b7280; font-size: 12px; margin: 20px 0 0 0;">
                This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject="Verify your OverseeX email",
            html_content=self._get_base_template(content),
            text_content=f"Hi {user_name}, verify your email: {confirmation_url}"
        )
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        organization_name: Optional[str] = None
    ) -> bool:
        """Send welcome email after email verification"""
        dashboard_url = f"{self.app_url}/dashboard"
        docs_url = f"{self.app_url}/docs"
        
        content = f"""
            <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                Welcome to OverseeX! 🎉
            </h1>
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6;">
                Hi {user_name}, your account is now active{f' for {organization_name}' if organization_name else ''}. 
                You're all set to start securing your AI agents.
            </p>
            
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <h3 style="color: white; font-size: 18px; margin: 0 0 15px 0;">🚀 Quick Start Guide</h3>
                <ul style="color: #9ca3af; font-size: 14px; margin: 0; padding-left: 20px; line-height: 2;">
                    <li>Create your first AI agent with built-in guardrails</li>
                    <li>Configure security policies for your organization</li>
                    <li>Integrate using our SDK or REST API</li>
                    <li>Monitor threats in real-time on your dashboard</li>
                </ul>
            </div>
            
            <a href="{dashboard_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3); margin-right: 12px;">
                Go to Dashboard
            </a>
            <a href="{docs_url}" 
               style="display: inline-block; background: transparent; color: #8b5cf6; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; border: 1px solid rgba(139, 92, 246, 0.5);">
                Read the Docs
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin: 30px 0 0 0;">
                Need help? Reply to this email or reach us at <a href="mailto:support@overseex.com" style="color: #8b5cf6;">support@overseex.com</a>
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject="Welcome to OverseeX! 🛡️",
            html_content=self._get_base_template(content),
            text_content=f"Welcome to OverseeX, {user_name}! Your account is now active. Get started: {dashboard_url}"
        )
    
    async def send_payment_success_email(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        currency: str = "USD",
        invoice_url: Optional[str] = None,
        billing_period: str = "monthly"
    ) -> bool:
        """Send payment confirmation email"""
        billing_url = f"{self.app_url}/dashboard/billing"
        
        content = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #10b981, #059669); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 32px;">✓</span>
                </div>
                <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                    Payment Successful!
                </h1>
                <p style="color: #9ca3af; font-size: 16px; margin: 0;">
                    Thank you for your payment, {user_name}
                </p>
            </div>
            
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Plan</td>
                        <td style="color: white; font-size: 14px; font-weight: 600; text-align: right;">{plan_name}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Billing Period</td>
                        <td style="color: white; font-size: 14px; font-weight: 600; text-align: right;">{billing_period.capitalize()}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 16px;">Amount Paid</td>
                        <td style="color: #10b981; font-size: 24px; font-weight: 700; text-align: right; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 16px;">${amount:.2f} {currency}</td>
                    </tr>
                </table>
            </div>
            
            <div style="text-align: center;">
                {f'<a href="{invoice_url}" style="display: inline-block; background: transparent; color: #8b5cf6; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; border: 1px solid rgba(139, 92, 246, 0.5); margin-right: 12px;">Download Invoice</a>' if invoice_url else ''}
                <a href="{billing_url}" 
                   style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                    View Billing
                </a>
            </div>
            
            <p style="color: #6b7280; font-size: 12px; margin: 30px 0 0 0; text-align: center;">
                A receipt has been sent to your email. Questions? Contact <a href="mailto:billing@overseex.com" style="color: #8b5cf6;">billing@overseex.com</a>
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"Payment confirmed - ${amount:.2f} for {plan_name}",
            html_content=self._get_base_template(content),
            text_content=f"Payment successful! ${amount:.2f} for {plan_name} ({billing_period}). View billing: {billing_url}"
        )
    
    async def send_payment_failed_email(
        self,
        to_email: str,
        user_name: str,
        plan_name: str,
        amount: float,
        currency: str = "USD",
        retry_url: Optional[str] = None
    ) -> bool:
        """Send payment failure notification"""
        billing_url = retry_url or f"{self.app_url}/dashboard/billing"
        
        content = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #ef4444, #dc2626); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 32px;">!</span>
                </div>
                <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                    Payment Failed
                </h1>
                <p style="color: #9ca3af; font-size: 16px; margin: 0;">
                    Hi {user_name}, we couldn't process your payment
                </p>
            </div>
            
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <p style="color: #fca5a5; font-size: 14px; margin: 0 0 15px 0;">
                    We were unable to charge your payment method for:
                </p>
                <p style="color: white; font-size: 24px; font-weight: 700; margin: 0;">
                    ${amount:.2f} {currency} - {plan_name}
                </p>
            </div>
            
            <p style="color: #9ca3af; font-size: 14px; margin: 0 0 30px 0; line-height: 1.6;">
                Please update your payment information to avoid service interruption. Common reasons for payment failures:
            </p>
            <ul style="color: #9ca3af; font-size: 14px; margin: 0 0 30px 0; padding-left: 20px; line-height: 2;">
                <li>Expired card</li>
                <li>Insufficient funds</li>
                <li>Card declined by bank</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{billing_url}" 
                   style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                    Update Payment Method
                </a>
            </div>
        """
        
        return self._send_email(
            to_email=to_email,
            subject="⚠️ Payment failed - Action required",
            html_content=self._get_base_template(content),
            text_content=f"Payment failed for {plan_name} (${amount:.2f}). Update your payment method: {billing_url}"
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        reset_url = f"{self.app_url}/reset-password?token={reset_token}"
        
        content = f"""
            <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                Reset Your Password
            </h1>
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6;">
                Hi {user_name}, we received a request to reset your password. Click the button below to create a new password.
            </p>
            
            <a href="{reset_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                Reset Password
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin: 30px 0 0 0;">
                Or copy and paste this link:<br>
                <a href="{reset_url}" style="color: #8b5cf6; word-break: break-all;">{reset_url}</a>
            </p>
            
            <div style="background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.2); border-radius: 12px; padding: 16px; margin-top: 30px;">
                <p style="color: #fbbf24; font-size: 14px; margin: 0;">
                    ⚠️ This link expires in 1 hour. If you didn't request this, please ignore this email or contact support if you're concerned.
                </p>
            </div>
        """
        
        return self._send_email(
            to_email=to_email,
            subject="Reset your OverseeX password",
            html_content=self._get_base_template(content),
            text_content=f"Reset your password: {reset_url} (expires in 1 hour)"
        )
    
    async def send_trial_expiring_email(
        self,
        to_email: str,
        user_name: str,
        days_remaining: int,
        upgrade_url: Optional[str] = None
    ) -> bool:
        """Send trial expiration reminder"""
        billing_url = upgrade_url or f"{self.app_url}/dashboard/billing/upgrade"
        
        content = f"""
            <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                Your Trial Ends in {days_remaining} Day{'s' if days_remaining != 1 else ''}
            </h1>
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6;">
                Hi {user_name}, your OverseeX trial is ending soon. Upgrade now to keep protecting your AI agents without interruption.
            </p>
            
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <h3 style="color: white; font-size: 18px; margin: 0 0 15px 0;">What you'll lose without upgrading:</h3>
                <ul style="color: #9ca3af; font-size: 14px; margin: 0; padding-left: 20px; line-height: 2;">
                    <li>Real-time threat detection & blocking</li>
                    <li>AI agent monitoring & analytics</li>
                    <li>Policy enforcement & guardrails</li>
                    <li>Team collaboration features</li>
                </ul>
            </div>
            
            <a href="{billing_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                Upgrade Now
            </a>
            
            <p style="color: #6b7280; font-size: 14px; margin: 30px 0 0 0;">
                Questions about our plans? <a href="mailto:sales@overseex.com" style="color: #8b5cf6;">Talk to our team</a>
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"⏰ Your trial ends in {days_remaining} day{'s' if days_remaining != 1 else ''}",
            html_content=self._get_base_template(content),
            text_content=f"Your trial ends in {days_remaining} days. Upgrade now: {billing_url}"
        )
    
    async def send_agent_created_notification(
        self,
        to_email: str,
        user_name: str,
        agent_name: str,
        agent_id: str
    ) -> bool:
        """Send notification when a new agent is created"""
        agent_url = f"{self.app_url}/dashboard/agents/{agent_id}"
        
        content = f"""
            <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                New Agent Created 🤖
            </h1>
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6;">
                Hi {user_name}, your new AI agent "<strong style="color: white;">{agent_name}</strong>" has been created and is ready to use.
            </p>
            
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Agent Name</td>
                        <td style="color: white; font-size: 14px; font-weight: 600; text-align: right;">{agent_name}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Agent ID</td>
                        <td style="color: white; font-size: 14px; font-family: monospace; text-align: right;">{agent_id}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Status</td>
                        <td style="text-align: right;"><span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">Active</span></td>
                    </tr>
                </table>
            </div>
            
            <a href="{agent_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                Configure Agent
            </a>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"✅ New agent created: {agent_name}",
            html_content=self._get_base_template(content),
            text_content=f"New agent '{agent_name}' created. Configure it: {agent_url}"
        )
    
    async def send_security_alert_email(
        self,
        to_email: str,
        user_name: str,
        alert_type: str,
        alert_message: str,
        severity: str = "high"
    ) -> bool:
        """Send security alert notification"""
        dashboard_url = f"{self.app_url}/dashboard/security"
        
        severity_colors = {
            "critical": ("#dc2626", "#fca5a5", "🚨"),
            "high": ("#f97316", "#fdba74", "⚠️"),
            "medium": ("#eab308", "#fde047", "⚡"),
            "low": ("#3b82f6", "#93c5fd", "ℹ️"),
        }
        
        color, text_color, icon = severity_colors.get(severity, severity_colors["high"])
        
        content = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 64px; height: 64px; background: {color}; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 32px;">{icon}</span>
                </div>
                <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                    Security Alert
                </h1>
                <p style="color: {text_color}; font-size: 14px; font-weight: 600; text-transform: uppercase;">
                    {severity.upper()} SEVERITY
                </p>
            </div>
            
            <div style="background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1); border: 1px solid rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.3); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <p style="color: white; font-size: 16px; font-weight: 600; margin: 0 0 10px 0;">
                    {alert_type}
                </p>
                <p style="color: #9ca3af; font-size: 14px; margin: 0; line-height: 1.6;">
                    {alert_message}
                </p>
            </div>
            
            <a href="{dashboard_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                View Security Dashboard
            </a>
            
            <p style="color: #6b7280; font-size: 12px; margin: 30px 0 0 0; text-align: center;">
                Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"{icon} Security Alert: {alert_type}",
            html_content=self._get_base_template(content),
            text_content=f"Security Alert ({severity}): {alert_type} - {alert_message}"
        )
    
    async def send_health_alert_email(
        self,
        to_email: str,
        agent_name: str,
        status: str,
        consecutive_failures: int,
        error_message: Optional[str],
        endpoint: str,
        last_success: str
    ) -> bool:
        """Send health check failure alert email"""
        dashboard_url = f"{self.app_url}/dashboard/agents"
        
        content = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 64px; height: 64px; background: #dc2626; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 32px;">🚨</span>
                </div>
                <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                    Agent Health Check Failed
                </h1>
            </div>
            
            <div style="background: rgba(220, 38, 38, 0.1); border: 1px solid rgba(220, 38, 38, 0.3); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Agent</td>
                        <td style="color: white; font-size: 14px; font-weight: 600; text-align: right;">{agent_name}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Status</td>
                        <td style="text-align: right;"><span style="background: rgba(220, 38, 38, 0.2); color: #fca5a5; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{status.upper()}</span></td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Consecutive Failures</td>
                        <td style="color: #fca5a5; font-size: 14px; font-weight: 600; text-align: right;">{consecutive_failures}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Endpoint</td>
                        <td style="color: white; font-size: 12px; font-family: monospace; text-align: right;">{endpoint}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Last Success</td>
                        <td style="color: white; font-size: 14px; text-align: right;">{last_success}</td>
                    </tr>
                </table>
            </div>
            
            {'<div style="background: rgba(220, 38, 38, 0.05); border-left: 4px solid #dc2626; padding: 16px; margin-bottom: 30px;"><p style="color: #fca5a5; font-size: 14px; margin: 0; font-family: monospace;">' + error_message + '</p></div>' if error_message else ''}
            
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <h3 style="color: white; font-size: 16px; margin: 0 0 15px 0;">Recommended Actions:</h3>
                <ol style="color: #9ca3af; font-size: 14px; margin: 0; padding-left: 20px; line-height: 2;">
                    <li>Check server logs for errors</li>
                    <li>Verify the agent process is running</li>
                    <li>Check for recent deployments</li>
                    <li>Review dependency status (APIs, databases)</li>
                </ol>
            </div>
            
            <a href="{dashboard_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                View Dashboard
            </a>
            
            <p style="color: #6b7280; font-size: 12px; margin: 30px 0 0 0; text-align: center;">
                Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
            </p>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"🚨 Agent Health Check Failed: {agent_name}",
            html_content=self._get_base_template(content),
            text_content=f"Health check failed for {agent_name}. {consecutive_failures} consecutive failures. Error: {error_message or 'No details'}"
        )
    
    async def send_health_recovery_email(
        self,
        to_email: str,
        agent_name: str,
        downtime_duration: str
    ) -> bool:
        """Send recovery notification when agent becomes healthy again"""
        dashboard_url = f"{self.app_url}/dashboard/agents"
        
        content = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="width: 64px; height: 64px; background: #10b981; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 32px;">✅</span>
                </div>
                <h1 style="color: white; font-size: 28px; margin: 0 0 10px 0; font-weight: 600;">
                    Agent Recovered
                </h1>
            </div>
            
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 16px; padding: 24px; margin-bottom: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Agent</td>
                        <td style="color: white; font-size: 14px; font-weight: 600; text-align: right;">{agent_name}</td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Status</td>
                        <td style="text-align: right;"><span style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">HEALTHY</span></td>
                    </tr>
                    <tr>
                        <td style="color: #9ca3af; font-size: 14px; padding: 8px 0;">Downtime Duration</td>
                        <td style="color: white; font-size: 14px; text-align: right;">{downtime_duration}</td>
                    </tr>
                </table>
            </div>
            
            <p style="color: #9ca3af; font-size: 16px; margin: 0 0 30px 0; line-height: 1.6; text-align: center;">
                Your agent is now responding to health checks normally.
            </p>
            
            <a href="{dashboard_url}" 
               style="display: inline-block; background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: 600; font-size: 16px; box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);">
                View Dashboard
            </a>
        """
        
        return self._send_email(
            to_email=to_email,
            subject=f"✅ Agent Recovered: {agent_name}",
            html_content=self._get_base_template(content),
            text_content=f"Agent {agent_name} has recovered. Downtime: {downtime_duration}"
        )


# Create singleton instance
email_service = EmailService()
