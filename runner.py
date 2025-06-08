import subprocess
import os
import json
import sys

def load_settings(settings_file="settings.txt"):
    """Load settings from JSON file"""
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        print(f"Error: Settings file '{settings_file}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in settings file: {e}")
        return None


def run_fetcher(path_iphone, hours_icloud):
    """Run fetcher.py to extract photos from Photos library"""
    # Normalize the path to handle special characters
    path_iphone = os.path.abspath(os.path.expanduser(path_iphone))
    
    print(f"Running photo fetcher with destination: {path_iphone}")
    print(f"Looking for photos from last {hours_icloud} hours")
    
    try:
        # Run fetcher.py as subprocess with command line arguments
        result = subprocess.run([
            sys.executable, 
            "fetcher.py", 
            path_iphone, 
            hours_icloud
        ], check=True, capture_output=True, text=True)
        
        print("Photo fetcher output:")
        print(result.stdout)
        if result.stderr:
            print("Photo fetcher warnings/errors:")
            print(result.stderr)
        
        print("Photo fetcher completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running fetcher.py: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False
    except FileNotFoundError:
        print("Error: fetcher.py not found in current directory")
        return False
    except Exception as e:
        print(f"Error running photo fetcher: {e}")
        return False


def run_grouper(path_iphone):
    """Run grouper.py with the specified path"""
    # Normalize the path to handle special characters
    path_iphone = os.path.abspath(os.path.expanduser(path_iphone))
    
    # Validate path
    if not os.path.exists(path_iphone):
        print(f"Error: Path does not exist: {path_iphone}")
        return "error"
    
    if not os.path.isdir(path_iphone):
        print(f"Error: Path is not a directory: {path_iphone}")
        return "error"
    
    print(f"Running grouper.py with path: {path_iphone}")
    
    try:
        # Run grouper.py with the specified path
        result = subprocess.run([
            sys.executable, 
            "grouper.py", 
            path_iphone
        ], capture_output=True, text=True, check=False)
        
        # Print output regardless of exit code
        if result.stdout:
            print("Grouper.py output:")
            print(result.stdout)
        if result.stderr:
            print("Grouper.py errors:")
            print(result.stderr)
        
        # Check exit code and return appropriate status
        if result.returncode == 0:
            print("Grouper.py completed successfully!")
            return "success"
        elif result.returncode == 1:
            print("No JPG files found in folder.")
            return "no_files"
        elif result.returncode == 2:
            print("No focus stacking groups were created.")
            return "no_groups"
        else:
            print(f"Grouper.py failed with exit code: {result.returncode}")
            return "error"
        
    except FileNotFoundError:
        print("Error: grouper.py not found in current directory")
        return "error"

def run_photoshop_script(stacker, path_grouped, photoshop_app):
    # Check if the script file exists
    if not os.path.exists(stacker):
        print(f"Error: Script file not found: {stacker}")
        return False
    
    # Pass folder path as argument to the JavaScript
    applescript_command = f'tell application "{photoshop_app}" to do javascript of file "{stacker}" with arguments {{"{path_grouped}"}}'
    
    try:
        subprocess.run(["osascript", "-e", applescript_command], check=True)
        print(f"Photoshop script executed successfully: {stacker}")
        print(f"With folder: {path_grouped}")
        
        # Close Photoshop after successful execution
        print("Closing Photoshop...")
        close_command = f'tell application "{photoshop_app}" to quit'
        subprocess.run(["osascript", "-e", close_command], check=True)
        print("Photoshop closed successfully.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing Photoshop script: {e}")
        print(f"AppleScript command was: {applescript_command}")
        return False

if __name__ == "__main__":
    # Load settings from file
    settings = load_settings()
    if settings is None:
        print("Error: Could not load settings. Please check the settings file.")
        exit(1)
    
    # Extract settings
    stacker = settings.get("stacker")
    path_grouped = settings.get("path_grouped") 
    path_iphone = settings.get("path_iphone")
    photoshop_app = settings.get("photoshop_app")
    hours_icloud = settings.get("hours_icloud")
    
    # Validate required settings
    if not all([stacker, path_grouped, path_iphone, photoshop_app, hours_icloud]):
        print("Error: Missing required settings (stacker, path_grouped, path_iphone, photoshop_app, hours_icloud)")
        exit(1)
    
    # Normalize and validate paths
    stacker = os.path.abspath(os.path.expanduser(stacker))
    path_grouped = os.path.abspath(os.path.expanduser(path_grouped))
    path_iphone = os.path.abspath(os.path.expanduser(path_iphone))
    
    # Check if stacker script exists
    if not os.path.exists(stacker):
        print(f"Error: Script file does not exist: {stacker}")
        exit(1)
    
    print(f"Using settings:")
    print(f"  Photo Fetcher: fetcher.py")
    print(f"  Grouper Script: grouper.py")
    print(f"  iPhone Photos: {path_iphone}")
    print(f"  Stacker Script: {stacker}")
    print(f"  Grouped Folder: {path_grouped}")
    print(f"  Photoshop: {photoshop_app}")
    print(f"  Hours to fetch: {hours_icloud}")
    print()
    
    # Step 1: Run fetcher.py to extract photos from Photos library
    print("=" * 50)
    print("STEP 1: Fetching photos from Photos library")
    print("=" * 50)
    
    if not run_fetcher(path_iphone, hours_icloud):
        print("Error: Photo fetcher failed. Cannot proceed to next steps.")
        exit(1)
    
    # Step 2: Run grouper.py to organize photos
    print("\n" + "=" * 50)
    print("STEP 2: Running grouper.py to organize photos")
    print("=" * 50)
    
    grouper_result = run_grouper(path_iphone)
    
    if grouper_result == "error":
        print("Error: Grouper.py failed with critical error. Cannot proceed.")
        exit(1)
    elif grouper_result == "no_files":
        print("No JPG files found. Workflow completed - nothing to process.")
        exit(0)
    elif grouper_result == "no_groups":
        print("\nNo focus stacking groups were created.")
        print("This means no photos were taken close enough in time to be considered for focus stacking.")
        print("Skipping Step 3 (Photoshop processing) - workflow completed.")
        print("\n" + "=" * 50)
        print("WORKFLOW COMPLETED: Photos fetched but no focus stacking needed")
        print("=" * 50)
        exit(0)
    elif grouper_result == "success":
        print("Photo grouping completed successfully! Proceeding to Photoshop step.")
    else:
        print(f"Unexpected result from grouper: {grouper_result}")
        exit(1)
    
    # Step 3: Run Photoshop script for focus stacking (only if groups were created)
    print("\n" + "=" * 50)
    print("STEP 3: Running Photoshop script for focus stacking")
    print("=" * 50)
    
    if not run_photoshop_script(stacker, path_grouped, photoshop_app):
        print("Error: Photoshop script failed.")
        exit(1)
    
    print("\n" + "=" * 50)
    print("SUCCESS: All three steps completed successfully!")
    print("=" * 50)