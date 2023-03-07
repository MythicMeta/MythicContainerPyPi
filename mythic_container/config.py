import os

from dynaconf import Dynaconf

settings = Dynaconf(
    GLOBAL_ENV_FOR_DYNACONF=False,
    settings_files=['rabbitmq_config.json'],
)

# `envvar_prefix` = export envvars with `export MYTHIC_FOO=bar`.
# `settings_files` = Load this files in the order.
