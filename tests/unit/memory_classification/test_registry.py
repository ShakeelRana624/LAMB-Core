"""
Unit tests for registries.

This module contains comprehensive unit tests for the memory type registry
and classifier registry.
"""

import pytest
from memory_classification.core.types import MemoryType, StoragePolicy
from memory_classification.core.models import TypeDefinition
from memory_classification.registry.memory_type_registry import (
    MemoryTypeRegistry,
    get_global_registry,
    reset_global_registry,
)
from memory_classification.registry.classifier_registry import (
    ClassifierRegistry,
    get_global_classifier_registry,
    reset_global_classifier_registry,
)
from memory_classification.classifiers.identity import IdentityClassifier
from memory_classification.classifiers.goal import GoalClassifier


class TestMemoryTypeRegistry:
    """Tests for MemoryTypeRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry instance."""
        return MemoryTypeRegistry()
    
    def test_register_type(self, registry):
        """Test registering a memory type."""
        definition = TypeDefinition(
            memory_type=MemoryType.IDENTITY_MEMORY,
            schema_definition={"fields": {}},
            validation_rules=[],
            storage_policy=StoragePolicy.STANDARD,
        )
        
        registry.register_type(definition)
        
        assert registry.validate_type(MemoryType.IDENTITY_MEMORY)
    
    def test_get_type(self, registry):
        """Test getting a memory type definition."""
        definition = registry.get_type(MemoryType.IDENTITY_MEMORY)
        
        assert definition is not None
        assert definition.memory_type == MemoryType.IDENTITY_MEMORY
    
    def test_get_all_types(self, registry):
        """Test getting all registered types."""
        types = registry.get_all_types()
        
        assert len(types) > 0
        assert MemoryType.IDENTITY_MEMORY in types
    
    def test_validate_type(self, registry):
        """Test validating a memory type."""
        assert registry.validate_type(MemoryType.IDENTITY_MEMORY)
        assert not registry.validate_type(MemoryType("invalid_type"))
    
    def test_get_storage_policy(self, registry):
        """Test getting storage policy for a type."""
        policy = registry.get_storage_policy(MemoryType.IDENTITY_MEMORY)
        
        assert policy is not None
        assert isinstance(policy, StoragePolicy)
    
    def test_get_schema(self, registry):
        """Test getting schema for a type."""
        schema = registry.get_schema(MemoryType.IDENTITY_MEMORY)
        
        assert schema is not None
        assert "fields" in schema
    
    def test_get_validation_rules(self, registry):
        """Test getting validation rules for a type."""
        rules = registry.get_validation_rules(MemoryType.IDENTITY_MEMORY)
        
        assert rules is not None
        assert isinstance(rules, list)
    
    def test_get_metadata(self, registry):
        """Test getting metadata for a type."""
        metadata = registry.get_metadata(MemoryType.IDENTITY_MEMORY)
        
        assert metadata is not None
        assert isinstance(metadata, dict)
    
    def test_unregister_type(self, registry):
        """Test unregistering a memory type."""
        assert registry.unregister_type(MemoryType.IDENTITY_MEMORY)
        assert not registry.validate_type(MemoryType.IDENTITY_MEMORY)
    
    def test_get_registry_info(self, registry):
        """Test getting registry information."""
        info = registry.get_registry_info()
        
        assert "total_types" in info
        assert "types" in info
        assert "storage_policies" in info
    
    def test_global_registry_singleton(self):
        """Test that global registry is a singleton."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        
        assert registry1 is registry2
    
    def test_reset_global_registry(self):
        """Test resetting global registry."""
        reset_global_registry()
        
        registry1 = get_global_registry()
        reset_global_registry()
        registry2 = get_global_registry()
        
        assert registry1 is not registry2


class TestClassifierRegistry:
    """Tests for ClassifierRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry instance."""
        return ClassifierRegistry()
    
    def test_register_classifier(self, registry):
        """Test registering a classifier."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        assert registry.has_classifier(classifier.memory_type)
    
    def test_get_classifier(self, registry):
        """Test getting a classifier."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        retrieved = registry.get_classifier(classifier.memory_type)
        
        assert retrieved is not None
        assert retrieved.memory_type == classifier.memory_type
    
    def test_get_all_classifiers(self, registry):
        """Test getting all classifiers."""
        classifier1 = IdentityClassifier()
        classifier2 = GoalClassifier()
        
        registry.register_classifier(classifier1)
        registry.register_classifier(classifier2)
        
        classifiers = registry.get_all_classifiers()
        
        assert len(classifiers) == 2
    
    def test_get_enabled_classifiers(self, registry):
        """Test getting enabled classifiers."""
        classifier1 = IdentityClassifier()
        classifier2 = GoalClassifier()
        classifier2.disable()
        
        registry.register_classifier(classifier1)
        registry.register_classifier(classifier2)
        
        enabled = registry.get_enabled_classifiers()
        
        assert len(enabled) == 1
        assert classifier1 in enabled
    
    def test_get_disabled_classifiers(self, registry):
        """Test getting disabled classifiers."""
        classifier1 = IdentityClassifier()
        classifier2 = GoalClassifier()
        classifier2.disable()
        
        registry.register_classifier(classifier1)
        registry.register_classifier(classifier2)
        
        disabled = registry.get_disabled_classifiers()
        
        assert len(disabled) == 1
        assert classifier2 in disabled
    
    def test_unregister_classifier(self, registry):
        """Test unregistering a classifier."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        assert registry.unregister_classifier(classifier.memory_type)
        assert not registry.has_classifier(classifier.memory_type)
    
    def test_enable_classifier(self, registry):
        """Test enabling a classifier."""
        classifier = IdentityClassifier()
        classifier.disable()
        registry.register_classifier(classifier)
        
        registry.enable_classifier(classifier.memory_type)
        
        assert registry.get_classifier(classifier.memory_type).is_enabled()
    
    def test_disable_classifier(self, registry):
        """Test disabling a classifier."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        registry.disable_classifier(classifier.memory_type)
        
        assert not registry.get_classifier(classifier.memory_type).is_enabled()
    
    def test_has_classifier(self, registry):
        """Test checking if classifier exists."""
        classifier = IdentityClassifier()
        
        assert not registry.has_classifier(classifier.memory_type)
        
        registry.register_classifier(classifier)
        
        assert registry.has_classifier(classifier.memory_type)
    
    def test_get_supported_memory_types(self, registry):
        """Test getting supported memory types."""
        classifier1 = IdentityClassifier()
        classifier2 = GoalClassifier()
        
        registry.register_classifier(classifier1)
        registry.register_classifier(classifier2)
        
        types = registry.get_supported_memory_types()
        
        assert len(types) == 2
        assert classifier1.memory_type in types
        assert classifier2.memory_type in types
    
    def test_get_registry_info(self, registry):
        """Test getting registry information."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        info = registry.get_registry_info()
        
        assert "total_classifiers" in info
        assert "enabled_count" in info
        assert "disabled_count" in info
        assert "memory_types" in info
    
    def test_clear(self, registry):
        """Test clearing the registry."""
        classifier = IdentityClassifier()
        registry.register_classifier(classifier)
        
        registry.clear()
        
        assert len(registry.get_all_classifiers()) == 0
    
    def test_global_classifier_registry_singleton(self):
        """Test that global classifier registry is a singleton."""
        registry1 = get_global_classifier_registry()
        registry2 = get_global_classifier_registry()
        
        assert registry1 is registry2
    
    def test_reset_global_classifier_registry(self):
        """Test resetting global classifier registry."""
        reset_global_classifier_registry()
        
        registry1 = get_global_classifier_registry()
        reset_global_classifier_registry()
        registry2 = get_global_classifier_registry()
        
        assert registry1 is not registry2
