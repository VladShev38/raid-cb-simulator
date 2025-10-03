import itertools
import uuid
from copy import deepcopy
from typing import List

from tqdm import tqdm

from characters import (
    CharacterConfig,
    DEMYTHA,
    HEIRESS,
    DOOMSCREECH,
    DEACON,
    DPS_1,
    DEMON_LORD,
    DEMON_LORD_UNM,
    DONNIE,
    DPS_2,
    DPS_3,
    DEMON_LORD_NM,
    DONNIE_MINE,
)
from effects import BuffType, DebuffType, Buff, Debuff, Effect, BuffTarget
from raid_cb_simulator.abilities import DEMON_LORD_A1

# Source: https://www.reddit.com/r/RaidShadowLegends/comments/15ktu28/how_does_turn_meter_works/
TURN_METER_TICK_MULTIPLIER = 0.07

DEMON_LORD_TURN_LIMIT = 50


class CharacterState:
    def __init__(self, character_config: CharacterConfig):
        self.character_config = character_config
        self.id = str(uuid.uuid4())[:7]
        self.ability_cooldowns: List[int] = [0 for _ in character_config.abilities]
        self.ability_delays: List[int] = [ability.delay for ability in character_config.abilities]
        self.turn_meter: float = 0
        self.buffs: List[Buff] = []
        self.debuffs: List[Debuff] = []
        self.donnies_passive_cooldown = 0

    @property
    def is_demon_lord(self) -> bool:
        return self.character_config.name == DEMON_LORD.name

    @property
    def uid(self) -> str:
        return f"{self.character_config.name}-{self.id}"

    def remove_expired_buffs_and_debuffs(self):
        self.buffs = [b for b in self.buffs if b.duration > 0]
        self.debuffs = [d for d in self.debuffs if d.duration > 0]


