"""
This generates script<->name mappings and a
list of valid territories for ISOToolsBase.py

I do this as the LangData class depends on the ISOTools class,
and ISOTools needs some information LangData as well, so this caches
the needed info from LangData to reduce some extremely hairy
dependency problems >_<
"""

from lang_data.data_paths import data_path
from toolkit.json_tools import dump
from lang_data.LangData import LangData

out = data_path('cldr', 'script_mappings.json')
ld_en = LangData('en-US')

# Get an English map from script->name and name->script
DName2Script = {}
DScript2Name = {}

for script in ld_en.get_L_scripts():
    script_name = ld_en.get_script_name(script)
    DName2Script[script_name.lower()] = script
    DScript2Name[script] = script_name

dump(out, {
    'DName2Script': DName2Script,
    'DScript2Name': DScript2Name,
    'LTerritories': ld_en.get_L_territories()
})
