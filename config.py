import configparser, pytz

from exceptions import ConfigError
from util import DotDict

def read_config_file(config_file_name):
    """Reads the configuration file and returns it as dotdict."""

    config = configparser.RawConfigParser()
    config.read(config_file_name)

    # Convert to plain dictionary.
    d = {}
    for section in config:
        d[section] = {}
        for k in config[section]:
            d[section][k] = config[section][k]
    d = DotDict(d)

    sections = ["general", "completion"]
    for section in sections:
        if section not in d:
            d[section] = {}

    # Add defaults, validate, and perform some transformations.
    if "default_time_zone" not in d.general:
        d.general.default_time_zone = "UTC"
    try:
        pytz.timezone(d.general.default_time_zone)
    except pytz.exceptions.UnknownTimeZoneError as exc:
        raise ConfigError(f"Unknown default time zone {d.general.default_time_zone}.") from exc

    if "default_language" not in d.general:
        d.general.default_language = "en-US"

    if "debug" in d.general:
        d.general.debug = d.general.debug.lower() == "true"
    else:
        d.general.debug = False

    for k in ["author", "city", "country"]:
        if k in d.completion:
            d.completion[k] = d.completion[k].split(",")
        else:
            d.completion[k] = []

    return d

