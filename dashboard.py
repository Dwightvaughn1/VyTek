# dashboard.py
# 3D Visualization Dashboard for Memnora 11D Resonance Nodes

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from resonance_node import ResonanceNode
from planetary_data import PlanetaryData
import numpy as np

# ----------------------------
# 1️⃣ Setup Nodes & Planetary Data
# ----------------------------
num_nodes = 30
nodes = [ResonanceNode() for _ in range(num_nodes)]
planet = PlanetaryData()  # Planetary input vector generator

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# ----------------------------
# 2️⃣ Update Function
# ----------------------------
def update(frame):
    ax.cla()  # Clear previous frame
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(0, 1)
    ax.set_xlabel('D1: Constructive/Destructive')
    ax.set_ylabel('D2: Emotional Alignment')
    ax.set_zlabel('D3: Planetary Context')
    ax.set_title('Memnora 11D Resonance Nodes Visualization')

    # Update planetary inputs
    planet.update()
    source_vector = np.array(planet.get_vector())

    xs, ys, zs = [], [], []
    colors, sizes, alphas = [], [], []

    for node in nodes:
        node.stabilize(source_vector)

        # Map first 3 dimensions to 3D axes
        x, y, z = node.vector[0], node.vector[1], node.vector[2]
        xs.append(x)
        ys.append(y)
        zs.append(z)

        # 4th dimension → red channel for color
        d4 = (node.vector[3] + 1) / 2
        # 7th and 8th dimensions → green & blue channels
        d7 = (node.vector[6] + 1) / 2
        d8 = (node.vector[7] + 1) / 2
        colors.append((d4, d7, d8))

        # 5th & 6th dimensions → node size
        size = 50 + 200 * ((node.vector[4] + node.vector[5]) / 2 + 1) / 2
        sizes.append(size)

        # 9th-11th dimensions → alpha (transparency)
        alpha = min(1, ((node.vector[8] + node.vector[9] + node.vector[10]) / 3 + 1) / 2)
        alphas.append(alpha)

    # Plot scatter with dynamic coloring, sizing, and alpha
    ax.scatter(xs, ys, zs, c=colors, s=sizes, alpha=0.7, edgecolors='w', linewidths=0.5)

# ----------------------------
# 3️⃣ Run Animation
# ----------------------------
ani = FuncAnimation(fig, update, frames=300, interval=100)
plt.show()