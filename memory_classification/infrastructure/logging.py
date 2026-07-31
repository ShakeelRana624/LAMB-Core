"""
Structured logging for the Memory Classification Engine.

This module provides structured JSON logging with context injection,
log level management, and classification-specific logging utilities.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json

from memory_classification.core.models import ClassificationConfig


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.
    
    Outputs logs in JSON format with consistent structure
    for easy parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
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
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra context if present
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        return json.dumps(log_data)


class ClassificationLogger:
    """
    Logger for classification-specific events.
    
    Provides convenience methods for logging classification events
    with consistent structure and context.
    """
    
    def __init__(self, name: str = "memory_classification", level: str = "INFO"):
        """
        Initialize the classification logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add structured handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
    
    def log_classification(
        self,
        memory_id: str,
        memory_types: list,
        confidence_scores: dict,
        computation_time_ms: float,
        context: Dict[str, Any] = None,
    ) -> None:
        """
        Log a classification event.
        
        Args:
            memory_id: Memory identifier
            memory_types: Classified memory types
            confidence_scores: Confidence scores per type
            computation_time_ms: Computation time in milliseconds
            context: Additional context
        """
        log_context = {
            "memory_id": memory_id,
            "memory_types": memory_types,
            "confidence_scores": confidence_scores,
            "computation_time_ms": computation_time,
            "event_type": "classification",
        }
        
        if context:
            log_context.update(context)
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            f"Classification completed for memory {memory_id}",
            (),
            None,
        )
        record.context = log_context
        self.logger.handle(record)
    
    def log_error(
        self,
        error: str,
        context: Dict[str, Any] = None,
        exc_info: bool = False,
    ) -> None:
        """
        Log an error event.
        
        Args:
            error: Error message
            context: Additional context
            exc_info: Whether to include exception info
        """
        log_context = {
            "event_type": "error",
            "error": error,
        }
        
        if context:
            log_context.update(context)
        
        if exc_info:
            self.logger.error(
                error,
                extra={"context": log_context},
                exc_info=True,
            )
        else:
            record = self.logger.makeRecord(
                self.logger.name,
                logging.ERROR,
                "",
                0,
                error,
                (),
                None,
            )
            record.context = log_context
            self.logger.handle(record)
    
    def log_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Log statistics event.
        
        Args:
            stats: Statistics dictionary
        """
        log_context = {
            "event_type": "statistics",
            **stats,
        }
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            "Classification statistics",
            (),
            None,
        )
        record.context = log_context
        self.logger.handle(record)
    
    def log_routing(
        self,
        memory_id: str,
        storage_locations: list,
        context: Dict[str, Any] = None,
    ) -> None:
        """
        Log a routing event.
        
        Args:
            memory_id: Memory identifier
            storage_locations: Storage locations
            context: Additional context
        """
        log_context = {
            "memory_id": memory_id,
            "storage_locations": storage_locations,
            "event_type": "routing",
        }
        
        if context:
            log_context.update(context)
        
        record = self.logger.makeRecord(
            self.logger.name,
            logging.INFO,
            "",
            0,
            f"Memory {memory_id} routed to storage",
            (),
            None,
        )
        record.context = log_context
        self.logger.handle(record)
    
    def set_level(self, level: str) -> None:
        """
        Set the log level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger.setLevel(getattr(logging, level.upper()))


def setup_logging(config: ClassificationConfig) -> ClassificationLogger:
    """
    Set up structured logging for the classification engine.
    
    Args:
        config: Classification configuration
        
    Returns:
        Configured ClassificationLogger instance
    """
    level = "INFO" if config.enable_logging else "WARNING"
    logger = ClassificationLogger(level=level)
    return logger


def get_logger(name: str = "memory_classification") -> ClassificationLogger:
    """
    Get or create a classification logger.
    
    Args:
        name: Logger name
        
    Returns:
        ClassificationLogger instance
    """
    return ClassificationLogger(name)
