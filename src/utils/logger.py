import coloredlogs, logging

# Create a logger object.
customLogger = logging.getLogger(__name__)
level = 'INFO'


coloredlogs.install(level=level, logger=customLogger)
