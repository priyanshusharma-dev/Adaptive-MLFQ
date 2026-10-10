from sklearn.ensemble import RandomForestClassifier
import numpy as np
from typing import List
from app.scheduler.process import Process, ProcessType
from app.ai.feature_extractor import FeatureExtractor
from app.services.workload_generator import WorkloadGenerator

class BehaviourClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.is_trained = False
        
        self.classes = [
            ProcessType.CPU_BOUND,
            ProcessType.IO_BOUND,
            ProcessType.INTERACTIVE
        ]
        
    def train(self):
        """Generates synthetic data and trains the random forest classifier."""
        X = []
        y = []
        
        # We generate a dataset using our workload generator
        dataset_sizes = {
            "cpu_heavy": ProcessType.CPU_BOUND,
            "io_heavy": ProcessType.IO_BOUND,
            "interactive": ProcessType.INTERACTIVE
        }
        
        for workload_type, label in dataset_sizes.items():
            configs = WorkloadGenerator.generate(workload_type, 100, seed=42)
            for cfg in configs:
                # Convert config to process to use feature extractor
                p = Process(cfg.pid, cfg.arrival_time, cfg.cpu_bursts, cfg.io_bursts)
                features = FeatureExtractor.extract(p)
                X.append(features)
                y.append(label.value)
                
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict(self, process: Process) -> ProcessType:
        if not self.is_trained:
            self.train()
            
        features = FeatureExtractor.extract(process)
        prediction = self.model.predict([features])[0]
        
        return ProcessType(prediction)
        
    def predict_with_confidence(self, process: Process) -> dict:
        if not self.is_trained:
            self.train()
            
        features = FeatureExtractor.extract(process)
        probabilities = self.model.predict_proba([features])[0]
        prediction = self.model.classes_[np.argmax(probabilities)]
        confidence = float(np.max(probabilities))
        
        return {
            "type": ProcessType(prediction),
            "confidence": confidence,
            "features": {
                "avg_cpu_burst": features[0],
                "avg_io_burst": features[1],
                "io_frequency": features[2],
                "cpu_io_ratio": features[3],
                "burst_variance": features[4],
                "preemption_count": features[5]
            }
        }

# Global singleton instance to avoid retraining
classifier_instance = BehaviourClassifier()
