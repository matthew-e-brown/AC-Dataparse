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
        message, commands = process_commands(message, info['endian'], verbose)

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


# Guide to adding commands (see Notes.md)
# - If it's a constant length command, just add its optlen.
# - If it has variants, add another dict that holds each variant's optlen.
# - If the command has variable option length where it should be read until a
#   terminator short (2 bytes), include a tuple indicating that short and if the
#   terminator should be kept in the options array
OPTION_LENGTHS = {
  '28 00': 4,
  '6E 00': 2,
  '32 00': 4,
  '3C 00': ( '00 00', True ),
  '00 00': { '00 00': 3, '02 00': 2, '03 00': 2, '04 00': 1 },
  '0A 00': { '00 00': 2, 'else': 1 }
}

def process_commands(message, endian, verbose=False):
  commands = []

  # Split the message into a list of pairs of two bytes
  short = ( message[i:i + 2] for i in range(0, len(message), 2) )
  iterator = enumerate(short)
  for i, pair in iterator:
    # Command escape
    if pair == b'\x0e\x00':
      c_index = i # the index into the iterator the command is found
      c_type = hex_stringify(next(iterator)[1]) # Read next pair of bytes

      # See what the option-length course-of-action is for this command
      try:
        command_choice = OPTION_LENGTHS[c_type]
      except KeyError:
        # Deal with weird russian exception (see Notes.md)
        if c_type == '3F 04': c_variant = None; c_optlen = 0
        else:
          raise Exception(
            f"Unknown command: {c_type}. Message index: {i * 2}."
          ) from None

      # Check what to do with that 
      if type(command_choice) is int: # fixed option-length
        c_variant = None
        c_optlen = command_choice
      elif type(command_choice) is dict: # variants with different opt-lengths
        c_variant = hex_stringify(next(iterator)[1])
        try: # check if this variant defined
          c_optlen = OPTION_LENGTHS[c_type][c_variant]
        except KeyError: # see if an else condition is defined
          try: c_optlen = OPTION_LENGTHS[c_type]['else']
          except KeyError: # throw exception
            raise Exception(
              f"Unknown variant {c_variant} for command {c_type}."
            ) from None
      elif type(command_choice) is tuple: # read-until
        c_variant = None
        c_optlen = None
        c_until = OPTION_LENGTHS[c_type]
      else:
        raise Exception(
          "Incorrect type in option-lengths dictionary: " +
          f" {type(command_choice)}."
        )

      # -- Now that we know how many shorts (options) follow, grab them
      c_options = []
      if type(c_optlen) is int: # if we know how long the options are
        # read that many of them
        for _ in range(0, c_optlen):
          c_options.append(hex_stringify(next(iterator)[1]))
      elif c_optlen is None: # if we don't know how long...
        # read until the most recently read short matches the terminator
        while True: # emulate do-while
          c_options.append(hex_stringify(next(iterator)[1]))
          if c_options[-1] == c_until[0]: break # emulate do-while
        if c_until[1] != True:
          c_options = c_options[:-1] # cut off terminator if not desired
      else:
        raise Exception(
          f"Incorrect type in option-lengths dictionary: {type(c_optlen)}."
        )

      commands.append({
        'index': c_index,
        'type': c_type,
        'variant': c_variant,
        'options': c_options
      })

  # End of iterating 

  # -- Now that we have the commands extracted, cut them from the main string
  # A lot of numbers need to be doubled to go from counting shorts to bytes...
  totalcut = 0
  for command in commands:
    cutsize = len(command['options']) + 2 # include escape and type (0E 00 & 28 00)
    if command['variant'] is not None: cutsize += 1 # include variant byte
    cutsize *= 2

    start = command['index'] * 2 - totalcut
    message = message[0 : start] + message[start + cutsize : ]

    totalcut += cutsize

  return message, commands