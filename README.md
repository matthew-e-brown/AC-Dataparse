# AC DataParse

This is a series of scripts with the goal of extracting several files from
Animal Crossing: New Horizons and formatting them in JSON format.

This repository is a set of tools that I'm using to develop another project of
mine. These tools have been pulled out of that project into their own repository
in the hopes that this code will be used, or, more likely, studied by other
aspiring dataminers.

For help understanding some of the scripts, check out Kinnay's Wiki on
Nintendo's custom file formats,
[here](https://github.com/Kinnay/Nintendo-File-Formats/wiki).

See [`Notes.md`](Notes.md) for a rundown of how the `00 0e` escape sequences
work.


## Scripts

### [`extract-dialogue.py`](extract-dialogue.py)

This file expects to be given a path to the `romfs` folder, extracted from the
`.XCI` of *Animal Crossing: New Horizons*. How you get that `romfs` is up to
your own discretion.

This script will create a folder within the `dataparse` folder called
`extracted`. In here, you will find `App.msbp`, the file that holds all of the
text-colour information, as well as folders for each of the languages from the
game's files. Inside each language-subfolder, there are dialogue, "`.msbt`",
files that contain all of the dialogue relating to each of the items you can
give to Blathers, as well as the dialogue files that label each of the item's
names.


### [`parse-dialogue.py`](parse-dialogue.py)

This file will take the output of [`extract.py`](#extractpy) and read through
the `.msbt` files to grab all of the dialogue. They are exported to a folder
called `parsed`.


## Vendors

This is where I got all of the files in [`vendor`](vendor):

- SARC Tool, AboodXD
  - https://github.com/aboood40091/SARC-Tool

Aside from linking to their respective original repositories, no changes have
been made to any vendored files.
