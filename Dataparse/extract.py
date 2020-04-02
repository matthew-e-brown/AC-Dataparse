# Extracts the .sarc.zs files to get MSBT files.
# Requires zstd (https://github.com/facebook/zstd) to be on PATH

import os
import re
import sys
import contextlib

from glob import glob
from subprocess import call
from shutil import rmtree, copyfile

from vendor import sarc

cwd = os.path.dirname(os.path.realpath(__file__))

def main(romfs_path):
  if romfs_path[1][-5:] != 'romfs' and '-f' not in romfs_path:
    print("Is this a valid romfs? (use -f to force)", file=sys.stderr)
    sys.exit(-1)
  else:
    from shutil import which
    if which('zstd') is None:
      print("ZSTD is not found on PATH! Please install it.", file=sys.stderr)
      sys.exit(-1)
  # done error checking

  romfolder = os.path.realpath(romfs_path[1])
  os.makedirs(f"{cwd}/extracted/", exist_ok=True)

  for filename in glob(f"{romfolder}/Message/*"):
    basename = os.path.basename(filename)

    # Yoink app real quick
    if basename == 'App.msbp':
      copyfile(filename, f"{cwd}/extracted/App.msbp")

    match = re.search(r"(TalkSNpc|String)_([A-Z]{2}[a-z]{2})\.sarc\.zs", basename)

    # Skip the files that we don't need
    if not match: continue
    # Get the file info from the name
    filetype = match.group(1)
    lang = match.group(2)

    # Make the temp directory
    tempfolder = f"{cwd}/temp/{lang}"
    os.makedirs(tempfolder, exist_ok=True)

    # Decompress:
    call(['zstd', '-dfq', filename, '-o', f"{tempfolder}/{basename[:-3]}"])

    # Extract:
    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f): # suppress print
      sarc.extract(f"{tempfolder}/{basename[:-3]}") # makes a folder w/o the sarc

    # Find the MSBT files we want
    if filetype == 'String':
      globname = f"{tempfolder}/{basename[:-8]}/Item/*"
    elif filetype == 'TalkSNpc':
      globname = f"{tempfolder}/{basename[:-8]}/owl/*"

    for dialoguefile in glob(globname):
      dialoguebase = os.path.basename(dialoguefile)
      valid = [
        'SP_owl_Comment_Fish.msbt',
        'SP_owl_Comment_Insect.msbt',
        'SP_owl_Comment_Fossil.msbt',
        'STR_ItemName_31_Fish.msbt',
        'STR_ItemName_30_Insect.msbt',
        'STR_ItemName_34_Fossil.msbt'
      ]
      if dialoguebase not in valid: continue

      os.makedirs(f"{cwd}/extracted/{lang}", exist_ok=True)
      os.rename(dialoguefile, f"{cwd}/extracted/{lang}/{dialoguebase}")

  rmtree(f"{cwd}/temp")


if __name__ == "__main__":
  if len(sys.argv) <= 1:
    if glob(f"{cwd}/romfs"): main([f"{cwd}/romfs/", "-f"])
    else:
      print("Missing romfs file path.", file=sys.stderr)
      sys.exit(-1)
  else:
    main(sys.argv)