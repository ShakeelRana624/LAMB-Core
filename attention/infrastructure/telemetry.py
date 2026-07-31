"""
OpenTelemetry instrumentation for the Attention Engine.

This module provides distributed tracing and metrics collection
for observability and performance monitoring.
"""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import time

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.metrics import get_meter_provider, set_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


class TelemetryManager:
    """
    Manages OpenTelemetry instrumentation.
    
    Provides tracing and metrics collection for the Attention Engine.
    """
    
    def __init__(self, service_name: str = "lamb-attention", enable_telemetry: bool = True):
        """
        Initialize the telemetry manager.
        
        Args:
            service_name: Name of the service
            enable_telemetry: Whether to enable telemetry
        """
        self.service_name = service_name
        self.enable_telemetry = enable_telemetry and OPENTELEMETRY_AVAILABLE
        self.tracer = None
        self.meter = None
        
        if self.enable_telemetry:
            self._setup_tracing()
            self._setup_metrics()
    
    def _setup_tracing(self) -> None:
        """Set up distributed tracing."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        # Create resource
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
        })
        
        # Create tracer provider
        provider = TracerProvider(resource=resource)
        
        # Configure Jaeger exporter (if available)
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        except Exception:
            # Fall back to console exporter
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
    
    def _setup_metrics(self) -> None:
        """Set up metrics collection."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        # Create Prometheus metric reader
        try:
            reader = PrometheusMetricReader()
            meter_provider = MeterProvider(metric_readers=[reader])
            set_meter_provider(meter_provider)
            self.meter = meter_provider.get_meter(__name__)
        except Exception:
            # Fall back to no metrics
            self.meter = None
    
    def trace_signal_computation(self, signal_name: str):
        """
        Decorator to trace signal computation.
        
        Args:
            signal_name: Name of the signal being traced
            
        Returns:
            Decorator function
        """
        if not self.enable_telemetry or not self.tracer:
            def decorator(func):
                @wraps(func)
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)
                return wrapper
            return decorator
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(
                    f"signal.{signal_name}",
                    attributes={"signal.name": signal_name}
                ) as span:
                    start_time = time.perf_counter()
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("success", False)
                        span.set_attribute("error", str(e))
                        span.record_exception(e)
                        raise
                    finally:
                        duration_ms = (time.perf_counter() - start_time) * 1000
                        span.set_attribute("duration_ms", duration_ms)
            return wrapper
        return decorator
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            attributes: Additional attributes
        """
        if not self.enable_telemetry or not self.meter:
            return
        
        try:
            histogram = self.meter.create_histogram(
                metric_name,
                description=f"Attention Engine metric: {metric_name}",
            )
            histogram.record(value, attributes or {})
        except Exception:
            pass


# Global telemetry manager instance
_telemetry_manager: Optional[TelemetryManager] = None


def setup_telemetry(
    service_name: str = "lamb-attention",
    enable_telemetry: bool = True,
) -> TelemetryManager:
    """
    Set up telemetry for the Attention Engine.
    
    Args:
        service_name: Name of the service
        enable_telemetry: Whether to enable telemetry
        
    Returns:
        TelemetryManager instance
    """
    global _telemetry_manager
    _telemetry_manager = TelemetryManager(service_name, enable_telemetry)
    return _telemetry_manager


def trace_signal_computation(signal_name: str):
    """
    Decorator to trace signal computation.
    
    Args:
        signal_name: Name of the signal being traced
        
    Returns:
        Decorator function
    """
    if _telemetry_manager is None:
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    return _telemetry_manager.trace_signal_computation(signal_name)
