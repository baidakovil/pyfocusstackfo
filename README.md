# pyfocusstackfo

[![Pylint](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/pylint.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/pylint.yml) [![Testing](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/python-pytest-flake8.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/python-pytest-flake8.yml) [![mypy](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/mypy.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/mypy.yml)

**Complete automated focus stacking workflow** for macro photography enthusiasts who want professional results with minimal effort.

## 🌟 What Makes This Special

This is a **fully automated 3-step intelligent workflow** that handles everything from iCloud Photos extraction to final focus stacked images:

* **Step 1**: `fetcher.py` - Automatically extracts recent photos from your iCloud Photos library
* **Step 2**: `grouper.py` - Intelligently analyzes timestamps and groups photos for focus stacking  
* **Step 3**: `stacker.js` - Processes focus stacks in Adobe Photoshop using advanced algorithms

**🧠 Intelligent Processing**: The system automatically detects when no focus stacking is needed and gracefully skips unnecessary processing steps, saving you time and resources. **No manual intervention required** - just run `python runner.py` and get professional results.  

## 🚀 Quick Start

### Prerequisites
- **macOS** (required for Photos app integration)
- **Adobe Photoshop** (tested with CC 2020 21.2.0 and newer)
- **Python 3.8+** with dependencies: `pip install -r requirements.txt`

### Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/baidakovil/pyfocusstackfo.git
   cd pyfocusstackfo
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
       "path_grouped": "/Users/yourname/Documents/focus_stacks/fs",
       "path_iphone": "/Users/yourname/Documents/extracted_photos/",
       "photoshop_app": "Adobe Photoshop 2025"
   }
   ```

### Running the Workflow
```bash
# Run with default settings.txt
python runner.py

# Or with custom settings file
python runner.py my_settings.txt

# The system automatically:
# 1. ✅ Extracts recent photos from iCloud Photos
# 2. 🔍 Analyzes photos for focus stacking opportunities  
# 3. 🎨 Processes groups in Photoshop (or skips if no groups found)

# Example output:
# ========================================
# 🎯 PYFOCUSSTACKFO - Automated Focus Stacking Workflow
# ========================================
# 
# Step 1: Fetching photos from iCloud Photos library...
# ✅ Step 1 (fetcher): Success
# 
# Step 2: Grouping photos for focus stacking...
# ✅ Step 2 (grouper): Success - groups created
# 
# Step 3: Processing focus stacks in Photoshop...
# ✅ Step 3 (stacker): Success
# 
# 🎉 Workflow completed successfully!
```

## 🧠 Intelligent Workflow

### Smart Decision Making
The system intelligently adapts to different photo scenarios:

| Scenario | Step 1 | Step 2 | Step 3 | Result |
|----------|---------|---------|---------|---------|
| **Normal Operation** | ✅ Photos extracted | ✅ Groups created | ✅ Photoshop processing | Focus stacked images |
| **No Recent Photos** | ❌ No photos found | ⏭️ Skipped | ⏭️ Skipped | Clean exit with message |
| **Photos but No Stacks** | ✅ Photos extracted | ⚠️ No groups (sequences too short) | ⏭️ **Intelligently skipped** | Graceful completion |
| **Error State** | ❌ Error occurred | ⏭️ Skipped | ⏭️ Skipped | Error reported to user |

### Why This Intelligence Matters

**🎯 Efficiency**: No time wasted on unnecessary Photoshop processing when photos don't need stacking

**🧠 User Experience**: The system "understands" your photo library and adapts accordingly

**📱 Real-world Scenarios**: Perfect for mixed photo libraries with both focus stacks and regular photos

**🔄 Workflow Integration**: Fits naturally into daily photography workflows without manual intervention

### Example Scenarios

```bash
# Scenario 1: Mixed photo session (some stacks, some singles)
# Photos extracted: 20 photos
# Groups created: 2 focus stacks (5 photos each)
# Result: 2 focus stacked images + 10 individual photos remain untouched

# Scenario 2: Portrait session (no focus stacking needed)  
# Photos extracted: 15 photos
# Groups created: 0 (all photos taken >2 seconds apart)
# Result: Step 3 automatically skipped, clean completion

# Scenario 3: No recent photos
# Photos extracted: 0
# Result: Workflow stops gracefully with informative message
```

The system handles different scenarios automatically:

```
Step 1: Extract photos from iCloud Photos
    ↓
Step 2: Analyze photos for focus stacking groups
    ├── No JPG files found → Exit with informative message
    ├── No groups created → Skip Step 3, complete gracefully ⭐
    └── Groups created → Proceed to Step 3
         ↓
Step 3: Process focus stacks in Photoshop
    ↓
Complete! 🎉
```

**🎯 Key Features:**
- **Smart Detection**: Automatically detects when no focus stacking is needed
- **Conditional Processing**: Skips Photoshop step when no groups are found
- **Robust Error Handling**: Graceful handling of all edge cases
- **iCloud Integration**: Direct extraction from Photos library
- **Professional Quality**: Photoshop's superior Auto-Align and Auto-Blend algorithms

## 📁 Project Structure

```
pyfocusstackfo/
├── runner.py                   # 🎯 Main workflow orchestrator (3-step intelligent workflow)
├── fetcher.py                  # 📱 Step 1: iCloud Photos extraction with CLI interface
├── grouper.py                  # 🔍 Step 2: Smart photo grouping with exit codes  
├── stacker.js                  # 🎨 Step 3: Photoshop automation (conditionally executed)
├── settings.txt                # ⚙️ Configuration file template
├── test_no_groups.py          # 🧪 Tests conditional Step 3 skipping
├── test_integration.py        # 🧪 Comprehensive workflow validation
├── demo_final.py              # 🎬 End-to-end demonstration
├── IMPLEMENTATION_SUMMARY.md  # 📋 Technical implementation details
└── requirements.txt           # 📦 Python dependencies
```

## 🔧 Component Details

### Step 1: Photo Fetcher (`fetcher.py`)
Extracts photos from the macOS Photos library based on recency:
- Uses AppleScript to communicate with Photos app
- Configurable time window (hours)
- Exports to specified destination folder
- Handles permissions and error cases

### Step 2: Photo Grouper (`grouper.py`)
Intelligently organizes photos into focus stacking groups:
- Analyzes EXIF timestamps to detect photo sequences
- Groups photos taken within `MAX_TIME_DELTA` (2 seconds by default)
- Only creates groups with minimum `MIN_STACK_LEN` photos (5 by default)
- **Smart exit codes**: 
  - `0` = Success (groups created and ready for Photoshop)
  - `1` = No JPG files found in source folder
  - `2` = Photos found but no groups created (sequences too short)
- **Intelligent communication**: Provides meaningful status to workflow orchestrator

### Step 3: Photoshop Processor (`stacker.js`)
**Conditionally executed** based on Step 2 results:
- Only runs when groups are successfully created in Step 2
- Processes multiple folders automatically in batch
- Uses Photoshop's Auto-Align and Auto-Blend functions for professional quality
- Exports high-quality JPEG results with automatic cleanup
- **Smart execution**: Automatically skipped when no groups exist

### Workflow Orchestrator (`runner.py`)
The intelligent brain that coordinates all components:
- **Settings management**: Loads configuration from JSON settings file
- **Step coordination**: Executes steps in sequence with proper error handling  
- **Status monitoring**: Interprets exit codes and makes intelligent decisions
- **User feedback**: Provides clear progress updates and completion status
- **Conditional logic**: Automatically skips Step 3 when Step 2 produces no groups
- **Robust execution**: Handles errors gracefully with informative messages

## 📷 Photography Setup & Experience

I have tried: [Zerene], [Helicon Focus], [ChimpStackr], [Enfuse]. The first two can compete when you tweak the settings, but this Photoshop-based solution works better without any tweaking.

[Helicon Focus]: https://www.heliconsoft.com/heliconsoft-products/helicon-focus/
[Zerene]: https://www.zerenesystems.com/cms/stacker
[ChimpStackr]: https://github.com/noah-peeters/ChimpStackr
[Enfuse]: https://enblend.sourceforge.net/enfuse.doc/enfuse_4.2.xhtml/enfuse.html

I shoot nature and can have **thousands of photos from a single walk**, with 5-10 photos in each stack, meaning ~100 focus stacks at once. With these scripts, it takes about an hour to get results for everything.

### Why Photoshop Works Best

Photoshop's *Auto-Align* and *Auto-Blend* functions work so well that you won't see a difference even with defocused, corrupted, or rotated photos among the good stacking photos. I tried experiments with cleaning unsuccessful photos before stacking, but didn't see much difference: with Photoshop, the result mostly depends on the *successful* photos. This ability is especially important to me as I often shoot without a tripod and half of my photos are suboptimal.

This is not the case with other focus stacking software: one bad photo will often ruin the whole result.

### Mobile Photography Integration

I use [CameraPixels](https://apps.apple.com/us/app/camerapixels-lite/id1125808205) iOS app on my iPhone in focus stacking mode. It takes photos with intervals of 0.5-1 seconds. Having `MAX_TIME_DELTA = 2 sec` in the grouper, I get files organized into folders correctly almost always 👍.

Sometimes there could be non-focus-stacking photos taken close to each other — but thanks to the `MIN_STACK_LEN` setting, they probably won't be grouped into a "stack".

Recent examples: [1], [2], [3], [4], [5].

[1]: https://www.inaturalist.org/observations/187942621
[2]: https://www.inaturalist.org/observations/187239060
[3]: https://www.inaturalist.org/observations/183093937
[4]: https://www.inaturalist.org/observations/169738063
[5]: https://www.inaturalist.org/observations/182633085

## ⚙️ Advanced Configuration

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
- **`MAX_TIME_DELTA`**: Increase if using slower shooting intervals (e.g., 3-4 seconds)
- **`MIN_STACK_LEN`**: Decrease to 3-4 for aggressive grouping, increase to 6-8 for conservative approach
- **`LENGTH_STACK_WARNING`**: Adjust based on your typical stack sizes

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
- **Step 2 → Step 3**: Automatic skip when `grouper.py` exits with code 2 (no groups)
- **Error handling**: Workflow stops on errors with clear diagnostic messages
- **Status reporting**: Real-time feedback on each step's progress and results

## 🧪 Testing & Validation

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
- ✅ **Normal operation**: Photos → Groups → Photoshop processing
- ✅ **No files scenario**: Empty source folder handling  
- ✅ **No groups scenario**: Photos present but no stacks needed (Step 3 skipped)
- ✅ **Error handling**: Invalid paths, missing dependencies, etc.

### Validation Results
All tests pass and confirm:
- Proper exit code communication between components
- Conditional Step 3 execution based on grouper results
- Graceful handling of edge cases
- Robust error reporting and user feedback

## 🔄 Workflow Details

### Complete 3-Step Process

#### Step 1: Photo Fetcher (`fetcher.py`)
```bash
python fetcher.py <destination_folder> <hours>
```
- Uses AppleScript to communicate with macOS Photos app
- Extracts photos taken within the specified time window
- Handles permissions and exports to destination folder
- **Exit codes**: 0 = success, 1 = error

#### Step 2: Photo Grouper (`grouper.py`)
```bash
python grouper.py <source_folder> <destination_folder>
```
1. Scans source folder for _.jpg_ files and **sorts them alphabetically**
2. Analyzes EXIF `Date taken` field for each photo
3. Groups photos taken within `MAX_TIME_DELTA` (2 seconds) into potential stacks
4. Only creates folders for groups with ≥ `MIN_STACK_LEN` photos (5 minimum)
5. Moves grouped photos to folders named: `{FIRST_FILE}_to_{LAST_FILE}`
6. **Smart exit codes**:
   - 0 = success (groups created)
   - 1 = no JPG files found
   - 2 = no groups created (all sequences too short)

#### Step 3: Photoshop Processor (`stacker.js`)
- **Conditionally executed** only when Step 2 creates groups
- Processes each folder automatically using Photoshop's Auto-Align and Auto-Blend
- Exports high-quality focus stacked results
- Handles multiple folders in batch

### Intelligent Decision Making

The workflow automatically handles different scenarios:

```
📱 Photos extracted → 🔍 Groups analyzed → Decision Point:
                                        ├── No groups? → Skip Photoshop ✅
                                        └── Groups found? → Process in Photoshop 🎨
```

**This intelligent behavior means**:
- No wasted time on unnecessary Photoshop processing
- Clean completion when no focus stacking opportunities exist
- Robust handling of edge cases (no photos, single photos, etc.)

## 🔧 Troubleshooting

### Common Scenarios & Solutions

**"Step 3 was skipped - no groups to process"**
- ✅ **Normal behavior** when photos don't form focus stacks
- Check that photos were taken within 2 seconds of each other
- Verify minimum 5 photos per sequence (adjustable in `grouper.py`)

**"No JPG files found"**
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
✅ Step 1 (fetcher): Success
✅ Step 2 (grouper): Success - groups created  
✅ Step 3 (stacker): Success

# Success but no groups (Step 3 skipped)
✅ Step 1 (fetcher): Success
⚠️ Step 2 (grouper): No groups created
⏭️ Step 3 (stacker): Skipped - no groups to process

# Error scenarios  
❌ Step 1 (fetcher): Error - <specific error message>
⏭️ Workflow stopped due to error
```

## Details on the _.js_ script

The JavaScript automation script handles the Adobe Photoshop integration:

**Original inspiration**: The first version was found in Adobe Community [Discussion] by user *SuperMerlin* for three-file focus stacking.

**Enhancements added**:
- **Arbitrary file quantity**: Processes focus stacks of any size
- **Batch processing**: Handles multiple subfolders automatically  
- **Integration**: Works seamlessly with the Python workflow orchestrator

**Important notes**:
1. **Auto-cropping not included**: If photos have poor alignment, result may have gray-filled edges requiring manual crop
2. **Folder validation**: Script requires non-empty folders to function properly
3. **Photoshop compatibility**: Tested with CC 2020+ versions

The script is automatically invoked by `runner.py` when Step 2 creates focus stacking groups.


[Discussion]: https://community.adobe.com/t5/photoshop-ecosystem-discussions/automate-focus-stacking-script-action-help-needed/m-p/10483237

## Build with

**[Adobe Photoshop]** - «Leading AI photo & Design software» since 1990 **|** *proprietary*  
**[JavaScript]** - Scripting language widely used in web pages and web applications since 1995 **|** *Licence depends on implementation*  
**[pyexif]** - Python wrapping for the exiftool library since 2011 **|** *Apache 2*  
**[Python]** - Language to work quickly and integrate systems more effectively since 1991 **|** *GPL compatible*    


[Adobe Photoshop]: https://www.adobe.com/products/photoshop.html
[pyexif]: https://pypi.org/project/pyexif/
[Python]: https://www.python.org/
[JavaScript]: https://ecma-international.org/publications-and-standards/standards/ecma-262/

## Contributions

Please feel free to contribute, create pull requests, comment and further. 

## Feedback and PyPi.org

If you find any of this scripts helpful, please leave feedback.  
In case you will happy to see `pyfocusstack.py` as **python package**, please write to me: If there will be at least single person who find this helpful, I reformat the code and add it to **PyPi** 🙃. 
