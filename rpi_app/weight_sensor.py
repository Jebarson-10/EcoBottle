"""
Weight Sensor Interface for HX711 Load Cell.
Includes mock mode for testing without hardware.
"""
import random
import config


class WeightSensor:
    """Interface for the HX711 weight sensor."""

    def __init__(self, mock=None):
        """
        Initialize the weight sensor.
        
        Args:
            mock: Override config.MOCK_WEIGHT_SENSOR if provided
        """
        self.mock = mock if mock is not None else config.MOCK_WEIGHT_SENSOR
        self.hx = None
        self.is_ready = False

        if not self.mock:
            self._init_hardware()
        else:
            print("[INFO] Weight sensor running in MOCK mode.")
            self.is_ready = True

    def _init_hardware(self):
        """Initialize the HX711 hardware."""
        try:
            import RPi.GPIO as GPIO
            from hx711 import HX711

            self.hx = HX711(
                dout_pin=config.HX711_DT_PIN,
                pd_sck_pin=config.HX711_SCK_PIN
            )
            self.hx.set_reading_format("MSB", "MSB")
            self.hx.set_reference_unit(config.WEIGHT_REFERENCE_UNIT)
            self.hx.reset()
            self.hx.tare()
            self.is_ready = True
            print("[INFO] HX711 weight sensor initialized successfully.")

        except ImportError:
            print("[WARNING] RPi.GPIO or hx711 not available. Switching to mock mode.")
            self.mock = True
            self.is_ready = True

        except Exception as e:
            print(f"[ERROR] Failed to initialize weight sensor: {e}")
            print("[INFO] Switching to mock mode.")
            self.mock = True
            self.is_ready = True

    def read_weight(self) -> float:
        """
        Read the current weight from the sensor.
        
        Returns:
            Weight in grams (float). Returns 0 if sensor not ready.
        """
        if not self.is_ready:
            return 0.0

        if self.mock:
            return self._mock_read()

        try:
            # Average of 5 readings for stability
            weight = self.hx.get_weight(5)
            self.hx.power_down()
            self.hx.power_up()

            # Clamp negative values to 0
            return max(0.0, round(weight, 2))

        except Exception as e:
            print(f"[ERROR] Failed to read weight: {e}")
            return 0.0

    def _mock_read(self) -> float:
        """Generate a simulated weight reading for testing."""
        # Simulate typical plastic bottle weights (10g to 50g)
        # with some variation
        base_weights = [12, 15, 18, 20, 22, 25, 28, 30, 35, 40, 45, 50]
        weight = random.choice(base_weights) + random.uniform(-2, 2)
        return round(max(0, weight), 2)

    def tare(self):
        """Reset the scale to zero."""
        if self.mock:
            print("[MOCK] Scale tared.")
            return

        if self.hx:
            try:
                self.hx.tare()
                print("[INFO] Scale tared successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to tare: {e}")

    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.mock and self.hx:
            try:
                import RPi.GPIO as GPIO
                GPIO.cleanup()
            except:
                pass
