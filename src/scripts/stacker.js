app.bringToFront();

// Check if folder path is provided as argument
if (arguments.length > 0) {
    var folderPath = arguments[0];
    var result = loopFolders(folderPath);
    "Focus stacking completed: " + result; // Return formatted result
} else {
    var result = loopFolders();
    "Focus stacking completed: " + result; // Return formatted result
}

function loopFolders(folderPath){
    
var mainFolder;
var processedFolders = 0;

if (folderPath) {
    mainFolder = new Folder(folderPath);
    if (!mainFolder.exists) {
        alert("Folder does not exist: " + folderPath);
        return "Error: Folder does not exist: " + folderPath;
    }
} else {
    mainFolder = Folder.selectDialog("Please select the folder with folerds to process");    
    if(mainFolder == null ) return "Error: No folder selected";
}

var folderList = mainFolder.getFiles();

var folderCount = folderList.length

for (var i = 0; i<folderCount; i++){
    var currentItem = folderList.shift();
    
    // Check if the item is actually a folder, not a file
    if (currentItem instanceof Folder) {
        main(currentItem, mainFolder);
        processedFolders++;
    }
};

return "Success: Processed " + processedFolders + " folder(s) for focus stacking";
        
};
	
function main(selectedFolder, outFolder){

//var selectedFolder = Folder.selectDialog("Please select the folder to process");    

if(selectedFolder == null ) return;

//var outFolder = Folder(selectedFolder);

// if(!outFolder.exists) outFolder.create();

var threeFiles = new Array();

var PictureFiles = selectedFolder.getFiles(/\.(jpg|jpe|jpeg|dng|bmp|tif|tiff|psd|crw|cr2|exr|pcx|nef|dcr|dc2|erf|raf|orf|tga|mos|pef|png)$/i);

var filescount = PictureFiles.length

var filescountminusone = filescount - 1

while(PictureFiles.length>filescountminusone){

for(var a = 0;a<filescount;a++){threeFiles.push(PictureFiles.shift());}

stackFiles(threeFiles);

selectAllLayers();

autoAlign();

autoBlendLayers();

// Autocrop to remove transparent areas from alignment
autoCrop();

var layerName = activeDocument.activeLayer.name.replace(/\....$/i,'');

var saveFile = new File(outFolder+ '/' + layerName + '_fs.jpg');

SaveJPG(saveFile);

app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);

threeFiles=[];

    }

};

function autoBlendLayers(){

var d=new ActionDescriptor();

d.putEnumerated(stringIDToTypeID("apply"), stringIDToTypeID("autoBlendType"), stringIDToTypeID("maxDOF"));

d.putBoolean(stringIDToTypeID("colorCorrection"), true);

d.putBoolean(stringIDToTypeID("autoTransparencyFill"), false);

executeAction(stringIDToTypeID("mergeAlignedLayers"), d, DialogModes.NO);

};

function SaveJPG(saveFile){

var jpgOptions = new JPEGSaveOptions();
jpgOptions.quality = 12;
jpgOptions.embedColorProfile = true;
jpgOptions.formatOptions = FormatOptions.PROGRESSIVE;
if(jpgOptions.formatOptions == FormatOptions.PROGRESSIVE){
jpgOptions.scans = 5};
jpgOptions.matte = MatteType.NONE;

activeDocument.saveAs(saveFile, jpgOptions, true, Extension.LOWERCASE); 

};

function selectAllLayers() {

var desc = new ActionDescriptor();

var ref = new ActionReference();

ref.putEnumerated( charIDToTypeID('Lyr '), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );

desc.putReference( charIDToTypeID('null'), ref );

executeAction( stringIDToTypeID('selectAllLayers'), desc, DialogModes.NO );

};

function stackFiles(sFiles){  

var loadLayersFromScript = true;  

var SCRIPTS_FOLDER =  decodeURI(app.path + '/' + localize('$$$/ScriptingSupport/InstalledScripts=Presets/Scripts')); 

$.evalFile( new File(SCRIPTS_FOLDER +  '/Load Files into Stack.jsx'));   

loadLayers.intoStack(sFiles);  

};

function autoAlign() {

var desc = new ActionDescriptor();

var ref = new ActionReference();

ref.putEnumerated( charIDToTypeID('Lyr '), charIDToTypeID('Ordn'), charIDToTypeID('Trgt') );

desc.putReference( charIDToTypeID('null'), ref );

desc.putEnumerated( charIDToTypeID('Usng'), charIDToTypeID('ADSt'), stringIDToTypeID('ADSContent') );

desc.putEnumerated( charIDToTypeID('Aply'), stringIDToTypeID('projection'), charIDToTypeID('Auto') );

desc.putBoolean( stringIDToTypeID('vignette'), false );

desc.putBoolean( stringIDToTypeID('radialDistort'), false );

executeAction( charIDToTypeID('Algn'), desc, DialogModes.NO );

};

function autoBlend() {

var desc = new ActionDescriptor();

desc.putEnumerated( charIDToTypeID('Aply'), stringIDToTypeID('autoBlendType'), stringIDToTypeID('maxDOF') );

desc.putBoolean( charIDToTypeID('ClrC'), true );

executeAction( stringIDToTypeID('mergeAlignedLayers'), desc, DialogModes.NO );

};

function autoCrop() {
    try {
        // Method 1: Trim transparent pixels (most common after alignment)
        var desc = new ActionDescriptor();
        desc.putEnumerated(charIDToTypeID('Base'), charIDToTypeID('Trns'), charIDToTypeID('Trns'));
        desc.putBoolean(charIDToTypeID('Top '), true);
        desc.putBoolean(charIDToTypeID('Btom'), true);
        desc.putBoolean(charIDToTypeID('Left'), true);
        desc.putBoolean(charIDToTypeID('Rght'), true);
        executeAction(charIDToTypeID('Trim'), desc, DialogModes.NO);
    } catch (e) {
        try {
            // Method 2: Fallback to crop to visible bounds if trim fails
            activeDocument.crop(activeDocument.bounds);
        } catch (e2) {
            // If both methods fail, continue without cropping
        }
    }
}

// Alternative autocrop method using content bounds
function autoCropToBounds() {
    try {
        // Get the bounds of all visible content
        var bounds = activeDocument.bounds;
        var left = bounds[0].value;
        var top = bounds[1].value;
        var right = bounds[2].value;
        var bottom = bounds[3].value;
        
        // Create crop area
        var cropArea = [left, top, right, bottom];
        activeDocument.crop(cropArea);
    } catch (e) {
        // Continue if cropping fails
    }
}

// Smart autocrop that tries multiple strategies
function smartAutoCrop() {
    try {
        // First try trimming transparent pixels
        autoCrop();
    } catch (e) {
        try {
            // If that fails, try cropping to content bounds
            autoCropToBounds();
        } catch (e2) {
            try {
                // Last resort: trim based on top-left pixel color
                var desc = new ActionDescriptor();
                desc.putEnumerated(charIDToTypeID('Base'), charIDToTypeID('Clr '), charIDToTypeID('TpLf'));
                desc.putBoolean(charIDToTypeID('Top '), true);
                desc.putBoolean(charIDToTypeID('Btom'), true);
                desc.putBoolean(charIDToTypeID('Left'), true);
                desc.putBoolean(charIDToTypeID('Rght'), true);
                executeAction(charIDToTypeID('Trim'), desc, DialogModes.NO);
            } catch (e3) {
                // If all methods fail, continue without cropping
            }
        }
    }
}