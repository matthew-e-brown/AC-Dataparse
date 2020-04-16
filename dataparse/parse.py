import os
import re
import json

cwd = os.path.dirname(os.path.realpath(__file__))

from lib import msbt
from lib import msbp

# BCSV Imports from Treeki (https://github.com/Treeki/CylindricalEarth)
from vendor import bcsv
from vendor import specs_100 as specs

def export(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w+') as exportfile:
    json.dump(data, exportfile, sort_keys=True, indent=2)


all_styles = msbp.parse_file(f"{cwd}/extracted/App.msbp", verbose=True)
fact_messages = {}
item_messages = {}

# Each filename is a different language
for filename in [ f for f in os.listdir(f"{cwd}/extracted") if os.path.isdir(f"{cwd}/extracted/{f}") ]:
  break
  print(f"Parsing {filename}:")
  fact_messages[filename] = {}
  item_messages[filename] = {}
  # Extract the comments:
  for name in ['Fish', 'Insect', 'Fossil']:
    fact_messages[filename][name] = msbt.parse_file(f"{cwd}/extracted/{filename}/SP_owl_Comment_{name}.msbt", verbose=True)

  # Extract the names:
  for n, name in [('31', 'Fish'), ('30', 'Insect'), ('34', 'Fossil')]:
    item_messages[filename][name] = msbt.parse_file(f"{cwd}/extracted/{filename}/STR_ItemName_{n}_{name}.msbt", verbose=True)

  print("\n", end='')

# Tidy up data a little bit:
for subset in [ fact_messages, item_messages ]:
  for filename, messages in dict.items(subset):
    for name, data in dict.items(messages):
      data['attributes'] = [ val.strip('\x00') for val in data['attributes'] ]
      data['attributes'] = [ val for val in data['attributes'] if val != '' ]

export(all_styles, f"{cwd}/output/styles.json")
export(fact_messages, f"{cwd}/output/comments.json")
export(item_messages, f"{cwd}/output/names.json")

bcsv_data = {}

for filename in [ f for f in os.listdir(f"{cwd}/extracted") if os.path.isfile(f"{cwd}/extracted/{f}")]:
  if filename[-5:] != '.bcsv': continue # tidy this up later

  rowclass = specs.lookup[filename]
  bcsvfile = bcsv.File(rowclass)

  with open(f"{cwd}/extracted/{filename}", 'rb') as f:
    bcsvfile.load(f.read())

  for row in bcsvfile.rows:
    for field in rowclass.fields():
      value = getattr(row, field)
      print(f"{f'FIELD: {field:>28}':>32} | {f'VALUE: {value}':>32}")
    print("\n\n")

# def hash(field):
#   hash = 0x0
#   for char in field:
#     hash *= 0x1F
#     hash += ord(char)
#   return hash