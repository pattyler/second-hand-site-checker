# Global logging config. Do first to avoid accidentally auto-configuring
# root logger in an imported module.
import logging.config
import yaml

with open('resources/logging-config.yml') as f:
    logging_config_yaml = yaml.load(f, Loader=yaml.CLoader)

logging.config.dictConfig(logging_config_yaml)


# Now run the actual application
import checker
import utils

logger = logging.getLogger(__name__)

jmty_checkers = [
    checker.Jmty("road bike"),
    checker.Jmty("gravel bike")
]

listed_items = utils.flatten([jmty_checker.check() for jmty_checker in jmty_checkers])
filtered_items = set(listed_items) # remove duplicates if present
[logging.info(f"{item}") for item in filtered_items]