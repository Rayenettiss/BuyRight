"""
Structured Logging Utility
Hackathon Deliverable: Non-Functional - Observability
Logs queries, scores, decisions, versions for traceability
"""
import structlog
import logging
import sys
from datetime import datetime
from app.config import settings


def setup_logging():
    """
    Configure structured logging with JSON output for production observability.
    Captures: queries, similarity scores, ranking decisions, model versions, errors.
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json"
            else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )


def get_logger(name: str):
    """Get a structured logger instance"""
    return structlog.get_logger(name)


# Specialized logging functions for hackathon traceability

def log_search_query(
    logger,
    user_id: str,
    query: str,
    filters: dict,
    results_count: int,
    duration_ms: float
):
    """
    Log search queries for traceability.
    Hackathon: Show evidence for recommendations.
    """
    logger.info(
        "search_query",
        user_id=user_id,
        query=query,
        filters=filters,
        results_count=results_count,
        duration_ms=round(duration_ms, 2),
        timestamp=datetime.utcnow().isoformat()
    )


def log_recommendation_decision(
    logger,
    user_id: str,
    product_id: str,
    score: float,
    ranking_factors: dict,
    explanation: str
):
    """
    Log recommendation decisions with ranking factors.
    Hackathon: Explainability - why these results?
    """
    logger.info(
        "recommendation_decision",
        user_id=user_id,
        product_id=product_id,
        similarity_score=round(score, 4),
        ranking_factors=ranking_factors,
        explanation=explanation,
        timestamp=datetime.utcnow().isoformat()
    )


def log_embedding_generation(
    logger,
    item_id: str,
    item_type: str,
    model: str,
    vector_dim: int,
    duration_ms: float
):
    """
    Log embedding generation for version tracking.
    Hackathon: Track model versions for reproducibility.
    """
    logger.info(
        "embedding_generated",
        item_id=item_id,
        item_type=item_type,
        model=model,
        vector_dim=vector_dim,
        duration_ms=round(duration_ms, 2),
        timestamp=datetime.utcnow().isoformat()
    )


def log_financial_filter(
    logger,
    user_id: str,
    budget_constraints: dict,
    products_before: int,
    products_after: int
):
    """
    Log financial filtering for transparency.
    Hackathon: Show how financial context affects results.
    """
    logger.info(
        "financial_filter_applied",
        user_id=user_id,
        budget_constraints=budget_constraints,
        products_before=products_before,
        products_after=products_after,
        filtered_out=products_before - products_after,
        timestamp=datetime.utcnow().isoformat()
    )


def log_data_quality_issue(
    logger,
    issue_type: str,
    affected_records: int,
    details: dict
):
    """
    Log data quality issues for reliability monitoring.
    Hackathon: Handle dirty/missing data gracefully.
    """
    logger.warning(
        "data_quality_issue",
        issue_type=issue_type,
        affected_records=affected_records,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )


# Initialize logging on module import
setup_logging()