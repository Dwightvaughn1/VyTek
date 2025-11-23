#!/usr/bin/env python3
# test_video_integration.py
# Test script for video intelligence integration with Memnora

import asyncio
import sys
import os
import time
import json
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required components can be imported"""
    print("🔍 Testing imports...")

    try:
        from video_sense import VideoSense, get_video_sense
        print("✅ VideoSense module imported successfully")
    except ImportError as e:
        print(f"❌ VideoSense import failed: {e}")
        return False

    try:
        from twelvelabs_client import TwelveLabsClient
        print("✅ TwelveLabs client imported successfully")
    except ImportError as e:
        print(f"❌ TwelveLabs client import failed: {e}")
        return False

    try:
        from Memnora import ResonanceNode, MemnoraOperator
        print("✅ Memnora core imported successfully")
    except ImportError as e:
        print(f"❌ Memnora core import failed: {e}")
        return False

    try:
        from Memnora_DARS import MemnoraCore
        print("✅ Memnora DARS imported successfully")
    except ImportError as e:
        print(f"❌ Memnora DARS import failed: {e}")
        return False

    return True

def test_video_sense_initialization():
    """Test VideoSense module initialization"""
    print("\n🧠 Testing VideoSense initialization...")

    try:
        from video_sense import get_video_sense

        # Test singleton creation
        video_sense_1 = get_video_sense()
        video_sense_2 = get_video_sense()

        if video_sense_1 is video_sense_2:
            print("✅ VideoSense singleton pattern working correctly")
        else:
            print("❌ VideoSense singleton pattern failed")
            return False

        # Test core components
        if hasattr(video_sense_1, 'converter') and hasattr(video_sense_1, 'client'):
            print("✅ VideoSense core components initialized")
        else:
            print("❌ VideoSense core components missing")
            return False

        return True

    except Exception as e:
        print(f"❌ VideoSense initialization failed: {e}")
        return False

def test_resonance_conversion():
    """Test video-to-resonance conversion functionality"""
    print("\n🔄 Testing resonance conversion...")

    try:
        from video_sense import VideoResonanceConverter, SceneData, ObjectDetection
        from twelvelabs_client import VideoAnalysisResult

        converter = VideoResonanceConverter()

        # Create mock video analysis result
        mock_analysis = VideoAnalysisResult(
            video_id="test_video_123",
            status="completed",
            summary="Test video showing a person talking in an office",
            scenes=[
                {
                    'start': 0,
                    'end': 10,
                    'description': 'Person talking in office environment',
                    'objects': [{'name': 'person', 'confidence': 0.9}],
                    'emotions': ['focused', 'professional'],
                    'activities': ['talking', 'presenting']
                }
            ],
            objects=[
                {
                    'name': 'person',
                    'confidence': 0.95,
                    'start': 0,
                    'end': 10
                },
                {
                    'name': 'computer',
                    'confidence': 0.8,
                    'start': 2,
                    'end': 8
                }
            ],
            speech_transcript="Hello everyone, welcome to this presentation about our new project.",
            temporal_patterns={
                'scene_count': 1,
                'avg_scene_duration': 10.0,
                'motion_intensity': 0.3,
                'temporal_variance': 0.0
            },
            embeddings=[0.1] * 1536  # Mock embedding vector
        )

        # Test conversion
        resonance_payload = converter.convert_analysis_to_resonance(mock_analysis)

        # Validate results
        if hasattr(resonance_payload, 'resonance_vector') and resonance_payload.resonance_vector:
            print(f"✅ Resonance vector generated: {len(resonance_payload.resonance_vector)} dimensions")
        else:
            print("❌ Resonance vector not generated")
            return False

        if len(resonance_payload.resonance_vector) == 11:
            print("✅ Resonance vector has correct 11 dimensions")
        else:
            print(f"❌ Resonance vector has {len(resonance_payload.resonance_vector)} dimensions (expected 11)")
            return False

        if hasattr(resonance_payload, 'coherence_score'):
            print(f"✅ Coherence score calculated: {resonance_payload.coherence_score:.3f}")
        else:
            print("❌ Coherence score not calculated")
            return False

        # Test scene analysis
        if resonance_payload.scenes:
            print(f"✅ {len(resonance_payload.scenes)} scenes processed")
        else:
            print("❌ No scenes processed")
            return False

        # Test object detection
        if resonance_payload.objects:
            print(f"✅ {len(resonance_payload.objects)} objects detected")
        else:
            print("❌ No objects detected")
            return False

        return True

    except Exception as e:
        print(f"❌ Resonance conversion test failed: {e}")
        return False

def test_dars_validation():
    """Test DARS validation with video inputs"""
    print("\n🛡️ Testing DARS validation...")

    try:
        from video_sense import VideoSense, VideoResonancePayload
        from Memnora_DARS import MemnoraCore

        # Create test resonance payload
        test_payload = VideoResonancePayload(
            video_id="test_validation",
            spectrum={'432Hz': 0.7, '528Hz': 0.8},
            emotion="focused",
            resonance_vector=[0.5] * 11,
            coherence_score=0.75
        )

        # Initialize VideoSense with DARS
        dars_core = MemnoraCore()
        video_sense = VideoSense(dars_core)

        # Test DARS validation
        coherence_score, explanation = video_sense.validate_with_dars(test_payload)

        print(f"✅ DARS validation completed")
        print(f"   Coherence score: {coherence_score} (trinary: -1, 0, +1)")
        print(f"   Explanation: {explanation}")

        # Test different coherence scenarios
        test_cases = [
            (0.9, "High coherence"),
            (0.5, "Medium coherence"),
            (0.2, "Low coherence")
        ]

        for score, description in test_cases:
            test_payload.coherence_score = score
            score_result, _ = video_sense.validate_with_dars(test_payload)
            print(f"   {description}: score {score} → trinary {score_result}")

        return True

    except Exception as e:
        print(f"❌ DARS validation test failed: {e}")
        return False

def test_twelvelabs_client():
    """Test TwelveLabs client functionality (mock test)"""
    print("\n🎬 Testing TwelveLabs client...")

    try:
        from twelvelabs_client import TwelveLabsClient

        # Test client initialization (will fail without API key, but that's expected)
        try:
            client = TwelveLabsClient("test_api_key")
            print("✅ TwelveLabs client initialized with test key")
        except Exception as e:
            if "TWELVELABS_API_KEY" in str(e):
                print("⚠️ TwelveLabs client requires valid API key (expected)")
            else:
                raise e

        # Test data structures
        from twelvelabs_client import VideoAnalysisResult
        test_result = VideoAnalysisResult(
            video_id="test",
            status="test"
        )

        if hasattr(test_result, 'video_id'):
            print("✅ TwelveLabs data structures working")
        else:
            print("❌ TwelveLabs data structures failed")
            return False

        return True

    except Exception as e:
        print(f"❌ TwelveLabs client test failed: {e}")
        return False

def test_integration_completeness():
    """Test overall integration completeness"""
    print("\n🔗 Testing integration completeness...")

    try:
        # Test that all components work together
        from video_sense import get_video_sense
        from Memnora import MemnoraOperator
        from Memnora_DARS import MemnoraCore

        # Initialize components
        video_sense = get_video_sense()
        memnora = MemnoraOperator()
        dars = MemnoraCore()

        print("✅ All core components initialized")

        # Test component interaction
        if hasattr(video_sense, 'converter') and hasattr(memnora, 'resonance_matrix'):
            print("✅ VideoSense and Memnora components compatible")

        if hasattr(video_sense, 'memnora_core'):
            print("✅ VideoSense properly integrated with DARS")

        return True

    except Exception as e:
        print(f"❌ Integration completeness test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("🧪 Starting Video Intelligence Integration Tests")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("VideoSense Initialization", test_video_sense_initialization),
        ("Resonance Conversion", test_resonance_conversion),
        ("DARS Validation", test_dars_validation),
        ("TwelveLabs Client", test_twelvelabs_client),
        ("Integration Completeness", test_integration_completeness)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Video intelligence integration is ready.")
    elif passed >= total * 0.8:
        print("⚠️ Most tests passed. Minor issues may need attention.")
    else:
        print("🚨 Several tests failed. Integration needs review.")

    print("="*50)

    return passed == total

def demo_functionality():
    """Demonstrate key functionality"""
    print("\n🎭 FUNCTIONALITY DEMONSTRATION")
    print("="*50)

    try:
        from video_sense import VideoResonanceConverter, VideoResonancePayload
        from twelvelabs_client import VideoAnalysisResult

        print("1. Creating mock video analysis...")
        mock_video = VideoAnalysisResult(
            video_id="demo_001",
            status="completed",
            summary="Person giving a presentation about sustainable technology",
            scenes=[
                {
                    'start': 0,
                    'end': 15,
                    'description': 'Introduction with confident posture',
                    'objects': [{'name': 'person', 'confidence': 0.95}],
                    'emotions': ['confident', 'professional'],
                    'activities': ['presenting', 'speaking']
                },
                {
                    'start': 15,
                    'end': 30,
                    'description': 'Technical explanation with visual aids',
                    'objects': [{'name': 'person', 'confidence': 0.9}, {'name': 'screen', 'confidence': 0.8}],
                    'emotions': ['focused', 'knowledgeable'],
                    'activities': ['explaining', 'presenting']
                }
            ],
            objects=[
                {'name': 'person', 'confidence': 0.92, 'start': 0, 'end': 30},
                {'name': 'screen', 'confidence': 0.8, 'start': 15, 'end': 30},
                {'name': 'presentation_remote', 'confidence': 0.6, 'start': 5, 'end': 25}
            ],
            speech_transcript="Good morning everyone. Today I want to talk about sustainable technology solutions...",
            temporal_patterns={
                'scene_count': 2,
                'avg_scene_duration': 15.0,
                'motion_intensity': 0.4,
                'temporal_variance': 0.5
            },
            embeddings=[i * 0.001 for i in range(1536)]  # Mock 1536-dim embedding
        )

        print("✅ Mock video analysis created")

        print("\n2. Converting to resonance payload...")
        converter = VideoResonanceConverter()
        payload = converter.convert_analysis_to_resonance(mock_video)

        print(f"✅ Resonance payload created")
        print(f"   Video ID: {payload.video_id}")
        print(f"   Primary emotion: {payload.emotion}")
        print(f"   Coherence score: {payload.coherence_score:.3f}")
        print(f"   Resonance vector: {payload.resonance_vector[:3]}... (first 3 of 11)")
        print(f"   Speech detected: {'Yes' if payload.speech_transcript else 'No'}")
        print(f"   Scene count: {len(payload.scenes) if payload.scenes else 0}")
        print(f"   Object count: {len(payload.objects) if payload.objects else 0}")

        print("\n3. Frequency spectrum generated:")
        for freq, amplitude in payload.spectrum.items():
            print(f"   {freq}: {amplitude:.3f}")

        print("\n4. DARS validation result:")
        from Memnora_DARS import MemnoraCore
        video_sense = VideoSense(MemnoraCore())
        score, explanation = video_sense.validate_with_dars(payload)
        print(f"   Coherence score: {score} (trinary)")
        print(f"   Explanation: {explanation}")

        print("\n🎉 Demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Memnora Video Intelligence Integration Test Suite")
    print("=" * 60)

    # Run all tests
    all_passed = run_all_tests()

    if all_passed:
        print("\n" + "="*60)
        # Run demo
        demo_success = demo_functionality()

        if demo_success:
            print("\n" + "="*60)
            print("🚀 INTEGRATION READY FOR DEPLOYMENT!")
            print("="*60)
            print("\nNext steps:")
            print("1. Set up TWELVELABS_API_KEY environment variable")
            print("2. Configure VIDEO_API_BASE for backend endpoints")
            print("3. Test with real video files")
            print("4. Deploy FastAPI backend (python Meditation_Metaworld.py)")
            print("5. Deploy Flask avatar interface (python Aten_Atena_Video.py)")
            print("6. Run 3D visualization (python dashboard_video.py)")
            print("="*60)
        else:
            print("\n⚠️ Demo failed, but tests passed. Review demo implementation.")
    else:
        print("\n🛠️ Integration needs fixes before deployment.")
        print("Review failed tests and resolve issues.")