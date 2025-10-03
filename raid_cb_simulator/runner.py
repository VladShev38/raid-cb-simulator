import itertools
import math
from multiprocessing import Pool, cpu_count
from copy import deepcopy
from tqdm import tqdm

from raid_cb_simulator.characters import (
    DEMYTHA,
    DONNIE,
    DPS_1,
    DEMON_LORD_UNM,
    DPS_2,
    DPS_3,
    DONNIE_MINE,
)
from raid_cb_simulator.simulator import DEMON_LORD_TURN_LIMIT, simulate


def generate_character_configs(base_character, speed_range):
    """
    Generate all possible configs for a single character:
    - speeds in speed_range
    - priorities as permutations of ability indices
    - delays as binary lists (at least one 0)
    """
    num_abilities = len(base_character.abilities)

    # Priorities: first ability fixed at 1, rest are permutations of 2..N
    if num_abilities == 1:
        priorities = [(1,)]
    else:
        priorities = [(1,) + rest for rest in itertools.permutations(range(2, num_abilities + 1))]

    # Delays: first ability fixed at 0, rest are binary vectors
    if num_abilities == 1:
        delays = [(0,)]
    else:
        delays = [(0,) + rest for rest in itertools.product([0, 1], repeat=num_abilities - 1)]

    # Combine into configs
    for speed in range(*speed_range):
        for prio in priorities:
            for delay in delays:
                yield base_character.to_config(speed=speed, priorities=prio, delays=list(delay))


def simulate_wrapper(args):
    """Wrapper to run simulate() on one full team config."""
    characters, demon_lord = args
    simulated_characters = [deepcopy(c) for c in characters]
    turns = simulate(characters=simulated_characters, demon_lord=demon_lord)
    return turns, characters


def run_configuration(speed_range, base_characters, demon_lord, turn_limit):
    """
    Run exhaustive search across all possible configurations
    for a list of characters against a given boss.

    Args:
        speed_range (tuple[int, int]): Speed search space.
        base_characters (list[Character]): Characters to test.
        demon_lord (CharacterConfig): Boss configuration.
        turn_limit (int): Maximum turns before forced stop.
    """

    character_config_lists = [list(generate_character_configs(c, speed_range)) for c in base_characters]
    all_combinations = itertools.product(*character_config_lists)

    total = math.prod(len(cfgs) for cfgs in character_config_lists)
    with Pool(processes=cpu_count()) as pool:
        for turns, team in tqdm(
            pool.imap_unordered(
                simulate_wrapper,
                ((list(chars), demon_lord) for chars in all_combinations),
            ),
            total=total,
        ):
            if turns == turn_limit:
                print("\n!!! New Solution Found !!!")
                print(f"Turns: {turns}")
                for i, c in enumerate(team):
                    print(
                        f"\t{c.name}: speed={c.speed}, abilities={[a.ability.name for a in c.abilities]}, priorities={[a.priority for a in c.abilities]}, delays={[a.delay for a in c.abilities]}"
                    )
                print("==========================")


def run_variable_configs(speed_range, fixed_characters, variable_characters, demon_lord, turn_limit):
    """
    Run simulations varying only a subset of characters.

    Args:
        speed_range (tuple[int, int]): Speed search space.
        fixed_characters (list[CharacterConfig]): Characters locked to a specific setup.
        variable_characters (list[Character]): Characters to explore.
        demon_lord (CharacterConfig): Boss configuration.
        turn_limit (int): Maximum turns before forced stop.
    """

    # Generate config sets for all variable chars
    variable_config_lists = [list(generate_character_configs(c, speed_range)) for c in variable_characters]
    all_combinations = itertools.product(*variable_config_lists)

    with Pool(processes=cpu_count()) as pool:
        for turns, team in pool.imap_unordered(
            simulate_wrapper,
            ((fixed_characters + list(vars_), demon_lord) for vars_ in all_combinations),
        ):
            if turns == turn_limit:
                var_speeds = [f"{c.name}: {c.speed}" for c in team]
                print(f"Turns: {turns}, speeds: {var_speeds}")


def run_all():
    """Exhaustively explore all configs for Demytha + Donnie against UNM Demon Lord."""

    speed_range = (150, 300)
    run_configuration(
        speed_range,
        [
            DEMYTHA,
            DONNIE_MINE,
            # DPS_1,
            # DPS_2,
            # DPS_3
        ],
        DEMON_LORD_UNM,
        DEMON_LORD_TURN_LIMIT,
    )


def run_some():
    """Run simulations with some fixed configs and a subset of variable DPS characters."""

    speed_range = (250, 300)
    fixed = [
        DEMYTHA.to_config(speed=257, priorities=[1, 3, 2], delays=[0, 1, 0]),
        DONNIE_MINE.to_config(speed=188, priorities=[1, 3, 2], delays=[0, 0, 0]),
    ]

    run_variable_configs(
        speed_range,
        fixed,
        [DPS_1, DPS_2],
        DEMON_LORD_UNM,
        DEMON_LORD_TURN_LIMIT,
    )


def run_some_selections():
    """Explore multiple fixed Demytha/Donnie speed selections with DPS variations."""

    demytha_speeds = [254, 283]
    donnie_speeds = [184, 189]
    speed_range = [150, 200]

    fixed = []
    for demytha_speed in range(demytha_speeds[0], demytha_speeds[1] + 1):
        for donnie_speed in range(donnie_speeds[0], donnie_speeds[1] + 1):
            fixed.append(
                [
                    DEMYTHA.to_config(speed=demytha_speed, priorities=[1, 3, 2], delays=[0, 1, 0]),
                    DONNIE_MINE.to_config(speed=donnie_speed, priorities=[1, 3, 2], delays=[0, 0, 0]),
                ]
            )

    for fixed_selection in tqdm(fixed):
        run_variable_configs(
            (speed_range[0], speed_range[1] + 1),
            fixed_selection,
            [DPS_1, DPS_2, DPS_3],
            DEMON_LORD_UNM,
            DEMON_LORD_TURN_LIMIT,
        )


def run_some_selections_fast():
    """Run faster search by fixing DPS1/DPS2 in a narrow speed range and only varying DPS3."""

    dps_speed_range = [264, 274]
    speed_range = [0, 400]

    fixed = []
    for dps_1_speed in range(dps_speed_range[0], dps_speed_range[1] + 1):
        for dps_2_speed in range(dps_speed_range[0], dps_speed_range[1] + 1):
            fixed.append(
                [
                    DEMYTHA.to_config(speed=257, priorities=[1, 3, 2], delays=[0, 1, 0]),
                    DONNIE_MINE.to_config(speed=188, priorities=[1, 3, 2], delays=[0, 0, 0]),
                    DPS_1.to_config(speed=dps_1_speed, priorities=[1]),
                    DPS_2.to_config(speed=dps_2_speed, priorities=[1]),
                ]
            )

    for fixed_selection in tqdm(fixed):
        run_variable_configs(
            (speed_range[0], speed_range[1] + 1),
            fixed_selection,
            [DPS_3],
            DEMON_LORD_UNM,
            DEMON_LORD_TURN_LIMIT,
        )


if __name__ == "__main__":
    run_some_selections_fast()
