import logging

def configure_logging(log_file_path='app.log'):
    # Create a custom logger
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file_path)
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger if they haven't been added yet
    if not logger.hasHandlers():
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger

# Configure logging when the module is imported
configure_logging()
