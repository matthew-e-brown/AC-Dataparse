# Functions for handling Style (MSBP) Files
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format

import sys
import errno

import lms

def parse_file(filename, verbose=False):
  try:
    with open(filename, 'rb') as f:
      data = f.read()
  except IOError as e:
    if e.errno == errno.EACCES:
      print(f"Cannot access {e.filename}", file=sys.stderr)
    elif e.errno == errno.ENOENT:
      print(f"Cannot find {e.filename}", file=sys.stderr)
    else:
      print(f"Uknown errno: {e.errno}", sys.stderr)
    
    if __name__ != "__main__": raise e
    else: sys.exit(-1)

  style_data = {}

  pntr = 0x00
  info, pntr = lms.parse_file_header(data)
  blocks, pntr = lms.parse_blocks(data, info)

  if verbose: print(blocks)

  colors = []
  labels = []

  for block in blocks:
    pntr = block['offset'] + 0x10

    if block['type'] == 'CLB1':
      labels, pntr = lms.parse_labels(data, info, block)
    elif block['type'] == 'CLR1':
      color_count, pntr = lms.read(data, pntr, 4)
      color_count = info['convert'](color_count)

      for i in range(0, color_count):
        color, pntr = lms.read(data, pntr, 4)
        colors.append('#' + color.hex())

    # Add more elifs in the future if it comes up

  style_data = {
    'labels': labels,
    'colors': colors
  }

  return style_data