def simulate(characters: List[CharacterConfig], demon_lord: CharacterConfig, debug: bool = False):
    entities = {}
    for character in characters:
        entity = CharacterState(character)
        entities[entity.uid] = entity

    demon_lord_entity = CharacterState(demon_lord)
    entities[demon_lord_entity.uid] = demon_lord_entity

    demon_lord_turns = 0
    while demon_lord_turns < DEMON_LORD_TURN_LIMIT - 1:
        entity_max_turn_meter = 0
        entity_to_move = None
        for entity_name, entity in entities.items():
            if entity.turn_meter >= 100 and entity.turn_meter > entity_max_turn_meter:
                # Only replace entity if it has more turn meter than the previous; this
                # ensures that in cases of speed ties:
                # - Between 2 champions: the champion higher in the team order gets chosen
                # - Between champion and demon lord: champion gets chosen
                entity_max_turn_meter = entity.turn_meter
                entity_to_move = entity

        extra_turn = False

        if entity_to_move is not None:
            # Reset turn meter
            entity_to_move.turn_meter = 0

            # Decrease cooldowns
            for i in range(len(entity_to_move.ability_cooldowns)):
                entity_to_move.ability_cooldowns[i] = max(0, entity_to_move.ability_cooldowns[i] - 1)
            entity_to_move.donnies_passive_cooldown = max(0, entity_to_move.donnies_passive_cooldown - 1)

            # Choose ability
            chosen_ability_config = None
            chosen_ability_priority = 0
            chosen_ability_index = -1
            for i, ability in enumerate(entity_to_move.character_config.abilities):
                if (
                    entity_to_move.ability_cooldowns[i] == 0
                    and entity_to_move.ability_delays[i] == 0
                    and ability.priority > chosen_ability_priority
                ):
                    chosen_ability_config = ability
                    chosen_ability_priority = ability.priority
                    chosen_ability_index = i

            # Reset cooldown
            entity_to_move.ability_cooldowns[chosen_ability_index] = entity_to_move.character_config.abilities[
                chosen_ability_index
            ].ability.cooldown

            # Decrease delays
            for i in range(len(entity_to_move.ability_delays)):
                entity_to_move.ability_delays[i] = max(0, entity_to_move.ability_delays[i] - 1)

            # Use ability: instant effects
            for effect in chosen_ability_config.ability.effects:
                character_entities = [e for e in entities.values() if not e.is_demon_lord]
                demon_lord_entities = [demon_lord_entity]
                if entity_to_move.is_demon_lord:
                    friendly_entities = demon_lord_entities
                    enemy_entities = character_entities
                else:
                    friendly_entities = character_entities
                    enemy_entities = demon_lord_entities

                if effect == Effect.INCREASE_BUFF_DURATION:
                    for friendly_entity in friendly_entities:
                        for friendly_entity_buff in friendly_entity.buffs:
                            friendly_entity_buff.duration += 1
                        friendly_entity.remove_expired_buffs_and_debuffs()
                elif effect == Effect.DECREASE_DEBUFF_DURATION:
                    for friendly_entity in friendly_entities:
                        for friendly_entity_debuff in friendly_entity.debuffs:
                            friendly_entity_debuff.duration -= 1
                        friendly_entity.remove_expired_buffs_and_debuffs()
                elif effect == Effect.REMOVE_1_DEBUFF:
                    for friendly_entity in friendly_entities:
                        if len(friendly_entity.debuffs) > 1:
                            raise ValueError("Friendly entity had more than one debuff")
                        friendly_entity.debuffs = []
                elif effect == Effect.REMOVE_ALL_DEBUFFS:
                    for friendly_entity in friendly_entities:
                        friendly_entity.debuffs = []
                elif effect == Effect.TURN_METER_BOOST_5_SELF:
                    entity_to_move.turn_meter += 5
                elif effect == Effect.TURN_METER_BOOST_10_SELF:
                    entity_to_move.turn_meter += 10
                elif effect == Effect.TURN_METER_BOOST_15:
                    for friendly_entity in friendly_entities:
                        friendly_entity.turn_meter += 15
                elif effect == Effect.TURN_METER_BOOST_20:
                    for friendly_entity in friendly_entities:
                        friendly_entity.turn_meter += 20
                elif effect == Effect.TURN_METER_BOOST_30:
                    for friendly_entity in friendly_entities:
                        friendly_entity.turn_meter += 30
                elif effect == Effect.EXTRA_TURN_SELF:
                    entity_to_move.turn_meter = 1e6
                    extra_turn = True
                elif effect == Effect.REDUCE_COOLDOWN_2_TURNS:
                    for friendly_entity in friendly_entities:
                        if entity_to_move != friendly_entity:
                            for i in range(len(friendly_entity.ability_cooldowns)):
                                friendly_entity.ability_cooldowns[i] = max(0, friendly_entity.ability_cooldowns[i] - 2)
                else:
                    raise TypeError(f"Unknown effect {effect}")

            # Decrease buff duration
            for buff in entity_to_move.buffs:
                buff.duration -= 1

            # Decrease debuff duration
            for debuff in entity_to_move.debuffs:
                debuff.duration -= 1

            # Remove expired buffs and debuffs
            entity_to_move.remove_expired_buffs_and_debuffs()

            # Use ability: distribute buffs
            for buff in chosen_ability_config.ability.buffs:
                if entity_to_move.is_demon_lord:
                    target_entities = [entity_to_move]
                else:
                    if buff.target == BuffTarget.ALL:
                        target_entities = [e for e in entities.values() if not e.is_demon_lord]
                    elif buff.target == BuffTarget.SELF:
                        target_entities = [entity_to_move]
                        raise NotImplementedError
                    else:
                        raise ValueError

                for target_entity in target_entities:
                    for existing_buff in target_entity.buffs:
                        if buff.buff_type == existing_buff.buff_type:
                            existing_buff.duration = max(buff.duration, existing_buff.duration)
                            break
                    else:
                        target_entity.buffs.append(deepcopy(buff))

            # Use ability: distribute debuffs
            for debuff in chosen_ability_config.ability.debuffs:
                if entity_to_move.is_demon_lord:
                    target_entities = [e for e in entities.values() if not e.is_demon_lord]
                else:
                    target_entities = [entity_to_move]

                for target_entity in target_entities:
                    for existing_debuff in target_entity.debuffs:
                        if debuff.debuff_type == existing_debuff.debuff_type:
                            existing_debuff.duration = max(debuff.duration, existing_debuff.duration)
                            break
                    else:
                        target_entity.debuffs.append(deepcopy(debuff))

            if entity_to_move.is_demon_lord:
                demon_lord_turns += 1

            if debug:
                event_name = "[CB turn]" if entity_to_move.is_demon_lord else "[champ turn]"
                print(
                    f"{event_name} character: {entity_to_move.uid}, ability: {chosen_ability_config.ability.name}, active buffs: {entity_to_move.buffs}, active debuffs: {entity_to_move.debuffs}"
                )

            # Check if failed
            if entity_to_move.is_demon_lord:
                failed = False

                everyone_has_block_damage = True
                for character in entities.values():
                    if character.is_demon_lord:
                        continue
                    character_has_block_damage = False
                    for character_buff in character.buffs:
                        if character_buff.buff_type == BuffType.BLOCK_DAMAGE:
                            character_has_block_damage = True
                            break
                    if not character_has_block_damage:
                        everyone_has_block_damage = False
                        break

                if not everyone_has_block_damage:
                    if chosen_ability_config.ability.name == DEMON_LORD_A1.name:
                        donnie = None
                        for character in entities.values():
                            if character.character_config.name == DONNIE.name:
                                donnie = character

                        if donnie is not None:
                            if donnie.donnies_passive_cooldown == 0:
                                donnie.donnies_passive_cooldown = 4
                            else:
                                failed = True
                        else:
                            failed = True
                    else:
                        failed = True

                if failed:
                    return demon_lord_turns + 1

        if not extra_turn:
            for entity in entities.values():
                current_speed = entity.character_config.speed
                for buff in entity.buffs:
                    if buff.buff_type == BuffType.INCREASE_SPEED_30:
                        current_speed *= 1.3
                for debuff in entity.debuffs:
                    if debuff.debuff_type == DebuffType.DECREASE_SPEED_15:
                        current_speed *= 0.85
                entity.turn_meter += current_speed * TURN_METER_TICK_MULTIPLIER

        if debug:
            print("\n[tick]")
            for e in entities.values():
                print(f"\tcharacter: {e.uid}, turn meter: {e.turn_meter}, ability cooldowns: {e.ability_cooldowns}")

    return demon_lord_turns + 1


