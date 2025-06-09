import subprocess
import os
import json
import sys

# Add the current directory to Python path to import folder_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from folder_manager import determine_workflow_action, create_folder_if_needed

def load_settings(settings_file="settings.txt"):
    """Load settings from JSON file"""
    try:
        # If settings_file is relative, look for it in the project root
        if not os.path.isabs(settings_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)  # Go up one level from src/
            settings_file = os.path.join(project_root, settings_file)
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        print(f"Error: Settings file '{settings_file}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in settings file: {e}")
        return None


def run_fetcher(path_current, hours_icloud):
    """Run fetcher.py to extract photos from Photos library"""
    # Normalize the path to handle special characters
    path_current = os.path.abspath(os.path.expanduser(path_current))
    
    print(f"Running photo fetcher with destination: {path_current}")
    print(f"Looking for photos from last {hours_icloud} hours")
    
    try:
        # Get the path to fetcher.py in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fetcher_path = os.path.join(script_dir, "fetcher.py")
        
        # Run fetcher.py as subprocess with command line arguments
        result = subprocess.run([
            sys.executable, 
            fetcher_path, 
            path_current, 
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


def run_grouper(path_current):
    """Run grouper.py with the specified path"""
    # Normalize the path to handle special characters
    path_current = os.path.abspath(os.path.expanduser(path_current))
    
    # Validate path
    if not os.path.exists(path_current):
        print(f"Error: Path does not exist: {path_current}")
        return "error"
    
    if not os.path.isdir(path_current):
        print(f"Error: Path is not a directory: {path_current}")
        return "error"
    
    print(f"Running grouper.py with path: {path_current}")
    
    try:
        # Get the path to grouper.py in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        grouper_path = os.path.join(script_dir, "grouper.py")
        
        # Run grouper.py with the specified path
        result = subprocess.run([
            sys.executable, 
            grouper_path, 
            path_current
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
            print("Grouper.py completed successfully with return code 0")
            return "success"
        elif result.returncode == 1:
            print("No image files found in folder.")
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
        result = subprocess.run(["osascript", "-e", applescript_command], check=True, capture_output=True, text=True)
        
        # Display the result from JavaScript execution
        if result.stdout.strip():
            js_output = result.stdout.strip()
            if js_output and js_output != "undefined":
                print(f"✨ {js_output}")
        
        print(f"📸 Photoshop script executed successfully: {os.path.basename(stacker)}")
        print(f"📁 Processed folder: {os.path.basename(path_grouped)}")
        
        # Close Photoshop after successful execution
        print("🔄 Closing Photoshop...")
        close_command = f'tell application "{photoshop_app}" to quit'
        subprocess.run(["osascript", "-e", close_command], check=True)
        print("✅ Photoshop closed successfully.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing Photoshop script: {e}")
        print(f"AppleScript command was: {applescript_command}")
        return False

def main():
    """Main workflow execution function"""
    # Load settings from file
    settings = load_settings()
    if settings is None:
        print("Error: Could not load settings. Please check the settings file.")
        exit(1)
    
    # Extract settings
    stacker = settings.get("stacker")
    folder_grouped = settings.get("folder_grouped") 
    path_all_storing = settings.get("path_all_storing")
    folder_current_storing = settings.get("folder_current_storing")
    photoshop_app = settings.get("photoshop_app")
    hours_icloud = settings.get("hours_icloud")
    
    # Validate required settings
    if not all([stacker, folder_grouped, path_all_storing, folder_current_storing, photoshop_app, hours_icloud]):
        print("Error: Missing required settings (stacker, folder_grouped, path_all_storing, folder_current_storing, photoshop_app, hours_icloud)")
        exit(1)
    
    # Normalize paths - update stacker path to account for new structure
    if not os.path.isabs(stacker):
        # If stacker path is relative, look for it in src/scripts/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stacker = os.path.join(script_dir, "scripts", stacker)
    else:
        stacker = os.path.abspath(os.path.expanduser(stacker))
    
    path_all_storing = os.path.abspath(os.path.expanduser(path_all_storing))
    
    # Check if stacker script exists
    if not os.path.exists(stacker):
        print(f"Error: Script file does not exist: {stacker}")
        exit(1)
    
    print("\n" + "=" * 55)
    print("⚙️ Using settings:")
    print("=" * 55)
    print(f"  Photo Fetcher: fetcher.py")
    print(f"  Grouper Script: grouper.py")
    print(f"  All Storage Path: {path_all_storing}")
    print(f"  Current Folder Pattern: {folder_current_storing}")
    print(f"  Grouped Folder Name: {folder_grouped}")
    print(f"  Stacker Script: {stacker}")
    print(f"  Photoshop: {photoshop_app}")
    print(f"  Hours to fetch: {hours_icloud}")
    print()
    
    # Determine what action to take based on existing folders
    print("=" * 55)
    print("🔍 WORKFLOW ANALYSIS: Checking existing folders")
    print("=" * 55)
    
    action, current_folder_path = determine_workflow_action(
        path_all_storing, 
        folder_current_storing, 
        folder_grouped
    )
    
    if action == "error":
        print(f"Error: {current_folder_path}")
        exit(1)
    
    print(f"Determined action: {action}")
    print(f"Working with folder: {current_folder_path}")
    
    # Calculate path_grouped for Photoshop script
    path_grouped = os.path.join(current_folder_path, folder_grouped)
    
    if action == "run_fetcher":
        # Create the folder if needed
        if not create_folder_if_needed(current_folder_path):
            print("Error: Could not create current folder. Cannot proceed.")
            exit(1)
        
        # Step 1: Run fetcher.py to extract photos from Photos library
        print("\n" + "=" * 55)
        print("📸 STEP 1: Fetching photos from Photos library")
        print("=" * 55)
        
        if not run_fetcher(current_folder_path, hours_icloud):
            print("Error: Photo fetcher failed. Cannot proceed to next steps.")
            exit(1)
        
        # Step 2: Run grouper.py to organize photos
        print("\n" + "=" * 55)
        print("📁 STEP 2: Running grouper.py to organize photos")
        print("=" * 55)
        
        grouper_result = run_grouper(current_folder_path)
        
        if grouper_result == "error":
            print("Error: Grouper.py failed with critical error. Cannot proceed.")
            exit(1)
        elif grouper_result == "no_files":
            print("No image files found. Workflow completed - nothing to process.")
            exit(0)
        elif grouper_result == "no_groups":
            print("\nNo focus stacking groups were created.")
            print("This means no photos were taken close enough in time to be considered for focus stacking.")
            print("Skipping Step 3 (Photoshop processing) - workflow completed.")
            print("\n" + "=" * 55)
            print("WORKFLOW COMPLETED: Photos fetched but no focus stacking needed")
            print("=" * 55)
            exit(0)
        elif grouper_result == "success":
            print("Photo grouping completed successfully! Proceeding to Photoshop step.")
        else:
            print(f"Unexpected result from grouper: {grouper_result}")
            exit(1)
    
    elif action == "run_grouper":
        # Step 2: Run grouper.py to organize existing photos
        print("\n" + "=" * 55)
        print("📁 STEP 2: Running grouper.py to organize existing photos")
        print("=" * 55)
        
        grouper_result = run_grouper(current_folder_path)
        
        if grouper_result == "error":
            print("Error: Grouper.py failed with critical error. Cannot proceed.")
            exit(1)
        elif grouper_result == "no_files":
            print("No image files found. Workflow completed - nothing to process.")
            exit(0)
        elif grouper_result == "no_groups":
            print("\nNo focus stacking groups were created.")
            print("This means no photos were taken close enough in time to be considered for focus stacking.")
            print("Skipping Step 3 (Photoshop processing) - workflow completed.")
            print("\n" + "=" * 55)
            print("WORKFLOW COMPLETED: Photos analyzed but no focus stacking needed")
            print("=" * 55)
            exit(0)
        elif grouper_result == "success":
            print("Photo grouping completed successfully! Proceeding to Photoshop step.")
        else:
            print(f"Unexpected result from grouper: {grouper_result}")
            exit(1)
    
    # Step 3: Run Photoshop script for focus stacking (only if groups were created)
    print("\n" + "=" * 55)
    print("🎨 STEP 3: Running Photoshop script for focus stacking")
    print("=" * 55)
    
    if not run_photoshop_script(stacker, path_grouped, photoshop_app):
        print("Error: Photoshop script failed.")
        exit(1)
    
    print("\n"+"=" * 55)
    print("🎉 SUCCESS: All workflow steps completed successfully! 🎉")
    print("=" * 55)


if __name__ == "__main__":
    main()