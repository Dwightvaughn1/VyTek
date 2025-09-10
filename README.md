# resonance_node.py

import numpy as np
import random

class ResonanceNode:
    """
    Represents a node in 11-dimensional resonance space.
    Each node has a vector and can stabilize towards a source vector.
    """

    def __init__(self):
        # Initialize an 11D vector with random values
        # Dimensions represent: D1=Constructive/Destructive, D2=Emotional, D3=Planetary, ...
        self.vector = np.array([random.uniform(-1,1) for _ in range(11)])

    def stabilize(self, source_vector, factor=0.1):
        """
        Simulates the Infinity Orbs process:
        Pull the node toward a source coherence vector.
        """
        # Calculate coherence score with the source vector
        coherence_score = np.dot(self.vector, source_vector)

        # Determine how much to move toward the source
        stability_factor = 1.0 - np.clip(coherence_score, 0, 1) / 2
        direction_vector = source_vector - self.vector

        # Apply stabilization
        self.vector += direction_vector * stability_factor * factor

        # Clamp values between -1 and 1 to stay within resonance bounds
        self.vector = np.clip(self.vector, -1, 1)

    def __repr__(self):
        return f"ResonanceNode(vector={self.vector})"
