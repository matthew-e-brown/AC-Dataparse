# BlathersDB

In Animal Crossing: New Horizons, the friendly museum curator Blathers offers
fun facts for each new Fish, Insect, and Fossil you bring him. The only issue is
that you can only hear them whenever you bring one of these items to him. When
you're dealing with incredibly rare or out-of-season Fish for example, you will
probably never hear each commentary once.

That's where BlathersDB comes in!


## Building

There are two python scripts in `./dataparse`.


### `extract.py`

This file expects to be given a path to the `romfs` folder, extracted from the
`.XCI` of *Animal Crossing: New Horizons*. How you get that `romfs` is up to
your own discretion, but please, don't be a pirate. This was originally built
from a legitimate copy from my own Switch.

**As a prerequisite**, you must have
[ZStandard](https://github.com/facebook/zstd) installed and on your `PATH` for
this script to work.

This script will create a folder within the `dataparse` folder called
`extracted`. In here, you will find `App.msbp`, the file that holds all of the
text-colour information, as well as folders for each of the languages from the
game's files. Inside each language-subfolder, there are dialogue, "`.msbt`",
files that contain all of the dialogue relating to each of the items you can
give to Blathers, as well as the dialogue files that label each of the item's
names.


### `parse.py`

This file will take the output of [`extract.py`](#extractpy) and read through
the `.msbt` files to grab all of the dialogue. 

Currently, this just exports them to JSON. This is temporary.


---


## Todo

- Interpret the escape sequences used in the messages:
  - What's the sequence to mark text as *blue?*
  - What makes the text small?
  - What causes Blathers' pauses?
- Change from JSON output to generating a full SQL file for the end database.