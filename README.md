# pyfocusstack

[![Pylint](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/pylint.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/pylint.yml) [![Testing](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/python-pytest-flake8.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/python-pytest-flake8.yml) [![mypy](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/mypy.yml/badge.svg)](https://github.com/baidakovil/pyfocusstackfo/actions/workflows/mypy.yml)

This repo for those who knows what focus stacking photographic technique is.  
And for those who don't know, but like macro photo.  

It consists of two scripts that make up the complete process of focus stacking:
* **pyfocusstackfo.py** - Organizes files from a camera into folders: 1 folder = 1 photo
* **photoshop_script_subfolders.js** - Does a focus stacking in Adobe Photoshop for multiple folders at a time

The workflow excellent for ease, robust, fast and well-expected results.  

I have tried: [Zerene], [Helicon Focus], [ChimpStackr], [Enfuse]. First two can compete when you tweak the settings. The one above is better without tweaking.

[Helicon Focus]: https://www.heliconsoft.com/heliconsoft-products/helicon-focus/
[Zerene]: https://www.zerenesystems.com/cms/stacker
[ChimpStackr]: https://github.com/noah-peeters/ChimpStackr
[Enfuse]: https://enblend.sourceforge.net/enfuse.doc/enfuse_4.2.xhtml/enfuse.html

##  Prepare files with .py script

Click for full size ⬇️

  <a href="docs/explanation.png"><img width="95%" src="docs/explanation.png"/></a>

More info below.

## Do focus stacking with .js script

Workflow below was tested with Photoshop **CC 2020 21.2.0**.  
Click for full size ⬇️

<a href="docs/photoshop_guide.png"><img width="95%" src="docs/photoshop_guide.png"/></a>


## My experience

I shoot nature and can have **thousand of photos from single walk**, with 5-10 photos in each stack, meaning ~100 focus stacks once. With this scripts, it takes an hour to get result for everything about everything.

Photoshop *Auto-Align* and *Auto-Blend* functions works so well that you won't see a difference even with defocused, corrupted, rotated photos among the good stacking photos. I tried some experiments with cleaning these unsuccessful photos before stacking, but I didn't see the difference: with Photoshop, result at most depends on *successfull* photos. This ability especially important to me as I offen shoot without a tripod and half of my photos are garbage .

This is not the case with other focus stacking software: one bad photo in most cases will ruin the whole result. 

I use [CameraPixels](https://apps.apple.com/us/app/camerapixels-lite/id1125808205) iOS app on my iPhone SE 1st Gen in focus stacking mode. It takes photos with intervals 0.5-1 seconds. So, having `MAX_TIME_DELTA = 2 sec` in `pyfocusstackfo.py`, I get files accumulated by folders right almost always 👍.   
Sometimes, of course, there could be non-focus-stacking photos taken close to each other — but thanks to `MIN_STACK_LEN` setting, they probably will not fall into "stack".

 Some of the last images, just for fun: [1], [2], [3], [4], [5].

[1]: https://www.inaturalist.org/observations/187942621
[2]: https://www.inaturalist.org/observations/187239060
[3]: https://www.inaturalist.org/observations/183093937
[4]: https://www.inaturalist.org/observations/169738063
[5]: https://www.inaturalist.org/observations/182633085

## Details on the _.py_ script

Again: **pyfocusstackfo.py** script used to collect *.jpg files into separate folders in order to further using with **photoshop_script_subfolders.js** to obtain focus stacking images.

#### How does it works

1. The script look for all the _.jpg_ files in folder and **sort them alphabetically** with python `sorted()` function. 
2. Iterating files from first to last, it looking at EXIF field `Date taken`. If neighbour files taken with interval less or equal `MAX_TIME_DELTA`, they added to "stack". If stack accumulates more than `MIN_STACK_LEN` files, this stack added to final list
3. If stack accumulates less files than `MIN_STACK_LEN`, files from this stack will left where they was without changes (magenta color on pic above)
4. If stack acuumulates more files than `LENGTH_STACK_WARNING` files, program will print warning message in console, but "stack" will managed as usual
5. After creating stack, files will be moved in new created folder. Folder names used: `{FIRST_FILE_IN_STACK}_to_{LAST_FILE_IN_STACK}`. This folders than go to Photoshop to create focus stacked images.
6. Now you can check folders to remove blurred, smoothed or out-of-focus photos. 

#### Path to jpgs
There is two modes to use `pyfocusstackfo.py` script:
* **without arguments**, as shown on pic above.  
  In this case script will look at current working directory
* **with `-l` argument** passed to command line, process would looking [like this](/docs/stacking-library.png).  
In this case you'll face interacive dialog, and «library path» saved in `PATH_LIBRARY_DEFAULT` will be added to your desired path automatically (if you press `Enter`). You'll have to only pass rest of the path (or `Enter` if «library path» _is_ desired path). This is handy if you have long and stable path to your photos and don't want to type `cd /home/photo/long_path` every time.

## Details on the _.js_ script

The very first version of `photoshop_script_subfolders.js`, provided focus stacking only for three files, was found in Adobe Community [Discussion], made by user *SuperMerlin*.  I add two functions:
- processing with arbitratry quantity of files
- looping on arbitrary quantity of subfolders, i.e. multiple focus stacking images

Be aware of:
1. Script **do not crop** resulting photos. If your photos have poor align, then result will have gray-filled areas on the photo edges. You'll have to crop them manually.
2. If there will be empty folders, script will fail.


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