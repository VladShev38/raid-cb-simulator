from dataclasses import dataclass, field
from typing import List
from effects import Effect, Buff, Debuff, BuffType, BuffTarget


@dataclass(frozen=True)
class Ability:
    name: str
    cooldown: int
    effects: List[Effect] = field(default_factory=set)
    buffs: List[Buff] = field(default_factory=set)
    debuffs: List[Debuff] = field(default_factory=set)


DEMON_LORD_A1 = Ability(
    name="demon_lord_stun",
    cooldown=1,
    # debuffs={Debuff(DebuffType.STUN, duration=1)}
)
DEMON_LORD_A2 = Ability(name="demon_lord_aoe_1", cooldown=3)
DEMON_LORD_A3 = Ability(name="demon_lord_aoe_2", cooldown=3)
STANDARD = Ability(name="a1", cooldown=1)
HEIRESS_A2 = Ability(
    name="heiress_a2",
    cooldown=3,
    effects=[Effect.DECREASE_DEBUFF_DURATION],
    buffs=[Buff(buff_type=BuffType.INCREASE_SPEED_30, duration=2)],
)
SEEKER_A2 = Ability(
    name="seeker_a2",
    cooldown=3,
    effects=[Effect.TURN_METER_BOOST_30, Effect.EXTRA_TURN_SELF],
)
DEACON_A2 = Ability(name="deacon_a2", cooldown=3)
DEACON_A3 = Ability(
    name="deacon_a3",
    cooldown=3,
    effects=[Effect.TURN_METER_BOOST_15, Effect.EXTRA_TURN_SELF],
)
DEMYTHA_A2 = Ability(
    name="demytha_a2",
    cooldown=3,
    effects=[Effect.INCREASE_BUFF_DURATION, Effect.DECREASE_DEBUFF_DURATION],
)
DEMYTHA_A3 = Ability(
    name="demytha_a3",
    cooldown=3,
    buffs=[Buff(buff_type=BuffType.BLOCK_DAMAGE, duration=1)],
)
HIGH_KHATUN_A2 = Ability(
    name="high_khatun_a2",
    cooldown=3,
    effects=[Effect.TURN_METER_BOOST_15],
    buffs=[Buff(buff_type=BuffType.INCREASE_SPEED_30, duration=2)],
)
HIGH_KHATUN_A3 = Ability(name="high_khatun_a3", cooldown=4)
DOOMSCREECH_A2 = Ability(
    name="doomscreech_a2",
    cooldown=3,
    effects=[Effect.TURN_METER_BOOST_30],
)
DOOMSCREECH_A3 = Ability(name="doomscreech_a3", cooldown=5)
DONNIE_A2 = Ability(
    name="donnie_a2",
    cooldown=4,
    effects=[Effect.REDUCE_COOLDOWN_2_TURNS],
    buffs=[Buff(buff_type=BuffType.INCREASE_SPEED_30, duration=2)],
)
DONNIE_A3 = Ability(
    name="donnie_a3",
    cooldown=3,
    effects=[Effect.REMOVE_ALL_DEBUFFS, Effect.TURN_METER_BOOST_20],
)
DONNIE_A3_MINE = Ability(
    name="donnie_a3_mine",
    cooldown=4,
    effects=[Effect.REMOVE_ALL_DEBUFFS, Effect.TURN_METER_BOOST_20],
)
MANEATER_A3 = Ability(
    name="maneater_a3",
    cooldown=5,
    buffs=[Buff(buff_type=BuffType.BLOCK_DAMAGE, duration=2)],
)
OTHORION_A1 = Ability(
    name="othorion_a1",
    cooldown=1,
    effects=[Effect.TURN_METER_BOOST_5_SELF],
)
OTHORION_A2 = Ability(
    name="othorion_a2",
    cooldown=3,
    effects=[Effect.TURN_METER_BOOST_5_SELF],
)
OTHORION_A3 = Ability(
    name="othorion_a3",
    cooldown=4,
    effects=[Effect.EXTRA_TURN_SELF],
    buffs=[Buff(buff_type=BuffType.INCREASE_SPEED_30, duration=3, target=BuffTarget.SELF)],
)
