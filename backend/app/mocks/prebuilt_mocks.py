"""
Pre-built mocks for popular external tools and APIs
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
import json
from app.services.mock_engine import ToolMock, MockResponse


class StripeMock:
    """Pre-built mocks for Stripe API"""
    
    @staticmethod
    def create_charge_mock() -> ToolMock:
        """Mock for Stripe charge creation"""
        mock = ToolMock("stripe_create_charge")
        
        # Success response
        mock.set_default_response({
            "id": f"ch_{random.randint(1000000, 9999999)}",
            "object": "charge",
            "amount": 1000,
            "amount_captured": 1000,
            "currency": "usd",
            "status": "succeeded",
            "paid": True,
            "refunded": False,
            "created": int(datetime.utcnow().timestamp()),
            "receipt_url": "https://pay.stripe.com/receipts/mock"
        })
        
        return mock
    
    @staticmethod
    def create_customer_mock() -> ToolMock:
        """Mock for Stripe customer creation"""
        mock = ToolMock("stripe_create_customer")
        
        mock.set_default_response({
            "id": f"cus_{random.randint(1000000, 9999999)}",
            "object": "customer",
            "email": "customer@example.com",
            "created": int(datetime.utcnow().timestamp()),
            "default_source": None,
            "sources": {"data": [], "total_count": 0}
        })
        
        return mock
    
    @staticmethod
    def create_subscription_mock() -> ToolMock:
        """Mock for Stripe subscription"""
        mock = ToolMock("stripe_create_subscription")
        
        mock.set_default_response({
            "id": f"sub_{random.randint(1000000, 9999999)}",
            "object": "subscription",
            "status": "active",
            "current_period_start": int(datetime.utcnow().timestamp()),
            "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
            "plan": {
                "id": "price_mock",
                "amount": 1999,
                "currency": "usd",
                "interval": "month"
            }
        })
        
        return mock


class SendGridMock:
    """Pre-built mocks for SendGrid email API"""
    
    @staticmethod
    def send_email_mock() -> ToolMock:
        """Mock for SendGrid email sending"""
        mock = ToolMock("sendgrid_send_email")
        
        mock.set_default_response({
            "message_id": f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "status": "delivered",
            "to": ["recipient@example.com"],
            "from": "sender@example.com",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return mock
    
    @staticmethod
    def send_bulk_email_mock() -> ToolMock:
        """Mock for SendGrid bulk email"""
        mock = ToolMock("sendgrid_send_bulk")
        
        mock.set_default_response({
            "batch_id": f"batch_{random.randint(1000000, 9999999)}",
            "status": "queued",
            "total_count": 100,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return mock


class GoogleCalendarMock:
    """Pre-built mocks for Google Calendar API"""
    
    @staticmethod
    def create_event_mock() -> ToolMock:
        """Mock for creating calendar event"""
        mock = ToolMock("google_calendar_create_event")
        
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        
        mock.set_default_response({
            "id": f"event_{random.randint(1000000, 9999999)}",
            "status": "confirmed",
            "htmlLink": "https://calendar.google.com/event?eid=mock",
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat(),
            "summary": "Mock Event",
            "description": "This is a mock calendar event",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "attendees": [],
            "creator": {
                "email": "creator@example.com",
                "self": True
            }
        })
        
        return mock
    
    @staticmethod
    def list_events_mock() -> ToolMock:
        """Mock for listing calendar events"""
        mock = ToolMock("google_calendar_list_events")
        
        mock.set_default_response({
            "items": [
                {
                    "id": f"event_{i}",
                    "summary": f"Mock Event {i}",
                    "start": {
                        "dateTime": (datetime.utcnow() + timedelta(days=i)).isoformat()
                    }
                }
                for i in range(3)
            ],
            "nextPageToken": None
        })
        
        return mock


class SlackMock:
    """Pre-built mocks for Slack API"""
    
    @staticmethod
    def post_message_mock() -> ToolMock:
        """Mock for posting Slack message"""
        mock = ToolMock("slack_post_message")
        
        mock.set_default_response({
            "ok": True,
            "channel": "C0123456789",
            "ts": f"{int(datetime.utcnow().timestamp())}.123456",
            "message": {
                "type": "message",
                "user": "U987654321",
                "text": "Mock message",
                "ts": f"{int(datetime.utcnow().timestamp())}.123456"
            }
        })
        
        return mock
    
    @staticmethod
    def upload_file_mock() -> ToolMock:
        """Mock for uploading file to Slack"""
        mock = ToolMock("slack_upload_file")
        
        mock.set_default_response({
            "ok": True,
            "file": {
                "id": f"F{random.randint(1000000, 9999999)}",
                "name": "mock_file.txt",
                "mimetype": "text/plain",
                "size": 1024,
                "url_private": "https://files.slack.com/mock"
            }
        })
        
        return mock


class GitHubMock:
    """Pre-built mocks for GitHub API"""
    
    @staticmethod
    def create_issue_mock() -> ToolMock:
        """Mock for creating GitHub issue"""
        mock = ToolMock("github_create_issue")
        
        mock.set_default_response({
            "id": random.randint(1000000000, 9999999999),
            "number": random.randint(1, 1000),
            "state": "open",
            "title": "Mock Issue",
            "body": "This is a mock issue",
            "user": {
                "login": "mockuser",
                "id": 12345
            },
            "labels": [],
            "assignees": [],
            "html_url": "https://github.com/org/repo/issues/42",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return mock
    
    @staticmethod
    def create_pr_mock() -> ToolMock:
        """Mock for creating GitHub pull request"""
        mock = ToolMock("github_create_pr")
        
        mock.set_default_response({
            "id": random.randint(1000000000, 9999999999),
            "number": random.randint(1, 1000),
            "state": "open",
            "title": "Mock PR",
            "body": "This is a mock pull request",
            "head": {"ref": "feature-branch"},
            "base": {"ref": "main"},
            "mergeable": True,
            "html_url": "https://github.com/org/repo/pull/42",
            "created_at": datetime.utcnow().isoformat()
        })
        
        return mock


class OpenAIMock:
    """Pre-built mocks for OpenAI API"""
    
    @staticmethod
    def create_completion_mock() -> ToolMock:
        """Mock for OpenAI completion"""
        mock = ToolMock("openai_create_completion")
        
        def completion_response(args, kwargs, state):
            prompt = kwargs.get("prompt", "") or (args[0] if args else "")
            prompt_words = len(str(prompt).split())
            
            return {
                "id": f"cmpl-{random.randint(1000000, 9999999)}",
                "object": "text_completion",
                "created": int(datetime.utcnow().timestamp()),
                "model": "gpt-4",
                "choices": [{
                    "text": f"Mock completion response for prompt with {prompt_words} words",
                    "index": 0,
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": prompt_words,
                    "completion_tokens": 20,
                    "total_tokens": prompt_words + 20
                }
            }
        
        mock.set_default_response(completion_response)
        return mock
    
    @staticmethod
    def create_chat_completion_mock() -> ToolMock:
        """Mock for OpenAI chat completion"""
        mock = ToolMock("openai_create_chat_completion")
        
        def chat_response(args, kwargs, state):
            messages = kwargs.get("messages", [])
            prompt_tokens = sum(len(str(m.get("content", "")).split()) for m in messages)
            
            return {
                "id": f"chatcmpl-{random.randint(1000000, 9999999)}",
                "object": "chat.completion",
                "created": int(datetime.utcnow().timestamp()),
                "model": "gpt-4",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Mock chat completion response"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": 25,
                    "total_tokens": prompt_tokens + 25
                }
            }
        
        mock.set_default_response(chat_response)
        return mock


class TwilioMock:
    """Pre-built mocks for Twilio API"""
    
    @staticmethod
    def send_sms_mock() -> ToolMock:
        """Mock for sending SMS via Twilio"""
        mock = ToolMock("twilio_send_sms")
        
        mock.set_default_response({
            "sid": f"SM{random.randint(10000000000000000000000000000000, 99999999999999999999999999999999)}",
            "date_created": datetime.utcnow().isoformat(),
            "date_updated": datetime.utcnow().isoformat(),
            "date_sent": datetime.utcnow().isoformat(),
            "account_sid": f"AC{random.randint(10000000000000000000000000000000, 99999999999999999999999999999999)}",
            "to": "+1234567890",
            "from_": "+0987654321",
            "body": "Mock SMS message",
            "status": "sent",
            "num_segments": "1",
            "direction": "outbound-api",
            "price": "-0.00750",
            "price_unit": "USD"
        })
        
        return mock


class AWSMock:
    """Pre-built mocks for AWS services"""
    
    @staticmethod
    def s3_upload_mock() -> ToolMock:
        """Mock for S3 file upload"""
        mock = ToolMock("aws_s3_upload")
        
        mock.set_default_response({
            "ETag": f'"{random.randint(1000000000000000, 9999999999999999)}"',
            "VersionId": f"v{random.randint(1, 100)}",
            "Location": "https://mock-bucket.s3.amazonaws.com/mock-file.txt",
            "Bucket": "mock-bucket",
            "Key": "mock-file.txt"
        })
        
        return mock
    
    @staticmethod
    def lambda_invoke_mock() -> ToolMock:
        """Mock for AWS Lambda invocation"""
        mock = ToolMock("aws_lambda_invoke")
        
        mock.set_default_response({
            "StatusCode": 200,
            "FunctionError": None,
            "Payload": json.dumps({"result": "success", "message": "Mock Lambda execution"})
        })
        
        return mock


# Registry of all pre-built mocks
PREBUILT_MOCKS = {
    # Stripe
    "stripe_create_charge": StripeMock.create_charge_mock,
    "stripe_create_customer": StripeMock.create_customer_mock,
    "stripe_create_subscription": StripeMock.create_subscription_mock,
    
    # SendGrid
    "sendgrid_send_email": SendGridMock.send_email_mock,
    "sendgrid_send_bulk": SendGridMock.send_bulk_email_mock,
    
    # Google Calendar
    "google_calendar_create_event": GoogleCalendarMock.create_event_mock,
    "google_calendar_list_events": GoogleCalendarMock.list_events_mock,
    
    # Slack
    "slack_post_message": SlackMock.post_message_mock,
    "slack_upload_file": SlackMock.upload_file_mock,
    
    # GitHub
    "github_create_issue": GitHubMock.create_issue_mock,
    "github_create_pr": GitHubMock.create_pr_mock,
    
    # OpenAI
    "openai_create_completion": OpenAIMock.create_completion_mock,
    "openai_create_chat_completion": OpenAIMock.create_chat_completion_mock,
    
    # Twilio
    "twilio_send_sms": TwilioMock.send_sms_mock,
    
    # AWS
    "aws_s3_upload": AWSMock.s3_upload_mock,
    "aws_lambda_invoke": AWSMock.lambda_invoke_mock,
}


def get_prebuilt_mock(tool_name: str) -> Optional[ToolMock]:
    """
    Get a pre-built mock by name
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        ToolMock instance or None if not found
    """
    mock_factory = PREBUILT_MOCKS.get(tool_name)
    if mock_factory:
        return mock_factory()
    return None


def list_available_mocks() -> List[str]:
    """
    List all available pre-built mocks
    
    Returns:
        List of mock names
    """
    return list(PREBUILT_MOCKS.keys())
