# ultimate_focusstacking_with_apple_and_adobe

[![Pylint](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/pylint.yml/badge.svg)](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/pylint.yml) [![Testing](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/python-pytest-flake8.yml/badge.svg)](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/python-pytest-flake8.yml) [![mypy](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/mypy.yml/badge.svg)](https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe/actions/workflows/mypy.yml)

Automated focus stacking workflow that handles photo extraction, grouping, and final stacked images. Supports photos from any source.

## What This Does

3-step automated workflow that processes focus stacks:

* **Step 1**: `fetcher.py` - Extracts recent photos from iCloud Photos library
* **Step 2**: `grouper.py` - Groups photos by timestamp for focus stacking  
* **Step 3**: `stacker.js` - Processes focus stacks in Adobe Photoshop

**Multiple Photo Sources**: Works with photos from iCloud, USB, network drives, manual copying - any way you get photos to your Mac.

**Incremental Folders**: Creates `!newstack`, `!newstack_1`, `!newstack_2` etc. and decides what to do based on folder contents.

**Multiple Formats**: Supports JPG, JPEG, TIFF, TIF, BMP, PNG, HEIC files.

**Smart Skip Logic**: Skips Photoshop step when no focus stacking groups are found. Run `python runner.py` and it figures out what needs to be done.  

## Quick Start

### Prerequisites
- **macOS** (required for Photos app integration)
- **Adobe Photoshop** (tested with CC 2020 21.2.0 and newer)
- **Python 3.8+** with dependencies: `pip install -r requirements.txt`

### Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/baidakovil/ultimate_focusstacking_with_apple_and_adobe.git
   cd ultimate_focusstacking_with_apple_and_adobe
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your settings**:
   ```bash
   cp settings.txt my_settings.txt
   ```
   Edit `my_settings.txt` with your paths and preferences:
   ```json
   {
       "hours_icloud": "24",
       "stacker": "stacker.js",
       "folder_grouped": "fs",
       "path_all_storing": "/Volumes/External HD/Naturalist/",
       "folder_current_storing": "!newstack",
       "photoshop_app": "Adobe Photoshop 2025"
   }
   ```

### Running the Workflow
```bash
# Run with default settings.txt
python main.py

# Or use the StackDealer.app for a GUI experience
open StackDealer.app

# The system automatically determines what to do:
# 1. Checks existing folders and decides next action
# 2. Extracts photos OR groups existing photos OR creates new folder
# 3. Processes groups in Photoshop (or skips if no groups found)

# Example output:
# ========================================
# WORKFLOW ANALYSIS: Checking existing folders
# ========================================
# Determined action: run_fetcher
# Working with folder: /Volumes/External HD/Naturalist/!newstack_3
# 
# STEP 1: Fetching photos from Photos library
# ✅ Photo fetcher completed successfully!
# 
# STEP 2: Running grouper.py to organize photos  
# ✅ Photo grouping completed successfully!
# 
# STEP 3: Running Photoshop script for focus stacking
# ✅ Photoshop script executed successfully!
```

## Workflow Logic

### How It Decides What To Do
The system checks your storage folder and makes decisions based on what it finds:

| Folder State | Action | What Happens |
|-------------|---------|--------------|
| **No folders exist** | Create `!newstack`, run fetcher | Extracts photos from iCloud |
| **Empty `!newstack` folder** | Use existing folder, run fetcher | Extracts photos into existing folder |
| **Folder with images, no `fs` subfolder** | Run grouper on existing photos | Groups photos from USB/manual copy/etc |
| **Folder with `fs` subfolder (completed)** | Create `!newstack_1`, run fetcher | Starts fresh with new increment |

### The Three Steps

```
📁 Folder Analysis → Determines next action
    ↓
Step 1: Extract photos from iCloud Photos (if needed)
    ↓
Step 2: Analyze photos for focus stacking groups  
    ├── No image files found → Exit with message
    ├── No groups created → Skip Step 3, exit gracefully ⭐
    └── Groups created → Proceed to Step 3
         ↓
Step 3: Process focus stacks in Photoshop
    ↓
Complete!
```

**Key Features:**
- Auto-increment folders: Never overwrites previous work
- Multi-source support: Works with photos from any source
- Conditional processing: Skips Photoshop when no groups found
- Multiple formats: JPG, JPEG, TIFF, TIF, BMP, PNG, HEIC
- Uses Photoshop's Auto-Align and Auto-Blend algorithms

## Project Structure

