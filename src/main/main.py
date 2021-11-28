# Global logging config. Do first to avoid accidently auto-configuring 
# root logger in an imported module.
import logging.config
import yaml

with open('resources/logging-config.yml') as f:
    logging_config_yaml = yaml.load(f, Loader=yaml.CLoader)

logging.config.dictConfig(logging_config_yaml)


# Now run the actual application
import checker.jmty as jmty_checker

logger = logging.getLogger(__name__)
listed_items = jmty_checker.run()
[logging.info(f"{item}") for item in listed_items]
