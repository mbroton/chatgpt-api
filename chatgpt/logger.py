import logging
import time

from chatgpt import config


def _get_logger() -> logging.Logger:
    class __IOFormatter(logging.Formatter):
        """Used to specify custom logging keys."""

        def format(self, record):
            record.timestamp = record.args.get("timestamp")
            record.input = record.args.get("input")
            record.output = record.args.get("output")
            record.id = record.args.get("id")
            record.conversation_id = record.args.get("conversation_id")
            record.parent_message_id = record.args.get("parent_message_id")
            return super().format(record)

    logger = logging.getLogger("ChatGPT")
    io_json_formatter = __IOFormatter(
        '{"timestamp":"%(timestamp)s",\
            "input": "%(input)s", "output": "%(output)s",\
            "id": "%(id)s", "conversation_id": "%(conversation_id)s",\
            "parent_message_id": "%(parent_message_id)s"}'
    )
    time_tuple = time.localtime(time.time())
    time_string = time.strftime("%H:%M:%S", time_tuple)
    if not config.LOGGING_DIR.exists():
        config.LOGGING_DIR.mkdir(parents=True, exist_ok=True)
    logging_path = config.LOGGING_DIR / f"chatgpt_logs_{time_string}.log"
    file_handler = logging.FileHandler(filename=str(logging_path), mode="w")
    file_handler.setFormatter(io_json_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(level=logging.DEBUG)
    return logger
