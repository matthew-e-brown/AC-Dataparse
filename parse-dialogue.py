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
shutil.rmtree(f"{cwd}/output", ignore_errors=True)

# Each "filename" is a different language
for output, files in OUTPUTS.items():
  print(f"Parsing {output}:") # JSON output
  data = {}
  for lang in get_subdirs(f"{cwd}/extracted"):
    data[lang] = {}
    print(f"  Parsing {lang}:")
    for f in files:
      print(f"    Parsing {f[0]}") # individual MSBT
      try:
        data[lang][f[1]] = msbt.parse_file(f"{cwd}/extracted/{lang}/{f[0]}", verbose=False)
      except IOError as e:
        print(f"    Couldn't access {f[0]}. Skipping.")
        continue

      # Convert from three lists to one dictionary
      data[lang][f[1]] = {
        label['value']: {
          'attribute': data[lang][f[1]]['attributes'][label['index']],
          'message': data[lang][f[1]]['messages'][label['index']]
        } for label in data[lang][f[1]]['labels']
      }

  export(data, f"{cwd}/output/{output}.json")