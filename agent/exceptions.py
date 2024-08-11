import enum
import fastapi as fa


class AgentExceptionErrorCode(str, enum.Enum):
    # common
    CPUUsageHighError = "CO00"

    # langchain
    ModelNotFoundError = "HF00"
    DataFileNotFoundError = "HF01"
    SplitterParameterError = "HF02"


class BaseAgentException(Exception):
    code_class = AgentExceptionErrorCode

    @property
    def message(self):
        return self.args[0]

    @property
    def info(self):
        try:
            info = self.args[1]
        except IndexError:
            return {}
        return info

    @property
    def error_code(self):
        return self.code_class[self.__class__.__name__]

    def __str__(self):
        return f"error_code: {self.error_code.value}, message: {self.message}"

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.error_code.value}>"

    def raise_http(self, status_code: int):
        return fa.HTTPException(
            status_code=status_code,
            detail={
                "message": self.message,
                "error_code": self.error_code.value,
                "info": self.info
            }
        )


class CPUUsageHighError(BaseAgentException):
    """Occurred error due to high usage of CPU."""


class ModelNotFoundError(BaseAgentException):
    """Model not founded from hugging-face."""


class DataFileNotFoundError(BaseAgentException):
    """Data files not founded when data is loaded."""


class SplitterParameterError(BaseAgentException):
    """The splitter parameter value is not appropriate."""
