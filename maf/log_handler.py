import logging
import time

import numpy as np

from abc import ABC, abstractmethod

from maf.core import ProcessInitConfig, Config, PositionState, FieldState, Field
from maf.communicator import Communicator, get_communicator
from maf import persistence, logger_config

logger: logging.Logger = logger_config.get_logger(__name__)


class LogHandler(ABC):
    config: Config
    communicator: Communicator

    def __init__(self, config: Config, communicator: Communicator):
        self.config = config
        self.communicator = communicator

    @abstractmethod
    def run(self): ...


"""
###############################################################################
######## PositionLogger #######################################################
###############################################################################
"""


class PositionLoggerConfig(Config):
    experiment_dir: str
    delay: int = 500  # ms
    reset_zoom: bool = False


class PositionLogger(LogHandler):
    config: PositionLoggerConfig
    communicator: Communicator

    scene: object
    animator: object
    points: object

    def __init__(self, config: dict, communicator: dict) -> None:
        super().__init__(PositionLoggerConfig(**config), get_communicator(communicator))

    def run(self):
        # For some reason mayavi imports need to be at method level
        from mayavi import mlab
        from mayavi.core.scene import Scene
        from mayavi.tools.animator import Animator
        from mayavi.tools.helper_functions import Points3d

        @mlab.animate(delay=self.config.delay)
        def anim():
            try:
                persistence.clear(
                    self.config.experiment_dir,
                    self.__class__.__name__,
                )
                while self.communicator.is_active():
                    x_new = []
                    y_new = []
                    z_new = []
                    for agent in self.communicator.fetch_registered_agents():
                        state: PositionState = self.communicator.fetch_agent_state(
                            agent
                        )
                        if state is None or state.position is None:
                            continue

                        x_new.append(state.position.x)
                        y_new.append(state.position.y)
                        z_new.append(state.position.z)
                        self.write_to_disk(agent, state)

                    x_new = np.array(x_new)
                    y_new = np.array(y_new)
                    z_new = np.array(z_new)

                    self.points.mlab_source.reset(x=x_new, y=y_new, z=z_new)

                    if self.config.reset_zoom:
                        self.scene.scene.reset_zoom()
                    yield
            finally:
                mlab.clf()
                self.animator.close()
                mlab.close(all=True)

        self.scene: Scene = mlab.figure(
            self.__class__.__name__,
            bgcolor=(1, 1, 1),
            fgcolor=(0, 0, 0),
            size=(960, 540),
        )

        mlab.clf()
        mlab.view(0, 180, None, (0, 0, 0))

        x, y, z = np.random.random((3, 0))
        self.points: Points3d = mlab.points3d(
            x, y, z, scale_factor=0.1, color=(0, 1, 0)
        )

        # Function to draw the axes
        def draw_axes():
            # TODO: get from environment
            x_min_limit = -2.5
            x_max_limit = 1.5
            y_min_limit = -1.0
            y_max_limit = 2.0
            z_max_limit = 2.5

            mlab.plot3d(
                [0, x_max_limit], [0, 0], [0, 0], color=(1, 0, 0), tube_radius=0.01
            )  # X axis in red
            mlab.plot3d(
                [0, 0], [0, y_max_limit], [0, 0], color=(0, 1, 0), tube_radius=0.01
            )  # Y axis in green
            mlab.plot3d(
                [0, 0], [0, 0], [0, z_max_limit], color=(0, 0, 1), tube_radius=0.01
            )  # Z axis in blue
            mlab.plot3d(
                [x_min_limit, 0], [0, 0], [0, 0], color=(1, 0, 0), tube_radius=0.01
            )  # Negative X axis in red
            mlab.plot3d(
                [0, 0], [y_min_limit, 0], [0, 0], color=(0, 1, 0), tube_radius=0.01
            )  # Negative Y axis in green

        def draw_xy_grid(grid_spacing=1.0):
            # TODO: get from environment
            x_min_limit = -2.5
            x_max_limit = 1.5
            y_min_limit = -1.0
            y_max_limit = 2.0
            grid_size = int(
                round(
                    max(
                        x_max_limit - x_min_limit,
                        y_max_limit - y_min_limit,
                    )
                )
            )

            for i in np.arange(-grid_size, grid_size + grid_spacing, grid_spacing):
                mlab.plot3d(
                    [-grid_size, grid_size],
                    [i, i],
                    [0, 0],
                    color=(0.7, 0.7, 0.7),
                    tube_radius=0.005,
                )
                mlab.plot3d(
                    [i, i],
                    [-grid_size, grid_size],
                    [0, 0],
                    color=(0.7, 0.7, 0.7),
                    tube_radius=0.005,
                )

        draw_axes()
        draw_xy_grid()

        self.animator: Animator = anim()
        mlab.orientation_axes(line_width=1, xlabel="X", ylabel="Y", zlabel="Z")
        mlab.show()

    def write_to_disk(self, agent: str, state: PositionState):
        persistence.store(
            self.config.experiment_dir,
            self.__class__.__name__,
            {"agent": agent, "state": state},
        )


