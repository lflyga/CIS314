"""
Author: L. Flygare
Description: lighweight save/load and logging utilities
            -sets up saves/ dir with slots/ and battles/
            -save slots for resuming a battle
            -archives battle logs with date/time
"""

from __future__ import annotations
import json, time
from pathlib import Path
from typing import Dict, List, Optional

class SaveManager:
    """
    makes and manages two subfolders: <root>/saves/slots , <root>/saves/battles
        saves/
            ├─ slots/    # named JSON snapshots (e.g., "autosave.json")
            └─ battles/  # timestamped battle logs (.json + .log)
    """
    def __init__(self, project_root: Path):
        self.root = project_root
        self.saves_dir = self.root / "saves"
        self.slots_dir = self.saves_dir / "slots"
        self.battles_dir = self.saves_dir / "battles"
        self.slots_dir.mkdir(parents = True, exist_ok = True)
        self.battles_dir.mkdir(parents = True, exist_ok = True)

    #========================
    #save slots for resuming
    #-save and restore arbitrary state dictionaries to/from slots
    #========================

    def save_slot(self, slot_name: str, state: Dict) -> Path:
        """writes a json snapshot of any dictionary state"""
        p = self.slots_dir / f"{slot_name}.json"
        with p.open("w", encoding = "utf-8") as f:
            json.dump(state, f, ensure_ascii = False, indent = 2)
        return p
    
    def load_slot(self, slot_name: str) -> Optional[Dict]:
        """loads a saved state dictionary if it exists, None if missing"""
        p = self.slots_dir / f"{slot_name}.json"
        if not p.exists():
            return None
        with p.open("r", encoding = "utf-8") as f:
            return json.load(f)
        
    def list_slots(self) -> List[str]:
        """lists available slot names"""
        return sorted([p.stem for p in self.slots_dir.glob("*.json")])
    
    #========================
    #battle history logging
    #-write a timestamped battle archive:
    # * JSON:  {"meta": {...}, "events": [...], "log": ["..."]}
    # * TEXT:  human-readable .log (one line per event)
    #========================

    def write_battle_log(self, meta: Dict, lines: List[str], events: List[Dict]) -> Dict[str, Path]:
        """writes a timestamped json (meta + events + log lines) and human readable .log file (eg YYYYMMDD_HHMMSS_battle_004_vs_007)"""
        ts = time.strftime("%Y%m%d_%H%M%S")     #removed originally included ':'s becaase it was throwing errors including it in the filename
        a = meta.get("a_dex", "unk").replace("#", "")
        b = meta.get("b_dex", "unk").replace("#", "")
        base = f"{ts}_battle_{a}_vs_{b}"
        json_path = self.battles_dir / f"{base}.json"
        log_path = self.battles_dir / f"{base}.log"

        #structured json for post analysis
        with json_path.open("w", encoding = "utf-8") as f:
            json.dump({"meta": meta, "events": events, "log": lines}, f, ensure_ascii = False, indent = 2)

        #human readable log for easy checking
        with log_path.open("w", encoding = "utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return {"json": json_path, "log": log_path}
    
    def rotate_battles(self, keep_last: int = 200):
        """keeps only the most recent keep_last battle logs (json + .log), deletes older ones"""
        items = sorted(self.battles_dir.glob("*.json"))
        if len(items) <= keep_last:
            return
        
        to_remove = items[0: len(items) - keep_last]

        #removing excess logs
        for p in to_remove:
            txt = p.with_suffix(".log")
            if txt.exists():
                txt.unlink(missing_ok = True)   #removes text log if present
            p.unlink(missing_ok = True)         #removes json log 
