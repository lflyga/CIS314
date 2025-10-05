import json
import re
from typing import Dict, List, Optional, Tuple  #for type hints for easier readabilty and understanding expected outputs
from .models import Move, Creature

#========================
#regex for parsing text-based data from the data folder for creatures and moves
#========================

#matches lines like:
#Creature: #004 Charmander | Type: Fire | HP: 39 | ATK: 52 | ...
CRE_RE_NUM = re.compile(
    r"^Creature:\s*#(?P<dex>\d{3})\s+(?P<name>[^|]+)\s*\|\s*Type:\s*(?P<types>[^|]+)\s*\|"
    r"\s*HP:\s*(?P<hp>\d+)\s*\|\s*ATK:\s*(?P<atk>\d+)\s*\|\s*DEF:\s*(?P<dfn>\d+)\s*\|"
    r"\s*SP\.ATK:\s*(?P<spa>\d+)\s*\|\s*SP\.DEF:\s*(?P<spd>\d+)\s*\|\s*SPD:\s*(?P<spe>\d+)\s*$"
)

#matches line like:
#Creature: No.004 Charmander | Type: Fire | ...
CRE_RE_NO = re.compile(
    r"^Creature:\s*No\.(?P<dex>\d{3})\s+(?P<name>[^|]+)\s*\|\s*Type:\s*(?P<types>[^|]+)\s*\|"
    r"\s*HP:\s*(?P<hp>\d+)\s*\|\s*ATK:\s*(?P<atk>\d+)\s*\|\s*DEF:\s*(?P<dfn>\d+)\s*\|"
    r"\s*SP\.ATK:\s*(?P<spa>\d+)\s*\|\s*SP\.DEF:\s*(?P<spd>\d+)\s*\|\s*SPD:\s*(?P<spe>\d+)\s*$"
)