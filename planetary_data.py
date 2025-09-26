# planetary_data.py
# Dynamic 11D planetary resonance simulation for Memnora

import math
import random

class PlanetaryData:
    """
    Simulates realistic planetary resonance, solar flare activity,
    and geomagnetic fluctuations to produce dynamic 11D vectors.
    """

    def __init__(self):
        # Time counter for oscillations
        self.time_counter = 0.0

        # Base values
        self.schumann_base = 7.83       # Hz
        self.solar_flare_base = 0.1     # 0-1 normalized
        self.kp_base = 2                # geomagnetic Kp index

    def update(self, dt=0.1):
        """
        Update planetary parameters over time.
        dt = time step in seconds
        """
        self.time_counter += dt

        # Schumann resonance (D3)
        self.schumann_resonance = self.schumann_base + 0.3 * math.sin(self.time_counter / 10)

        # Solar flare intensity (D5)
        self.solar_flare_index = self.solar_flare_base + 0.5 * random.random() * math.sin(self.time_counter / 5)

        # Geomagnetic Kp index (D11)
        self.kp_index = self.kp_base + random.randint(0, 3) * math.sin(self.time_counter / 15)

    def get_vector(self):
        """
        Map planetary inputs to an 11D resonance vector:

        D1-D2: neutral 0 (user or node-modified)
        D3: Schumann resonance normalized 0-1
        D4: stability oscillation 0-1
        D5: solar flare intensity 0-1
        D6: bodily resonance fluctuation 0-1
        D7-D8: spiritual/higher consciousness (-0.5 to 0.5)
        D9-D10: soul purpose/twin-flame (-0.5 to 0.5)
        D11: collective impact normalized (Kp geomagnetic)
        """
        vector = [0]*11
        vector[2] = self.schumann_resonance / 10                # D3
        vector[3] = 0.5 + 0.5 * math.sin(self.time_counter / 20) # D4
        vector[4] = min(1.0, self.solar_flare_index)            # D5
        vector[5] = random.uniform(0, 1)                        # D6
        vector[6] = random.uniform(-0.5, 0.5)                   # D7
        vector[7] = random.uniform(-0.5, 0.5)                   # D8
        vector[8] = random.uniform(-0.5, 0.5)                   # D9
        vector[9] = random.uniform(-0.5, 0.5)                   # D10
        vector[10] = min(1.0, self.kp_index / 9)                # D11 normalized
        return vector