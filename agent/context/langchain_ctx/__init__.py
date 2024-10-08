import logging


def get_logger():
    logger = logging.getLogger("langchain")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = get_logger()

from .ctx import (
    EmbeddingModelLiteral,
    LLMModelLiteral,
    LoaderLiteral,
    SplitterLiteral,
    RetrieverLiteral,
    LangchainParameterBase
)

from .plugins import *
