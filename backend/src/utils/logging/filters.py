import logging

class WarningOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.WARNING
    
# Info or Debug Filter
class InfoDebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.INFO, logging.DEBUG)