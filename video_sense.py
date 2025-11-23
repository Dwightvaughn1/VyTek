# video_sense.py
# Memnora VideoSense Module - Video Intelligence to Resonance Conversion
# Author: VyTek VideoSense Team
# Description: Bridge TwelveLabs video intelligence with Memnora resonance matrix

import numpy as np
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from twelvelabs_client import TwelveLabsClient, VideoAnalysisResult
from Memnora import ResonanceNode
from Memnora_DARS import Helper, MemnoraCore


@dataclass
class SceneData:
    """Structured scene data from video analysis"""
    start_time: float
    end_time: float
    description: str
    objects: List[str]
    emotions: List[str]
    activities: List[str]
    resonance_impact: Optional[List[float]] = None


@dataclass
class ObjectDetection:
    """Object detection result with temporal context"""
    object_name: str
    confidence: float
    start_time: float
    end_time: float
    bounding_box: Optional[Dict[str, float]] = None


@dataclass
class VideoResonancePayload:
    """Extended resonance payload with video intelligence data"""
    video_id: str
    spectrum: Dict[str, float]
    emotion: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scenes: List[SceneData] = None
    objects: List[ObjectDetection] = None
    speech_transcript: Optional[str] = None
    temporal_patterns: Dict[str, float] = None
    video_embeddings: Optional[List[float]] = None
    resonance_vector: Optional[List[float]] = None
    coherence_score: Optional[float] = None