def test():
    turns = simulate(
        # MythHeirAlternate
        # characters=[
        #     DEMYTHA.to_config(speed=348, priorities=[1, 2, 3], delays=[0, 1, 1]),
        #     HEIRESS.to_config(speed=283, priorities=[1, 2], delays=[0, 1]),
        #     DOOMSCREECH.to_config(speed=281, priorities=[1, 3, 2], delays=[0, 2, 1]),
        #     DEACON.to_config(speed=198, priorities=[1, 2, 3], delays=[0, 0, 0]),
        #     DPS.to_config(speed=180, priorities=[1]),
        # ],

        # # Spreadsheet
        # characters=[
        #     DEMYTHA.to_config(speed=219, priorities=[1, 2, 3], delays=[0, 0, 0]),
        #     DONNIE.to_config(speed=224, priorities=[1, 3, 2], delays=[0, 1, 1]),
        #     DPS.to_config(speed=220, priorities=[1]),
        # ],

        # Solution 1?
        # characters=[
        #     DEMYTHA.to_config(speed=254, priorities=[1, 3, 2], delays=[0, 1, 0]),
        #     DONNIE.to_config(speed=188, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DPS_1.to_config(speed=189, priorities=[1]),  # working speeds: 176-178, 277-285
        #     DPS_2.to_config(speed=187, priorities=[1]),  # working speeds: 176-178, 277-285
        #     DPS_3.to_config(speed=180, priorities=[1]),  # working speeds: 176-178, 277-285
        # ],

        # # In-game test 1
        # characters=[
        #     DEMYTHA.to_config(speed=257, priorities=[1, 3, 2], delays=[0, 1, 0]),
        #     DONNIE_MINE.to_config(speed=188, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DPS_1.to_config(speed=181, priorities=[1]),  # akemtum
        #     DPS_2.to_config(speed=184, priorities=[1]),  # mikey
        #     DPS_3.to_config(speed=189, priorities=[1]),  # anax
        # ],

        # In-game test 2
        # characters=[
        #     DONNIE_MINE.to_config(speed=188, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DEMYTHA.to_config(speed=257, priorities=[1, 3, 2], delays=[0, 1, 0]),
        #     DPS_1.to_config(speed=183, priorities=[1]),  # mikey
        #     DPS_2.to_config(speed=185, priorities=[1]),  # akemtum
        #     DPS_3.to_config(speed=189, priorities=[1]),  # anax
        # ],

        # In-game test 3
        # characters=[
        #     # DONNIE_MINE.to_config(speed=188-0.0888+1, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DONNIE_MINE.to_config(speed=188.8, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DEMYTHA.to_config(speed=257, priorities=[1, 3, 2], delays=[0, 1, 0]),
        #     DPS_1.to_config(speed=189, priorities=[1]),  # akemtum
        #     DPS_2.to_config(speed=184, priorities=[1]),  # mikey
        #     # DPS_3.to_config(speed=181, priorities=[1]),  # anax
        #     # DPS_3.to_config(speed=181.35, priorities=[1]),  # anax
        #     DPS_3.to_config(speed=180.52+1, priorities=[1]),  # sanguinia
        # ],

        # # Ikuyo Kita
        # characters=[
        #     DONNIE.to_config(speed=98 * 1.12 + 78, priorities=[1, 3, 2], delays=[0, 0, 0]),
        #     DEMYTHA.to_config(speed=102 * (1 + (0.12 * 1.15)) + 138, priorities=[1, 3, 2], delays=[0, 1, 0]),
        #     DPS_1.to_config(speed=99 * (1 + (0.05 * 1.15)) + 84, priorities=[1]),  # mikey - LoS
        #     DPS_2.to_config(speed=99 * (1 + (0.12 * 1.15)) + 67, priorities=[1]),  # alice - LoS
        #     DPS_3.to_config(speed=95 * (1 + (0.1 * 1.15)) + 80, priorities=[1]),  # orn - LoS
        # ],

        # Ikuyo Kita - testing
        characters=[
            DONNIE.to_config(speed=98 * 1.12 + 78 + 1, priorities=[1, 3, 2], delays=[0, 0, 0]),
            DEMYTHA.to_config(speed=102 * (1 + (0.12 * 1.15)) + 138, priorities=[1, 3, 2], delays=[0, 1, 0]),
            DPS_1.to_config(speed=99 * (1 + (0.05 * 1.15)) + 84 + 1, priorities=[1]),  # mikey - LoS
            DPS_2.to_config(speed=99 * (1 + (0.12 * 1.15)) + 67, priorities=[1]),  # alice - LoS
            DPS_3.to_config(speed=95 * (1 + (0.1 * 1.15)) + 80, priorities=[1]),  # orn - LoS
        ],
        demon_lord=DEMON_LORD_UNM,
        debug=True,
    )
    if turns == DEMON_LORD_TURN_LIMIT:
        print("Run successful")
    else:
        print(f"Run failed at demon lord turn {turns}")


