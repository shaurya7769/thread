import math
from collections import deque

class CalculationEngine:
    def __init__(self, gauge_base=1676.0):
        self.gauge_base = gauge_base
        # History for Twist calculation (e.g., 3m and 10m)
        self.history = deque(maxlen=1000) 
        self.last_processed = None

    def process_packet(self, packet):
        """
        Calculates:
        1. Cross-level (mm) = sinus(tilt_deg) * gauge
        2. Twist = Change in cross-level over a distance base
        """
        tilt_deg = packet["tilt"]
        dist_m = packet["distance"]
        
        # Cross-level in mm
        cross_level_mm = math.sin(math.radians(tilt_deg)) * self.gauge_base
        
        # Store in history
        state = {
            "distance": dist_m,
            "cross_level": cross_level_mm,
            "tilt": tilt_deg,
            "gauge": packet["gauge"],
            "timestamp": packet["timestamp"]
        }
        self.history.append(state)
        
        # Calculate Twist (3.0m base)
        twist_3m = 0.0
        if len(self.history) > 1:
            for old_state in reversed(self.history):
                if (dist_m - old_state["distance"]) >= 3.0:
                    twist_3m = (cross_level_mm - old_state["cross_level"])
                    break
        
        state["twist_3m"] = twist_3m
        self.last_processed = state
        return state

    def get_latest(self):
        return self.last_processed
