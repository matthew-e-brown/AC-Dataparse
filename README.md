# AC DataParse

This is a series of scripts with the goal of extracting several files from
Animal Crossing: New Horizons and formatting them in an SQL format.


## [`extract.py`](extract.py)

This file expects to be given a path to the `romfs` folder, extracted from the
`.XCI` of *Animal Crossing: New Horizons*, v.1.0.0. How you get that `romfs` is
up to your own discretion.

This script will create a folder within the `dataparse` folder called
`extracted`. In here, you will find `App.msbp`, the file that holds all of the
text-colour information, as well as folders for each of the languages from the
game's files. Inside each language-subfolder, there are dialogue, "`.msbt`",
files that contain all of the dialogue relating to each of the items you can
give to Blathers, as well as the dialogue files that label each of the item's
names.


## [`parse.py`](parse.py)

This file will take the output of [`extract.py`](#extractpy) and read through
the `.msbt` files to grab all of the dialogue. 

Currently, this just exports them to JSON. This is temporary.


## Vendors

This is where I got all of the files in [`dataparse/vendor`](dataparse/vendor):

- SARC Tool, AboodXD
  - https://github.com/aboood40091/SARC-Tool
- BCSV Tools and its specs, Treeki
  - https://github.com/Treeki/CylindricalEarth

The only modifications to these files have been to add links to their original
repositories at the top.


---


## Todo

- Interpret the escape sequences used in the messages:
  - What's the sequence to mark text as *blue?*
  - What makes the text small?
  - What causes Blathers' pauses?
- Change from JSON output to generating a full SQL file for the end database.
