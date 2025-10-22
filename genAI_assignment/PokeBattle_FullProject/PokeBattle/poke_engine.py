import random, os, datetime

LOGS_DIR = "logs"

class Move:
    def __init__(self, d):
        self.name = d.get("Name")
        self.power = int(d.get("Power", 0))
        self.accuracy = int(d.get("Accuracy", 100))
        self.priority = int(d.get("Priority", 0))
        self.category = d.get("Category", "Physical")
        self.effect = d.get("Effect", "None")

class CreatureInstance:
    def __init__(self, name, hp, atk, defe, spd, moves):
        self.name, self.max_hp, self.hp = name, int(hp), int(hp)
        self.atk, self.defe, self.spd = int(atk), int(defe), int(spd)
        self.status = None
        self.moves = [Move(m) if isinstance(m, dict) else Move({"Name": m, "Power":40, "Accuracy":100}) for m in moves]

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("Name"), d.get("HP",10), d.get("Attack",10), d.get("Defense",10), d.get("Speed",10), d.get("Moves", []))

    def choose_move_index(self):
        print(f"\n{self.name} HP: {self.hp}/{self.max_hp} — choose move:")
        for i,m in enumerate(self.moves): print(f" {i+1}. {m.name} (Pow {m.power}, Acc {m.accuracy})")
        while True:
            try:
                i = int(input("Move #: ")) - 1
                if 0 <= i < len(self.moves): return i
            except: pass
            print("Invalid.")

    def is_fainted(self): return self.hp <= 0
    def to_dict(self): return {"Name":self.name,"HP":self.hp,"Attack":self.atk,"Defense":self.defe,"Speed":self.spd,"Moves":[m.__dict__ for m in self.moves]}

class BattleEngine:
    CRIT_RATE = 0.0625
    def __init__(self, team_a, team_b):
        self.team_a, self.team_b, self.turn = team_a, team_b, 0
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.log_path = os.path.join(LOGS_DIR, f"battle_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.log_lines = []

    def log(self, msg): self.log_lines.append(msg); print(msg)
    def save_log(self):
        with open(self.log_path,'w') as f: f.write('\n'.join(self.log_lines))
        print(f"Battle log saved to {self.log_path}")

    def damage_calc(self,a,d,m):
        base = ((2*50/5+2)*m.power*(a.atk/d.defe))/50+2
        crit = random.random()<self.CRIT_RATE
        if crit: base*=1.5
        return int(base*random.uniform(0.85,1)), crit

    def get_active(self,t): return next((c for c in t if not c.is_fainted()), None)
    def alive(self,t): return any(not c.is_fainted() for c in t)

    def apply_status(self,creature):
        if creature.status == "Paralyzed" and random.random()<0.25:
            self.log(f"{creature.name} is paralyzed and can't move!")
            return False
        return True

    def run_cli_battle(self):
        self.log("Battle start!")
        while self.alive(self.team_a) and self.alive(self.team_b):
            self.turn+=1
            a,b=self.get_active(self.team_a),self.get_active(self.team_b)
            self.log(f"--- Turn {self.turn}: {a.name} vs {b.name} ---")
            m1=a.moves[a.choose_move_index()]
            m2=b.moves[random.randrange(len(b.moves))]
            order=sorted([(a,m1),(b,m2)],key=lambda x:(x[1].priority,x[0].spd),reverse=True)
            for actor,move in order:
                if actor.is_fainted(): continue
                target=b if actor is a else a
                if not self.apply_status(actor): continue
                if random.randint(1,100)>move.accuracy:
                    self.log(f"{actor.name}'s {move.name} missed!"); continue
                dmg,crit=self.damage_calc(actor,target,move)
                target.hp=max(0,target.hp-dmg)
                txt=f"{actor.name} used {move.name}! {'CRITICAL! ' if crit else ''}{target.name} took {dmg} dmg ({target.hp}/{target.max_hp})."
                self.log(txt)
                if move.effect=="BurnChance" and random.random()<0.1: target.status="Burned"; self.log(f"{target.name} was burned!")
                if move.effect=="ParalyzeChance" and random.random()<0.1: target.status="Paralyzed"; self.log(f"{target.name} was paralyzed!")
                if target.is_fainted(): self.log(f"{target.name} fainted!"); break
            for t in (self.team_a+self.team_b):
                if t.status=="Burned" and not t.is_fainted():
                    burn_dmg=max(1,int(t.max_hp*0.05));t.hp-=burn_dmg;self.log(f"{t.name} is hurt by its burn ({t.hp}/{t.max_hp}).")
        self.log("You won!" if self.alive(self.team_a) else "You lost!")
        self.save_log()
