"""Dataset loading utilities for ClassificationBench."""

import json
from pathlib import Path
from typing import Dict, List, Any


class DatasetLoader:
    """Load and manage benchmark datasets."""
    
    def __init__(self, dataset_dir: Path):
        self.dataset_dir = dataset_dir
    
    def load_dataset(self, memory_type: str) -> Dict[str, Any]:
        """Load a specific memory type dataset."""
        file_path = self.dataset_dir / f"{memory_type}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_datasets(self) -> Dict[str, Dict[str, Any]]:
        """Load all available datasets."""
        datasets = {}
        
        dataset_files = [
            "identity", "goal", "preference", "relationship",
            "project", "skill", "procedural", "task",
            "episodic", "semantic", "emotional", "temporal", "robustness"
        ]
        
        for dataset_name in dataset_files:
            try:
                datasets[dataset_name] = self.load_dataset(dataset_name)
            except FileNotFoundError:
                print(f"Warning: Dataset {dataset_name} not found, skipping")
        
        return datasets
    
    def get_all_test_cases(self) -> List[Dict[str, Any]]:
        """Get all test cases from all datasets."""
        all_cases = []
        datasets = self.load_all_datasets()
        
        for dataset_name, dataset in datasets.items():
            test_cases = dataset.get("test_cases", [])
            for case in test_cases:
                case["memory_type"] = dataset_name
                all_cases.append(case)
        
        return all_cases
    
    def get_test_cases_by_memory_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """Get test cases for a specific memory type."""
        dataset = self.load_dataset(memory_type)
        return dataset.get("test_cases", [])
    
    def get_total_test_case_count(self) -> int:
        """Get total number of test cases across all datasets."""
        datasets = self.load_all_datasets()
        total = 0
        
        for dataset in datasets.values():
            total += len(dataset.get("test_cases", []))
        
        return total
