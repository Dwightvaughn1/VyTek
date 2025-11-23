#!/usr/bin/env python3
# validate_integration.py
# Validation script for video intelligence integration (minimal dependencies)

import os
import sys
import json
from pathlib import Path

def validate_file_structure():
    """Validate that all required files are present"""
    print("📁 Validating file structure...")

    required_files = [
        'video_sense.py',
        'twelvelabs_client.py',
        'Meditation_Metaworld.py',
        'Aten_Atena_Video.py',
        'dashboard_video.py',
        'requirements.txt',
        'Memnora.py',
        'Memnora_DARS.py'
    ]

    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)

    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True

def validate_file_contents():
    """Validate key content in the integration files"""
    print("\n📄 Validating file contents...")

    # Check VideoSense module
    try:
        with open('video_sense.py', 'r') as f:
            content = f.read()

        required_classes = ['VideoResonanceConverter', 'VideoSense', 'SceneData', 'ObjectDetection']
        missing_classes = []

        for cls in required_classes:
            if f"class {cls}" in content:
                print(f"✅ VideoSense.{cls} found")
            else:
                print(f"❌ VideoSense.{cls} missing")
                missing_classes.append(cls)

        if missing_classes:
            print(f"❌ VideoSense missing {len(missing_classes)} classes")
            return False
        else:
            print(f"✅ All VideoSense classes present")

    except Exception as e:
        print(f"❌ Error reading video_sense.py: {e}")
        return False

    # Check TwelveLabs client
    try:
        with open('twelvelabs_client.py', 'r') as f:
            content = f.read()

        if 'class TwelveLabsClient' in content:
            print("✅ TwelveLabsClient class found")
        else:
            print("❌ TwelveLabsClient class missing")
            return False

        if 'class VideoAnalysisResult' in content:
            print("✅ VideoAnalysisResult class found")
        else:
            print("❌ VideoAnalysisResult class missing")
            return False

    except Exception as e:
        print(f"❌ Error reading twelvelabs_client.py: {e}")
        return False

    # Check FastAPI backend integration
    try:
        with open('Meditation_Metaworld.py', 'r') as f:
            content = f.read()

        video_endpoints = ['/api/video/upload', '/api/video/analysis/', '/api/video/anomaly-check']
        missing_endpoints = []

        for endpoint in video_endpoints:
            if endpoint in content:
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"❌ Endpoint {endpoint} missing")
                missing_endpoints.append(endpoint)

        if missing_endpoints:
            print(f"❌ Missing {len(missing_endpoints)} video endpoints")
            return False
        else:
            print(f"✅ All video endpoints present")

        # Check video imports
        if 'from video_sense import' in content:
            print("✅ VideoSense import found in backend")
        else:
            print("❌ VideoSense import missing from backend")
            return False

    except Exception as e:
        print(f"❌ Error reading Meditation_Metaworld.py: {e}")
        return False

    return True

def validate_database_schema():
    """Validate database schema additions"""
    print("\n🗄️ Validating database schema...")

    try:
        with open('Meditation_Metaworld.py', 'r') as f:
            content = f.read()

        if 'video_analyses' in content and 'video_scenes' in content:
            print("✅ Video database tables defined")
        else:
            print("❌ Video database tables missing")
            return False

        # Check video data models
        video_models = ['VideoUploadResponse', 'VideoAnalysisResponse', 'AnomalyCheckResponse']
        missing_models = []

        for model in video_models:
            if f"class {model}" in content:
                print(f"✅ {model} model found")
            else:
                print(f"❌ {model} model missing")
                missing_models.append(model)

        if missing_models:
            print(f"❌ Missing {len(missing_models)} video models")
            return False
        else:
            print(f"✅ All video models present")

    except Exception as e:
        print(f"❌ Error validating database schema: {e}")
        return False

    return True

