import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from typing import Any, cast

# CONCURRENCY = 8


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
    move: str = ""
    level: int = 100
    item: None | str = None
    moves: list[str] = field(default_factory=list)
    tera_type: None | str = None
    is_tera: bool = False
    is_single_target: bool = True

    def to_json(self):
        if self.name == "Urshifu-Single-Strike":
            name = "Urshifu"
        elif self.name == "Indeedee-Male":
            name = "Indeedee"
        elif self.name == "Indeedee-Female":
            name = "Indeedee-F"
        elif self.name == "Tornadus-Incarnate":
            name = "Tornadus"
        elif self.name == "Landorus-Incarnate":
            name = "Landorus"
        else:
            name = self.name

        json_dict: dict[str, str | dict[str, int | None] | int] = {
            "name": name,
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


def csv_row_to_pokemon(row: list[str]) -> tuple[Pokemon, Pokemon]:
    # ,Spread,Category
    try:
        aname = row[0]
        a_move = row[1]
        a_ability = row[2]
        a_item = row[3]
        a_nature = row[4]
        a_hp = int(row[5])
        a_attack = int(row[6])
        a_defense = int(row[7])
        a_special_attack = int(row[8])
        a_special_defense = int(row[9])
        a_speed = int(row[10])
        attacking = Pokemon(
            name=aname,
            move=a_move,
            ability=a_ability,
            item=a_item,
            nature=a_nature,
            evs=Stats(
                a_hp, a_attack, a_defense, a_special_attack, a_special_defense, a_speed
            ),
            ivs=None,
            level=50,
        )

        dname = row[11]
        d_ability = row[12]
        d_item = row[13]
        d_nature = row[14]
        d_hp = int(row[15])
        d_attack = int(row[16])
        d_defense = int(row[17])
        d_special_attack = int(row[18])
        d_special_defense = int(row[19])
        d_speed = int(row[20])

        try:
            is_single_target = float(row[21]) == 1
        except Exception:
            is_single_target = False

        attacking.is_single_target = is_single_target
        defending = Pokemon(
            name=dname,
            ability=d_ability,
            item=d_item,
            nature=d_nature,
            evs=Stats(
                d_hp, d_attack, d_defense, d_special_attack, d_special_defense, d_speed
            ),
            ivs=None,
            level=50,
        )
        return (attacking, defending)
    except Exception:
        raise Exception(f"Row failed: {row}")


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


async def process_row(
    idx: int, line: str, rolls_dict: dict[int, list[int]], sem: asyncio.Semaphore
):
    async with sem:
        row = line.split(",")
        attacking, defending = csv_row_to_pokemon(row)

        input = json.dumps(
            {
                "attacking_pokemon": attacking.to_json(),
                "defending_pokemon": defending.to_json(),
            }
        )
        child = subprocess.run(["bun", "run", "index.ts", input], capture_output=True)
        if child.returncode != 0:
            print(attacking.name, defending.name)
            raise Exception("Failed to run calc")

        output: str = child.stdout.decode("utf-8").strip()

        local_rolls: list[int] = []
        local_rolls = cast(list[int], json.loads(output))
        rolls_dict[idx] = local_rolls


def process_rows(lines: list[str]) -> list[list[int]]:
    data: list[dict[str, Any]] = []
    for line in lines:
        if len(line) == 0:
            break
        row = line.split(",")
        attacking, defending = csv_row_to_pokemon(row)
        data.append(
            {
                "attacking_pokemon": attacking.to_json(),
                "defending_pokemon": defending.to_json(),
            }
        )

    child = subprocess.run(
        ["bun", "run", "index.ts", json.dumps(data)], capture_output=True
    )
    if child.returncode != 0:
        raise Exception("Failed to run calc")

    output: str = child.stdout.decode("utf-8").strip()

    local_rolls: list[list[int]] = []
    local_rolls = cast(list[list[int]], json.loads(output))
    return local_rolls


async def main():
    with open("data.csv", "r") as f:
        data = f.read()
    lines = data.split("\n")
    # skip header
    lines = lines[1:]

    # rolls_dict: dict[int, list[int]] = {}
    # sem = asyncio.Semaphore(CONCURRENCY)
    # tasks = [process_row(idx, line, rolls_dict, sem) for idx, line in enumerate(lines)]
    # _ = await asyncio.gather(*tasks)

    # rolls: list[list[int]] = [[] for _ in range(len(lines))]
    # for idx, roll in rolls_dict.items():
    #     rolls[idx] = roll

    rolls = process_rows(lines)

    with open("rolls.csv", "w") as f:
        for roll in rolls:
            roll_str = list(map(lambda x: str(x), roll))
            _ = f.write(",".join(roll_str) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