```
pyfocusstackfo/
├── main.py                     # Main entry point for the workflow
├── settings.txt                # Production configuration file
├── settings_test.txt           # Test configuration file
├── requirements.txt            # Python dependencies
├── StackDealer.app/            # macOS app bundle for easy launching
├── StackDealer.applescript     # Source for the app bundle
├── src/                        # Core Python modules
│   ├── runner.py               # Workflow orchestrator (3-step workflow)
│   ├── fetcher.py              # Step 1: iCloud Photos extraction with CLI interface
│   ├── grouper.py              # Step 2: Smart photo grouping (supports multiple formats)
│   ├── folder_manager.py       # Incremental folder logic and workflow decisions
│   └── scripts/
│       └── stacker.js          # Step 3: Photoshop automation (conditionally executed)
├── tests/                      # Test files and test data
│   ├── test_enhanced_workflow.py
│   ├── test_integration.py
│   ├── test_no_groups.py
│   └── data/                   # Test data files
├── demos/                      # Demonstration scripts
│   └── demo_enhanced_workflow.py
└── docs/                       # Documentation and guides
    ├── ENHANCED_WORKFLOW_SUMMARY.md
    └── IMPLEMENTATION_SUMMARY.md
```

## Component Details

### Step 1: Photo Fetcher (`fetcher.py`)
Extracts photos from the macOS Photos library based on recency:
- Uses AppleScript to communicate with Photos app
- Configurable time window (hours)
- Exports to specified destination folder
- Handles permissions and error cases

### Step 2: Photo Grouper (`grouper.py`)
Groups photos into focus stacking sequences based on timestamps:
- **Multiple format support**: JPG, JPEG, TIFF, TIF, BMP, PNG, HEIC
- **Case insensitive**: Handles `.JPG`, `.jpg`, `.Jpg` etc.
- Analyzes EXIF timestamps to detect photo sequences
- Groups photos taken within `MAX_TIME_DELTA` (2 seconds by default)
- Only creates groups with minimum `MIN_STACK_LEN` photos (5 by default)
- **Exit codes**: 
  - `0` = Success (groups created and ready for Photoshop)
  - `1` = No image files found in source folder
  - `2` = Photos found but no groups created (sequences too short)

### Step 3: Photoshop Processor (`stacker.js`)
Conditionally executed based on Step 2 results:
- Only runs when groups are successfully created in Step 2
- Processes multiple folders automatically in batch
- Uses Photoshop's Auto-Align and Auto-Blend functions
- Exports high-quality JPEG results with automatic cleanup
- Automatically skipped when no groups exist

### Workflow Orchestrator (`runner.py`)
Coordinates all components and makes workflow decisions:
- **Settings management**: Loads configuration from JSON settings file
- **Folder analysis**: Uses `folder_manager.py` to determine next action
- **Step coordination**: Executes steps in sequence with proper error handling  
- **Status monitoring**: Interprets exit codes and makes decisions
- **Conditional logic**: Automatically skips Step 3 when Step 2 produces no groups
- **Incremental folders**: Creates `!newstack_1`, `!newstack_2` etc. automatically

### Folder Manager (`folder_manager.py`)
Handles incremental folder creation and workflow decisions:
- **Folder detection**: Finds existing folders with increment patterns
- **State analysis**: Determines if folder is empty, has images, or is completed
- **Workflow routing**: Decides whether to run fetcher, grouper, or create new folder
- **Auto-increment**: Creates next available folder number when needed

## Photography Setup & Experience

I have tried: [Zerene], [Helicon Focus], [ChimpStackr], [Enfuse]. The first two can compete when you tweak the settings, but this Photoshop-based solution works better without any tweaking.

[Helicon Focus]: https://www.heliconsoft.com/heliconsoft-products/helicon-focus/
[Zerene]: https://www.zerenesystems.com/cms/stacker
[ChimpStackr]: https://github.com/noah-peeters/ChimpStackr
[Enfuse]: https://enblend.sourceforge.net/enfuse.doc/enfuse_4.2.xhtml/enfuse.html

I shoot nature and can have thousands of photos from a single walk, with 5-10 photos in each stack, meaning ~100 focus stacks at once. With these scripts, it takes about an hour to get results for everything.

### Why Photoshop Works Best

Photoshop's Auto-Align and Auto-Blend functions work so well that you won't see a difference even with defocused, corrupted, or rotated photos among the good stacking photos. I tried experiments with cleaning unsuccessful photos before stacking, but didn't see much difference: with Photoshop, the result mostly depends on the successful photos. This ability is especially important to me as I often shoot without a tripod and half of my photos are suboptimal.

