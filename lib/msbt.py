# Functions for handing Message (MSBT) files
# https://github.com/Kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format

# Builtins
import sys
import errno

# My own imports
from . import lms

def hex_stringify(bytestring):
  s = bytestring.hex().upper()
  return " ".join(s[i : i+2] for i in range(0, len(s), 2))


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
      print(f"Unknown errno: {e.errno}", file=sys.stderr)

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
        message, commands = process_escapes(message, info['endian'], verbose)

        message = {
          'body': message.decode(f"utf-{info['encode']}"),
          'commands': commands
        }

        messages.append(message)

    elif block['type'] == 'ATR1':
      attr_count, pntr = lms.read(data, pntr, 4)
      attr_count = info['convert'](attr_count)

      attr_size, pntr = lms.read(data, pntr, 4)
      attr_size = info['convert'](attr_size)

      for i in range(0, attr_count):
        attr, pntr = lms.read(data, pntr, attr_size)
        # Just stringify their bytes
        attr = hex_stringify(attr)
        attributes.append(attr)

  message_data = {
    'labels': labels,
    'message': messages,
    'attributes': attributes
  }

  return message_data


def process_escapes(message, endian, verbose=False):
  commands = []

  # Split the message into a list of pairs of two bytes
  raw_bytes = ( message[i:i + 2] for i in range(0, len(message), 2) )
  iterator = enumerate(raw_bytes)
  for i, pair in iterator:
    # Command escape
    if pair == b'\x0e\x00':
      command = {}
      command['index'] = i # the index into the iterator the command is found
      command['type'] = next(iterator)[1] # Read next pair of bytes

      # - Variable length commands
      if command['type'] == b'\x00\x00':
        command['variant'] = next(iterator)[1]
        if command['variant'] == b'\x00\x00': command['optlen'] = 3
        elif command['variant'] == b'\x02\x00': command['optlen'] = 2
        elif command['variant'] == b'\x03\x00': command['optlen'] = 2
        elif command['variant'] == b'\x04\x00': command['optlen'] = 1

      # - Variable length, no variants. Will be read until 0x0000
      elif command['type'] == b'\x3c\x00':
        command['variant'] = None
        command['optlen'] = None

      # - Constant length commands
      else:
        command['variant'] = None # these commands have no variants

        if command['type'] == b'\x28\x00': command['optlen'] = 4
        elif command['type'] == b'\x0a\x00': command['optlen'] = 2
        elif command['type'] == b'\x6e\x00': command['optlen'] = 2
        elif command['type'] == b'\x32\x00': command['optlen'] = 4
        elif command['type'] == b'\x3c\x00': command['optlen'] = 1
        else:
          # Weird russian exception in SYS_Get_Fish.msbt in one spot
          if command['type'] == b'\x3f\x04': continue
          raise Exception(f"Unknown command: 0x{command['type'].hex()}")

      # -- Now that we know how many shorts (options) follow, grab them
      command['options'] = []
      reads = 0
      while True: # certain types have different break-points
        raw_option = next(iterator)[1]

        # break if optlen not given, and we hit a 0x0000 string
        if command['optlen'] is None and raw_option == b'\x00\x00':
          # store how many bytes we read, used to cut them off later
          command['optlen'] = reads + 1
          break

        # Else
        reads += 1
        option = int.from_bytes(raw_option, endian, signed=False)
        command['options'].append(option)

        # break if optlen is given *and* surpassed
        if command['optlen'] is not None and reads >= command['optlen']:
          break

      # Serialize the type and variant (can't be binary-strings)
      for prop in ('variant', 'type'):
        if command[prop] is not None:
          command[prop] = hex_stringify(command[prop])

      commands.append(command)

  # End of iterating 

  # -- Now that we have the commands extracted, cut them from the main string
  # A lot of numbers need to be doubled to go from counting shorts to bytes...
  totalcut = 0
  for command in commands:
    cutsize = command['optlen'] + 2 # include escape and type (0E 00 & 28 00)
    if command['variant'] is not None: cutsize += 1 # include variant byte
    cutsize *= 2

    start = command['index'] * 2 - totalcut
    message = message[0 : start] + message[start + cutsize : ]

    totalcut += cutsize
    del command['optlen']

  return message, commands