def run_configuration(speed_ranges, characters):
    speeds = range(*speed_ranges)
    total_size = len(speeds) ** len(characters)
    max_turns = 0

    for speeds in tqdm(itertools.product(speeds, repeat=len(characters)), total=total_size):
        simulated_characters = [deepcopy(c) for c in characters]
        assert len(simulated_characters) == len(speeds)
        for i in range(len(speeds)):
            simulated_characters[i].speed = speeds[i]

        turns = simulate(
            characters=simulated_characters,
            demon_lord=DEMON_LORD_UNM,
        )
        if turns > max_turns:
            max_turns = turns
            print(f"New high found: {max_turns}, at {speeds=}")
        if turns == DEMON_LORD_TURN_LIMIT:
            print(f"fNew solution found at {speeds=}")


def run():
    speed_ranges = [150, 400, 3]

    print("\n\nHeiress run")
    run_configuration(
        speed_ranges,
        [
            DEMYTHA.to_config(speed=0, priorities=[1, 2, 3], delays=[0, 0, 0]),
            DONNIE.to_config(speed=0, priorities=[1, 3, 2], delays=[0, 1, 1]),
            DPS_1.to_config(speed=0, priorities=[1]),
            HEIRESS.to_config(speed=0, priorities=[1, 2], delays=[0, 1]),
        ],
    )

    print("\n\nDoomscreech run")
    run_configuration(
        speed_ranges,
        [
            DEMYTHA.to_config(speed=0, priorities=[1, 2, 3], delays=[0, 0, 0]),
            DONNIE.to_config(speed=0, priorities=[1, 3, 2], delays=[0, 1, 1]),
            DPS_1.to_config(speed=0, priorities=[1]),
            DOOMSCREECH.to_config(speed=0, priorities=[1, 3, 2], delays=[0, 2, 1]),
        ],
    )


if __name__ == "__main__":
    test()
