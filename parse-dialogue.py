# Parses the 

import os
import re
import json

cwd = os.path.dirname(os.path.realpath(__file__))

from lib import msbt
from lib import msbp

def export(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w+') as exportfile:
    json.dump(data, exportfile, sort_keys=True, indent=2)


all_styles = msbp.parse_file(f"{cwd}/extracted/App.msbp", verbose=True)
fact_messages = {}
item_messages = {}
fox_stuff = {}

# Each "filename" is a different language
for lang in [ f for f in os.listdir(f"{cwd}/extracted") if os.path.isdir(f"{cwd}/extracted/{f}") ]:
  print(f"Parsing {lang}:")
  fact_messages[lang] = {}
  item_messages[lang] = {}
  fox_stuff[lang] = {}

  # Extract the comments:
  for name in ['Fish', 'Insect', 'Fossil']:
    fact_messages[lang][name] = msbt.parse_file(f"{cwd}/extracted/{lang}/SP_owl_Comment_{name}.msbt", verbose=True)

  fox_stuff[lang] = msbt.parse_file(f"{cwd}/extracted/{lang}/SP_owl_22_Museum_RenualQuest.msbt", verbose=True)

  # Extract the names:
  for n, name in [('01', 'Art'), ('31', 'Fish'), ('30', 'Insect'), ('34', 'Fossil')]:
    item_messages[lang][name] = msbt.parse_file(f"{cwd}/extracted/{lang}/STR_ItemName_{n}_{name}.msbt", verbose=True)

  print("\n", end='')

# Tidy up data a little bit:
for lang in item_messages.values():            # CHzh
  for item in lang.values():                   # Fish
    for i, m in enumerate(item['messages']):   # List of messages
      # \u000e2\u0000\u0004\u0100\ucd03koi\u0000
      # m = m[:-1] # cut off null terminator
      # if m[0] == '\u000e':
      #   m = m[6:] # cut off first six "junk(?)" chars

      item['messages'][i] = m


export(all_styles, f"{cwd}/output/styles.json")
export(fact_messages, f"{cwd}/output/comments.json")
export(item_messages, f"{cwd}/output/names.json")
export(fox_stuff, f"{cwd}/output/renual.json")