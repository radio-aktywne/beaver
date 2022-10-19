import logging
from typing import Optional, TextIO, Iterable

from omegaconf import OmegaConf

from emishows import resource_text
from emishows.config.models import Config

logger = logging.getLogger(__name__)


class ConfigLoader:
    config: Config = None

    @staticmethod
    def load(
        f: Optional[TextIO] = None, overrides: Optional[Iterable[str]] = None
    ) -> Config:
        config = OmegaConf.create(resource_text("config.yaml"))
        if f is not None:
            config = OmegaConf.merge(config, OmegaConf.load(f))
        if overrides is not None:
            config = OmegaConf.merge(
                config, OmegaConf.from_dotlist(list(overrides))
            )
        config = OmegaConf.to_container(config, resolve=True)
        ConfigLoader.config = Config.parse_obj(config)
        return ConfigLoader.config

    @staticmethod
    def get() -> Config:
        if ConfigLoader.config is None:
            logger.warning("Config not loaded, loading with default values...")
            return ConfigLoader.load()
        return ConfigLoader.config
