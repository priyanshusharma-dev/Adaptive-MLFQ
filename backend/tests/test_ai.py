import pytest
from app.scheduler.process import Process, ProcessType
from app.ai.feature_extractor import FeatureExtractor
from app.ai.classifier import classifier_instance
from app.ai.predictor import AdaptivePredictor

def test_feature_extraction():
    p = Process("P1", 0, cpu_bursts=[10, 20], io_bursts=[5])
    features = FeatureExtractor.extract(p)
    
    assert features[0] == 15.0 # avg cpu
    assert features[1] == 5.0  # avg io
    assert features[2] == 0.5  # io freq (1/2)
    assert features[3] == 3.0  # cpu/io ratio
    assert features[4] == 50.0 # variance

def test_classifier_training_and_prediction():
    # Model should auto-train on first predict
    
    cpu_heavy = Process("P1", 0, cpu_bursts=[50, 60, 40], io_bursts=[2, 1])
    io_heavy = Process("P2", 0, cpu_bursts=[2, 3, 2, 1], io_bursts=[40, 50, 30])
    
    pred_cpu = classifier_instance.predict(cpu_heavy)
    assert pred_cpu == ProcessType.CPU_BOUND
    
    pred_io = classifier_instance.predict(io_heavy)
    assert pred_io == ProcessType.IO_BOUND

def test_adaptive_predictor():
    io_heavy = Process("P2", 0, cpu_bursts=[2, 3, 2, 1], io_bursts=[40, 50, 30])
    
    result = AdaptivePredictor.get_adaptive_policy(io_heavy)
    
    assert result["prediction"]["type"] == ProcessType.IO_BOUND
    assert result["policy"]["recommended_queue"] == 0
    assert result["policy"]["recommended_quantum"] == 4
