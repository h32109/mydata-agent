from enum import Enum


class StrEnum(str, Enum):
    ...


class Environment(StrEnum):
    PROD = "production"
    DEV = "development"


class Device(StrEnum):
    GPU = "gpu"
    CPU = "cpu"


class SearchType(StrEnum):
    SIMILARITY = "similarity"
    MMR = "mmr"


class ChainType(StrEnum):
    STUFF = "stuff"
    MAP_REDUCE = "map_reduce"
    REFINE = "refine"


class FileExtension(StrEnum):
    PDF = ".pdf"