class VideoResonanceConverter:
    """Converts video analysis results to 11-dimensional resonance vectors"""

    def __init__(self):
        # Resonance dimension mappings (11 dimensions total)
        self.dimension_mappings = {
            # Dimensions 1-3: Physical Environment (Spatial awareness)
            'spatial_environment': {
                'indoor': [0.8, 0.3, 0.2],
                'outdoor': [0.2, 0.8, 0.3],
                'office': [0.9, 0.1, 0.4],
                'nature': [0.1, 0.9, 0.2],
                'urban': [0.5, 0.7, 0.6],
                'home': [0.7, 0.2, 0.5]
            },

            # Dimensions 4-6: Human Activity (Social/behavioral patterns)
            'social_behavior': {
                'talking': [0.6, 0.7, 0.5],
                'presenting': [0.8, 0.6, 0.7],
                'meeting': [0.7, 0.8, 0.6],
                'working': [0.6, 0.5, 0.7],
                'exercising': [0.3, 0.8, 0.9],
                'eating': [0.4, 0.6, 0.3],
                'sleeping': [0.1, 0.2, 0.1]
            },

            # Dimensions 7-9: Emotional Context (Affective resonance)
            'emotional_context': {
                'happy': [0.9, 0.2, 0.8],
                'sad': [0.1, 0.9, 0.2],
                'angry': [0.8, 0.9, 0.3],
                'calm': [0.3, 0.1, 0.9],
                'excited': [0.9, 0.7, 0.8],
                'focused': [0.7, 0.3, 0.7],
                'confused': [0.4, 0.6, 0.3],
                'neutral': [0.5, 0.5, 0.5]
            },

            # Dimensions 10-11: Temporal Flow (Timeline coherence)
            'temporal_flow': {
                'fast_paced': [0.9, 0.3],
                'slow_paced': [0.2, 0.8],
                'rhythmic': [0.6, 0.7],
                'irregular': [0.4, 0.3],
                'stable': [0.3, 0.9],
                'changing': [0.8, 0.4]
            }
        }

        # Object impact weights
        self.object_impacts = {
            'person': 0.8,
            'computer': 0.6,
            'phone': 0.5,
            'book': 0.4,
            'food': 0.3,
            'vehicle': 0.7,
            'animal': 0.6,
            'furniture': 0.4
        }

    def analyze_scene_for_resonance(self, scene_description: str, objects: List[str]) -> List[float]:
        """
        Convert scene description and objects to resonance vector components

        Args:
            scene_description: Text description of the scene
            objects: List of detected objects

        Returns:
            11-dimensional resonance vector
        """
        vector = np.zeros(11)

        # Normalize text for analysis
        text = (scene_description + ' ' + ' '.join(objects)).lower()

        # Analyze spatial environment (dimensions 1-3)
        for env, values in self.dimension_mappings['spatial_environment'].items():
            if env in text:
                vector[0:3] += np.array(values) * 0.5

        # Analyze social behavior (dimensions 4-6)
        for behavior, values in self.dimension_mappings['social_behavior'].items():
            if behavior in text:
                vector[3:6] += np.array(values) * 0.5

        # Analyze emotional context (dimensions 7-9)
        for emotion, values in self.dimension_mappings['emotional_context'].items():
            if emotion in text:
                vector[6:9] += np.array(values) * 0.5

        # Object impact weighting
        object_count = len(objects)
        if object_count > 0:
            total_impact = sum(self.object_impacts.get(obj.lower(), 0.3) for obj in objects)
            normalized_impact = min(total_impact / object_count, 1.0)
            vector[6:9] *= (1 + normalized_impact * 0.3)  # Amplify emotional context based on objects

        return vector.tolist()

    def analyze_speech_patterns(self, transcript: Optional[str]) -> Dict[str, float]:
        """
        Analyze speech transcript for emotional and temporal patterns

        Args:
            transcript: Speech transcript text

        Returns:
            Dictionary of speech pattern features
        """
        if not transcript:
            return {}

        patterns = {
            'sentiment_positive': 0.0,
            'sentiment_negative': 0.0,
            'energy_level': 0.5,
            'complexity': 0.5,
            'pace_indicator': 0.5
        }

        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'happy', 'wonderful', 'amazing', 'love', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'sad', 'angry', 'hate', 'frustrated', 'disappointed']

        words = re.findall(r'\b\w+\b', transcript.lower())
        word_count = len(words)

        if word_count > 0:
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)

            patterns['sentiment_positive'] = positive_count / word_count
            patterns['sentiment_negative'] = negative_count / word_count
            patterns['energy_level'] = min((positive_count - negative_count) / word_count + 0.5, 1.0)

            # Complexity based on sentence length
            sentences = transcript.split('.')
            avg_sentence_length = len(words) / max(len(sentences), 1)
            patterns['complexity'] = min(avg_sentence_length / 15, 1.0)

            # Pace indicator based on word frequency assumptions
            patterns['pace_indicator'] = min(word_count / 100, 1.0)

        return patterns

    def calculate_temporal_flow(self, scenes: List[SceneData], temporal_patterns: Dict[str, float]) -> List[float]:
        """
        Calculate temporal flow resonance (dimensions 10-11)

        Args:
            scenes: List of scene data
            temporal_patterns: Temporal pattern features

        Returns:
            2-dimensional temporal flow vector
        """
        if not scenes:
            return [0.5, 0.5]  # Neutral temporal flow

        vector = np.zeros(2)

        # Analyze scene count and duration for pace
        scene_count = len(scenes)
        avg_duration = temporal_patterns.get('avg_scene_duration', 5.0)

        if avg_duration < 3.0:
            # Fast-paced
            vector[0] = 0.8
            vector[1] = 0.3
        elif avg_duration > 10.0:
            # Slow-paced
            vector[0] = 0.2
            vector[1] = 0.8
        else:
            # Moderate pace
            vector[0] = 0.5
            vector[1] = 0.6

        # Temporal variance affects stability
        variance = temporal_patterns.get('temporal_variance', 0.0)
        if variance < 2.0:
            # Stable/rhythmic
            vector[0] = (vector[0] + 0.6) / 2
            vector[1] = (vector[1] + 0.7) / 2
        elif variance > 8.0:
            # Irregular/changing
            vector[0] = (vector[0] + 0.8) / 2
            vector[1] = (vector[1] + 0.3) / 2

        return vector.tolist()

    def convert_analysis_to_resonance(self, analysis_result: VideoAnalysisResult) -> VideoResonancePayload:
        """
        Convert TwelveLabs analysis result to Memnora resonance payload

        Args:
            analysis_result: Result from TwelveLabs video analysis

        Returns:
            VideoResonancePayload ready for Memnora processing
        """
        if analysis_result.error:
            raise ValueError(f"Analysis failed: {analysis_result.error}")

        # Process scenes
        scenes = []
        for scene_data in analysis_result.scenes or []:
            scene = SceneData(
                start_time=scene_data.get('start', 0),
                end_time=scene_data.get('end', 0),
                description=scene_data.get('description', ''),
                objects=[obj.get('name', '') for obj in scene_data.get('objects', [])],
                emotions=scene_data.get('emotions', []),
                activities=scene_data.get('activities', [])
            )
            scenes.append(scene)

        # Process objects
        objects = []
        for obj_data in analysis_result.objects or []:
            obj = ObjectDetection(
                object_name=obj_data.get('name', ''),
                confidence=obj_data.get('confidence', 0),
                start_time=obj_data.get('start', 0),
                end_time=obj_data.get('end', 0),
                bounding_box=obj_data.get('bounding_box')
            )
            objects.append(obj)

        # Calculate resonance vector
        resonance_vector = np.zeros(11)

        if scenes:
            # Aggregate scene analyses
            scene_vectors = []
            for scene in scenes:
                scene_vector = self.analyze_scene_for_resonance(
                    scene.description,
                    scene.objects
                )
                scene_vectors.append(np.array(scene_vector))

            if scene_vectors:
                resonance_vector[0:9] = np.mean(scene_vectors, axis=0)

        # Add temporal flow (dimensions 10-11)
        temporal_patterns = analysis_result.temporal_patterns or {}
        temporal_vector = self.calculate_temporal_flow(scenes, temporal_patterns)
        resonance_vector[9:11] = temporal_vector

        # Analyze speech patterns
        speech_patterns = self.analyze_speech_patterns(analysis_result.speech_transcript)

        # Create frequency spectrum (simulated from video content)
        spectrum = self._generate_spectrum_from_video(
            resonance_vector,
            speech_patterns,
            temporal_patterns
        )

        # Determine primary emotion
        primary_emotion = self._extract_primary_emotion(scenes, speech_patterns)

        return VideoResonancePayload(
            video_id=analysis_result.video_id,
            spectrum=spectrum,
            emotion=primary_emotion,
            metadata={
                'video_length': analysis_result.temporal_patterns.get('total_duration', 0) if temporal_patterns else 0,
                'scene_count': len(scenes),
                'object_count': len(objects),
                'has_speech': bool(analysis_result.speech_transcript),
                'speech_patterns': speech_patterns,
                'analysis_status': analysis_result.status
            },
            scenes=scenes,
            objects=objects,
            speech_transcript=analysis_result.speech_transcript,
            temporal_patterns=temporal_patterns,
            video_embeddings=analysis_result.embeddings,
            resonance_vector=resonance_vector.tolist(),
            coherence_score=self._calculate_coherence_score(resonance_vector)
        )

    def _generate_spectrum_from_video(self, resonance_vector: np.ndarray,
                                    speech_patterns: Dict[str, float],
                                    temporal_patterns: Dict[str, float]) -> Dict[str, float]:
        """Generate frequency spectrum from video analysis"""
        spectrum = {}

        # Base frequencies mapped from resonance dimensions
        base_frequencies = {
            '432Hz': (resonance_vector[0] + 1) / 2,  # Grounding frequency
            '528Hz': (resonance_vector[6] + 1) / 2,  # Love/emotional frequency
            '741Hz': (resonance_vector[3] + 1) / 2,  # Clarity/intellectual frequency
            '963Hz': (resonance_vector[9] + 1) / 2,  # Divine connection frequency
        }

        # Modulate based on speech patterns
        energy_multiplier = 1 + speech_patterns.get('energy_level', 0.5) * 0.5

        for freq, amplitude in base_frequencies.items():
            spectrum[freq] = amplitude * energy_multiplier

        # Add harmonics based on temporal patterns
        if temporal_patterns.get('motion_intensity', 0.5) > 0.7:
            spectrum['216Hz'] = 0.6  # Lower harmonic for high motion
            spectrum['864Hz'] = 0.4  # Upper harmonic

        return spectrum

    def _extract_primary_emotion(self, scenes: List[SceneData],
                               speech_patterns: Dict[str, float]) -> Optional[str]:
        """Extract primary emotional state from video analysis"""
        emotions = []

        # Collect emotions from scenes
        for scene in scenes:
            emotions.extend(scene.emotions)

        # Add sentiment from speech
        if speech_patterns.get('sentiment_positive', 0) > speech_patterns.get('sentiment_negative', 0):
            emotions.append('positive')
        elif speech_patterns.get('sentiment_negative', 0) > 0.3:
            emotions.append('negative')

        if speech_patterns.get('energy_level', 0.5) > 0.7:
            emotions.append('excited')
        elif speech_patterns.get('energy_level', 0.5) < 0.3:
            emotions.append('calm')

        # Return most common emotion
        if emotions:
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            return max(emotion_counts, key=emotion_counts.get)

        return None

    def _calculate_coherence_score(self, resonance_vector: np.ndarray) -> float:
        """Calculate coherence score for resonance vector"""
        # Coherence based on vector alignment with optimal resonance state
        optimal_vector = np.ones(11) * 0.7  # Balanced positive state

        if resonance_vector.size == 0:
            return 0.0

        # Calculate cosine similarity with optimal state
        dot_product = np.dot(resonance_vector, optimal_vector)
        magnitude = np.linalg.norm(resonance_vector) * np.linalg.norm(optimal_vector)

        if magnitude == 0:
            return 0.0

        coherence = (dot_product / magnitude + 1) / 2  # Normalize to 0-1
        return float(coherence)


