# twelvelabs_client.py
# TwelveLabs API Client for Video Intelligence Integration
# Author: VyTek VideoSense Team
# Description: Wrapper for TwelveLabs multimodal video understanding API

import os
import json
import asyncio
import aiohttp
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class VideoAnalysisResult:
    """Structure for TwelveLabs video analysis results"""
    video_id: str
    status: str
    summary: Optional[str] = None
    scenes: Optional[List[Dict[str, Any]]] = None
    objects: Optional[List[Dict[str, Any]]] = None
    speech_transcript: Optional[str] = None
    embeddings: Optional[List[float]] = None
    temporal_patterns: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class TwelveLabsClient:
    """Client for TwelveLabs Video Intelligence API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWELVELABS_API_KEY")
        if not self.api_key:
            raise ValueError("TWELVELABS_API_KEY environment variable required")

        self.base_url = "https://api.twelvelabs.io/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _handle_response_error(self, response_data: Dict[str, Any], status_code: int) -> None:
        """Handle API error responses"""
        if status_code >= 400:
            error_msg = response_data.get("message", f"API Error {status_code}")
            if status_code == 401:
                raise ValueError("Invalid TwelveLabs API key")
            elif status_code == 429:
                raise ValueError("Rate limit exceeded. Please wait before retrying.")
            elif status_code >= 500:
                raise ValueError("TwelveLabs service temporarily unavailable")
            else:
                raise ValueError(f"TwelveLabs API error: {error_msg}")

    async def upload_video(self, video_file_path: str) -> str:
        """
        Upload a video file to TwelveLabs for analysis

        Args:
            video_file_path: Path to video file (mp4, mov, webm, avi)

        Returns:
            video_id: Unique identifier for uploaded video
        """
        if not os.path.exists(video_file_path):
            raise FileNotFoundError(f"Video file not found: {video_file_path}")

        # Validate file format
        allowed_formats = ['.mp4', '.mov', '.webm', '.avi']
        file_ext = os.path.splitext(video_file_path)[1].lower()
        if file_ext not in allowed_formats:
            raise ValueError(f"Unsupported video format: {file_ext}")

        # Check file size (500MB max)
        file_size = os.path.getsize(video_file_path)
        max_size = 500 * 1024 * 1024  # 500MB
        if file_size > max_size:
            raise ValueError(f"Video file too large: {file_size} bytes (max: {max_size})")

        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            with open(video_file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('video', f,
                             filename=os.path.basename(video_file_path),
                             content_type='video/mp4')

                async with self.session.post(f"{self.base_url}/videos", data=data) as response:
                    response_data = await response.json()
                    self._handle_response_error(response_data, response.status)

                    return response_data.get('id')

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to upload video: {str(e)}")

    async def get_analysis_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the analysis status of a uploaded video

        Args:
            video_id: Unique identifier for video

        Returns:
            Dict containing status information
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}") as response:
                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get analysis status: {str(e)}")

    async def get_video_summary(self, video_id: str) -> Optional[str]:
        """
        Get AI-generated summary of video content

        Args:
            video_id: Unique identifier for video

        Returns:
            Video summary text or None if not available
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}/summary") as response:
                if response.status == 404:
                    return None  # Summary not available yet

                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data.get('summary')

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get video summary: {str(e)}")

    async def get_video_embeddings(self, video_id: str) -> Optional[List[float]]:
        """
        Get vector embeddings for video content

        Args:
            video_id: Unique identifier for video

        Returns:
            List of embedding values or None if not available
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}/embeddings") as response:
                if response.status == 404:
                    return None  # Embeddings not available yet

                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data.get('embeddings')

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get video embeddings: {str(e)}")

    async def get_video_scenes(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get scene breakdown and timeline analysis

        Args:
            video_id: Unique identifier for video

        Returns:
            List of scene data with timestamps and descriptions
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}/scenes") as response:
                if response.status == 404:
                    return []  # Scenes not available yet

                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data.get('scenes', [])

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get video scenes: {str(e)}")

    async def get_video_objects(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get object detection results from video

        Args:
            video_id: Unique identifier for video

        Returns:
            List of detected objects with timestamps
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}/objects") as response:
                if response.status == 404:
                    return []  # Objects not available yet

                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data.get('objects', [])

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get video objects: {str(e)}")

    async def get_speech_transcript(self, video_id: str) -> Optional[str]:
        """
        Get speech transcript from video

        Args:
            video_id: Unique identifier for video

        Returns:
            Speech transcript text or None if not available
        """
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.session.get(f"{self.base_url}/videos/{video_id}/transcript") as response:
                if response.status == 404:
                    return None  # Transcript not available yet

                response_data = await response.json()
                self._handle_response_error(response_data, response.status)
                return response_data.get('transcript')

        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to get speech transcript: {str(e)}")

    async def analyze_video(self, video_id: str, timeout: int = 300) -> VideoAnalysisResult:
        """
        Complete video analysis pipeline - wait for completion and return all results

        Args:
            video_id: Unique identifier for video
            timeout: Maximum time to wait for analysis (seconds)

        Returns:
            Complete VideoAnalysisResult with all available data
        """
        start_time = datetime.now()

        while True:
            # Check timeout
            if (datetime.now() - start_time).seconds > timeout:
                raise TimeoutError(f"Video analysis timeout after {timeout} seconds")

            # Get current status
            status_data = await self.get_analysis_status(video_id)
            status = status_data.get('status', 'unknown')

            if status == 'completed':
                # Analysis complete - fetch all results
                summary = await self.get_video_summary(video_id)
                scenes = await self.get_video_scenes(video_id)
                objects = await self.get_video_objects(video_id)
                transcript = await self.get_speech_transcript(video_id)
                embeddings = await self.get_video_embeddings(video_id)

                # Calculate temporal patterns
                temporal_patterns = self._extract_temporal_patterns(scenes)

                return VideoAnalysisResult(
                    video_id=video_id,
                    status=status,
                    summary=summary,
                    scenes=scenes,
                    objects=objects,
                    speech_transcript=transcript,
                    embeddings=embeddings,
                    temporal_patterns=temporal_patterns
                )

            elif status == 'failed':
                error_msg = status_data.get('error', 'Analysis failed')
                return VideoAnalysisResult(
                    video_id=video_id,
                    status=status,
                    error=error_msg
                )

            elif status in ['pending', 'processing']:
                # Wait and retry
                await asyncio.sleep(5)

            else:
                raise ValueError(f"Unknown analysis status: {status}")

    def _extract_temporal_patterns(self, scenes: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract temporal patterns from scene data

        Args:
            scenes: List of scene data

        Returns:
            Dictionary of temporal pattern features
        """
        if not scenes:
            return {}

        patterns = {
            'scene_count': len(scenes),
            'avg_scene_duration': 0,
            'motion_intensity': 0.5,  # Default, would be calculated from actual data
            'temporal_variance': 0.0
        }

        # Calculate average scene duration
        if len(scenes) > 1:
            durations = []
            for i, scene in enumerate(scenes):
                start = scene.get('start', 0)
                end = scene.get('end', start)
                duration = end - start
                if duration > 0:
                    durations.append(duration)

            if durations:
                patterns['avg_scene_duration'] = sum(durations) / len(durations)
                patterns['temporal_variance'] = max(durations) - min(durations) if len(durations) > 1 else 0

        return patterns

    # Synchronous wrapper methods for easier integration
    def upload_video_sync(self, video_file_path: str) -> str:
        """Synchronous wrapper for upload_video"""
        return asyncio.run(self.upload_video(video_file_path))

    def analyze_video_sync(self, video_id: str, timeout: int = 300) -> VideoAnalysisResult:
        """Synchronous wrapper for analyze_video"""
        async def _analyze():
            async with self:
                return await self.analyze_video(video_id, timeout)

        return asyncio.run(_analyze())


# Singleton instance for easy access
_twelvelabs_client = None

def get_twelvelabs_client() -> TwelveLabsClient:
    """Get singleton TwelveLabs client instance"""
    global _twelvelabs_client
    if _twelvelabs_client is None:
        _twelvelabs_client = TwelveLabsClient()
    return _twelvelabs_client