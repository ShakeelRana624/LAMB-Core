"""
Classification Engine implementation.

This module implements the main Classification Engine orchestrator that
coordinates multiple classifiers, merges results, applies confidence
thresholds, and generates final classifications.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from memory_classification.core.types import MemoryType, ClassificationMethod
from memory_classification.core.interfaces import MemoryInput, ClassificationResult
from memory_classification.core.models import (
    UniversalMemoryObject,
    ClassificationConfig,
    MemoryInputModel,
)
from memory_classification.core.exceptions import (
    ClassificationFailedError,
    ClassifierNotFoundError,
    ConfigurationError,
)
from memory_classification.registry.classifier_registry import ClassifierRegistry
from memory_classification.core.router import MemoryRouter


class ClassificationEngine:
    """
    Main orchestrator for memory classification.
    
    This engine coordinates multiple classifiers, merges their results,
    applies confidence thresholds, and generates the final classification
    output as a Universal Memory Object.
    """
    
    def __init__(
        self,
        config: ClassificationConfig = None,
        classifier_registry: ClassifierRegistry = None,
        memory_router: MemoryRouter = None,
    ):
        """
        Initialize the classification engine.
        
        Args:
            config: Classification configuration
            classifier_registry: Registry of classifiers
            memory_router: Memory router for storage
        """
        self.config = config or ClassificationConfig()
        self.classifier_registry = classifier_registry or ClassifierRegistry()
        self.memory_router = memory_router
        
        # Statistics
        self._stats = {
            "total_classifications": 0,
            "successful_classifications": 0,
            "failed_classifications": 0,
            "total_computation_time_ms": 0.0,
            "classifier_usage": {},
        }
    
    async def classify(
        self,
        memory_input: MemoryInput,
        enable_routing: bool = False,
        existing_memories: List[Dict[str, Any]] = None,
    ) -> UniversalMemoryObject:
        """
        Classify a memory input into memory types.
        
        This method runs all enabled classifiers, merges their results,
        applies confidence thresholds, and returns a Universal Memory Object.
        
        Args:
            memory_input: The memory input to classify
            enable_routing: Whether to route the memory to storage
            existing_memories: List of existing memories for deduplication
            
        Returns:
            UniversalMemoryObject with classification results
            
        Raises:
            ClassificationFailedError: If classification fails
        """
        start_time = time.perf_counter()
        
        try:
            # Convert to model if needed
            if not isinstance(memory_input, MemoryInputModel):
                memory_input = MemoryInputModel(**memory_input.to_dict())
            
            # Get enabled classifiers
            enabled_classifiers = self.classifier_registry.get_enabled_classifiers()
            
            if not enabled_classifiers:
                raise ClassificationFailedError(
                    "No enabled classifiers available",
                    memory_input=memory_input.to_dict()
                )
            
            # Run classifiers in parallel
            classification_results = await self._run_classifiers(
                memory_input,
                enabled_classifiers
            )
            
            # Merge classification results
            merged_result = self._merge_classification_results(classification_results)
            
            # Apply confidence thresholds
            filtered_result = self._apply_confidence_thresholds(merged_result)
            
            # Create Universal Memory Object
            memory_object = self._create_memory_object(
                memory_input,
                filtered_result,
                start_time
            )
            
            # Route to storage if enabled
            if enable_routing and self.memory_router:
                await self.memory_router.route(memory_object, existing_memories)
            
            # Update statistics
            self._stats["total_classifications"] += 1
            self._stats["successful_classifications"] += 1
            self._stats["total_computation_time_ms"] += filtered_result.computation_time_ms
            
            for memory_type in filtered_result.memory_types:
                if memory_type not in self._stats["classifier_usage"]:
                    self._stats["classifier_usage"][memory_type] = 0
                self._stats["classifier_usage"][memory_type] += 1
            
            return memory_object
            
        except Exception as e:
            self._stats["total_classifications"] += 1
            self._stats["failed_classifications"] += 1
            
            if isinstance(e, ClassificationFailedError):
                raise
            
            raise ClassificationFailedError(
                f"Classification failed: {str(e)}",
                memory_input=memory_input.to_dict(),
                details={"error": str(e)}
            )
    
    async def batch_classify(
        self,
        memory_inputs: List[MemoryInput],
        enable_routing: bool = False,
        existing_memories: List[Dict[str, Any]] = None,
    ) -> List[UniversalMemoryObject]:
        """
        Classify multiple memory inputs in batch.
        
        Args:
            memory_inputs: List of memory inputs to classify
            enable_routing: Whether to route memories to storage
            existing_memories: List of existing memories for deduplication
            
        Returns:
            List of Universal Memory Objects with classification results
        """
        # Process in batches to control concurrency
        batch_size = self.config.batch_size
        results = []
        
        for i in range(0, len(memory_inputs), batch_size):
            batch = memory_inputs[i:i + batch_size]
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.config.max_concurrent_classifications)
            
            async def process_with_semaphore(mem_input):
                async with semaphore:
                    return await self.classify(mem_input, enable_routing, existing_memories)
            
            # Process batch in parallel
            batch_tasks = [process_with_semaphore(mem_input) for mem_input in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    # Log error but continue with other results
                    continue
                results.append(result)
        
        return results
    
    async def _run_classifiers(
        self,
        memory_input: MemoryInput,
        classifiers: List,
    ) -> List[ClassificationResult]:
        """
        Run multiple classifiers in parallel.
        
        Args:
            memory_input: The memory input to classify
            classifiers: List of classifier instances
            
        Returns:
            List of classification results
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrent_classifications)
        
        async def run_single_classifier(classifier):
            async with semaphore:
                try:
                    return await classifier.classify(memory_input)
                except Exception as e:
                    # Return empty result on failure
                    return ClassificationResult(
                        memory_types=[],
                        confidence_scores={},
                        reasoning={},
                        metadata={"error": str(e)},
                        computation_time_ms=0.0,
                    )
        
        # Run all classifiers in parallel
        tasks = [run_single_classifier(classifier) for classifier in classifiers]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def _merge_classification_results(
        self,
        results: List[ClassificationResult],
    ) -> ClassificationResult:
        """
        Merge multiple classification results.
        
        Args:
            results: List of classification results to merge
            
        Returns:
            Merged classification result
        """
        merged_memory_types = []
        merged_confidence_scores = {}
        merged_reasoning = {}
        merged_metadata = {}
        total_computation_time = 0.0
        
        for result in results:
            # Add memory types
            for memory_type in result.memory_types:
                if memory_type not in merged_memory_types:
                    merged_memory_types.append(memory_type)
            
            # Merge confidence scores (take maximum for each type)
            for memory_type, score in result.confidence_scores.items():
                if memory_type not in merged_confidence_scores:
                    merged_confidence_scores[memory_type] = score
                else:
                    merged_confidence_scores[memory_type] = max(
                        merged_confidence_scores[memory_type],
                        score
                    )
            
            # Merge reasoning (combine all reasoning)
            for memory_type, reasoning in result.reasoning.items():
                if memory_type not in merged_reasoning:
                    merged_reasoning[memory_type] = reasoning
                else:
                    merged_reasoning[memory_type] += f"; {reasoning}"
            
            # Merge metadata
            merged_metadata.update(result.metadata)
            
            # Sum computation time
            total_computation_time += result.computation_time_ms
        
        return ClassificationResult(
            memory_types=merged_memory_types,
            confidence_scores=merged_confidence_scores,
            reasoning=merged_reasoning,
            metadata=merged_metadata,
            computation_time_ms=total_computation_time,
            classifier_method=ClassificationMethod.HYBRID,
        )
    
    def _apply_confidence_thresholds(
        self,
        result: ClassificationResult,
    ) -> ClassificationResult:
        """
        Apply confidence thresholds to filter memory types.
        
        Args:
            result: Classification result to filter
            
        Returns:
            Filtered classification result
        """
        filtered_memory_types = []
        filtered_confidence_scores = {}
        filtered_reasoning = {}
        
        global_threshold = self.config.confidence_threshold
        
        for memory_type in result.memory_types:
            confidence = result.confidence_scores.get(memory_type, 0.0)
            
            # Get classifier-specific threshold if available
            classifier_config = self.config.get_classifier_config(memory_type)
            threshold = classifier_config.confidence_threshold if classifier_config else global_threshold
            
            if confidence >= threshold:
                filtered_memory_types.append(memory_type)
                filtered_confidence_scores[memory_type] = confidence
                filtered_reasoning[memory_type] = result.reasoning.get(memory_type, "")
        
        return ClassificationResult(
            memory_types=filtered_memory_types,
            confidence_scores=filtered_confidence_scores,
            reasoning=filtered_reasoning,
            metadata=result.metadata,
            computation_time_ms=result.computation_time_ms,
            classifier_method=result.classifier_method,
        )
    
    def _create_memory_object(
        self,
        memory_input: MemoryInput,
        classification_result: ClassificationResult,
        start_time: float,
    ) -> UniversalMemoryObject:
        """
        Create a Universal Memory Object from input and classification result.
        
        Args:
            memory_input: The original memory input
            classification_result: The classification result
            start_time: The start time of classification
            
        Returns:
            Universal Memory Object
        """
        return UniversalMemoryObject(
            content=memory_input.content,
            memory_types=classification_result.memory_types,
            confidence_scores=classification_result.confidence_scores,
            reasoning=classification_result.reasoning,
            tenant_id=memory_input.tenant_id,
            session_id=memory_input.session_id,
            agent_id=memory_input.agent_id,
            metadata=memory_input.metadata,
            timestamp=memory_input.timestamp,
            attention_vector=memory_input.metadata.get("attention_vector"),
            classifier_method=classification_result.classifier_method,
            classification_metadata={
                "computation_time_ms": classification_result.computation_time_ms,
                "classifier_metadata": classification_result.metadata,
            },
        )
    
    def register_classifier(self, classifier) -> None:
        """
        Register a classifier with the engine.
        
        Args:
            classifier: The classifier instance to register
        """
        self.classifier_registry.register_classifier(classifier)
    
    def unregister_classifier(self, memory_type: MemoryType) -> bool:
        """
        Unregister a classifier from the engine.
        
        Args:
            memory_type: The memory type of the classifier to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        return self.classifier_registry.unregister_classifier(memory_type)
    
    def enable_classifier(self, memory_type: MemoryType) -> bool:
        """
        Enable a classifier.
        
        Args:
            memory_type: The memory type of the classifier to enable
            
        Returns:
            True if enabled, False if not found
        """
        return self.classifier_registry.enable_classifier(memory_type)
    
    def disable_classifier(self, memory_type: MemoryType) -> bool:
        """
        Disable a classifier.
        
        Args:
            memory_type: The memory type of the classifier to disable
            
        Returns:
            True if disabled, False if not found
        """
        return self.classifier_registry.disable_classifier(memory_type)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get engine statistics.
        
        Returns:
            Dictionary with engine statistics
        """
        return {
            "total_classifications": self._stats["total_classifications"],
            "successful_classifications": self._stats["successful_classifications"],
            "failed_classifications": self._stats["failed_classifications"],
            "success_rate": (
                self._stats["successful_classifications"] / self._stats["total_classifications"]
                if self._stats["total_classifications"] > 0 else 0.0
            ),
            "average_computation_time_ms": (
                self._stats["total_computation_time_ms"] / self._stats["successful_classifications"]
                if self._stats["successful_classifications"] > 0 else 0.0
            ),
            "classifier_usage": self._stats["classifier_usage"],
            "classifier_registry_info": self.classifier_registry.get_registry_info(),
        }
    
    def reset_statistics(self) -> None:
        """Reset engine statistics."""
        self._stats = {
            "total_classifications": 0,
            "successful_classifications": 0,
            "failed_classifications": 0,
            "total_computation_time_ms": 0.0,
            "classifier_usage": {},
        }
    
    def update_config(self, config: ClassificationConfig) -> None:
        """
        Update the engine configuration.
        
        Args:
            config: New configuration
        """
        self.config = config
