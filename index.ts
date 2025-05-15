import { calculate, Generations, Pokemon, Move, Field } from "@smogon/calc";
import type { Terrain, TypeName } from "@smogon/calc/dist/data/interface";

type Stats = {
  hp?: number;
  attack?: number;
  defense?: number;
  special_attack?: number;
  special_defense?: number;
  speed?: number;
};

type CalcStats = {
  hp?: number;
  atk?: number;
  def?: number;
  spa?: number;
  spd?: number;
  spe?: number;
};

type PokemonData = {
  name: string;
  ability: string;
  item?: string;
  nature: string;
  evs?: Stats;
  ivs?: Stats;
  move: string;
  is_single_target: boolean;
  level: number;
  tera_type?: string;
  is_tera: boolean;
};

type DataFile = {
  attacking_pokemon: PokemonData;
  defending_pokemon: PokemonData;
  terrain_override?: string;
};

function setStats(raw_stats: Stats): CalcStats {
  const stats: CalcStats = {};
  if (raw_stats.hp) {
    stats.hp = raw_stats.hp;
  }
  if (raw_stats.attack) {
    stats.atk = raw_stats.attack;
  }
  if (raw_stats.defense) {
    stats.def = raw_stats.defense;
  }
  if (raw_stats.special_attack) {
    stats.spa = raw_stats.special_attack;
  }
  if (raw_stats.special_defense) {
    stats.spd = raw_stats.special_defense;
  }
  if (raw_stats.speed) {
    stats.spe = raw_stats.speed;
  }
  return stats;
}

const lastAutoTerrain = ["", ""];
function autosetTerrain(ability: string, i: number) {
  const currentTerrain = "No terrain";
  if (lastAutoTerrain.indexOf(currentTerrain) === -1) {
    lastAutoTerrain[1 - i] = "";
  }
  switch (ability) {
    case "Electric Surge":
    case "Hadron Engine":
      lastAutoTerrain[i] = "Electric";
      break;
    case "Grassy Surge":
      lastAutoTerrain[i] = "Grassy";
      break;
    case "Misty Surge":
      lastAutoTerrain[i] = "Misty";
      break;
    case "Psychic Surge":
      lastAutoTerrain[i] = "Psychic";
      break;
    default:
      lastAutoTerrain[i] = "";
  }
}

async function main() {
  const number = process.argv[2] as string;
  const input = Bun.file(`data-${number}.json`);
  const data_json = (await input.json()) as unknown as DataFile[];

  const return_rolls: number[][] = [];

  for (const data of data_json) {
    const attacking_pokemon = data.attacking_pokemon;
    const attacking_stats = setStats(attacking_pokemon.evs ?? {});
    const attacking_ivs = setStats(attacking_pokemon.ivs ?? {});
    let attacking_tera_type: TypeName | undefined = undefined;
    if (attacking_pokemon.is_tera) {
      attacking_tera_type = attacking_pokemon.tera_type as unknown as TypeName;
    }

    const game_type = attacking_pokemon.is_single_target
      ? "Singles"
      : "Doubles";

    const defending_pokemon = data.defending_pokemon;
    const defending_stats = setStats(defending_pokemon.evs ?? {});
    const defending_ivs = setStats(defending_pokemon.ivs ?? {});
    let defending_tera_type: TypeName | undefined = undefined;
    if (defending_pokemon.is_tera) {
      defending_tera_type = defending_pokemon.tera_type as unknown as TypeName;
    }

    // console.log(attacking_pokemon);
    // console.log(defending_pokemon);

    autosetTerrain(attacking_pokemon.ability, 0);
    autosetTerrain(defending_pokemon.ability, 1);

    const gen = Generations.get(9);
    const attacking_pokemon_object = new Pokemon(gen, attacking_pokemon.name, {
      level: attacking_pokemon.level,
      ability: attacking_pokemon.ability,
      item: attacking_pokemon.item,
      nature: attacking_pokemon.nature,
      evs: attacking_stats,
      ivs: attacking_ivs,
      teraType: attacking_tera_type,
    });
    const defending_pokemon_object = new Pokemon(gen, defending_pokemon.name, {
      level: defending_pokemon.level,
      ability: defending_pokemon.ability,
      item: defending_pokemon.item,
      nature: defending_pokemon.nature,
      evs: defending_stats,
      ivs: defending_ivs,
      teraType: defending_tera_type,
    });

    let terrain_string = "No Terrain";
    if (
      lastAutoTerrain[0] !== "No Terrain" &&
      lastAutoTerrain[1] !== "No Terrain"
    ) {
      // Find which pokemon is SLOWER, then apply THAT terrain
      const attacking_pokemon_speed = attacking_pokemon_object.rawStats.spe;
      const defending_pokemon_speed = defending_pokemon_object.rawStats.spe;
      if (attacking_pokemon_speed > defending_pokemon_speed) {
        terrain_string = lastAutoTerrain[1] as string;
      } else if (attacking_pokemon_speed < defending_pokemon_speed) {
        terrain_string = lastAutoTerrain[0] as string;
      } else {
        // const idx = Math.floor(Math.random() * 2);
        // terrain_string = lastAutoTerrain[idx] as string;

        // Normally, this is a coin flip to decide, but for the sake of determinism, let's
        // just use the attacking terrain
        terrain_string = lastAutoTerrain[0] as string;
      }
    } else if (
      lastAutoTerrain[0] !== "No Terrain" &&
      lastAutoTerrain[1] === "No Terrain"
    ) {
      terrain_string = lastAutoTerrain[0] as string;
    } else if (
      lastAutoTerrain[0] === "No Terrain" &&
      lastAutoTerrain[1] !== "No Terrain"
    ) {
      terrain_string = lastAutoTerrain[1] as string;
    }

    let terrain: Terrain | undefined = undefined;
    if (terrain_string !== "No Terrain") {
      terrain = terrain_string as Terrain;
    }

    if (data.terrain_override) {
      terrain = data.terrain_override as Terrain;
    }
    // console.log(`Terrain: ${terrain}`);

    const result = calculate(
      gen,
      attacking_pokemon_object,
      defending_pokemon_object,
      new Move(gen, attacking_pokemon.move),
      new Field({
        gameType: game_type,
        terrain: terrain,
      }),
    );

    const rolls = result.damage;
    if (typeof rolls === "number") {
      return_rolls.push([rolls]);
    } else {
      return_rolls.push(rolls as number[]);
    }
  }
  const output = Bun.file(`output-${number}.json`);
  output.write(JSON.stringify(return_rolls));
}

main();