"""
###############################################################################
######## FieldStateLogger #####################################################
###############################################################################
"""


class FieldStateLoggerConfig(Config):
    agent_id: str
    experiment_dir: str
    delay: int = 500  # ms


class FieldStateLogger(LogHandler):
    config: FieldStateLoggerConfig
    communicator: Communicator

    scene: object
    animator: object
    surface: object

    def __init__(self, config: dict, communicator: dict) -> None:
        super().__init__(
            FieldStateLoggerConfig(**config), get_communicator(communicator)
        )

    def run(self):
        # For some reason mayavi imports need to be at method level
        from mayavi import mlab
        from mayavi.core.scene import Scene
        from mayavi.tools.animator import Animator
        from mayavi.modules.surface import Surface

        @mlab.animate(delay=self.config.delay)
        def anim():
            try:
                persistence.clear(
                    self.config.experiment_dir,
                    self.__class__.__name__,
                )
                while self.communicator.is_active():
                    field_state: FieldState = self.communicator.fetch_agent_state(
                        self.config.agent_id
                    )
                    if field_state is None:
                        field_state = FieldState(
                            field=Field(data=np.random.random((84, 84)))
                        )
                    data: np.array = field_state.field.data
                    self.surface.mlab_source.reset(scalars=data.T)
                    self.scene.scene.reset_zoom()
                    self.write_to_disk(self.config.agent_id, field_state)
                    yield
            finally:
                mlab.clf()
                self.animator.close()
                mlab.close(all=True)

        self.scene: Scene = mlab.figure(
            f"FieldState for [{self.config.agent_id}]",
            bgcolor=(1, 1, 1),
            fgcolor=(0, 0, 0),
            size=(480, 480),
        )
        mlab.clf()
        mlab.view(0, 180, None, (0, 0, 0))
        self.surface: Surface = mlab.surf(np.random.random((84, 84)), warp_scale="auto")

        def draw_axes():
            axes_length = 42.0
            mlab.plot3d(
                [0, axes_length], [0, 0], [0, 0], color=(1, 0, 0), tube_radius=0.1
            )  # X axis in red
            mlab.plot3d(
                [0, 0], [0, axes_length], [0, 0], color=(0, 1, 0), tube_radius=0.1
            )  # Y axis in green
            mlab.plot3d(
                [0, 0], [0, 0], [0, axes_length], color=(0, 0, 1), tube_radius=0.1
            )  # Z axis in blue
            mlab.plot3d(
                [-axes_length, 0], [0, 0], [0, 0], color=(1, 0, 0), tube_radius=0.1
            )  # Negative X axis in red
            mlab.plot3d(
                [0, 0], [-axes_length, 0], [0, 0], color=(0, 1, 0), tube_radius=0.1
            )  # Negative Y axis in green

        draw_axes()

        self.animator: Animator = anim()
        mlab.orientation_axes(line_width=1, xlabel="X", ylabel="Y", zlabel="Z")
        mlab.show()

    def write_to_disk(self, agent: str, state: FieldState):
        persistence.store(
            self.config.experiment_dir,
            self.__class__.__name__,
            {"agent": agent, "state": state},
        )


"""
###############################################################################
######## HelloWorldLogger #####################################################
###############################################################################
"""


class HelloWorldLoggerConfig(Config):
    experiment_dir: str = "hello_world"
    delay: int = 1000  # ms


class HelloWorldLogger(LogHandler):
    config: HelloWorldLoggerConfig
    communicator: Communicator

    def __init__(self, config: dict, communicator: dict) -> None:
        super().__init__(
            HelloWorldLoggerConfig(**config), get_communicator(communicator)
        )

    def run(self):
        while self.communicator.is_active():
            info: str = self.communicator.fetch_environment_state()
            logger.info(info)
            persistence.store(
                self.config.experiment_dir,
                self.__class__.__name__,
                {"info": info},
            )
            delay_seconds = self.config.delay / 1000
            time.sleep(delay_seconds)


def spawn_log_handler(init_config: ProcessInitConfig):
    """
    This method is the entrypoint for the logger process
    """
    logger.debug(f"Spawn {init_config.class_name} log handler {init_config.worker}!")
    log_handler_class: type[LogHandler] = globals()[init_config.class_name]
    assert issubclass(
        log_handler_class, LogHandler
    ), f"LogHandler [{init_config.class_name}] was not found"
    log_handler: LogHandler = log_handler_class(**init_config.params)
    log_handler.run()
    logger.debug(f"Finished {init_config.class_name} log handler {init_config.worker}!")
