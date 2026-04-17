import collections
import math

class CalculationEngine:
    def __init__(self, gauge_base=1676.0, twist_base_mm=3000):
        self.gauge = gauge_base
        self.twist_base = twist_base_mm
        
        # History for Twist: (chainage_mm, crosslevel_mm)
        self.history = collections.deque(maxlen=10000)
        
        # Filters for sensor stability
        self.tilt_filter = collections.deque(maxlen=10) # 10-point moving average
        
    def _moving_average(self, val, buffer):
        buffer.append(val)
        return sum(buffer) / len(buffer)

    def process_packet(self, packet):
        # 1. Distance (m to mm)
        dist_mm = packet['distance'] * 1000.0
        
        # 2. Filter Tilt and Calc Crosslevel
        # Formula: gauge * sin(tilt_rad)
        filt_tilt = self._moving_average(packet['tilt'], self.tilt_filter)
        rad = math.radians(filt_tilt)
        crosslevel = self.gauge * math.sin(rad)
        
        # 3. Store in history
        self.history.append((dist_mm, crosslevel))
        
        # 4. Calc Twist (change over twist_base)
        twist = 0.0
        twist_rate = 0.0
        
        target_ch = dist_mm - self.twist_base
        if target_ch >= 0:
            # Find closest historical point
            best_cl = 0.0
            min_err = 999999
            for ch, cl in self.history:
                err = abs(ch - target_ch)
                if err < min_err:
                    min_err = err
                    best_cl = cl
                if err < 50: break # Close enough optimization
            
            twist = abs(crosslevel - best_cl)
            twist_rate = twist / (self.twist_base / 1000.0)

        return {
            'timestamp': packet['timestamp'],
            'distance': packet['distance'],
            'tilt': filt_tilt,
            'crosslevel': crosslevel,
            'twist': twist,
            'twist_rate': twist_rate,
            'gauge': self.gauge,
            'status': 'ALARM' if twist_rate > 2.0 else 'OK'
        }
        state["twist_3m"] = twist_3m
        self.last_processed = state
        return state

    def get_latest(self):
        return self.last_processed
