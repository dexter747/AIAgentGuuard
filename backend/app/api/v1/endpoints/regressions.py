from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.core.database import get_db
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.user import User
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


class RegressionAlert(BaseModel):
    id: str
    agent_id: str
    agent_name: str
    metric_type: str  # 'success_rate', 'avg_latency', 'error_rate'
    current_value: float
    baseline_value: float
    change_percent: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    detected_at: datetime
    time_window: str


class RegressionDetail(BaseModel):
    id: str
    agent_id: str
    agent_name: str
    metric_type: str
    current_value: float
    baseline_value: float
    change_percent: float
    severity: str
    detected_at: datetime
    time_window: str
    hourly_data: List[dict]  # Last 24 hours
    sample_failures: List[dict]  # Recent failed traces


@router.get("/regressions", response_model=List[RegressionAlert])
async def list_regressions(
    time_window: str = Query("24h", description="Time window: 1h, 6h, 24h, 7d"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all detected performance regressions across agents.
    Compares current metrics against baseline to detect degradations.
    """
    # Parse time window
    window_hours = {"1h": 1, "6h": 6, "24h": 24, "7d": 168}
    hours = window_hours.get(time_window, 24)
    
    current_start = datetime.utcnow() - timedelta(hours=hours)
    baseline_start = current_start - timedelta(hours=hours)
    
    # Get all agents for user's organization
    agents = db.query(Agent).filter(
        Agent.org_id == current_user.org_id
    ).all()
    
    regressions = []
    
    for agent in agents:
        # Calculate current period metrics
        current_traces = db.query(Trace).filter(
            and_(
                Trace.agent_id == agent.id,
                Trace.created_at >= current_start
            )
        ).all()
        
        # Calculate baseline period metrics
        baseline_traces = db.query(Trace).filter(
            and_(
                Trace.agent_id == agent.id,
                Trace.created_at >= baseline_start,
                Trace.created_at < current_start
            )
        ).all()
        
        if len(current_traces) < 10 or len(baseline_traces) < 10:
            continue  # Not enough data for comparison
        
        # Calculate success rates
        current_success_rate = (
            len([t for t in current_traces if t.status == 'success']) / len(current_traces) * 100
        )
        baseline_success_rate = (
            len([t for t in baseline_traces if t.status == 'success']) / len(baseline_traces) * 100
        )
        
        # Check for success rate regression (> 10% drop)
        success_change = current_success_rate - baseline_success_rate
        if success_change < -10:
            severity_level = (
                'critical' if success_change < -30 else
                'high' if success_change < -20 else
                'medium'
            )
            
            if not severity or severity == severity_level:
                regressions.append(RegressionAlert(
                    id=f"{agent.id}_success_rate_{int(current_start.timestamp())}",
                    agent_id=agent.id,
                    agent_name=agent.name,
                    metric_type="success_rate",
                    current_value=current_success_rate,
                    baseline_value=baseline_success_rate,
                    change_percent=success_change,
                    severity=severity_level,
                    detected_at=datetime.utcnow(),
                    time_window=time_window
                ))
        
        # Calculate average latencies (exclude failures)
        current_latencies = [
            t.total_duration for t in current_traces 
            if t.status == 'success' and t.total_duration
        ]
        baseline_latencies = [
            t.total_duration for t in baseline_traces 
            if t.status == 'success' and t.total_duration
        ]
        
        if current_latencies and baseline_latencies:
            current_avg_latency = sum(current_latencies) / len(current_latencies)
            baseline_avg_latency = sum(baseline_latencies) / len(baseline_latencies)
            
            # Check for latency regression (> 50% increase)
            latency_change_percent = (
                (current_avg_latency - baseline_avg_latency) / baseline_avg_latency * 100
            )
            
            if latency_change_percent > 50:
                severity_level = (
                    'critical' if latency_change_percent > 200 else
                    'high' if latency_change_percent > 100 else
                    'medium'
                )
                
                if not severity or severity == severity_level:
                    regressions.append(RegressionAlert(
                        id=f"{agent.id}_avg_latency_{int(current_start.timestamp())}",
                        agent_id=agent.id,
                        agent_name=agent.name,
                        metric_type="avg_latency",
                        current_value=current_avg_latency,
                        baseline_value=baseline_avg_latency,
                        change_percent=latency_change_percent,
                        severity=severity_level,
                        detected_at=datetime.utcnow(),
                        time_window=time_window
                    ))
        
        # Calculate error rates
        current_error_rate = (
            len([t for t in current_traces if t.status == 'error']) / len(current_traces) * 100
        )
        baseline_error_rate = (
            len([t for t in baseline_traces if t.status == 'error']) / len(baseline_traces) * 100
        )
        
        # Check for error rate increase (> 5% absolute increase)
        error_change = current_error_rate - baseline_error_rate
        if error_change > 5:
            severity_level = (
                'critical' if error_change > 20 else
                'high' if error_change > 10 else
                'medium'
            )
            
            if not severity or severity == severity_level:
                regressions.append(RegressionAlert(
                    id=f"{agent.id}_error_rate_{int(current_start.timestamp())}",
                    agent_id=agent.id,
                    agent_name=agent.name,
                    metric_type="error_rate",
                    current_value=current_error_rate,
                    baseline_value=baseline_error_rate,
                    change_percent=error_change,
                    severity=severity_level,
                    detected_at=datetime.utcnow(),
                    time_window=time_window
                ))
    
    # Sort by severity and change magnitude
    severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    regressions.sort(
        key=lambda r: (severity_order.get(r.severity, 0), abs(r.change_percent)),
        reverse=True
    )
    
    return regressions


@router.get("/regressions/{regression_id}", response_model=RegressionDetail)
async def get_regression_detail(
    regression_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed regression analysis with hourly breakdown and sample failures.
    """
    # Parse regression_id: {agent_id}_{metric_type}_{timestamp}
    try:
        parts = regression_id.rsplit('_', 2)
        agent_id = parts[0]
        metric_type = parts[1]
        timestamp = int(parts[2])
    except:
        raise HTTPException(status_code=400, detail="Invalid regression ID format")
    
    # Get agent
    agent = db.query(Agent).filter(
        and_(
            Agent.id == agent_id,
            Agent.org_id == current_user.org_id
        )
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Reconstruct time windows
    current_start = datetime.fromtimestamp(timestamp)
    time_window = "24h"  # Default, could be parsed from somewhere
    hours = 24
    baseline_start = current_start - timedelta(hours=hours)
    
    # Get hourly breakdown for last 24 hours
    hourly_data = []
    for i in range(24):
        hour_start = datetime.utcnow() - timedelta(hours=23-i)
        hour_end = hour_start + timedelta(hours=1)
        
        hour_traces = db.query(Trace).filter(
            and_(
                Trace.agent_id == agent_id,
                Trace.created_at >= hour_start,
                Trace.created_at < hour_end
            )
        ).all()
        
        if hour_traces:
            success_count = len([t for t in hour_traces if t.status == 'success'])
            total_count = len(hour_traces)
            
            hourly_data.append({
                'hour': hour_start.isoformat(),
                'total_traces': total_count,
                'success_rate': success_count / total_count * 100,
                'avg_latency': sum([t.total_duration for t in hour_traces if t.total_duration]) / len(hour_traces) if hour_traces else 0,
                'error_count': len([t for t in hour_traces if t.status == 'error'])
            })
        else:
            hourly_data.append({
                'hour': hour_start.isoformat(),
                'total_traces': 0,
                'success_rate': 0,
                'avg_latency': 0,
                'error_count': 0
            })
    
    # Get sample failures (last 10)
    sample_failures = []
    failed_traces = db.query(Trace).filter(
        and_(
            Trace.agent_id == agent_id,
            Trace.status == 'error',
            Trace.created_at >= current_start
        )
    ).order_by(desc(Trace.created_at)).limit(10).all()
    
    for trace in failed_traces:
        sample_failures.append({
            'trace_id': trace.id,
            'error_message': trace.error if trace.error else 'Unknown error',
            'timestamp': trace.created_at.isoformat(),
            'duration_ms': trace.total_duration
        })
    
    # Calculate current and baseline values
    current_traces = db.query(Trace).filter(
        and_(
            Trace.agent_id == agent_id,
            Trace.created_at >= current_start
        )
    ).all()
    
    baseline_traces = db.query(Trace).filter(
        and_(
            Trace.agent_id == agent_id,
            Trace.created_at >= baseline_start,
            Trace.created_at < current_start
        )
    ).all()
    
    if metric_type == 'success_rate':
        current_value = len([t for t in current_traces if t.status == 'success']) / len(current_traces) * 100
        baseline_value = len([t for t in baseline_traces if t.status == 'success']) / len(baseline_traces) * 100
        change_percent = current_value - baseline_value
    elif metric_type == 'avg_latency':
        current_latencies = [t.total_duration for t in current_traces if t.total_duration]
        baseline_latencies = [t.total_duration for t in baseline_traces if t.total_duration]
        current_value = sum(current_latencies) / len(current_latencies) if current_latencies else 0
        baseline_value = sum(baseline_latencies) / len(baseline_latencies) if baseline_latencies else 0
        change_percent = (current_value - baseline_value) / baseline_value * 100 if baseline_value else 0
    elif metric_type == 'error_rate':
        current_value = len([t for t in current_traces if t.status == 'error']) / len(current_traces) * 100
        baseline_value = len([t for t in baseline_traces if t.status == 'error']) / len(baseline_traces) * 100
        change_percent = current_value - baseline_value
    else:
        raise HTTPException(status_code=400, detail="Invalid metric type")
    
    # Determine severity
    if metric_type == 'success_rate':
        severity = 'critical' if change_percent < -30 else 'high' if change_percent < -20 else 'medium'
    elif metric_type == 'avg_latency':
        severity = 'critical' if change_percent > 200 else 'high' if change_percent > 100 else 'medium'
    else:  # error_rate
        severity = 'critical' if change_percent > 20 else 'high' if change_percent > 10 else 'medium'
    
    return RegressionDetail(
        id=regression_id,
        agent_id=agent_id,
        agent_name=agent.name,
        metric_type=metric_type,
        current_value=current_value,
        baseline_value=baseline_value,
        change_percent=change_percent,
        severity=severity,
        detected_at=datetime.utcnow(),
        time_window=time_window,
        hourly_data=hourly_data,
        sample_failures=sample_failures
    )