This is not the case with other focus stacking software: one bad photo will often ruin the whole result.

### Mobile Photography Integration

I use [CameraPixels](https://apps.apple.com/us/app/camerapixels-lite/id1125808205) iOS app on my iPhone in focus stacking mode. It takes photos with intervals of 0.5-1 seconds. Having `MAX_TIME_DELTA = 2 sec` in the grouper, I get files organized into folders correctly almost always.

Sometimes there could be non-focus-stacking photos taken close to each other — but thanks to the `MIN_STACK_LEN` setting, they probably won't be grouped into a "stack".

Recent examples: [1], [2], [3], [4], [5].

[1]: https://www.inaturalist.org/observations/187942621
[2]: https://www.inaturalist.org/observations/187239060
[3]: https://www.inaturalist.org/observations/183093937
[4]: https://www.inaturalist.org/observations/169738063
[5]: https://www.inaturalist.org/observations/182633085

## Advanced Configuration

### Settings File (`settings.txt`)
The workflow uses JSON configuration for all parameters:

```json
{
    "hours_icloud": "24",
    "stacker": "stacker.js", 
    "path_grouped": "/Users/yourname/Documents/focus_stacks/fs",
    "path_iphone": "/Users/yourname/Documents/extracted_photos/",
    "photoshop_app": "Adobe Photoshop 2025"
}
```

**Configuration Parameters:**
- `hours_icloud`: Time window for photo extraction (hours back from now)
- `path_iphone`: Destination folder for Step 1 (photo extraction)  
- `path_grouped`: Base folder for Step 2 (grouping creates `/fs` subfolder automatically)
- `stacker`: Path to JavaScript file for Photoshop automation
- `photoshop_app`: Exact application name for your Photoshop installation

### Grouper Algorithm Settings
Key parameters in `grouper.py` for fine-tuning:

```python
MAX_TIME_DELTA = timedelta(seconds=2)    # Maximum time between photos in a stack
MIN_STACK_LEN = 5                        # Minimum photos required to create a stack  
LENGTH_STACK_WARNING = 10                # Warns about unusually large stacks
```

**Tuning Guidelines:**
- `MAX_TIME_DELTA`: Increase if using slower shooting intervals (e.g., 3-4 seconds)
- `MIN_STACK_LEN`: Decrease to 3-4 for aggressive grouping, increase to 6-8 for conservative approach
- `LENGTH_STACK_WARNING`: Adjust based on your typical stack sizes

### Runner Behavior Settings
The workflow orchestrator (`runner.py`) supports:

```bash
# Use default settings.txt
python runner.py

# Use custom settings file
python runner.py my_custom_settings.txt

# Settings file must be valid JSON format
```

**Intelligent Decision Points:**
- Step 2 → Step 3: Automatic skip when `grouper.py` exits with code 2 (no groups)
- Error handling: Workflow stops on errors with clear diagnostic messages
- Status reporting: Real-time feedback on each step's progress and results

## Testing & Validation

The project includes comprehensive test suites to validate the intelligent workflow:

### Test Scripts
```bash
# Test the conditional workflow logic
python test_no_groups.py        # Validates Step 3 skipping when no groups

# Run comprehensive integration tests  
python test_integration.py      # Tests all workflow scenarios

# Final demonstration of complete workflow
python demo_final.py           # Shows end-to-end intelligent processing
```

### Test Scenarios Covered
- Normal operation: Photos → Groups → Photoshop processing
- No files scenario: Empty source folder handling  
- No groups scenario: Photos present but no stacks needed (Step 3 skipped)
- Error handling: Invalid paths, missing dependencies, etc.

### Validation Results
All tests pass and confirm:
- Proper exit code communication between components
- Conditional Step 3 execution based on grouper results
- Graceful handling of edge cases
- Robust error reporting and user feedback

## 🔄 Workflow Details

### Complete 3-Step Process

#### Step 1: Photo Fetcher (`src/fetcher.py`)
```bash
python src/fetcher.py <destination_folder> <hours>
```
- Uses AppleScript to communicate with macOS Photos app
- Extracts photos taken within the specified time window
- Handles permissions and exports to destination folder
- Exit codes: 0 = success, 1 = error

#### Step 2: Photo Grouper (`src/grouper.py`)
```bash
python src/grouper.py <source_folder> <destination_folder>
```
1. Scans source folder for image files and sorts them alphabetically
2. Analyzes EXIF `Date taken` field for each photo
3. Groups photos taken within `MAX_TIME_DELTA` (2 seconds) into potential stacks
4. Only creates folders for groups with ≥ `MIN_STACK_LEN` photos (5 minimum)
5. Moves grouped photos to folders named: `{FIRST_FILE}_to_{LAST_FILE}`
6. Exit codes:
   - 0 = success (groups created)
   - 1 = no image files found
   - 2 = no groups created (all sequences too short)

#### Step 3: Photoshop Processor (`src/scripts/stacker.js`)
- Conditionally executed only when Step 2 creates groups
- Processes each folder automatically using Photoshop's Auto-Align and Auto-Blend
- Exports high-quality focus stacked results
- Handles multiple folders in batch

### Intelligent Decision Making

The workflow automatically handles different scenarios:

```
Photos extracted → Groups analyzed → Decision Point:
                                   ├── No groups? → Skip Photoshop
                                   └── Groups found? → Process in Photoshop
```

This intelligent behavior means:
- No wasted time on unnecessary Photoshop processing
- Clean completion when no focus stacking opportunities exist
- Robust handling of edge cases (no photos, single photos, etc.)

## Troubleshooting

### Common Scenarios & Solutions

**"Step 3 was skipped - no groups to process"**
- Normal behavior when photos don't form focus stacks
- Check that photos were taken within 2 seconds of each other
- Verify minimum 5 photos per sequence (adjustable in `grouper.py`)

**"No image files found"**
- Check Photos app permissions for the fetcher script
- Verify the time window (`hours_icloud` setting) includes your photos
- Ensure photos are actually present in the specified time range

**"Photoshop automation failed"**
- Verify `photoshop_app` name matches your installation exactly
- Check that Photoshop is closed before running the workflow
- Ensure grouped folders contain actual image files

**Settings file issues**
- Validate JSON syntax (use online JSON validator if needed)
- Check all paths exist and are accessible
- Ensure forward slashes in paths, even on Windows

### Workflow Status Messages

```bash
# Success with groups created
Step 1 (fetcher): Success
Step 2 (grouper): Success - groups created  
Step 3 (stacker): Success

# Success but no groups (Step 3 skipped)
Step 1 (fetcher): Success
Step 2 (grouper): No groups created
Step 3 (stacker): Skipped - no groups to process

# Error scenarios  
Step 1 (fetcher): Error - <specific error message>
Workflow stopped due to error
```

## Details on the _.js_ script

The JavaScript automation script handles the Adobe Photoshop integration:

**Original inspiration**: The first version was found in Adobe Community [Discussion] by user *SuperMerlin* for three-file focus stacking.

**Enhancements added**:
- Arbitrary file quantity: Processes focus stacks of any size
- Batch processing: Handles multiple subfolders automatically  
- Integration: Works seamlessly with the Python workflow orchestrator

**Important notes**:
1. Auto-cropping not included: If photos have poor alignment, result may have gray-filled edges requiring manual crop
2. Folder validation: Script requires non-empty folders to function properly
3. Photoshop compatibility: Tested with CC 2020+ versions

The script is automatically invoked by `runner.py` when Step 2 creates focus stacking groups.


[Discussion]: https://community.adobe.com/t5/photoshop-ecosystem-discussions/automate-focus-stacking-script-action-help-needed/m-p/10483237

## Build with

**[Adobe Photoshop]** - Photo editing and design software since 1990 | *proprietary*  
**[AppleScript]** - Automation scripting language for macOS since 1993 | *Apple proprietary*  
**[JavaScript]** - Scripting language for web pages and applications since 1995 | *License depends on implementation*  
**[macOS Photos.app]** - System photo library and management application | *Apple proprietary*  
**[pyexif]** - Python wrapper for the exiftool library since 2011 | *Apache 2*  
**[Python]** - Programming language for system integration since 1991 | *GPL compatible*  
**[JSON]** - Lightweight data interchange format | *Open standard*


[Adobe Photoshop]: https://www.adobe.com/products/photoshop.html
[AppleScript]: https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html
[macOS Photos.app]: https://www.apple.com/macos/photos/
[pyexif]: https://pypi.org/project/pyexif/
[Python]: https://www.python.org/
[JavaScript]: https://ecma-international.org/publications-and-standards/standards/ecma-262/
[JSON]: https://www.json.org/

## Contributions

Please feel free to contribute, create pull requests, comment and further. 

## Feedback and PyPi.org

If you find any of these scripts helpful, please leave feedback.  
In case you would like to see `pyfocusstack.py` as a python package, please write to me: If there will be at least one person who finds this helpful, I will reformat the code and add it to PyPi. 
