# dashboard_video.py
# Enhanced 3D Visualization Dashboard for Memnora with Video Intelligence Integration

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import json
import threading
import time
from collections import deque
from datetime import datetime

# Try to import video intelligence components
try:
    from video_sense import VideoSense, get_video_sense
    from twelvelabs_client import TwelveLabsClient
    VIDEO_INTELLIGENCE_ENABLED = True
except ImportError:
    VIDEO_INTELLIGENCE_ENABLED = False

# Try to import existing components
try:
    from resonance_node import ResonanceNode
    from planetary_data import PlanetaryData
    LEGACY_COMPONENTS_AVAILABLE = True
except ImportError:
    # Fallback implementations
    LEGACY_COMPONENTS_AVAILABLE = False

# Mock implementations for when original components aren't available
if not LEGACY_COMPONENTS_AVAILABLE:
    class ResonanceNode:
        def __init__(self):
            self.vector = np.random.uniform(-1, 1, 11)

        def stabilize(self, source_vector):
            source_vector = np.array(source_vector)
            if source_vector.shape != self.vector.shape:
                raise ValueError("source_vector must match node vector dimensions")

            coherence_score = np.dot(self.vector, source_vector)
            stability_factor = 1.0 - np.clip(coherence_score / 11.0, 0, 1) / 2
            direction_vector = source_vector - self.vector
            self.vector += direction_vector * stability_factor * 0.1
            self.vector = np.clip(self.vector, -1, 1)

    class PlanetaryData:
        def __init__(self):
            self.vector = np.zeros(11)

        def update(self):
            self.vector = np.random.uniform(-0.5, 0.5, 11)

        def get_vector(self):
            return self.vector.tolist()

class VideoDataManager:
    """Manages real-time video intelligence data for visualization"""

    def __init__(self):
        self.video_analyses = deque(maxlen=100)  # Store last 100 video analyses
        self.current_video_data = None
        self.video_source_vectors = deque(maxlen=50)  # Video-derived source vectors
        self.emotional_timeline = deque(maxlen=200)  # Emotional state timeline
        self.scene_transitions = deque(maxlen=50)  # Scene transition data

    def add_video_analysis(self, video_payload):
        """Add new video analysis data to the visualization system"""
        if not video_payload:
            return

        analysis_entry = {
            'timestamp': datetime.now(),
            'video_id': video_payload.get('video_id', 'unknown'),
            'resonance_vector': video_payload.get('resonance_vector', [0] * 11),
            'coherence_score': video_payload.get('coherence_score', 0.5),
            'emotional_state': video_payload.get('emotion', 'neutral'),
            'scene_count': len(video_payload.get('scenes', [])),
            'object_count': len(video_payload.get('objects', [])),
            'speech_detected': bool(video_payload.get('speech_transcript')),
            'temporal_patterns': video_payload.get('temporal_patterns', {})
        }

        self.video_analyses.append(analysis_entry)
        self.current_video_data = analysis_entry

        # Convert resonance vector to source vector for nodes
        if analysis_entry['resonance_vector']:
            vector = np.array(analysis_entry['resonance_vector'])
            # Amplify video signal for visualization
            amplified_vector = vector * 1.2
            self.video_source_vectors.append(amplified_vector.tolist())

        # Extract emotional timeline data
        self._extract_emotional_timeline(video_payload)

        # Track scene transitions
        self._track_scene_transitions(video_payload)

    def _extract_emotional_timeline(self, video_payload):
        """Extract emotional state data from video analysis"""
        emotional_data = {
            'timestamp': datetime.now(),
            'primary_emotion': video_payload.get('emotion', 'neutral'),
            'coherence': video_payload.get('coherence_score', 0.5),
            'intensity': self._calculate_emotional_intensity(video_payload),
            'stability': self._assess_emotional_stability(video_payload)
        }

        self.emotional_timeline.append(emotional_data)

    def _calculate_emotional_intensity(self, video_payload):
        """Calculate emotional intensity from video analysis"""
        intensity = 0.5  # Base intensity

        # Factors affecting intensity
        if video_payload.get('speech_patterns'):
            speech_energy = video_payload['speech_patterns'].get('energy_level', 0.5)
            intensity = (intensity + speech_energy) / 2

        if video_payload.get('temporal_patterns'):
            motion = video_payload['temporal_patterns'].get('motion_intensity', 0.5)
            intensity = (intensity + motion) / 2

        return min(intensity, 1.0)

    def _assess_emotional_stability(self, video_payload):
        """Assess emotional stability from video content"""
        stability = 0.5  # Base stability

        if video_payload.get('temporal_patterns'):
            variance = video_payload['temporal_patterns'].get('temporal_variance', 5.0)
            scene_count = video_payload['temporal_patterns'].get('scene_count', 1)

            # Lower variance and reasonable scene count indicate stability
            if variance < 3.0 and 2 <= scene_count <= 10:
                stability = 0.8
            elif variance > 8.0 or scene_count > 20:
                stability = 0.2

        return stability

    def _track_scene_transitions(self, video_payload):
        """Track scene transitions for temporal flow visualization"""
        scenes = video_payload.get('scenes', [])
        if len(scenes) > 1:
            transition_data = {
                'timestamp': datetime.now(),
                'transition_count': len(scenes) - 1,
                'avg_duration': np.mean([scene.get('end', 0) - scene.get('start', 0) for scene in scenes]),
                'flow_pattern': self._analyze_flow_pattern(scenes)
            }

            self.scene_transitions.append(transition_data)

    def _analyze_flow_pattern(self, scenes):
        """Analyze temporal flow pattern from scenes"""
        if not scenes:
            return 'stable'

        durations = [scene.get('end', 0) - scene.get('start', 0) for scene in scenes]
        if not durations:
            return 'stable'

        variance = np.var(durations)
        if variance < 2.0:
            return 'rhythmic'
        elif variance > 10.0:
            return 'chaotic'
        else:
            return 'dynamic'

    def get_latest_source_vector(self, fallback_vector=None):
        """Get the latest source vector for node stabilization"""
        if self.video_source_vectors:
            return np.array(self.video_source_vectors[-1])
        elif fallback_vector is not None:
            return np.array(fallback_vector)
        else:
            return np.zeros(11)

