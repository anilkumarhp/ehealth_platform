# src/lab_management/core/logging_config.py

import logging
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON log formatter to add specific fields to the log record.
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['name'] = record.name
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created

def setup_logging():
    """
    Configures structured JSON logging for the entire application.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a handler to output logs to the console (stdout)
    log_handler = logging.StreamHandler(sys.stdout)

    # Use our custom JSON formatter
    # Example format: %(timestamp)s %(level)s %(name)s %(message)s
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    logging.info("Structured JSON logging configured.")