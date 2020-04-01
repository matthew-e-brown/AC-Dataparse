import os
import json

import msbt
import msbp

def export(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w+') as exportfile:
    json.dump(data, exportfile, sort_keys=True, indent=2)

cwd = os.path.dirname(os.path.realpath(__file__))

all_styles = msbp.parse_file(f"{cwd}/Extracted/App.msbp", verbose=True)
fact_messages = {}
item_messages = {}

# Extract the comments:
for name in ['Fish', 'Insect', 'Fossil']:
  fact_messages[name] = msbt.parse_file(f"{cwd}/Extracted/SP_owl_Comment_{name}.msbt", verbose=True)

# Extract the names:
for n, name in [('31', 'Fish'), ('30', 'Insect'), ('34', 'Fossil')]:
  item_messages[name] = msbt.parse_file(f"{cwd}/Extracted/STR_ItemName_{n}_{name}.msbt", verbose=True)

export(all_styles, f"{cwd}/Output/styles.json")
export(fact_messages, f"{cwd}/Output/comments.json")
export(item_messages, f"{cwd}/Output/names.json")