class VideoEnhancedDashboard:
    """Enhanced dashboard with video intelligence integration"""

    def __init__(self, num_nodes=30):
        self.num_nodes = num_nodes
        self.nodes = [ResonanceNode() for _ in range(num_nodes)]
        self.planet = PlanetaryData() if LEGACY_COMPONENTS_AVAILABLE else PlanetaryData()
        self.video_manager = VideoDataManager()

        # Enhanced visualization settings
        self.video_mode = False
        self.show_video_trail = False
        self.emotional_overlay = True
        self.frame_count = 0

        # Setup the figure
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Memnora Video Intelligence Dashboard - 11D Resonance Visualization', fontsize=16, fontweight='bold')

        # Main 3D visualization
        self.ax = self.fig.add_subplot(121, projection='3d')

        # Video analysis info panel
        self.info_ax = self.fig.add_subplot(222)
        self.info_ax.axis('off')

        # Emotional timeline chart
        self.emotion_ax = self.fig.add_subplot(224)

        # Initialize video intelligence if available
        if VIDEO_INTELLIGENCE_ENABLED:
            self.video_sense = get_video_sense()
            self._setup_video_monitoring()

    def _setup_video_monitoring(self):
        """Setup background monitoring for video analysis results"""
        def monitor_videos():
            while True:
                try:
                    # Simulate receiving video analysis data
                    # In real implementation, this would connect to the video analysis API
                    time.sleep(5)  # Check every 5 seconds

                    # For demo, generate random video data occasionally
                    if np.random.random() > 0.8:  # 20% chance
                        mock_video_data = self._generate_mock_video_data()
                        self.video_manager.add_video_analysis(mock_video_data)

                except Exception as e:
                    print(f"Video monitoring error: {e}")
                    time.sleep(10)  # Wait longer on error

        monitor_thread = threading.Thread(target=monitor_videos, daemon=True)
        monitor_thread.start()

    def _generate_mock_video_data(self):
        """Generate mock video analysis data for demonstration"""
        emotions = ['happy', 'focused', 'calm', 'energetic', 'contemplative']
        selected_emotion = np.random.choice(emotions)

        mock_data = {
            'video_id': f"demo_{int(time.time())}",
            'resonance_vector': np.random.uniform(-0.8, 0.8, 11).tolist(),
            'coherence_score': np.random.uniform(0.3, 0.9),
            'emotion': selected_emotion,
            'scenes': [
                {'start': i * 10, 'end': (i + 1) * 10, 'description': f'Scene {i+1}'}
                for i in range(np.random.randint(3, 8))
            ],
            'objects': [{'name': f'object_{i}', 'confidence': np.random.random()} for i in range(5)],
            'speech_transcript': "Sample speech transcript for demonstration" if np.random.random() > 0.5 else None,
            'temporal_patterns': {
                'scene_count': np.random.randint(3, 10),
                'avg_scene_duration': np.random.uniform(5, 15),
                'motion_intensity': np.random.uniform(0.2, 0.9),
                'temporal_variance': np.random.uniform(1, 8)
            }
        }

        return mock_data

    def update(self, frame):
        """Main update function for the enhanced visualization"""
        self.frame_count = frame
        self.ax.cla()

        # Get appropriate source vector
        if self.video_mode and self.video_manager.video_source_vectors:
            source_vector = self.video_manager.get_latest_source_vector()
            self.ax.set_title('Video Intelligence Mode - Real-time Analysis', fontsize=14)
        else:
            self.planet.update()
            source_vector = np.array(self.planet.get_vector())
            self.ax.set_title('Planetary Resonance Mode - Environmental Inputs', fontsize=14)

        # Set axis labels based on video intelligence context
        if self.video_mode:
            self.ax.set_xlabel('Physical Environment (D1-3)')
            self.ax.set_ylabel('Social Patterns (D4-6)')
            self.ax.set_zlabel('Emotional Context (D7-9)')
        else:
            self.ax.set_xlabel('D1: Constructive/Destructive')
            self.ax.set_ylabel('D2: Emotional Alignment')
            self.ax.set_zlabel('D3: Planetary Context')

        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)

        # Update nodes with video intelligence
        xs, ys, zs = [], [], []
        colors, sizes, alphas = [], [], []

        for node in self.nodes:
            node.stabilize(source_vector)

            # Enhanced dimension mapping with video intelligence
            x, y, z = node.vector[0], node.vector[1], node.vector[2]
            xs.append(x)
            ys.append(y)
            zs.append(z)

            # Enhanced color mapping with video emotional context
            if self.video_mode and self.video_manager.current_video_data:
                # Use video emotional data for coloring
                emotional_state = self.video_manager.current_video_data['emotional_state']
                coherence = self.video_manager.current_video_data['coherence_score']

                # Map emotional state to color
                emotion_colors = {
                    'happy': (0.9, 0.7, 0.2),
                    'focused': (0.2, 0.8, 0.9),
                    'calm': (0.3, 0.9, 0.5),
                    'energetic': (0.9, 0.3, 0.2),
                    'contemplative': (0.6, 0.3, 0.9)
                }

                base_color = emotion_colors.get(emotional_state, (0.5, 0.5, 0.5))
                # Modulate by dimensions 4, 7, 8
                d4, d7, d8 = (node.vector[3] + 1) / 2, (node.vector[6] + 1) / 2, (node.vector[7] + 1) / 2
                color = tuple(c * (0.5 + 0.5 * v) for c, v in zip(base_color, (d4, d7, d8)))
            else:
                # Standard coloring
                d4, d7, d8 = (node.vector[3] + 1) / 2, (node.vector[6] + 1) / 2, (node.vector[7] + 1) / 2
                color = (d4, d7, d8)

            colors.append(color)

            # Enhanced size mapping with video data
            if self.video_mode and self.video_manager.current_video_data:
                # Incorporate video intensity into node size
                video_intensity = self.video_manager._calculate_emotional_intensity(
                    self.video_manager.current_video_data
                )
                size = 50 + 300 * ((node.vector[4] + node.vector[5]) / 2 + 1) / 2 * (0.5 + video_intensity)
            else:
                size = 50 + 200 * ((node.vector[4] + node.vector[5]) / 2 + 1) / 2

            sizes.append(size)

            # Enhanced alpha with temporal flow
            if self.video_mode and self.video_manager.scene_transitions:
                # Use scene transition data for alpha modulation
                transition_data = self.video_manager.scene_transitions[-1] if self.video_manager.scene_transitions else None
                if transition_data:
                    flow_multiplier = 0.7 if transition_data['flow_pattern'] == 'rhythmic' else 1.0
                else:
                    flow_multiplier = 1.0

                alpha = min(1, ((node.vector[8] + node.vector[9] + node.vector[10]) / 3 + 1) / 2 * flow_multiplier)
            else:
                alpha = min(1, ((node.vector[8] + node.vector[9] + node.vector[10]) / 3 + 1) / 2)

            alphas.append(alpha)

        # Plot main nodes
        scatter = self.ax.scatter(xs, ys, zs, c=colors, s=sizes, alpha=0.7, edgecolors='w', linewidths=0.5)

        # Add video trail visualization
        if self.show_video_trail and len(self.video_manager.video_source_vectors) > 1:
            self._add_video_trail()

        # Update info panel
        self._update_info_panel()

        # Update emotional timeline
        self._update_emotional_timeline()

        # Toggle video mode periodically for demo
        if frame % 100 == 50:  # Switch to video mode at frame 50
            self.video_mode = True
            self.show_video_trail = True
        elif frame % 100 == 0:  # Switch back at frame 0
            self.video_mode = False
            self.show_video_trail = False

    def _add_video_trail(self):
        """Add visualization trail for video-derived resonance changes"""
        if len(self.video_manager.video_source_vectors) < 2:
            return

        vectors = list(self.video_manager.video_source_vectors)[-10:]  # Last 10 vectors
        xs, ys, zs = [], [], []

        for vector in vectors:
            xs.append(vector[0])
            ys.append(vector[1])
            zs.append(vector[2])

        # Plot trail with gradient
        for i in range(len(xs) - 1):
            alpha = (i + 1) / len(xs) * 0.5
            self.ax.plot(xs[i:i+2], ys[i:i+2], zs[i:i+2],
                        color='cyan', alpha=alpha, linewidth=2)

    def _update_info_panel(self):
        """Update the video analysis information panel"""
        self.info_ax.clear()
        self.info_ax.axis('off')

        info_text = "Video Intelligence Status\n" + "="*25 + "\n\n"

        if VIDEO_INTELLIGENCE_ENABLED:
            info_text += "🎬 VideoSense: ENABLED\n"
            info_text += f"📊 Analyses: {len(self.video_manager.video_analyses)}\n"

            if self.video_manager.current_video_data:
                data = self.video_manager.current_video_data
                info_text += f"\n🎥 Current Analysis:\n"
                info_text += f"   Video ID: {data['video_id'][:12]}...\n"
                info_text += f"   Emotion: {data['emotional_state']}\n"
                info_text += f"   Coherence: {data['coherence_score']:.2f}\n"
                info_text += f"   Scenes: {data['scene_count']}\n"
                info_text += f"   Objects: {data['object_count']}\n"
                info_text += f"   Speech: {'Yes' if data['speech_detected'] else 'No'}\n"

                if data.get('temporal_patterns'):
                    patterns = data['temporal_patterns']
                    info_text += f"   Avg Duration: {patterns.get('avg_scene_duration', 0):.1f}s\n"
                    info_text += f"   Motion: {patterns.get('motion_intensity', 0):.2f}\n"
        else:
            info_text += "🎬 VideoSense: DISABLED\n"
            info_text += "Install video components for full functionality\n"

        info_text += f"\n🔄 Mode: {'Video Intelligence' if self.video_mode else 'Planetary Resonance'}\n"
        info_text += f"⏱️ Frame: {self.frame_count}\n"

        self.info_ax.text(0.1, 0.9, info_text, transform=self.info_ax.transAxes,
                        fontsize=10, verticalalignment='top', fontfamily='monospace')

    def _update_emotional_timeline(self):
        """Update the emotional timeline chart"""
        self.emotion_ax.clear()

        if not self.video_manager.emotional_timeline:
            self.emotion_ax.set_title('Emotional Timeline (No Data)')
            self.emotion_ax.set_xlabel('Time')
            self.emotion_ax.set_ylabel('Coherence')
            return

        timeline = list(self.video_manager.emotional_timeline)[-50:]  # Last 50 entries

        times = range(len(timeline))
        coherence_scores = [entry['coherence'] for entry in timeline]
        intensities = [entry['intensity'] for entry in timeline]

        self.emotion_ax.plot(times, coherence_scores, 'b-', label='Coherence', linewidth=2)
        self.emotion_ax.plot(times, intensities, 'r-', label='Intensity', linewidth=1, alpha=0.7)

        # Highlight current emotion
        if self.video_manager.current_video_data:
            current_emotion = self.video_manager.current_video_data['emotional_state']
            self.emotion_ax.set_title(f'Emotional Timeline - Current: {current_emotion.upper()}')
        else:
            self.emotion_ax.set_title('Emotional Timeline')

        self.emotion_ax.set_xlabel('Analysis #')
        self.emotion_ax.set_ylabel('Value')
        self.emotion_ax.legend(loc='upper right')
        self.emotion_ax.grid(True, alpha=0.3)
        self.emotion_ax.set_ylim(0, 1)

    def run(self):
        """Start the enhanced visualization"""
        ani = FuncAnimation(self.fig, self.update, frames=1000, interval=100, repeat=True)

        # Add keyboard controls
        def on_key(event):
            if event.key == 'v':
                self.video_mode = not self.video_mode
                print(f"Video mode: {'ON' if self.video_mode else 'OFF'}")
            elif event.key == 't':
                self.show_video_trail = not self.show_video_trail
                print(f"Video trail: {'ON' if self.show_video_trail else 'OFF'}")
            elif event.key == 'e':
                self.emotional_overlay = not self.emotional_overlay
                print(f"Emotional overlay: {'ON' if self.emotional_overlay else 'OFF'}")

        self.fig.canvas.mpl_connect('key_press_event', on_key)

        # Add instructions
        print("\n" + "="*50)
        print("MEMNORA VIDEO INTELLIGENCE DASHBOARD")
        print("="*50)
        print("Controls:")
        print("  'v' - Toggle video intelligence mode")
        print("  't' - Toggle video trail visualization")
        print("  'e' - Toggle emotional overlay")
        print("  'q' - Quit visualization")
        print("="*50 + "\n")

        plt.tight_layout()
        plt.show()

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    # Create and run the enhanced dashboard
    dashboard = VideoEnhancedDashboard(num_nodes=25)
    dashboard.run()