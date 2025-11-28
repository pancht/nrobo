def test_logger_level_change_is_isolated(caplog):
    import logging

    from nrobo.helpers.logging import get_logger, set_logger_level

    test_logger = get_logger("nrobo.test.temp_logger")
    original_level = test_logger.level

    try:
        set_logger_level(test_logger, stream_level=logging.DEBUG, file_level=logging.DEBUG)

        with caplog.at_level(logging.DEBUG, logger=test_logger.name):
            test_logger.debug("✅ debug visible")
        assert "✅ debug visible" in caplog.text

    finally:
        test_logger.setLevel(original_level)
