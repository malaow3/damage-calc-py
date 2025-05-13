import { calculate, Generations, Pokemon, Move } from "@smogon/calc";
import type { TypeName } from "@smogon/calc/dist/data/interface";

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
  level: number;
  tera_type?: string;
  is_tera: boolean;
};

type DataFile = {
  attacking_pokemon: PokemonData;
  defending_pokemon: PokemonData;
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

async function main() {
  const data_raw = Bun.file("data.json");
  const data_json = (await data_raw.json()) as unknown as DataFile;

  const attacking_pokemon = data_json.attacking_pokemon;
  const attacking_stats = setStats(attacking_pokemon.evs ?? {});
  const attacking_ivs = setStats(attacking_pokemon.ivs ?? {});
  let attacking_tera_type: TypeName | undefined = undefined;
  if (attacking_pokemon.is_tera) {
    attacking_tera_type = attacking_pokemon.tera_type as unknown as TypeName;
  }

  const defending_pokemon = data_json.defending_pokemon;
  const defending_stats = setStats(defending_pokemon.evs ?? {});
  const defending_ivs = setStats(defending_pokemon.ivs ?? {});
  let defending_tera_type: TypeName | undefined = undefined;
  if (defending_pokemon.is_tera) {
    defending_tera_type = defending_pokemon.tera_type as unknown as TypeName;
  }

  const gen = Generations.get(9);
  const result = calculate(
    gen,
    new Pokemon(gen, attacking_pokemon.name, {
      level: attacking_pokemon.level,
      ability: attacking_pokemon.ability,
      item: attacking_pokemon.item,
      nature: attacking_pokemon.nature,
      evs: attacking_stats,
      ivs: attacking_ivs,
      teraType: attacking_tera_type,
    }),
    new Pokemon(gen, defending_pokemon.name, {
      level: defending_pokemon.level,
      ability: defending_pokemon.ability,
      item: defending_pokemon.item,
      nature: defending_pokemon.nature,
      evs: defending_stats,
      ivs: defending_ivs,
      teraType: defending_tera_type,
    }),
    new Move(gen, attacking_pokemon.move),
  );

  const rolls = result.damage;

  const output = Bun.file("output.json");
  await output.write(JSON.stringify(rolls));
}

main();
