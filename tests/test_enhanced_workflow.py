#!/usr/bin/env python3
"""
Test script to verify the enhanced workflow functionality.
Tests the new image format support and incremental folder management.
"""

import os
import sys
import tempfile
import shutil
from zipfile import ZipFile
import json
import subprocess

def test_multiple_image_formats():
    """Test that grouper.py now supports multiple image formats"""
    print("=" * 60)
    print("TEST 1: Multiple Image Format Support")
    print("=" * 60)
    
    test_dir = tempfile.mkdtemp(prefix="focusstack_formats_test_")
    print(f"Created test directory: {test_dir}")
    
    try:
        # Create test files with different extensions
        test_files = [
            "IMG_001.jpg",
            "IMG_002.JPEG", 
            "IMG_003.tiff",
            "IMG_004.TIF",
            "IMG_005.png",
            "IMG_006.bmp",
            "IMG_007.HEIC"
        ]
        
        # Create dummy files (they won't have proper EXIF but will test format detection)
        for filename in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write("dummy content")
        
        print(f"Created {len(test_files)} test files with different formats")
        
        # Test that grouper detects all formats
        # Note: This will fail at EXIF reading, but should at least detect the files
        result = subprocess.run([
            sys.executable, 
            "grouper.py", 
            test_dir
        ], capture_output=True, text=True)
        
        # Check if it detected the files (even if EXIF reading fails)
        if "image files" in result.stdout.lower():
            print("✅ Grouper successfully detected multiple image formats")
            return True
        else:
            print("❌ Grouper did not detect image formats properly")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_folder_increment_logic():
    """Test the incremental folder creation and decision logic"""
    print("\n" + "=" * 60)
    print("TEST 2: Incremental Folder Management")
    print("=" * 60)
    
    test_base_dir = tempfile.mkdtemp(prefix="focusstack_increment_test_")
    print(f"Created test base directory: {test_base_dir}")
    
    try:
        from folder_manager import determine_workflow_action, create_folder_if_needed
        
        # Test 1: No folders exist - should create first folder
        action, folder_path = determine_workflow_action(test_base_dir, "!newstack", "fs")
        expected_folder = os.path.join(test_base_dir, "!newstack")
        
        print(f"Test 1 - No folders exist:")
        print(f"  Action: {action}")
        print(f"  Folder: {folder_path}")
        print(f"  Expected: {expected_folder}")
        
        if action == "run_fetcher" and folder_path == expected_folder:
            print("✅ Test 1 passed")
        else:
            print("❌ Test 1 failed")
            return False
        
        # Create the folder and test again
        create_folder_if_needed(folder_path)
        
        # Test 2: Empty folder exists - should use same folder
        action, folder_path = determine_workflow_action(test_base_dir, "!newstack", "fs")
        
        print(f"\nTest 2 - Empty folder exists:")
        print(f"  Action: {action}")
        print(f"  Folder: {folder_path}")
        
        if action == "run_fetcher" and folder_path == expected_folder:
            print("✅ Test 2 passed")
        else:
            print("❌ Test 2 failed")
            return False
        
        # Test 3: Add some dummy image files to simulate "ready for grouper"
        dummy_image = os.path.join(folder_path, "test.jpg")
        with open(dummy_image, 'w') as f:
            f.write("dummy")
        
        action, folder_path = determine_workflow_action(test_base_dir, "!newstack", "fs")
        
        print(f"\nTest 3 - Folder with images (ready for grouper):")
        print(f"  Action: {action}")
        print(f"  Folder: {folder_path}")
        
        if action == "run_grouper" and folder_path == expected_folder:
            print("✅ Test 3 passed")
        else:
            print("❌ Test 3 failed")
            return False
        
        # Test 4: Add "fs" folder to simulate completed processing
        fs_folder = os.path.join(folder_path, "fs")
        os.makedirs(fs_folder)
        
        action, folder_path = determine_workflow_action(test_base_dir, "!newstack", "fs")
        expected_next_folder = os.path.join(test_base_dir, "!newstack_1")
        
        print(f"\nTest 4 - Completed folder (should create next increment):")
        print(f"  Action: {action}")
        print(f"  Folder: {folder_path}")
        print(f"  Expected: {expected_next_folder}")
        
        if action == "run_fetcher" and folder_path == expected_next_folder:
            print("✅ Test 4 passed")
        else:
            print("❌ Test 4 failed")
            return False
        
        print("✅ All incremental folder tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        shutil.rmtree(test_base_dir, ignore_errors=True)


def test_settings_format():
    """Test that the new settings format is working"""
    print("\n" + "=" * 60)
    print("TEST 3: Settings Format Validation")
    print("=" * 60)
    
    try:
        from runner import load_settings
        
        # Test loading current settings.txt
        settings = load_settings("settings.txt")
        
        if not settings:
            print("❌ Failed to load settings.txt")
            return False
        
        # Check all required new format fields
        required_fields = [
            "hours_icloud",
            "stacker", 
            "folder_grouped",
            "path_all_storing",
            "folder_current_storing",
            "photoshop_app"
        ]
        
        print("Checking required fields:")
        all_present = True
        for field in required_fields:
            if field in settings:
                print(f"  ✅ {field}: {settings[field]}")
            else:
                print(f"  ❌ {field}: MISSING")
                all_present = False
        
        # Verify no old format fields are present
        old_fields = ["path_grouped", "path_iphone"]
        for field in old_fields:
            if field in settings:
                print(f"  ⚠️  Old field still present: {field}")
                all_present = False
        
        if all_present:
            print("✅ Settings format validation passed!")
            return True
        else:
            print("❌ Settings format validation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def test_runner_integration():
    """Test that runner.py works with the new settings format"""
    print("\n" + "=" * 60)
    print("TEST 4: Runner Integration Test")
    print("=" * 60)
    
    try:
        # Test that runner can import and validate settings
        result = subprocess.run([
            sys.executable, 
            "-c",
            """
import sys
sys.path.insert(0, '.')
from runner import load_settings
from folder_manager import determine_workflow_action

# Load settings
settings = load_settings('settings.txt')
if not settings:
    print('FAIL: Could not load settings')
    exit(1)

# Extract settings
folder_grouped = settings.get('folder_grouped') 
path_all_storing = settings.get('path_all_storing')
folder_current_storing = settings.get('folder_current_storing')

# Test folder logic (using a safe test path)
import tempfile
test_dir = tempfile.mkdtemp()
action, folder_path = determine_workflow_action(test_dir, folder_current_storing, folder_grouped)

print(f'SUCCESS: action={action}, folder_type={type(folder_path).__name__}')

import shutil
shutil.rmtree(test_dir)
"""
        ], cwd="/Users/baidakov/Git/pyfocusstackfo", capture_output=True, text=True)
        
        print("Runner integration test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode == 0 and "SUCCESS:" in result.stdout:
            print("✅ Runner integration test passed!")
            return True
        else:
            print("❌ Runner integration test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def main():
    """Run all enhanced workflow tests"""
    print("🚀 ENHANCED WORKFLOW TESTING")
    print("Testing new image format support and incremental folder management")
    print()
    
    os.chdir("/Users/baidakov/Git/pyfocusstackfo")
    
    tests = [
        ("Multiple Image Formats", test_multiple_image_formats),
        ("Incremental Folder Management", test_folder_increment_logic),
        ("Settings Format", test_settings_format),
        ("Runner Integration", test_runner_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nSummary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Enhanced workflow is ready!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please review.")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
