from app.scheduler.process import Process, ProcessType
from app.ai.classifier import classifier_instance

class AdaptivePredictor:
    @staticmethod
    def get_adaptive_policy(process: Process) -> dict:
        """
        Takes a process, classifies it using the ML model, 
        and returns recommended queue and quantum.
        """
        prediction_data = classifier_instance.predict_with_confidence(process)
        p_type = prediction_data["type"]
        
        # Policy definition based on research parameters
        if p_type == ProcessType.CPU_BOUND:
            # CPU bound favors lower priority queues with larger quantums
            policy = {
                "recommended_queue": 2, 
                "recommended_quantum": 16,
                "reason": "Low I/O frequency, high CPU burst average."
            }
        elif p_type == ProcessType.IO_BOUND:
            # IO bound favors higher priority queues with smaller quantums
            policy = {
                "recommended_queue": 0,
                "recommended_quantum": 4,
                "reason": "High I/O frequency, low CPU burst average."
            }
        elif p_type == ProcessType.INTERACTIVE:
            # Interactive favors medium/high priority with very short quantums
            policy = {
                "recommended_queue": 1,
                "recommended_quantum": 4,
                "reason": "Many short CPU and I/O bursts."
            }
        else:
            policy = {
                "recommended_queue": 0,
                "recommended_quantum": 8,
                "reason": "Fallback default policy."
            }
            
        return {
            "prediction": prediction_data,
            "policy": policy
        }
