from dataclasses import dataclass
from enum import Enum, auto


class Effect(Enum):
    INCREASE_BUFF_DURATION = auto()
    DECREASE_DEBUFF_DURATION = auto()
    REMOVE_1_DEBUFF = auto()
    REMOVE_ALL_DEBUFFS = auto()
    TURN_METER_BOOST_5_SELF = auto()
    TURN_METER_BOOST_10_SELF = auto()
    TURN_METER_BOOST_15 = auto()
    TURN_METER_BOOST_20 = auto()
    TURN_METER_BOOST_30 = auto()
    EXTRA_TURN_SELF = auto()
    REDUCE_COOLDOWN_2_TURNS = auto()


class BuffType(Enum):
    INCREASE_SPEED_30 = auto()
    BLOCK_DAMAGE = auto()


class DebuffType(Enum):
    DECREASE_SPEED_15 = auto()
    # DECREASE_SPEED_30 = auto()
    # STUN = auto()


class BuffTarget(Enum):
    SELF = auto()
    ALL = auto()


# @dataclass(frozen=True)
@dataclass
class Buff:
    buff_type: BuffType
    duration: int
    target: BuffTarget = BuffTarget.ALL


# @dataclass(frozen=True)
@dataclass
class Debuff:
    debuff_type: DebuffType
    duration: int
