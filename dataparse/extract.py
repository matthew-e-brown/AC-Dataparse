# Extracts the .sarc.zs files to get MSBT files.

import os
import re
import sys
import contextlib

from glob import glob
from subprocess import call
from shutil import rmtree, copyfile
import zstandard as zstd

# SARC import from AboodXD (https://github.com/aboood40091/SARC-Tool)
from vendor import sarc

# Edit this to change what the script exports
EXTRACT_APP = True
MSBT_FILES = [
  {
    'archive_name': 'TalkSNpc',     # .sarc.zs file to pull from
    'globname': 'owl/*',            # where to get the .msbt files from
    'dialogues': [                  # files that you want
      'SP_owl_Comment_Fish.msbt',
      'SP_owl_Comment_Insect.msbt',
      'SP_owl_Comment_Fossil.msbt'
    ]
  },
  {
    'archive_name': 'String',
    'globname': 'Item/*',
    'dialogues': [
      'STR_ItemName_31_Fish.msbt',
      'STR_ItemName_30_Insect.msbt',
      'STR_ItemName_34_Fossil.msbt'
    ]
  }
]

BCSV_FILES = [
  "FishAppearRiverParam.bcsv",
  "FishAppearSeaParam.bcsv",
  "InsectAppearParam.bcsv"
]

cwd = os.path.dirname(os.path.realpath(__file__))

def main(romfs_path, force=False):
  if romfs_path[1][-5:] != 'romfs' and not force:
    print("Is this a valid romfs? (use -f to force)", file=sys.stderr)
    sys.exit(-1)

  romfolder = os.path.realpath(romfs_path)

  # Make the destination folder
  made = False
  extracted = f"{cwd}/extracted/"
  while not made:
    try: os.makedirs(extracted, exist_ok=False); made = True
    except FileExistsError: rmtree(extracted)
  del made, extracted

  # Get MSBT and MSBP Files
  for filename in glob(f"{romfolder}/Message/*"):
    basename = os.path.basename(filename)

    # Yoink app real quick
    if EXTRACT_APP and basename == 'App.msbp':
      copyfile(filename, f"{cwd}/extracted/App.msbp")

    regexprefix = '|'.join(f['archive_name'] for f in MSBT_FILES)
    match = re.search(fr"({regexprefix})_([A-Z]{{2}}[a-z]{{2}})\.sarc\.zs", basename)

    # Skip the files that we don't need
    if not match: continue
    # Get the file info from the name
    filetype = match.group(1)
    filelang = match.group(2)

    # Check which dictionary entry we matched against
    FILE = next((i for i in MSBT_FILES if i['archive_name'] == filetype), None)

    # Make the temp directory
    tempfolder = f"{cwd}/temp/{filelang}"
    os.makedirs(tempfolder, exist_ok=True)

    # Decompress:
    with open(filename, 'rb') as s, open(f"{tempfolder}/{basename[:-3]}", 'w+b') as d:
      decompressed = zstd.ZstdDecompressor().decompress(s.read())
      d.write(decompressed)

    # Extract:
    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f): # suppress print
      sarc.extract(f"{tempfolder}/{basename[:-3]}") # makes a folder w/o the sarc

    # Glob the filenames defined in VALID_FILES
    for dialoguefile in glob(f"{tempfolder}/{basename[:-8]}/{FILE['globname']}"):
      dialoguebase = os.path.basename(dialoguefile)
      if dialoguebase not in FILE['dialogues']: continue

      os.makedirs(f"{cwd}/extracted/{filelang}", exist_ok=True)
      os.rename(dialoguefile, f"{cwd}/extracted/{filelang}/{dialoguebase}")

  rmtree(f"{cwd}/temp")

  for filename in glob(f"{romfolder}/Bcsv/*"):
    basename = os.path.basename(filename)
    if basename not in BCSV_FILES: continue

    # No decompressing or extracting need to be done, so just copy it
    copyfile(filename, f"{cwd}/extracted/{basename}")


if __name__ == "__main__":
  # Check if romfs given
  if len(sys.argv) <= 1:
    # Check if in working dir
    if glob(f"{cwd}/romfs"): main(f"{cwd}/romfs/", force=True)
    else:
      print("Missing romfs file path.", file=sys.stderr)
      sys.exit(-1)
  else:
    main(sys.argv[1], force=bool('-f' in sys.argv))