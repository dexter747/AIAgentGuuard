# Celery configuration for background tasks
from celery import Celery
from kombu import Exchange, Queue
import os

# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery instance
celery_app = Celery(
    "agentguard",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.health_tasks",
        "app.tasks.webhook_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.analytics_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Health checks every 5 minutes
        "run-health-checks": {
            "task": "app.tasks.health_tasks.run_all_health_checks",
            "schedule": 300.0,  # 5 minutes
        },
        # Process webhook queue every minute
        "process-webhook-queue": {
            "task": "app.tasks.webhook_tasks.process_webhook_queue",
            "schedule": 60.0,  # 1 minute
        },
        # Cleanup old data daily at 3 AM
        "cleanup-old-data": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_traces",
            "schedule": {
                "hour": 3,
                "minute": 0,
            },
        },
        # Generate daily analytics at midnight
        "generate-daily-analytics": {
            "task": "app.tasks.analytics_tasks.generate_daily_report",
            "schedule": {
                "hour": 0,
                "minute": 5,
            },
        },
        # Send weekly summary emails on Monday at 9 AM
        "send-weekly-summary": {
            "task": "app.tasks.email_tasks.send_weekly_summaries",
            "schedule": {
                "day_of_week": 1,
                "hour": 9,
                "minute": 0,
            },
        },
    },
    
    # Queue configuration
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
        Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
        Queue("emails", Exchange("emails"), routing_key="emails"),
        Queue("webhooks", Exchange("webhooks"), routing_key="webhooks"),
    ),
    
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    
    # Task routes
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "emails"},
        "app.tasks.webhook_tasks.*": {"queue": "webhooks"},
        "app.tasks.health_tasks.*": {"queue": "high_priority"},
        "app.tasks.cleanup_tasks.*": {"queue": "low_priority"},
        "app.tasks.analytics_tasks.*": {"queue": "low_priority"},
    },
)

# Optional: Configure logging
celery_app.conf.update(
    worker_hijack_root_logger=False,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)