class VideoSense:
    """Main VideoSense module integrating video intelligence with Memnora"""

    def __init__(self, memnora_core: Optional[MemnoraCore] = None):
        self.converter = VideoResonanceConverter()
        self.client = TwelveLabsClient()
        self.memnora_core = memnora_core or MemnoraCore()
        self.video_cache = {}

    async def analyze_video_file(self, video_file_path: str) -> VideoResonancePayload:
        """
        Complete video analysis pipeline from file to resonance payload

        Args:
            video_file_path: Path to video file

        Returns:
            VideoResonancePayload ready for Memnora processing
        """
        # Upload video
        video_id = await self.client.upload_video(video_file_path)

        # Analyze video
        analysis_result = await self.client.analyze_video(video_id)

        # Convert to resonance payload
        resonance_payload = self.converter.convert_analysis_to_resonance(analysis_result)

        # Cache result
        self.video_cache[video_id] = resonance_payload

        return resonance_payload

    def validate_with_dars(self, payload: VideoResonancePayload) -> Tuple[int, str]:
        """
        Validate video payload using DARS system

        Args:
            payload: Video resonance payload to validate

        Returns:
            Tuple of (coherence_score: int, explanation: str)
        """
        # Create signal for DARS analysis
        signal = {
            'id': payload.video_id,
            'risk': 1.0 - payload.coherence_score if payload.coherence_score else 0.5,
            'content_score': payload.coherence_score,
            'object_density': len(payload.objects) if payload.objects else 0,
            'emotional_intensity': self._calculate_emotional_intensity(payload),
            'temporal_stability': self._assess_temporal_stability(payload)
        }

        # Process through DARS
        result = self.memnora_core.process_signal(signal)

        # Convert DARS result to trinary score
        if payload.coherence_score and payload.coherence_score > 0.7:
            coherence_score = 1  # Coherent
        elif payload.coherence_score and payload.coherence_score > 0.4:
            coherence_score = 0  # Neutral
        else:
            coherence_score = -1  # Dissonant

        explanation = f"DARS validation: {result}"
        return coherence_score, explanation

    def _calculate_emotional_intensity(self, payload: VideoResonancePayload) -> float:
        """Calculate emotional intensity from payload"""
        intensity = 0.5  # Base intensity

        if payload.emotion:
            emotion_intensity_map = {
                'excited': 0.9, 'angry': 0.8, 'happy': 0.7,
                'sad': 0.6, 'calm': 0.3, 'neutral': 0.5
            }
            intensity = emotion_intensity_map.get(payload.emotion.lower(), 0.5)

        if payload.speech_patterns:
            speech_energy = payload.speech_patterns.get('energy_level', 0.5)
            intensity = (intensity + speech_energy) / 2

        return intensity

    def _assess_temporal_stability(self, payload: VideoResonancePayload) -> float:
        """Assess temporal stability of video content"""
        if not payload.temporal_patterns:
            return 0.5

        variance = payload.temporal_patterns.get('temporal_variance', 5.0)
        scene_count = payload.temporal_patterns.get('scene_count', 1)

        # Lower variance and appropriate scene count indicate stability
        stability = max(0, 1 - (variance / 10.0))

        # Adjust for scene count (extremely high or low scene count is less stable)
        if 3 <= scene_count <= 15:
            stability *= 1.2
        elif scene_count > 30 or scene_count < 2:
            stability *= 0.7

        return min(stability, 1.0)

    def get_cached_analysis(self, video_id: str) -> Optional[VideoResonancePayload]:
        """Retrieve cached video analysis"""
        return self.video_cache.get(video_id)

    def clear_cache(self, video_id: Optional[str] = None):
        """Clear video analysis cache"""
        if video_id:
            self.video_cache.pop(video_id, None)
        else:
            self.video_cache.clear()


# Singleton instance
_video_sense = None

def get_video_sense(memnora_core: Optional[MemnoraCore] = None) -> VideoSense:
    """Get singleton VideoSense instance"""
    global _video_sense
    if _video_sense is None:
        _video_sense = VideoSense(memnora_core)
    return _video_sense