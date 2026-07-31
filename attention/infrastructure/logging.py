"""
Structured logging setup for the Attention Engine.

This module provides structured logging with JSON formatting,
context injection, and log level management.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json

from attention.core.models import AttentionConfig


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.
    
    Outputs logs in JSON format with consistent structure
    for easy parsing and analysis.
    """
    
    def __init__(self):
        """Initialize the structured formatter."""
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


def setup_logging(config: AttentionConfig) -> logging.Logger:
    """
    Set up structured logging for the Attention Engine.
    
    Args:
        config: Attention configuration
        
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger("attention")
    
    # Set log level from config
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Add console handler with structured formatter
    if config.enable_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(StructuredFormatter())
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "attention") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class AttentionLogger:
    """
    Convenience wrapper for attention-specific logging.
    
    Provides methods for logging attention-related events
    with consistent structure.
    """
    
    def __init__(self, config: AttentionConfig):
        """
        Initialize the attention logger.
        
        Args:
            config: Attention configuration
        """
        self.config = config
        self.logger = setup_logging(config)
    
    def log_signal_computation(
        self,
        signal_name: str,
        score: float,
        computation_time_ms: float,
        session_id: str,
        agent_id: str,
    ) -> None:
        """
        Log signal computation.
        
        Args:
            signal_name: Name of the signal
            score: Computed score
            computation_time_ms: Computation time in milliseconds
            session_id: Session ID
            agent_id: Agent ID
        """
        extra_fields = {
            "signal_name": signal_name,
            "score": score,
            "computation_time_ms": computation_time_ms,
            "session_id": session_id,
            "agent_id": agent_id,
            "event_type": "signal_computation",
        }
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            f"Signal '{signal_name}' computed: score={score:.3f}, time={computation_time_ms:.2f}ms",
            (),
            None,
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
    
    def log_aggregation(
        self,
        aggregated_score: float,
        should_store: bool,
        computation_time_ms: float,
        session_id: str,
        agent_id: str,
    ) -> None:
        """
        Log aggregation result.
        
        Args:
            aggregated_score: Final aggregated score
            should_store: Whether to store
            computation_time_ms: Computation time in milliseconds
            session_id: Session ID
            agent_id: Agent ID
        """
        extra_fields = {
            "aggregated_score": aggregated_score,
            "should_store": should_store,
            "computation_time_ms": computation_time_ms,
            "session_id": session_id,
            "agent_id": agent_id,
            "event_type": "aggregation",
        }
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            f"Aggregation: score={aggregated_score:.3f}, store={should_store}, time={computation_time_ms:.2f}ms",
            (),
            None,
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        session_id: str,
        agent_id: str,
    ) -> None:
        """
        Log an error with context.
        
        Args:
            error: Exception that occurred
            context: Additional context
            session_id: Session ID
            agent_id: Agent ID
        """
        extra_fields = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "session_id": session_id,
            "agent_id": agent_id,
            "event_type": "error",
        }
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.ERROR,
            "",
            0,
            f"Error: {type(error).__name__}: {str(error)}",
            (),
            (type(error), error, None),
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
