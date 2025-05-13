import json
import subprocess
from dataclasses import dataclass, field
from typing import cast


@dataclass
class Stats:
    hp: None | int = None
    attack: None | int = None
    defense: None | int = None
    special_attack: None | int = None
    special_defense: None | int = None
    speed: None | int = None

    def to_json(self):
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "special_attack": self.special_attack,
            "special_defense": self.special_defense,
            "speed": self.speed,
        }


@dataclass
class Pokemon:
    name: str
    ability: str
    nature: str
    evs: None | Stats
    ivs: None | Stats
    move: str
    level: int = 100
    item: None | str = None
    moves: list[str] = field(default_factory=list)
    tera_type: None | str = None
    is_tera: bool = False

    def to_json(self):
        json_dict: dict[str, str | dict[str, int | None] | int] = {
            "name": self.name,
            "ability": self.ability,
            "nature": self.nature,
            "move": self.move,
            "level": self.level,
            "is_tera": self.is_tera,
        }

        if self.tera_type is not None:
            json_dict["tera_type"] = self.tera_type
        else:
            del json_dict["is_tera"]

        if self.item is not None:
            json_dict["item"] = self.item
        if self.ivs is not None:
            json_dict["ivs"] = self.ivs.to_json()
        if self.evs is not None:
            json_dict["evs"] = self.evs.to_json()

        return json_dict


def pokemon_from_paste(paste: str) -> Pokemon:
    lines = paste.split("\n")
    name_and_item = lines[0].split("@")
    name = name_and_item[0]
    if len(name_and_item) > 1:
        item = lines[0].split("@")[1]
    else:
        item = None

    ability = ""
    nature = ""
    level = 100
    evs = None
    ivs = None
    moves: list[str] = []
    tera_type = None
    for line in lines[1:]:
        if line.startswith("Ability:"):
            ability = line.split(":")[1].strip()
        if line.startswith("Nature:"):
            nature = line.split(":")[1].strip()
        if line.startswith("Level:"):
            level = int(line.split(":")[1].strip())

        if line.startswith("EVs:"):
            sections = line.split(":")[1].strip().split(" / ")
            hp = None
            attack = None
            defense = None
            special_attack = None
            special_defense = None
            speed = None
            for section in sections:
                if "HP" in section:
                    hp = int(section.split(" ")[0])
                if "Atk" in section:
                    attack = int(section.split(" ")[0])
                if "Def" in section:
                    defense = int(section.split(" ")[0])
                if "SpA" in section:
                    special_attack = int(section.split(" ")[0])
                if "SpD" in section:
                    special_defense = int(section.split(" ")[0])
                if "Spe" in section:
                    speed = int(section.split(" ")[0])
            evs = Stats(hp, attack, defense, special_attack, special_defense, speed)
        if line.startswith("IVs:"):
            sections = line.split(":")[1].strip().split(" / ")
            hp = None
            attack = None
            defense = None
            special_attack = None
            special_defense = None
            speed = None
            for section in sections:
                if "HP" in section:
                    hp = int(section.split(" ")[0])
                if "Atk" in section:
                    attack = int(section.split(" ")[0])
                if "Def" in section:
                    defense = int(section.split(" ")[0])
                if "SpA" in section:
                    special_attack = int(section.split(" ")[0])
                if "SpD" in section:
                    special_defense = int(section.split(" ")[0])
                if "Spe" in section:
                    speed = int(section.split(" ")[0])
            ivs = Stats(hp, attack, defense, special_attack, special_defense, speed)
        if "Nature" in line:
            nature = line.split(" ")[0].strip()
        if line.startswith("Tera Type:"):
            tera_type = line.split(":")[1].strip()
        if line.startswith("- "):
            moves.append(line.split("- ")[1].strip())

    return Pokemon(
        name=name,
        ability=ability,
        level=level,
        ivs=ivs,
        evs=evs,
        moves=moves,
        move=moves[0],
        nature=nature,
        item=item,
        tera_type=tera_type,
    )


def main():
    abomasnow = """Abomasnow @ Heavy-Duty Boots
Level: 50
Bold Nature
Tera Type: Water
Ability: Snow Warning
EVs: 248 HP / 252 Def / 8 Spe
- Blizzard
- Giga Drain
- Earth Power
- Aurora Veil
"""

    houndoom = """Houndoom @ Houndoominite
Level: 50
Timid Nature
Ability: Flash Fire
EVs: 252 SpA / 4 SpD / 252 Spe
IVs: 0 Atk
- Dark Pulse
- Fire Blast
- Sludge Bomb
- Nasty Plot
"""

    attacking = pokemon_from_paste(houndoom)
    attacking.move = attacking.moves[1]
    defending = pokemon_from_paste(abomasnow)
    defending.is_tera = True

    with open("data.json", "w") as f:
        _ = f.write(
            json.dumps(
                {
                    "attacking_pokemon": attacking.to_json(),
                    "defending_pokemon": defending.to_json(),
                }
            )
        )

    child = subprocess.run(["bun", "run", "index.ts"])
    if child.returncode != 0:
        raise Exception("Failed to run calc")

    rolls: list[int] = []
    with open("output.json", "r") as f:
        rolls = cast(list[int], json.load(f))
    print(rolls)


if __name__ == "__main__":
    main()
