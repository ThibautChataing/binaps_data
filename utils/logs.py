import logging


def set_logger(file_name=None, log_level=logging.DEBUG):
    # create logger for prd_ci
    """
    Args:
        file_name: name for the file to log (full path and extension ex: output/run.log)
        :param log_level:
    """
    log = logging.getLogger()
    log.setLevel(level=log_level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(levelname)s] %(module)s in %(funcName)s at %(lineno)dl : %(message)s')

    if file_name:
        # create file handler for logger.
        fh = logging.FileHandler(file_name, mode='w')
        fh.setLevel(level=log_level)
        fh.setFormatter(formatter)
    # reate console handler for logger.
    ch = logging.StreamHandler()
    ch.setLevel(level=log_level)
    ch.setFormatter(formatter)

    # add handlers to logger.
    if file_name:
        log.addHandler(fh)

    log.addHandler(ch)

    return log


log = set_logger()


if __name__ == "__main__":
    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")