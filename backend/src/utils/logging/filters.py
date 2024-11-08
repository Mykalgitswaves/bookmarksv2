import logging

class WarningOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.WARNING
    
# Info Filter
class InfoOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO