# Multi-Tenant Architecture for Memory Classification Engine

## Overview

The Memory Classification Engine is designed to support multi-tenancy, allowing multiple tenants (organizations, users, or applications) to use the same infrastructure while maintaining complete isolation of their data, configurations, and resources.

## Design Principles

- **Tenant Isolation**: Complete data and configuration isolation between tenants
- **Resource Quotas**: Per-tenant resource limits to prevent noisy neighbor problems
- **Configurable Policies**: Tenant-specific classification and storage policies
- **Scalability**: Support for thousands of concurrent tenants
- **Security**: Tenant-aware authentication and authorization
- **Performance**: Minimal performance overhead for multi-tenancy

## Tenant Identification

### Tenant ID

Every classification request must include a `tenant_id` that identifies the tenant:

```python
memory_input = MemoryInput(
    content="Memory content",
    session_id="session-id",
    agent_id="agent-id",
    tenant_id="tenant-123",  # Required
)
```

### Tenant Context

The tenant ID is propagated throughout the classification pipeline:

1. **Classification Engine**: Routes requests to tenant-specific configurations
2. **Classifiers**: Apply tenant-specific rules and thresholds
3. **Memory Router**: Routes to tenant-isolated storage
4. **Logging/Telemetry**: Tags all logs and metrics with tenant ID

## Isolation Levels

### Strict Isolation (Default)

Complete isolation at all levels:

- **Data Isolation**: Separate storage namespaces per tenant
- **Configuration Isolation**: Independent classifier configurations per tenant
- **Resource Isolation**: Dedicated resource quotas per tenant
- **Network Isolation**: Tenant-specific network policies (if applicable)

### Moderate Isolation

Shared infrastructure with logical separation:

- **Data Isolation**: Logical separation within shared storage
- **Configuration Isolation**: Tenant-specific configuration overrides
- **Resource Isolation**: Shared resource pool with quotas
- **Network Isolation**: Shared network with tenant tagging

### None Isolation

Single-tenant mode (for testing or single deployments):

- **Data Isolation**: No separation
- **Configuration Isolation**: Global configuration only
- **Resource Isolation**: No quotas
- **Network Isolation**: No separation

## Tenant Configuration

### Per-Tenant Classifier Configuration

Each tenant can have custom classifier configurations:

```python
# Tenant-specific classifier config
classifier_config = ClassifierConfig(
    enabled=True,
    weight=1.0,
    confidence_threshold=0.6,  # Tenant-specific threshold
    method=ClassificationMethod.RULE_BASED,
    parameters={"tenant_specific_rules": True},
)

engine.config.set_classifier_config(
    MemoryType.IDENTITY_MEMORY,
    classifier_config,
    tenant_id="tenant-123",
)
```

### Per-Tenant Storage Policies

Tenants can have different storage policies:

```python
# Tenant-specific storage policy
storage_policy = StoragePolicy.LONG_TERM  # For enterprise tenants
# vs
storage_policy = StoragePolicy.SHORT_TERM  # For trial tenants
```

## Resource Quotas

### Quota Types

1. **Classification Quota**: Maximum classifications per time period
2. **Storage Quota**: Maximum storage capacity per tenant
3. **Concurrent Request Quota**: Maximum concurrent classifications
4. **Memory Quota**: Maximum memory usage per tenant

### Quota Enforcement

```python
class TenantQuotaManager:
    """Manages tenant resource quotas."""
    
    def check_classification_quota(self, tenant_id: str) -> bool:
        """Check if tenant has classification quota available."""
        pass
    
    def check_storage_quota(self, tenant_id: str) -> bool:
        """Check if tenant has storage quota available."""
        pass
    
    def record_classification(self, tenant_id: str) -> None:
        """Record a classification for quota tracking."""
        pass
```

### Quota Configuration

```python
tenant_quotas = {
    "tenant-123": {
        "classifications_per_day": 100000,
        "storage_gb": 100,
        "max_concurrent_requests": 50,
    },
    "tenant-456": {
        "classifications_per_day": 10000,
        "storage_gb": 10,
        "max_concurrent_requests": 10,
    },
}
```

## Storage Isolation

### Namespace-Based Isolation

Each tenant gets a separate storage namespace:

```
storage/
├── tenant-123/
│   ├── identity_memories/
│   ├── goal_memories/
│   └── ...
├── tenant-456/
│   ├── identity_memories/
│   ├── goal_memories/
│   └── ...
```

### Tenant-Aware Storage Backend