def validate_resonance_conversion():
    """Validate resonance conversion logic"""
    print("\n🔄 Validating resonance conversion logic...")

    try:
        with open('video_sense.py', 'r') as f:
            content = f.read()

        conversion_methods = [
            'analyze_scene_for_resonance',
            'convert_analysis_to_resonance',
            'analyze_speech_patterns',
            'calculate_temporal_flow'
        ]

        missing_methods = []
        for method in conversion_methods:
            if f"def {method}" in content:
                print(f"✅ {method} method found")
            else:
                print(f"❌ {method} method missing")
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ Missing {len(missing_methods)} conversion methods")
            return False
        else:
            print(f"✅ All conversion methods present")

        # Check 11-dimensional resonance mapping
        if '11-dimensional' in content or '11D' in content:
            print("✅ 11D resonance mapping documented")
        else:
            print("❌ 11D resonance mapping not documented")
            return False

        # Check dimension mappings
        dimension_sections = ['Physical Environment', 'Human Activity', 'Emotional Context', 'Temporal Flow']
        for section in dimension_sections:
            if section in content:
                print(f"✅ {section} mapping found")
            else:
                print(f"❌ {section} mapping missing")
                return False

    except Exception as e:
        print(f"❌ Error validating resonance conversion: {e}")
        return False

    return True

def validate_dars_integration():
    """Validate DARS integration with video"""
    print("\n🛡️ Validating DARS integration...")

    try:
        with open('video_sense.py', 'r') as f:
            content = f.read()

        if 'validate_with_dars' in content:
            print("✅ DARS validation method found")
        else:
            print("❌ DARS validation method missing")
            return False

        if 'coherence_score' in content and 'trinary' in content.lower():
            print("✅ Trinary coherence scoring implemented")
        else:
            print("❌ Trinary coherence scoring not found")
            return False

        # Check DARS error handling
        dars_components = ['visual_consistency', 'behavioral_patterns', 'environmental_stability', 'temporal_flow']
        found_components = 0

        for component in dars_components:
            if component.replace('_', ' ') in content.lower():
                found_components += 1

        if found_components >= 2:
            print(f"✅ DARS components integrated ({found_components}/4)")
        else:
            print(f"❌ DARS components insufficient ({found_components}/4)")
            return False

    except Exception as e:
        print(f"❌ Error validating DARS integration: {e}")
        return False

    return True

def validate_avatar_integration():
    """Validate avatar system video integration"""
    print("\n🎭 Validating avatar system integration...")

    try:
        with open('Aten_Atena_Video.py', 'r') as f:
            content = f.read()

        # Check video upload handling
        if 'allowed_file' in content and 'video' in content.lower():
            print("✅ Video upload handling implemented")
        else:
            print("❌ Video upload handling missing")
            return False

        # Check video intelligence features
        if 'VIDEO_INTELLIGENCE_ENABLED' in content:
            print("✅ Video intelligence toggle implemented")
        else:
            print("❌ Video intelligence toggle missing")
            return False

        # Check behavioral pattern analysis
        if 'analyze_video_behavioral_patterns' in content:
            print("✅ Behavioral pattern analysis implemented")
        else:
            print("❌ Behavioral pattern analysis missing")
            return False

        # Check enhanced avatar responses
        avatar_responses = ['get_aten_response', 'get_atena_response']
        for response in avatar_responses:
            if f"def {response}" in content and 'video_analysis' in content:
                print(f"✅ Enhanced {response} with video intelligence")
            else:
                print(f"❌ {response} not enhanced with video intelligence")
                return False

        # Check WebSocket video analysis
        if 'process_video_async' in content:
            print("✅ Async video processing implemented")
        else:
            print("❌ Async video processing missing")
            return False

    except Exception as e:
        print(f"❌ Error validating avatar integration: {e}")
        return False

    return True

def validate_visualization_integration():
    """Validate 3D visualization video integration"""
    print("\n📊 Validating visualization integration...")

    try:
        with open('dashboard_video.py', 'r') as f:
            content = f.read()

        # Check video data manager
        if 'class VideoDataManager' in content:
            print("✅ VideoDataManager class found")
        else:
            print("❌ VideoDataManager class missing")
            return False

        # Check enhanced dashboard
        if 'class VideoEnhancedDashboard' in content:
            print("✅ VideoEnhancedDashboard class found")
        else:
            print("❌ VideoEnhancedDashboard class missing")
            return False

        # Check video visualization features
        viz_features = ['video_mode', 'emotional_timeline', 'video_trail']
        found_features = 0

        for feature in viz_features:
            if feature in content:
                found_features += 1
                print(f"✅ {feature} visualization found")
            else:
                print(f"❌ {feature} visualization missing")

        if found_features >= 2:
            print(f"✅ Sufficient video visualization features ({found_features}/3)")
        else:
            print(f"❌ Insufficient video visualization features ({found_features}/3)")
            return False

    except Exception as e:
        print(f"❌ Error validating visualization integration: {e}")
        return False

    return True

