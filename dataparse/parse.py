import os
import re
import json

from lib import msbt
from lib import msbp

def export(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w+') as exportfile:
    json.dump(data, exportfile, sort_keys=True, indent=2)

cwd = os.path.dirname(os.path.realpath(__file__))

all_styles = msbp.parse_file(f"{cwd}/extracted/App.msbp", verbose=True)
fact_messages = {}
item_messages = {}

for lang in [ f for f in os.listdir(f"{cwd}/extracted") if os.path.isdir(f"{cwd}/extracted/{f}") ]:
  print(f"Parsing {lang}:")
  fact_messages[lang] = {}
  item_messages[lang] = {}
  # Extract the comments:
  for name in ['Fish', 'Insect', 'Fossil']:
    fact_messages[lang][name] = msbt.parse_file(f"{cwd}/extracted/{lang}/SP_owl_Comment_{name}.msbt", verbose=True)

  # Extract the names:
  for n, name in [('31', 'Fish'), ('30', 'Insect'), ('34', 'Fossil')]:
    item_messages[lang][name] = msbt.parse_file(f"{cwd}/extracted/{lang}/STR_ItemName_{n}_{name}.msbt", verbose=True)

  print("\n", end='')

# Tidy up data a little bit:
for subset in [ fact_messages, item_messages ]:
  for lang, messages in dict.items(subset):
    for name, data in dict.items(messages):
      data['attributes'] = [ val.strip('\x00') for val in data['attributes'] ]
      data['attributes'] = [ val for val in data['attributes'] if val != '' ]

export(all_styles, f"{cwd}/output/styles.json")
export(fact_messages, f"{cwd}/output/comments.json")
export(item_messages, f"{cwd}/output/names.json")