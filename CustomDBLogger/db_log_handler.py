# CustomDBLogger/db_log_handler.py

import logging

db_default_formatter = logging.Formatter()

DJANGO_DB_LOGGER_ENABLE_FORMATTER = False
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from .models import StatusLog

        trace = None

        if record.exc_info:
            trace = db_default_formatter.formatException(record.exc_info)

        if DJANGO_DB_LOGGER_ENABLE_FORMATTER:
            msg = self.format(record)
        else:
            msg = record.getMessage()

        if hasattr(record, 'custom_category'):
            custom_category = record.custom_category
        else:
            custom_category = None

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'trace': trace,
            'custom_category': custom_category
        }

        StatusLog.objects.create(**kwargs)

    def format(self, record):
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = db_default_formatter

        if type(fmt) == logging.Formatter:
            record.message = record.getMessage()

            if fmt.usesTime():
                record.asctime = fmt.formatTime(record, fmt.datefmt)

            # ignore exception traceback and stack info

            return fmt.formatMessage(record)
        else:
            return fmt.format(record)
