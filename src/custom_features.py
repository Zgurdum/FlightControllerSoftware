"""
Custom Features Module
Extensible framework for adding custom drone programming features
"""

import logging
from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CustomFeature(ABC):
    """Base class for custom features"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.callbacks = {}
    
    @abstractmethod
    def initialize(self, flight_controller):
        """Initialize the feature"""
        pass
    
    @abstractmethod
    def update(self, telemetry: Dict[str, Any]):
        """Update feature with latest telemetry"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Cleanup when feature is disabled"""
        pass
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for feature event"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def trigger_callback(self, event: str, data: Any = None):
        """Trigger all callbacks for an event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Callback error in {self.name}: {e}")


class FeatureManager:
    """Manage custom features"""
    
    def __init__(self):
        self.features: Dict[str, CustomFeature] = {}
    
    def register_feature(self, feature: CustomFeature):
        """Register a custom feature"""
        self.features[feature.name] = feature
        logger.info(f"Registered feature: {feature.name}")
    
    def enable_feature(self, name: str, flight_controller):
        """Enable a feature"""
        if name in self.features:
            feature = self.features[name]
            feature.initialize(flight_controller)
            feature.enabled = True
            logger.info(f"Enabled feature: {name}")
            return True
        return False
    
    def disable_feature(self, name: str):
        """Disable a feature"""
        if name in self.features:
            feature = self.features[name]
            feature.shutdown()
            feature.enabled = False
            logger.info(f"Disabled feature: {name}")
            return True
        return False
    
    def update_all(self, telemetry: Dict[str, Any]):
        """Update all enabled features"""
        for feature in self.features.values():
            if feature.enabled:
                try:
                    feature.update(telemetry)
                except Exception as e:
                    logger.error(f"Feature update error ({feature.name}): {e}")
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features"""
        return [name for name, feature in self.features.items() if feature.enabled]


# Custom Feature Examples (Placeholder for future implementations)

class DataLogger(CustomFeature):
    """Log telemetry data to file"""
    
    def __init__(self):
        super().__init__("DataLogger")
        self.log_file = None
    
    def initialize(self, flight_controller):
        """Initialize data logger"""
        self.log_file = open("data/flight_log.csv", "w")
        self.log_file.write("timestamp,gyro_x,gyro_y,gyro_z,acc_x,acc_y,acc_z,m1,m2,m3,m4\n")
        logger.info("Data logger initialized")
    
    def update(self, telemetry: Dict[str, Any]):
        """Log telemetry data"""
        if self.log_file:
            import time
            sensors = telemetry.get('sensors', {})
            motors = telemetry.get('motors', [0, 0, 0, 0])
            
            gyro = sensors.get('gyro', {})
            acc = sensors.get('accelerometer', {})
            
            line = f"{time.time()},{gyro.get('x', 0)},{gyro.get('y', 0)},{gyro.get('z', 0)}," \
                   f"{acc.get('x', 0)},{acc.get('y', 0)},{acc.get('z', 0)}," \
                   f"{motors[0] if len(motors) > 0 else 0}," \
                   f"{motors[1] if len(motors) > 1 else 0}," \
                   f"{motors[2] if len(motors) > 2 else 0}," \
                   f"{motors[3] if len(motors) > 3 else 0}\n"
            self.log_file.write(line)
            self.log_file.flush()
    
    def shutdown(self):
        """Close log file"""
        if self.log_file:
            self.log_file.close()
            logger.info("Data logger closed")


class MotorTest(CustomFeature):
    """Test motors individually"""
    
    def __init__(self):
        super().__init__("MotorTest")
        self.fc = None
        self.test_motor = None
        self.test_speed = 1100
    
    def initialize(self, flight_controller):
        """Initialize motor test"""
        self.fc = flight_controller
        logger.info("Motor test initialized")
    
    def update(self, telemetry: Dict[str, Any]):
        """Update motor test"""
        pass
    
    def shutdown(self):
        """Stop motor test"""
        logger.info("Motor test stopped")
    
    def test_single_motor(self, motor_index: int, speed: int = 1100):
        """Test a single motor"""
        # TODO: Implement motor testing via MSP commands
        pass


class SensorAnalyzer(CustomFeature):
    """Analyze sensor data for drift and issues"""
    
    def __init__(self):
        super().__init__("SensorAnalyzer")
        self.gyro_drift = [0, 0, 0]
        self.samples = 0
    
    def initialize(self, flight_controller):
        """Initialize sensor analyzer"""
        logger.info("Sensor analyzer initialized")
    
    def update(self, telemetry: Dict[str, Any]):
        """Analyze sensor data"""
        sensors = telemetry.get('sensors', {})
        gyro = sensors.get('gyro', {})
        
        if gyro:
            # Simple drift detection
            for axis, key in enumerate(['x', 'y', 'z']):
                self.gyro_drift[axis] += gyro.get(key, 0)
            self.samples += 1
            
            if self.samples % 100 == 0:
                avg_drift = [d / self.samples for d in self.gyro_drift]
                if any(abs(d) > 5 for d in avg_drift):
                    self.trigger_callback('drift_detected', avg_drift)
    
    def shutdown(self):
        """Stop sensor analyzer"""
        logger.info("Sensor analyzer stopped")


# Initialize feature manager
feature_manager = FeatureManager()
