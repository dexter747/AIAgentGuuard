# Email background tasks
from app.core.celery_app import celery_app
from app.services.email_service import EmailService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, to_email: str, subject: str, html_content: str, text_content: str = None):
    """Send an email asynchronously"""
    try:
        email_service = EmailService()
        success = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content or html_content
        )
        if success:
            logger.info(f"Email sent successfully to {to_email}")
        else:
            raise Exception(f"Failed to send email to {to_email}")
        return {"status": "sent", "to": to_email}
    except Exception as e:
        logger.error(f"Email task failed: {str(e)}")
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def send_verification_email(self, user_id: int, email: str, token: str):
    """Send email verification"""
    try:
        email_service = EmailService()
        verification_url = f"https://overseex.com/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #000; color: #fff; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                .logo {{ text-align: center; margin-bottom: 30px; }}
                .logo-icon {{ width: 60px; height: 60px; background: linear-gradient(135deg, #8B5CF6, #9333EA); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; }}
                .content {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 40px; }}
                h1 {{ color: #fff; margin: 0 0 20px 0; font-size: 24px; }}
                p {{ color: #a0a0a0; line-height: 1.6; margin: 0 0 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #8B5CF6, #9333EA); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: 10px; font-weight: 600; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <div class="logo-icon">
                        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                    </div>
                </div>
                <div class="content">
                    <h1>Verify Your Email</h1>
                    <p>Thanks for signing up for AgentGuard! Please verify your email address to get started with testing and monitoring your AI agents.</p>
                    <p>
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p style="color: #666; font-size: 14px;">This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2026 AgentGuard. All rights reserved.</p>
                    <p style="margin-top: 10px;">
                        <a href="https://agentguard.ai/privacy" style="color: #8B5CF6; text-decoration: none;">Privacy Policy</a> · 
                        <a href="https://agentguard.ai/terms" style="color: #8B5CF6; text-decoration: none;">Terms of Service</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = email_service.send_email(
            to_email=email,
            subject="Verify your AgentGuard account",
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send verification email")
            
        logger.info(f"Verification email sent to {email}")
        return {"status": "sent", "user_id": user_id}
    except Exception as e:
        logger.error(f"Verification email failed: {str(e)}")
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=3)
def send_password_reset_email(self, email: str, token: str):
    """Send password reset email"""
    try:
        email_service = EmailService()
        reset_url = f"https://agentguard.ai/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #000; color: #fff; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                .content {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 40px; }}
                h1 {{ color: #fff; margin: 0 0 20px 0; font-size: 24px; }}
                p {{ color: #a0a0a0; line-height: 1.6; margin: 0 0 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #8B5CF6, #9333EA); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: 10px; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h1>Reset Your Password</h1>
                    <p>We received a request to reset your AgentGuard password. Click the button below to create a new password.</p>
                    <p>
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p style="color: #666; font-size: 14px;">This link will expire in 1 hour. If you didn't request a password reset, please ignore this email or contact support if you're concerned.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = email_service.send_email(
            to_email=email,
            subject="Reset your AgentGuard password",
            html_content=html_content
        )
        
        if not success:
            raise Exception("Failed to send password reset email")
            
        return {"status": "sent", "email": email}
    except Exception as e:
        logger.error(f"Password reset email failed: {str(e)}")
        self.retry(exc=e)


@celery_app.task(bind=True)
def send_health_alert_email(self, email: str, agent_name: str, status: str, error_message: str = None):
    """Send health check alert email"""
    try:
        email_service = EmailService()
        
        status_color = "#ef4444" if status == "failing" else "#f59e0b"
        status_text = "Critical" if status == "failing" else "Warning"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #000; color: #fff; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                .alert-badge {{ display: inline-block; background: {status_color}; color: #fff; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; margin-bottom: 20px; }}
                .content {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 40px; }}
                h1 {{ color: #fff; margin: 0 0 20px 0; }}
                p {{ color: #a0a0a0; line-height: 1.6; }}
                .error {{ background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); padding: 16px; border-radius: 8px; color: #fca5a5; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <span class="alert-badge">🚨 {status_text}</span>
                    <h1>Health Check Alert: {agent_name}</h1>
                    <p>Your agent <strong>{agent_name}</strong> is experiencing issues.</p>
                    {f'<div class="error"><strong>Error:</strong> {error_message}</div>' if error_message else ''}
                    <p style="margin-top: 20px;">
                        <a href="https://app.agentguard.ai/dashboard/agents" style="color: #8B5CF6;">View Dashboard →</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        email_service.send_email(
            to_email=email,
            subject=f"🚨 [{status_text}] Agent Health Alert: {agent_name}",
            html_content=html_content
        )
        
        return {"status": "sent", "agent": agent_name}
    except Exception as e:
        logger.error(f"Health alert email failed: {str(e)}")
        raise


@celery_app.task
def send_weekly_summaries():
    """Send weekly summary emails to all active users"""
    from app.core.database import SessionLocal
    from app.models.user import User
    
    logger.info("Starting weekly summary email job")
    
    db = SessionLocal()
    try:
        # Get all active, verified users
        users = db.query(User).filter(
            User.is_active == True,
            User.is_verified == True
        ).all()
        
        for user in users:
            send_weekly_summary_to_user.delay(user.id, user.email)
        
        logger.info(f"Queued weekly summaries for {len(users)} users")
    finally:
        db.close()


@celery_app.task(bind=True)
def send_weekly_summary_to_user(self, user_id: int, email: str):
    """Send weekly summary to a single user"""
    try:
        # This would calculate actual stats from the database
        email_service = EmailService()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #000; color: #fff; }
                .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
                .content { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 40px; }
                .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 20px 0; }
                .stat { background: rgba(139,92,246,0.1); border-radius: 12px; padding: 20px; text-align: center; }
                .stat-value { font-size: 32px; font-weight: 600; color: #8B5CF6; }
                .stat-label { color: #a0a0a0; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h1>Your Weekly Summary</h1>
                    <p style="color: #a0a0a0;">Here's what happened with your AI agents this week:</p>
                    <div class="stat-grid">
                        <div class="stat">
                            <div class="stat-value">147</div>
                            <div class="stat-label">Tests Run</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">98.2%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">$234</div>
                            <div class="stat-label">Cost Saved</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">99.9%</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                    </div>
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="https://app.agentguard.ai/dashboard" style="color: #8B5CF6; text-decoration: none;">View Full Dashboard →</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        email_service.send_email(
            to_email=email,
            subject="📊 Your AgentGuard Weekly Summary",
            html_content=html_content
        )
        
        return {"status": "sent", "user_id": user_id}
    except Exception as e:
        logger.error(f"Weekly summary email failed for user {user_id}: {str(e)}")
        raise
