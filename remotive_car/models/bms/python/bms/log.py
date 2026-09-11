import logging

import structlog


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(asctime)s.%(msecs)03d %(name)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    logging.getLogger("remotivelabs.topology").setLevel(logging.ERROR)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%H:%M:%S.%f", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
