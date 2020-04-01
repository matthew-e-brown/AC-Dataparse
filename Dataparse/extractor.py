import os, sys
import errno
import json

from pprint import pprint

# https://github.com/Kinnay/Nintendo-File-Formats/wiki/LMS-File-Format
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format

# -------------------------------------------------------------------- Functions
def calc_hash(label, num_slots):
  hash = 0
  for char in label:
    hash = hash * 0x492 + ord(char)
  return (hash & 0xFFFFFFFF) % num_slots

# Reads count bytes starting at pointer, and returns pointer += count as the
# second return value
def read(data, pointer, bytecount):
  return data[pointer : pointer + bytecount], pointer + bytecount

# ------------------------------------------------------------------------- Info
def getinfo(data):
  pntr = 0x0
  info = {
    'magic': '',
    'endian': '',
    'encode': 8, # utf-_
    'blocks': 0,
    'size': 0
  }

  info['magic'], pntr = read(data, pntr, 8)

  info['endian'], pntr = read(data, pntr, 2)
  info['endian'] = 'big' if info['endian'] == 0xFEFF else 'little'

  # Once you know endian-ness, you know how to make ints
  def to_int(rawbytes):
    return int.from_bytes(rawbytes, info['endian'])

  pntr += 2
  info['encode'], pntr = read(data, pntr, 1)

  if to_int(info['encode']) == 0x00: info['encode'] = 8
  elif to_int(info['encode']) == 0x01: info['encode'] = 16
  elif to_int(info['encode']) == 0x02: info['encode'] = 32

  pntr += 1
  info['blocks'], pntr = read(data, pntr, 2)
  info['blocks'] = to_int(info['blocks'])

  pntr += 2
  info['size'], pntr = read(data, pntr, 4)
  info['size'] = to_int(info['size'])

  pntr += 10

  return info, pntr, to_int
# ------------------------------------------------------------------ End of info

# ----------------------------------------------------------------------- Blocks
def getblocks(data, pntr):
  blocks = []
  for i in range(0, info['blocks']):
    block = {}

    block['offset'] = pntr

    block['type'], pntr = read(data, pntr, 4)
    block['type'] = block['type'].decode('utf-8') # always utf-8

    block['size'], pntr = read(data, pntr, 4)
    block['size'] = to_int(block['size'])

    blocks.append(block)

    pntr += 8 # header padding
    pntr += block['size'] # block
    while data[pntr : pntr + 1] == b'\xab': pntr += 1 # block padding

  return blocks, pntr
# ---------------------------------------------------------------- End of blocks

# Extracts the labels from the block starting at pntr
def getlabels(data, info, pntr):
  # Start by reading in the hash table's buckets/slots
  hashslots = []
  
  slotcount, pntr = read(data, pntr, 4)
  slotcount = to_int(slotcount)

  for i in range(0, slotcount):
    slot = {}
    
    slot['numlabels'], pntr = read(data, pntr, 4)
    slot['numlabels'] = to_int(slot['numlabels'])

    slot['offset'], pntr = read(data, pntr, 4)
    slot['offset'] = to_int(slot['offset'])

    hashslots.append(slot)

  # Read the rest, should be all labels
  labels = []
  while (pntr < block['offset'] + block['size']):
    label = {}

    length, pntr = read(data, pntr, 1)
    length = to_int(length)

    label['value'], pntr = read(data, pntr, length)
    label['value'] = label['value'].decode('utf-8') # always utf8

    label['itemindex'], pntr = read(data, pntr, 4)
    label['itemindex'] = to_int(label['itemindex'])

    labels.append(label)

  labels = sorted(labels, key=lambda l: l['itemindex'])
  return labels, pntr
# ---------------------------------------------------------------- End of labels

# ------------------------------------------------------------- End of functions

msbpraw = None # will just be one data dict
msbtraw = {} # will have 'Fish' => xxx 'Fossil' => xxx 'Insect' => xxx

cwd = os.path.dirname(os.path.realpath(__file__))

try:
  with open(f'{cwd}/Extracted/App.msbp', 'rb') as msbp:
    msbpraw = msbp.read()

  for name in ['Fish', 'Fossil', 'Insect']:
    with open(f'{cwd}/Extracted/SP_owl_Comment_{name}.msbt', 'rb') as f:
      msbtraw[name] = f.read()
      
except IOError as error:
  if error.errno == errno.EACCES:
    print(f"Cannot access {error.filename}", file=sys.stderr)
  elif error.errno == errno.ENOENT:
    print(f"Cannot find {error.filename}", file=sys.stderr)
  else:
    print(f"Uknown errno: {error.errno}", sys.stderr)
  sys.exit(-1)

messagedata = {}
for name, data in msbtraw.items():
  info, pntr, to_int = getinfo(data)
  blocks, pntr = getblocks(data, pntr)

  print(blocks)

  for block in blocks:
    pntr = block['offset'] + 0x10 # block header

    if block['type'] == 'LBL1':
      labels, pntr = getlabels(data, info, pntr)

    elif block['type'] == 'TXT2':
      # Get ready to receive a bunch of messages...
      messages = []
      
      msgcount, pntr = read(data, pntr, 4)
      msgcount = to_int(msgcount)

      offsets = []
      for i in range(0, msgcount):
        offset, pntr = read(data, pntr, 4)
        offset = to_int(offset)

        offsets.append(offset)

      for i, offset in enumerate(offsets):
        chars = []

        size = int(info['encode'] / 8) # char size (utf-16 = 2 long)

        pntr = block['offset'] + 0x10 + offset
        if (i < len(offsets) - 1):
          # Read until the start of the next msg...
          endpntr = block['offset'] + 0x10 + offsets[i + 1]
        else:
          # ... Or until the end of the block
          endpntr = block['offset'] + 0x10 + block['size']

        while (pntr < endpntr):
          char, pntr = read(data, pntr, size)

          # Decode character
          char = char.decode(f"utf-{info['encode']}")
          chars.append(char)

        messages.append(''.join(chars))

    elif block['type'] == 'ATR1': # I can't tell what this block does lol
      attrs = []

      attrcount, pntr = read(data, pntr, 4)
      attrcount = to_int(attrcount)

      attrsize, pntr = read(data, pntr, 4)
      attrsize = to_int(attrsize)

      for i in range(0, attrcount):
        attr, pntr = read(data, pntr, attrsize)
        attr.decode(f"utf-{info['encode']}")

  messagedata[name] = {
    'labels': labels,
    'messages': messages,
    'attributes': attrs
  }

# --- For styles: they don't need their own for loop (too bad for scope)
data = msbpraw
info, pntr, to_int = getinfo(data)
blocks, pntr = getblocks(data, pntr)

print(blocks)

for block in blocks:
  pntr = block['offset'] + 0x10

  if block['type'] == 'CLR1':
    colors = []

    colorcount, pntr = read(data, pntr, 4)
    colorcount = to_int(colorcount)

    for i in range(0, colorcount):
      color, pntr = read(data, pntr, 4)
      colors.append('#' + color.hex())

  elif block['type'] == 'CLB1':
    labels, pntr = getlabels(data, info, pntr)

styledata = {
  'colors': colors,
  'labels': labels
}

with open('messages.json', 'w+') as mfile, open('styles.json', 'w+') as sfile:
  json.dump(messagedata, mfile, sort_keys=True, indent=2)
  json.dump(styledata, sfile, sort_keys=True, indent=2)