```python
class TenantAwareStorageBackend(StorageBackend):
    """Storage backend with tenant isolation."""
    
    async def store(self, memory_object: Dict[str, Any]) -> str:
        """Store memory in tenant-isolated namespace."""
        tenant_id = memory_object["tenant_id"]
        namespace = f"tenant-{tenant_id}"
        # Store in tenant-specific namespace
        pass
    
    async def retrieve(self, memory_id: str, tenant_id: str) -> Optional[Dict]:
        """Retrieve memory from tenant-isolated namespace."""
        namespace = f"tenant-{tenant_id}"
        # Retrieve from tenant-specific namespace
        pass
```

## Security Considerations

### Tenant Authentication

- Validate tenant ID on every request
- Ensure tenant has permission to access requested resources
- Prevent cross-tenant data access

### Tenant Authorization

- Role-based access control within tenants
- Tenant-specific permissions for different operations
- Audit logging of all tenant operations

### Data Privacy

- Encrypt tenant data at rest
- Encrypt tenant data in transit
- Implement data retention policies per tenant

## Performance Optimization

### Tenant-Specific Caching

```python
class TenantAwareCache:
    """Cache with tenant isolation."""
    
    def get(self, tenant_id: str, key: str) -> Optional[Any]:
        """Get cached value for tenant."""
        pass
    
    def set(self, tenant_id: str, key: str, value: Any) -> None:
        """Set cached value for tenant."""
        pass
```

### Connection Pooling

- Per-tenant connection pools for storage backends
- Connection pool sizing based on tenant quotas
- Automatic connection pool management

### Load Balancing

- Tenant-aware load balancing
- Route requests based on tenant load
- Prevent hot-spotting across tenants

## Monitoring and Observability

### Tenant-Specific Metrics

- Classification rate per tenant
- Error rate per tenant
- Latency percentiles per tenant
- Resource utilization per tenant

### Tenant-Specific Logging

- Tag all logs with tenant ID
- Separate log streams per tenant (optional)
- Tenant-specific log retention policies

### Tenant-Specific Tracing

- Distributed tracing with tenant context
- Tenant-specific trace sampling
- Cross-tenant request correlation

## Tenant Lifecycle Management

### Tenant Onboarding

1. Create tenant ID
2. Allocate storage namespace
3. Set default configuration
4. Configure resource quotas
5. Enable tenant in system

### Tenant Offboarding

1. Disable new classifications
2. Export tenant data
3. Archive or delete tenant data
4. Release allocated resources
5. Remove tenant from system

### Tenant Migration

- Migrate tenant data between storage backends
- Migrate tenant configurations
- Zero-downtime migration support

## Configuration Example

```python
from memory_classification.core.models import ClassificationConfig

# Multi-tenant configuration
config = ClassificationConfig(
    enable_multi_tenancy=True,
    tenant_isolation_level="strict",
    
    # Default quotas
    default_quotas={
        "classifications_per_day": 10000,
        "storage_gb": 10,
        "max_concurrent_requests": 10,
    },
    
    # Tenant-specific overrides
    tenant_configs={
        "enterprise-tenant": {
            "quotas": {
                "classifications_per_day": 1000000,
                "storage_gb": 1000,
                "max_concurrent_requests": 100,
            },
            "storage_policy": "long_term",
        },
        "trial-tenant": {
            "quotas": {
                "classifications_per_day": 1000,
                "storage_gb": 1,
                "max_concurrent_requests": 5,
            },
            "storage_policy": "short_term",
        },
    },
)
```

## Best Practices

1. **Always include tenant_id**: Every request must have a valid tenant ID
2. **Validate tenant_id**: Verify tenant exists and is active before processing
3. **Enforce quotas**: Reject requests that exceed tenant quotas
4. **Monitor per-tenant metrics**: Track usage and performance per tenant
5. **Implement rate limiting**: Prevent abuse by individual tenants
6. **Tenant-aware logging**: Include tenant ID in all logs for debugging
7. **Regular cleanup**: Implement data retention policies per tenant
8. **Tenant-specific testing**: Test multi-tenant scenarios thoroughly

## Failure Handling

### Tenant-Specific Failures

- Isolate failures to specific tenants
- Prevent cascading failures across tenants
- Implement tenant-specific circuit breakers

### Graceful Degradation

- Degrade service for over-quota tenants
- Provide clear error messages for quota violations
- Implement retry logic with exponential backoff

### Dead Letter Queue

- Route failed classifications to tenant-specific DLQ
- Enable manual intervention for failed classifications
- Maintain audit trail of failures
