from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Cluster:
    ilvl: int
    passives: int
    jewel_type: str
    jewel_base: str
    mods: list[str]
