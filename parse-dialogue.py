import os
import re
import json
import shutil

from lib import msbt
from lib import msbp

def export(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w+', encoding='utf-16') as exportfile:
    json.dump(data, exportfile, sort_keys=True, indent=2, ensure_ascii=False)

def get_subdirs(dirname):
  return [ f for f in os.listdir(dirname) if os.path.isdir(f"{dirname}/{f}") ]

cwd = os.path.dirname(os.path.realpath(__file__))
all_styles = msbp.parse_file(f"{cwd}/extracted/App.msbp", verbose=False)

# The JSON files that should be made and what MSBT they come from
OUTPUTS = {
  'Comments': [
    # (File to come from, JSON key)
    ('SP_owl_Comment_Fish.msbt', 'Fish'),
    ('SP_owl_Comment_Fossil.msbt', 'Fossil'),
    ('SP_owl_Comment_Insect.msbt', 'Insect')
  ],
  'ItemNames': [
    ('STR_ItemName_01_Art.msbt', 'Art'),
    ('STR_ItemName_30_Insect.msbt', 'Fish'),
    ('STR_ItemName_31_Fish.msbt', 'Fossil'),
    ('STR_ItemName_34_Fossil.msbt', 'Insect')
  ],
  'CatchPuns': [
    ('SYS_Get_Fish.msbt', 'Fish'),
    ('SYS_Get_Insect.msbt', 'Insect')
  ],
  'ArtFacts': [
    ('SYS_Museum_Art.msbt', 'Art')
  ]
}

# Clear old files
shutil.rmtree(f"{cwd}/parsed", ignore_errors=True)

# Each "filename" is a different language
for output, files in OUTPUTS.items():
  print(f"Parsing {output}:") # JSON output
  for lang in get_subdirs(f"{cwd}/extracted"):
    data = {}
    print(f"  Parsing {lang}:")
    for (name, key) in files:
      print(f"    Parsing {name}") # individual MSBT
      try:
        data[key] = msbt.parse_file(f"{cwd}/extracted/{lang}/{name}", verbose=False)
      except IOError as e:
        print(f"    Couldn't access {name}. Skipping.")
        continue

      # Convert from three lists to one dictionary
      data[key] = {
        label['value']: {
          'attributes': data[key]['attributes'][label['index']],
          'message': data[key]['message'][label['index']]
        } for label in data[key]['labels']
      }

    # Need to give each language its own folder to avoid MemoryError
    export(data, f"{cwd}/parsed/{lang}/{output}.json")