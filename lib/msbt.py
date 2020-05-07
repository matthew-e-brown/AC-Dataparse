# Functions for handing Message (MSBT) files
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format

# Builtins
import sys
import errno

# My own imports
from . import lms

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
      print(f"Uknown errno: {e.errno}", file=sys.stderr)

    if __name__ != "__main__": raise e
    else: sys.exit(-1)

  message_data = {}

  pntr = 0x00
  info, pntr = lms.parse_file_header(data)
  blocks, pntr = lms.parse_blocks(data, info)

  if verbose: print(blocks)

  labels = []
  messages = []
  attributes = []

  for block in blocks:
    pntr = block['offset'] + 0x10 # block's header size

    # Parse the block:
    if block['type'] == 'LBL1':
      # Deal with message lables
      labels, pntr = lms.parse_labels(data, info, block)
    elif block['type'] == 'TXT2':
      # Deal with message bodies
      msg_count, pntr = lms.read(data, pntr, 4)
      msg_count = info['convert'](msg_count)

      # For each message, get where it starts
      offsets = []
      for i in range(0, msg_count):
        offset, pntr = lms.read(data, pntr, 4)
        offset = info['convert'](offset)
        offsets.append(offset)

      # Now read their text
      for i, offset in enumerate(offsets):
        pntr = block['offset'] + 0x10 + offset
        if (i < len(offsets) - 1): # If there is a next message
          # Stop at the start of the next message
          endpntr = block['offset'] + 0x10 + offsets[i + 1]
        else:
          # Stop at the end of the block
          endpntr = block['offset'] + 0x10 + block['size']

        message, pntr = lms.read(data, pntr, endpntr - pntr)
        messages.append(message.decode(f"utf-{info['encode']}"))

    elif block['type'] == 'ATR1':
      attr_count, pntr = lms.read(data, pntr, 4)
      attr_count = info['convert'](attr_count)

      attr_size, pntr = lms.read(data, pntr, 4)
      attr_size = info['convert'](attr_size)

      for i in range(0, attr_count):
        attr, pntr = lms.read(data, pntr, attr_size)
        # Decode as unicode if possible... else just make it an int
        try:
          attr = attr.decode(f"utf-{info['encode']}")
        except UnicodeDecodeError as e:
          attr = int.from_bytes(attr, info['endian'])

        attributes.append(attr)

  message_data = {
    'labels': labels,
    'messages': messages,
    'attributes': attributes
  }

  return message_data