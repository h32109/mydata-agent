from enum import Enum


class Environment(str, Enum):
    PROD = "production"
    DEV = "development"


class Device(str, Enum):
    GPU = "gpu"
    CPU = "cpu"


class SearchType(str, Enum):
    SIMILARITY = "similarity"
    MMR = "mmr"


class ChainType(str, Enum):
    STUFF = "stuff"
    MAP_REDUCE = "map_reduce"
    REFINE = "refine"


class RetrieverType(str, Enum):
    DEFAULT = "default"
    MULTI_QUERY = "multi_query"


class FileExtension(str, Enum):
    PDF = ".pdf"


class HuggingFaceModel(str, Enum):
    KO_SBERT_MULTITASK = "jhgan/ko-sbert-multitask"
    KF_DEBERT_MULTITASK = "upskyy/kf-deberta-multitask"
    BGE_M3 = "BAAI/bge-m3"
