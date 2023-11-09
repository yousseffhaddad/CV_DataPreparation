from bisect import bisect
from logging import Formatter, LogRecord
from typing import Dict


class LoggingLevelFormatter(Formatter):
    # By default, there is no way to make a logger message format of certain level different from
    # the other levels format. This class overrides the default formatter to allow this behavior
    def __init__(self, formats: Dict[int, str]):
        super().__init__()
        self.formats = sorted((level, Formatter(fmt)) for level, fmt in formats.items())

    def format(self, record: LogRecord) -> str:
        idx = bisect(self.formats, (record.levelno,), hi=len(self.formats) - 1)
        level, formatter = self.formats[idx]
        return formatter.format(record)