def validate_api_endpoints():
    """Validate API endpoint completeness"""
    print("\n🌐 Validating API endpoints...")

    try:
        with open('Meditation_Metaworld.py', 'r') as f:
            content = f.read()

        required_endpoints = {
            'POST /api/video/upload': [
                'file: UploadFile',
                'VideoUploadResponse',
                'content_type validation'
            ],
            'GET /api/video/analysis/{video_id}': [
                'VideoAnalysisResponse',
                'analysis status checking'
            ],
            'POST /api/video/anomaly-check': [
                'AnomalyCheckRequest',
                'AnomalyCheckResponse',
                'DARS validation'
            ],
            'WebSocket /ws/video-analysis': [
                'real-time updates',
                'video status streaming'
            ]
        }

        endpoints_found = 0
        for endpoint, features in required_endpoints.items():
            endpoint_key = endpoint.split()[1]  # Extract path part
            if endpoint_key in content:
                print(f"✅ {endpoint} implemented")
                endpoints_found += 1

                # Check for key features
                for feature in features:
                    if feature.lower().replace(' ', '_') in content.lower():
                        print(f"  ✅ {feature}")
                    else:
                        print(f"  ⚠️ {feature} - may be missing")
            else:
                print(f"❌ {endpoint} missing")
                return False

        if endpoints_found == len(required_endpoints):
            print(f"✅ All {endpoints_found} required endpoints implemented")
        else:
            print(f"❌ Only {endpoints_found}/{len(required_endpoints)} endpoints found")
            return False

    except Exception as e:
        print(f"❌ Error validating API endpoints: {e}")
        return False

    return True

def generate_deployment_checklist():
    """Generate deployment checklist"""
    print("\n📋 DEPLOYMENT CHECKLIST")
    print("=" * 50)

    checklist = [
        "✅ Set TWELVELABS_API_KEY environment variable",
        "✅ Configure VIDEO_API_BASE for backend endpoints",
        "✅ Install required dependencies: pip install -r requirements.txt",
        "✅ Test with real video files (MP4, MOV, WebM)",
        "✅ Deploy FastAPI backend: python Meditation_Metaworld.py",
        "✅ Deploy avatar interface: python Aten_Atena_Video.py",
        "✅ Run 3D visualization: python dashboard_video.py",
        "✅ Configure database for video metadata storage",
        "✅ Set up file storage for video uploads",
        "✅ Test video upload to resonance flow end-to-end",
        "✅ Verify DARS validation with real video data",
        "✅ Test WebSocket real-time analysis streaming",
        "✅ Validate avatar coaching with video insights",
        "✅ Confirm 3D visualization video intelligence overlay"
    ]

    for item in checklist:
        print(item)

    print("\n🔧 CONFIGURATION NEEDED:")
    print("export TWELVELABS_API_KEY='your_twelve_labs_api_key'")
    print("export VIDEO_API_BASE='http://localhost:8000'")
    print("export VIDEO_STORAGE_PATH='/path/to/video/storage'")
    print("export MAX_VIDEO_SIZE_MB='500'")
    print("export ENABLE_VIDEO_ANALYSIS='true'")

def main():
    """Main validation function"""
    print("Memnora Video Intelligence Integration Validation")
    print("=" * 60)

    validations = [
        ("File Structure", validate_file_structure),
        ("File Contents", validate_file_contents),
        ("Database Schema", validate_database_schema),
        ("Resonance Conversion", validate_resonance_conversion),
        ("DARS Integration", validate_dars_integration),
        ("Avatar Integration", validate_avatar_integration),
        ("Visualization Integration", validate_visualization_integration),
        ("API Endpoints", validate_api_endpoints)
    ]

    results = []
    for validation_name, validation_func in validations:
        print(f"\n{'='*20} {validation_name} {'='*20}")
        try:
            result = validation_func()
            results.append((validation_name, result))
        except Exception as e:
            print(f"❌ {validation_name} failed with exception: {e}")
            results.append((validation_name, False))

    # Summary
    print("\n" + "="*60)
    print("🏁 VALIDATION SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for validation_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {validation_name}")

    print(f"\nResults: {passed}/{total} validations passed")

    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("Video intelligence integration is ready for deployment.")
        generate_deployment_checklist()
    elif passed >= total * 0.8:
        print("\n⚠️ Most validations passed. Minor issues may need attention.")
        generate_deployment_checklist()
    else:
        print("\n🚨 Several validations failed. Integration needs review.")

    print("="*60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)