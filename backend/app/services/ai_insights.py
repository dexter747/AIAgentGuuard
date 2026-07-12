from typing import List, Literal
from pydantic import BaseModel, Field
from app.models.trace import Trace
from sqlalchemy.orm import Session
import json


class AIInsight(BaseModel):
    type: Literal["error", "optimization", "cost-savings"]
    title: str
    description: str
    confidence: int = Field(ge=0, le=100)
    impact: Literal["high", "medium", "low"]


class InsightResponse(BaseModel):
    trace_id: str
    insights: List[AIInsight]
    total_insights: int


def analyze_trace_for_insights(trace: Trace, db: Session) -> InsightResponse:
    """
    Analyze a trace and generate AI-powered insights
    
    This is a simplified version. In production, this would:
    1. Use embeddings to compare with known error patterns
    2. Run statistical analysis on performance metrics
    3. Query cost optimization database
    4. Use LLM to generate insights
    """
    insights: List[AIInsight] = []
    
    # Parse trace data
    try:
        trace_data = json.loads(trace.data) if isinstance(trace.data, str) else trace.data
    except:
        trace_data = {}
    
    # 1. Check for high latency (performance optimization)
    if trace.duration and trace.duration > 2.0:
        insights.append(AIInsight(
            type="optimization",
            title="High latency detected",
            description=f"Trace completed in {trace.duration}s. Consider caching or parallel execution.",
            confidence=85,
            impact="medium"
        ))
    
    # 2. Check for expensive tokens (cost optimization)
    if trace.total_tokens and trace.total_tokens > 1000:
        insights.append(AIInsight(
            type="cost-savings",
            title="High token usage detected",
            description=f"Used {trace.total_tokens} tokens. Consider prompt optimization or smaller model.",
            confidence=90,
            impact="high"
        ))
    
    # 3. Check for errors in trace data
    if trace_data.get("status") == "error" or trace_data.get("error"):
        error_msg = trace_data.get("error", "Unknown error")
        insights.append(AIInsight(
            type="error",
            title="Execution error detected",
            description=f"Error: {error_msg}. Check input validation and error handling.",
            confidence=95,
            impact="high"
        ))
    
    # 4. Check for sequential steps that could be parallelized
    steps = trace_data.get("steps", [])
    if len(steps) > 2:
        sequential_count = sum(1 for i in range(len(steps) - 1) 
                              if steps[i].get("end_time", 0) <= steps[i+1].get("start_time", 0))
        
        if sequential_count >= 2:
            insights.append(AIInsight(
                type="optimization",
                title="Parallel execution opportunity",
                description=f"Found {sequential_count} sequential steps that could run in parallel.",
                confidence=75,
                impact="medium"
            ))
    
    # 5. Check for model overkill (using GPT-4 for simple tasks)
    if trace_data.get("model") == "gpt-4" and trace.total_tokens and trace.total_tokens < 500:
        insights.append(AIInsight(
            type="cost-savings",
            title="Model downgrade suggestion",
            description="Using GPT-4 for a simple task. GPT-3.5-turbo could save 90% cost.",
            confidence=88,
            impact="high"
        ))
    
    # 6. Check for retry patterns (inefficiency)
    if trace_data.get("retry_count", 0) > 0:
        insights.append(AIInsight(
            type="optimization",
            title="Multiple retries detected",
            description=f"Agent retried {trace_data['retry_count']} times. Improve error handling.",
            confidence=92,
            impact="medium"
        ))
    
    return InsightResponse(
        trace_id=str(trace.id),
        insights=insights,
        total_insights=len(insights)
    )


def get_trace_insights(trace_id: str, db: Session) -> InsightResponse:
    """Get AI insights for a specific trace"""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    
    if not trace:
        raise ValueError(f"Trace {trace_id} not found")
    
    return analyze_trace_for_insights(trace, db)


def get_bulk_insights(trace_ids: List[str], db: Session) -> List[InsightResponse]:
    """Get AI insights for multiple traces"""
    traces = db.query(Trace).filter(Trace.id.in_(trace_ids)).all()
    
    return [analyze_trace_for_insights(trace, db) for trace in traces]
