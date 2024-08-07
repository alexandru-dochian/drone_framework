import logging
import time
from abc import ABC, abstractmethod

import numpy as np

from maf import field_modulation, logger_config
from maf.core import (
    Config,
    Communicator,
    ProcessInitConfig,
    State,
    Position,
    SpaceLimit,
    FieldModulationEnvironmentState,
)
from maf.communicator import get_communicator

logger: logging.Logger = logger_config.get_logger(__name__)


class Environment(ABC):
    config: Config
    state: State
    communicator: Communicator

    def __init__(self, config: Config, state: State, communicator: Communicator):
        self.config = config
        self.state = state
        self.communicator = communicator

    @abstractmethod
    def run(self): ...


"""
###############################################################################
######## FieldModulationEnvironment ###########################################
###############################################################################
"""


class FieldModulationEnvironmentConfig(Config):
    delay: int = 100  # ms
    space_limit: SpaceLimit
    modulations: list[Position] = []
    rotation_center: Position
    theta: float = 5  # degrees


class FieldModulationEnvironment(Environment):
    config: FieldModulationEnvironmentConfig
    state: FieldModulationEnvironmentState
    communicator: Communicator

    def __init__(self, config: dict, communicator: dict):
        config: FieldModulationEnvironmentConfig = FieldModulationEnvironmentConfig(
            **config
        )
        state: FieldModulationEnvironmentState = FieldModulationEnvironmentState(
            modulations=np.array(
                list(map(lambda position: position.to_numpy_2d(), config.modulations))
            ),
            space_limit=config.space_limit,
        )
        super().__init__(
            config,
            state,
            get_communicator(communicator),
        )

    def run(self):
        while self.communicator.is_active():
            self.update_state()
            self.communicator.broadcast_environment_state(self.state)

            delay_seconds = self.config.delay / 1000
            time.sleep(delay_seconds)

    def update_state(self):
        self.state.modulations = field_modulation.rotate_points(
            self.state.modulations,
            self.config.rotation_center.to_numpy_2d(),
            self.config.theta,
        )


"""
###############################################################################
######## HelloWorldEnvironment ################################################
###############################################################################
"""


class HelloWorldEnvironmentConfig(Config):
    delay: int = 1000  # ms
    initial_state: int = 0


class HelloWorldEnvironment(Environment):
    config: HelloWorldEnvironmentConfig

    state: int
    communicator: Communicator

    def __init__(self, config: dict, communicator: dict):
        config: HelloWorldEnvironmentConfig = HelloWorldEnvironmentConfig(**config)
        super().__init__(
            config=config,
            state=config.initial_state,
            communicator=get_communicator(communicator),
        )

    def run(self):
        while self.communicator.is_active():
            updated_info: str = ""
            for agent in self.communicator.fetch_registered_agents():
                updated_info += self.communicator.fetch_agent_state(agent)

            updated_info = f"[{updated_info}] | [{self.__class__.__name__} says hello {self.state}]"
            self.communicator.broadcast_environment_state(updated_info)

            delay_seconds = self.config.delay / 1000
            time.sleep(delay_seconds)
            self.state += 1


def spawn_environment(
    init_config: ProcessInitConfig,
):
    """
    This method is the entrypoint for the environment process
    """
    logger.debug(f"Spawn {init_config.class_name} environment {init_config.worker}!")
    environment_class: type[Environment] = globals()[init_config.class_name]
    assert issubclass(
        environment_class, Environment
    ), f"Environment [{init_config.class_name}] was not found"
    environment: Environment = environment_class(**init_config.params)
    environment.run()
    logger.debug(f"Finished {init_config.class_name} environment!")
