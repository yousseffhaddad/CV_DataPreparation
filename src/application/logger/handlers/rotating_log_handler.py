import os
import re
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Union


class RotatingLogHandler(TimedRotatingFileHandler):
    """
    Handler for logging to a set of files, which switches from one file
    to the next when the current file reaches a certain size, or at certain
    timed intervals
    """

    def __init__(self, filename: Union[str, 'os.PathLike[str]'], maxBytes: int = 0, backupCount: int = 0,
                 encoding: str = None, delay: bool = False, when: str = 'h', interval: int = 1, utc: bool = False):
        TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
        self.maxBytes: int = maxBytes
        self.suffix: str = "%Y%m%dT%H%M%S"
        self.extMatch = r"^\d{4}\d{2}\d{2}T\d{2}\d{2}\d{2}(\.\w+)?$"
        self.extMatch = re.compile(self.extMatch, re.ASCII)

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.
        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """

        # Size based rotation condition
        if self.stream is None:  # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1

        # Time based rotation condition
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        """
        dir_name, base_name = os.path.split(self.baseFilename)
        file_names = os.listdir(dir_name)
        prefix = str(Path(base_name).with_suffix("")) + "."
        result = []
        file_names = [file_name for file_name in file_names if file_name.startswith(prefix)]
        file_names.sort()
        nb_files_to_delete = len(file_names) - self.backupCount
        if nb_files_to_delete > 0:
            result = [os.path.join(dir_name, file_name) for file_name in file_names[:nb_files_to_delete]]
        return result

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        log_suffix = str(Path(self.baseFilename).suffix)
        dfn = self.rotation_filename(
            str(Path(self.baseFilename).with_suffix("")) + "." + time.strftime(self.suffix, timeTuple) + log_suffix)
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
