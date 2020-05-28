# Mostly for bfres files. Main dict should hopefully be fairly self-explanatory
# to figure out how to add more files to.

import os
import re
import sys
import contextlib
from glob import glob
from shutil import rmtree, copyfile

from vendor import sarc
import zstandard as zstd

cwd = os.path.dirname(os.path.realpath(__file__))

FILE_LIST = [
  {
    'romfs_sub': 'Model',
    'dest_sub': 'models',
    'regex': r'^(?:Fish|Insect)(?:[A-Z]\w*)+(?:Museum)?\.Nin_NX_NVN\.zs$',
    'sarc': True # if the output of the zstd decompress should be de-sarc'ed
  },
  {
    'romfs_sub': 'Model',
    'dest_sub': 'models',
    'regex': r'^FtrFossil(?:(?:[A-Z]\w*)+)\.Nin_NX_NVN\.zs$',
    'sarc': True
  },
  {
    'romfs_sub': 'Model',
    'dest_sub': 'models',
    'regex': r'^FtrArt(?:(?:[A-Z]\w*)+)\.Nin_NX_NVN\.zs$',
    'sarc': True
  }
]

def main(romfs_path, force=False):
  # clear existing folders to replace
  for subfolder in [ FILE['dest_sub'] for FILE in FILE_LIST ]:
    rmtree(f"{cwd}/extracted/{subfolder}", ignore_errors=True)

  # Reset temp dir
  rmtree(f"{cwd}/temp", ignore_errors=True)
  os.makedirs(f"{cwd}/temp", exist_ok=True)

  for FILE in FILE_LIST:
    # Check all files over
    for f in os.listdir(f"{romfs_path}/{FILE['romfs_sub']}"):
      if not re.search(FILE['regex'], f): continue # didn't find anything
      else: dest_subfolder = f"{cwd}/extracted/{FILE['dest_sub']}"

      # Found a file! Extract it!
      os.makedirs(dest_subfolder, exist_ok=True)

      source_zs = f"{romfs_path}/{FILE['romfs_sub']}/{f}"
      tempfile = f"{cwd}/temp/{f[:f.index('.')]}"
      with open(source_zs, 'rb') as s, open(f"{tempfile}.temp", 'wb') as d:
        decompressed = zstd.ZstdDecompressor().decompress(s.read())
        d.write(decompressed)

      if FILE['sarc']:
        with open(os.devnull, 'w') as p, contextlib.redirect_stdout(p): # suppress print
          sarc.extract(f"{tempfile}.temp")

        # If there was only one file in the archive
        files = os.listdir(tempfile) # tempfile is now extracted folder
        if len(files) == 1:
          # lazy but w/e. {cwd}/extracted/models/FishKoi.bfres, for example
          f1 = files[0]
          dest = f"{cwd}/extracted/{FILE['dest_sub']}/{f[:f.index('.')]}{f1[f1.index('.'):]}"
          copyfile(f"{tempfile}/{files[0]}", dest)

  rmtree(f"{cwd}/temp", ignore_errors=False)


if __name__ == "__main__":
  if len(sys.argv) <= 1:
    # Check if ROMFS is in CWD before exiting
    if glob(f"{cwd}/romfs"):
      main(f"{cwd}/romfs", force=True)
    else:
      print("Please include a path to romfs.", file=sys.stderr)
      sys.exit(1)
  else:
    main(sys.argv[1], force=bool('-f' in sys.argv))