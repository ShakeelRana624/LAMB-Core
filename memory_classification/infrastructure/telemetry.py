"""
OpenTelemetry integration for the Memory Classification Engine.

This module provides distributed tracing and metrics for the classification
system, enabling observability and performance monitoring.
"""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import time

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.metrics import get_meter
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None


class ClassificationTelemetry:
    """
    Telemetry manager for classification operations.
    
    Provides tracing and metrics for classification operations
    using OpenTelemetry.
    """
    
    def __init__(
        self,
        service_name: str = "memory-classification-engine",
        otlp_endpoint: Optional[str] = None,
        enable_tracing: bool = True,
        enable_metrics: bool = True,
    ):
        """
        Initialize the telemetry manager.
        
        Args:
            service_name: Name of the service
            otlp_endpoint: OTLP endpoint for exporting traces/metrics
            enable_tracing: Whether to enable tracing
            enable_metrics: Whether to enable metrics
        """
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.enable_tracing = enable_tracing and OTEL_AVAILABLE
        self.enable_metrics = enable_metrics and OTEL_AVAILABLE
        
        self.tracer = None
        self.meter = None
        self._metrics = {}
        
        if self.enable_tracing or self.enable_metrics:
            self._setup_telemetry()
    
    def _setup_telemetry(self) -> None:
        """Set up OpenTelemetry tracing and metrics."""
        if not OTEL_AVAILABLE:
            return
        
        # Set up tracing
        if self.enable_tracing:
            trace_provider = TracerProvider()
            trace.set_tracer_provider(trace_provider)
            
            if self.otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
                span_processor = BatchSpanProcessor(otlp_exporter)
                trace_provider.add_span_processor(span_processor)
            
            self.tracer = trace.get_tracer(self.service_name)
        
        # Set up metrics
        if self.enable_metrics:
            if self.otlp_endpoint:
                metric_reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=self.otlp_endpoint)
                )
                meter_provider = MeterProvider(metric_readers=[metric_reader])
            else:
                meter_provider = MeterProvider()
            
            self.meter = get_meter(self.service_name)
            self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize standard metrics."""
        if not self.meter:
            return
        
        # Classification metrics
        self._metrics["classifications_total"] = self.meter.create_counter(
            "classifications_total",
            description="Total number of classifications"
        )
        
        self._metrics["classifications_successful"] = self.meter.create_counter(
            "classifications_successful",
            description="Number of successful classifications"
        )
        
        self._metrics["classifications_failed"] = self.meter.create_counter(
            "classifications_failed",
            description="Number of failed classifications"
        )
        
        self._metrics["classification_duration"] = self.meter.create_histogram(
            "classification_duration_ms",
            description="Classification duration in milliseconds"
        )
        
        self._metrics["classifier_usage"] = self.meter.create_counter(
            "classifier_usage",
            description="Classifier usage count",
        )
    
    def record_classification(
        self,
        memory_types: list,
        duration_ms: float,
        success: bool = True,
        attributes: Dict[str, Any] = None,
    ) -> None:
        """
        Record a classification event.
        
        Args:
            memory_types: Classified memory types
            duration_ms: Classification duration in milliseconds
            success: Whether classification was successful
            attributes: Additional attributes
        """
        if not self.enable_metrics:
            return
        
        attrs = attributes or {}
        attrs["memory_types"] = ",".join([mt.value for mt in memory_types])
        attrs["success"] = str(success)
        
        self._metrics["classifications_total"].add(1, attrs)
        
        if success:
            self._metrics["classifications_successful"].add(1, attrs)
        else:
            self._metrics["classifications_failed"].add(1, attrs)
        
        self._metrics["classification_duration"].record(duration_ms, attrs)
        
        for memory_type in memory_types:
            type_attrs = attrs.copy()
            type_attrs["memory_type"] = memory_type.value
            self._metrics["classifier_usage"].add(1, type_attrs)
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        attributes: Dict[str, Any] = None,
    ) -> None:
        """
        Record a custom metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            attributes: Additional attributes
        """
        if not self.enable_metrics or metric_name not in self._metrics:
            return
        
        self._metrics[metric_name].record(value, attributes or {})
    
    def trace_classification(self, memory_id: str = None):
        """
        Decorator to trace classification operations.
        
        Args:
            memory_id: Memory identifier for tracing
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enable_tracing or not self.tracer:
                    return await func(*args, **kwargs)
                
                span_name = f"{func.__name__}"
                if memory_id:
                    span_name += f"_{memory_id}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("memory_id", memory_id or "unknown")
                    span.set_attribute("function", func.__name__)
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("success", False)
                        span.set_attribute("error", str(e))
                        span.record_exception(e)
                        raise
            
            return wrapper
        return decorator
    
    def get_tracer(self):
        """Get the OpenTelemetry tracer."""
        return self.tracer
    
    def get_meter(self):
        """Get the OpenTelemetry meter."""
        return self.meter


def setup_telemetry(
    service_name: str = "memory-classification-engine",
    otlp_endpoint: Optional[str] = None,
    enable_tracing: bool = True,
    enable_metrics: bool = True,
) -> ClassificationTelemetry:
    """
    Set up telemetry for the classification engine.
    
    Args:
        service_name: Name of the service
        otlp_endpoint: OTLP endpoint for exporting traces/metrics
        enable_tracing: Whether to enable tracing
        enable_metrics: Whether to enable metrics
        
    Returns:
        Configured ClassificationTelemetry instance
    """
    return ClassificationTelemetry(
        service_name=service_name,
        otlp_endpoint=otlp_endpoint,
        enable_tracing=enable_tracing,
        enable_metrics=enable_metrics,
    )
