# Functions for handling the superset of MSBT and MSBP files
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/LMS-File-Format

global ENDIAN
ENDIAN = 'little'

def calculate_hash(label, num_slots):
  hash = 0
  for char in label:
    hash = hash * 0x492 + ord(char)
  return (hash & 0xFFFFFFFF) % num_slots


def read(data, pointer, bytecount):
  return data[pointer : pointer + bytecount], pointer + bytecount


def parse_file_header(data):
  pntr = 0x0
  info = {}

  info['magic'], pntr = read(data, pntr, 8)
  info['magic'] = info['magic'].decode('utf-8') # always utf-8

  info['endian'], pntr = read(data, pntr, 2)
  info['endian'] = 'big' if info['endian'] == b'\xFE\xFF' else 'little'

  # To return later, now that we know what endian is
  info['convert'] = lambda b: int.from_bytes(b, info['endian'])

  pntr += 2
  info['encode'], pntr = read(data, pntr, 1)

  if info['convert'](info['encode']) == 0x00: info['encode'] = 8
  elif info['convert'](info['encode']) == 0x01: info['encode'] = 16
  elif info['convert'](info['encode']) == 0x02: info['encode'] = 32

  pntr += 1
  info['blocks'], pntr = read(data, pntr, 2)
  info['blocks'] = info['convert'](info['blocks'])

  pntr += 2
  info['size'], pntr = read(data, pntr, 4)
  info['size'] = info['convert'](info['size'])

  pntr += 10

  return info, pntr


def parse_blocks(data, info):
  pntr = 0x20 # blocks always start here
  blocks = []

  for i in range(0, info['blocks']):
    block = {}

    block['offset'] = pntr

    block['type'], pntr = read(data, pntr, 4)
    block['type'] = block['type'].decode('utf-8') # always utf-8

    block['size'], pntr = read(data, pntr, 4)
    block['size'] = info['convert'](block['size'])

    blocks.append(block)

    # Shunt pntr along to the end of the block
    pntr += 8 # header padding
    pntr += block['size'] # block
    while data[pntr : pntr + 1] == b'\xab': pntr += 1 # block padding

  return blocks, pntr


def parse_labels(data, info, block):
  pntr = block['offset'] + 0x10

  # Start by reading in the hash table's buckets/slots
  hashslots = []
  
  slotcount, pntr = read(data, pntr, 4)
  slotcount = info['convert'](slotcount)

  for i in range(0, slotcount):
    slot = {}
    
    slot['numlabels'], pntr = read(data, pntr, 4)
    slot['numlabels'] = info['convert'](slot['numlabels'])

    slot['offset'], pntr = read(data, pntr, 4)
    slot['offset'] = info['convert'](slot['offset'])

    hashslots.append(slot)

  # Read the rest, should be all labels
  labels = []
  while (pntr < block['offset'] + block['size']):
    label = {}

    length, pntr = read(data, pntr, 1)
    length = info['convert'](length)

    label['value'], pntr = read(data, pntr, length)
    label['value'] = label['value'].decode('utf-8') # always utf8

    label['itemindex'], pntr = read(data, pntr, 4)
    label['itemindex'] = info['convert'](label['itemindex'])

    labels.append(label)

  labels = sorted(labels, key=lambda l: l['itemindex'])
  return labels, pntr