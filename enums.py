from enum import Enum


class Arg(str, Enum):
    LOGS_DIR = 'logs-dir'
    OUTPUT = 'output-file'

class Col(str, Enum):
    PLAYER = 'PLAYER'
    HERO = 'HERO'
    ELIMS = 'ELIMS'
    FB = 'FB'
    DMG = 'DMG_DONE'
    DEATHS = 'DEATHS'
    HEALING = 'HEALING_DEALT'
    DMG_BLOCKED = 'DAMAGE_BLOCKED'


class LogCol(str, Enum):
    SECONDS = 'seconds'
    PLAYER = Col.PLAYER.value
    HERO = Col.HERO.value
    ELIMS = Col.ELIMS.value
    FB = Col.FB.value
    DMG = Col.DMG.value
    DEATHS = Col.DEATHS.value
    HEALING = Col.HEALING.value
    DMG_BLOCKED = Col.DMG_BLOCKED.value


class StatsCol(str, Enum):
    PLAYER = Col.PLAYER.value
    HERO = Col.HERO.value
    ELIMS = Col.ELIMS.value
    FB = Col.FB.value
    DMG = Col.DMG.value
    DEATHS = Col.DEATHS.value
    HEALING = Col.HEALING.value
    DMG_BLOCKED = Col.DMG_BLOCKED.value
    TIME = 'TIME_PLAYED'