"""
SQLAlchemy ORM models for the Campaign Investigation Tracker.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text,
    Numeric,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# TODO [Step 4 — Day 1 / Module 04 — AIDLC]: Add SQLAlchemy relationship from Campaign
#   to CampaignHealth (e.g. `health_snapshots = relationship("CampaignHealth", back_populates=...)`)
#   so the campaign detail endpoint can eagerly load health data.


class Campaign(Base):
    """Campaign table — represents a marketing campaign."""
    __tablename__ = "campaigns"

    id = Column(String(50), primary_key=True, index=True)
    campaign_code = Column(String(50), unique=True, index=True)
    name = Column(String(255))
    advertiser_name = Column(String(255))
    status = Column(String(50))
    objective = Column(String(255))
    channel = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget_usd = Column(Float)
    owner_name = Column(String(255))
    region = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investigations = relationship(
        "Investigation", back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignHealth(Base):
    """Campaign health snapshots — time-series performance data."""
    __tablename__ = "campaign_health"

    id = Column(String(50), primary_key=True, index=True)
    campaign_id = Column(String(50), ForeignKey("campaigns.id"), index=True)
    snapshot_at = Column(DateTime)
    impressions = Column(Integer)
    clicks = Column(Integer)
    ctr = Column(Float)
    viewability = Column(Float)
    completion_rate = Column(Float)
    spend_usd = Column(Float)
    budget_pacing_pct = Column(Float)
    delivery_rate_pct = Column(Float)
    anomaly_flag = Column(Boolean, default=False)
    anomaly_reason = Column(String(255))
    delivery_note = Column(Text)


class Investigation(Base):
    """Investigation table — structured triage record against a campaign."""
    __tablename__ = "investigations"

    id = Column(String(50), primary_key=True, index=True)
    campaign_id = Column(String(50), ForeignKey("campaigns.id"), index=True)
    source_snapshot_id = Column(String(50), ForeignKey("campaign_health.id"))
    issue_type = Column(String(100))
    severity = Column(String(50))
    status = Column(String(50))
    owner_name = Column(String(255))
    question = Column(Text)
    hypothesis = Column(Text)
    next_action = Column(Text)
    resolution_summary = Column(Text)
    opened_at = Column(DateTime)
    updated_at = Column(DateTime)
    resolved_at = Column(DateTime)

    campaign = relationship("Campaign", back_populates="investigations")
    evidence = relationship(
        "InvestigationEvidence",
        back_populates="investigation",
        order_by="InvestigationEvidence.sort_order",
        cascade="all, delete-orphan",
    )
    ai_runs = relationship(
        "AiRun",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )


class InvestigationEvidence(Base):
    """Typed evidence rows attached to an investigation."""
    __tablename__ = "investigation_evidence"

    id = Column(String(50), primary_key=True, index=True)
    investigation_id = Column(String(50), ForeignKey("investigations.id"), index=True)
    snapshot_id = Column(String(50), ForeignKey("campaign_health.id"))
    evidence_type = Column(String(50))
    title = Column(String(255))
    summary = Column(Text)
    metric_name = Column(String(100))
    metric_value = Column(Numeric(12, 4))
    metric_unit = Column(String(50))
    source_label = Column(String(255))
    source_ref = Column(String(255))
    captured_at = Column(DateTime)
    captured_by = Column(String(255))
    is_key_evidence = Column(Boolean, default=False)
    sort_order = Column(Integer)

    investigation = relationship("Investigation", back_populates="evidence")


class AiRun(Base):
    """Log row capturing a single AI model invocation tied to an investigation."""
    __tablename__ = "ai_runs"

    id = Column(String(50), primary_key=True, index=True)
    investigation_id = Column(String(50), ForeignKey("investigations.id"), index=True)
    model = Column(String(100))
    task_type = Column(String(50))
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    estimated_cost_usd = Column(Numeric(10, 4))
    latency_ms = Column(Integer)
    prompt_summary = Column(Text)
    recommendation_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="ai_runs")
