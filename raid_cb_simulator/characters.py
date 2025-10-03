from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from abilities import (
    Ability,
    STANDARD,
    HEIRESS_A2,
    SEEKER_A2,
    DEACON_A2,
    DEACON_A3,
    DEMYTHA_A2,
    DEMYTHA_A3,
    HIGH_KHATUN_A2,
    HIGH_KHATUN_A3,
    DOOMSCREECH_A2,
    DOOMSCREECH_A3,
    DEMON_LORD_A1,
    DEMON_LORD_A2,
    DEMON_LORD_A3,
    DONNIE_A2,
    DONNIE_A3,
    DONNIE_A3_MINE,
    MANEATER_A3,
    OTHORION_A1,
    OTHORION_A2,
    OTHORION_A3,
)


@dataclass(frozen=True)
class Character:
    name: str
    abilities: List[Ability]

    def to_config(self, speed: int, priorities: List[int], delays: Optional[List[int]] = None) -> CharacterConfig:
        if delays is None:
            delays = [0 for _ in range(len(self.abilities))]

        assert delays[0] == 0
        assert len(self.abilities) == len(priorities)
        assert len(self.abilities) == len(delays)

        return CharacterConfig(
            name=self.name,
            speed=speed,
            abilities=[AbilityConfig(a, p, d) for a, p, d in zip(self.abilities, priorities, delays)],
        )


@dataclass(frozen=True)
class AbilityConfig:
    ability: Ability
    priority: int
    delay: int = 0


# @dataclass(frozen=True)
@dataclass
class CharacterConfig:
    name: str
    speed: int
    abilities: List[AbilityConfig]


DEMON_LORD = Character(name="demon_lord", abilities=[DEMON_LORD_A1, DEMON_LORD_A2, DEMON_LORD_A3])
DEMON_LORD_NM = DEMON_LORD.to_config(speed=170, priorities=[1, 2, 3])
DEMON_LORD_UNM = DEMON_LORD.to_config(speed=190, priorities=[1, 2, 3])

HEIRESS = Character(name="heiress", abilities=[STANDARD, HEIRESS_A2])
SEEKER = Character(name="seeker", abilities=[STANDARD, SEEKER_A2])
DEACON = Character(name="deacon", abilities=[STANDARD, DEACON_A2, DEACON_A3])
DEMYTHA = Character(name="demytha", abilities=[STANDARD, DEMYTHA_A2, DEMYTHA_A3])
HIGH_KHATUN = Character(name="high_khatun", abilities=[STANDARD, HIGH_KHATUN_A2, HIGH_KHATUN_A3])
DOOMSCREECH = Character(name="doomscreech", abilities=[STANDARD, DOOMSCREECH_A2, DOOMSCREECH_A3])
DONNIE = Character(name="donnie", abilities=[STANDARD, DONNIE_A2, DONNIE_A3])
DONNIE_MINE = Character(name="donnie", abilities=[STANDARD, DONNIE_A2, DONNIE_A3_MINE])
MANEATER = Character(name="maneater", abilities=[STANDARD, MANEATER_A3])
OTHORION = Character(name="othorion", abilities=[OTHORION_A1, OTHORION_A2, OTHORION_A3])
DPS_1 = Character(name="dps_1", abilities=[STANDARD])
DPS_2 = Character(name="dps_2", abilities=[STANDARD])
DPS_3 = Character(name="dps_3", abilities=[STANDARD])
