import logging

from colorlog import ColoredFormatter

from nrobo.helpers.logging import get_logger, set_logger_level


def test_logger_level_change_is_isolated(caplog):

    test_logger = get_logger("nrobo.test.temp_logger")
    original_level = test_logger.level

    try:
        set_logger_level(test_logger, stream_level=logging.DEBUG, file_level=logging.DEBUG)

        with caplog.at_level(logging.DEBUG, logger=test_logger.name):
            test_logger.debug("✅ debug visible")
        assert "✅ debug visible" in caplog.text

    finally:
        test_logger.setLevel(original_level)


def test_get_logger_returns_configured_logger(caplog):
    logger_name = "test.logger"
    logger = get_logger(name=logger_name)

    assert isinstance(logger, logging.Logger), "Returned object should be a Logger"

    # Check at least one StreamHandler with a ColoredFormatter
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    assert stream_handlers, "Logger should have a StreamHandler"

    color_formatters = [
        h.formatter for h in stream_handlers if isinstance(h.formatter, ColoredFormatter)
    ]
    assert color_formatters, "StreamHandler should use ColoredFormatter"

    # Emit a log and capture it
    with caplog.at_level(logging.INFO, logger=logger_name):
        logger.info("🔥 Test log message")

    assert "🔥 Test log message" in caplog.text
