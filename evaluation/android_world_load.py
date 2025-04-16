from android_world.env.env_launcher import setup_env
from android_world.env import android_world_controller
from android_world.env import interface
from android_world.env.android_world_controller import AndroidWorldController, _write_default_task_proto
from android_env.components import config_classes
from android_env.components import coordinator as coordinator_lib
from android_env.components import device_settings as device_settings_lib
from android_env.components import task_manager as task_manager_lib
from android_env.loader import _load_task, _process_emulator_launcher_config
from android_env import environment
from android_env.components.simulators.emulator import emulator_simulator

class EmulatorSimulator_docker(emulator_simulator.EmulatorSimulator):
    def adb_device_name(self) -> str:
        return 'localhost:%s' % (self._config.emulator_launcher.adb_port - 1)
    

def load(config: config_classes.AndroidEnvConfig) -> environment.AndroidEnv:
    """Loads an AndroidEnv instance."""

    task = _load_task(config.task)
    task_manager = task_manager_lib.TaskManager(task)

    _process_emulator_launcher_config(config.simulator)
    simulator = EmulatorSimulator_docker(config=config.simulator)

    device_settings = device_settings_lib.DeviceSettings(simulator)
    coordinator = coordinator_lib.Coordinator(
        simulator, task_manager, device_settings
    )
    return environment.AndroidEnv(
        simulator=simulator, coordinator=coordinator, task_manager=task_manager
    )

DEFAULT_ADB_PATH = '~/Android/Sdk/platform-tools/adb'

def get_controller(
        console_port: int = 5554,
        adb_path: str = DEFAULT_ADB_PATH,
        grpc_port: int = 8554,
    ) -> AndroidWorldController:
    """Creates a controller by connecting to an existing Android environment."""

    config = config_classes.AndroidEnvConfig(
        task=config_classes.FilesystemTaskConfig(
            path=_write_default_task_proto()
        ),
        simulator=config_classes.EmulatorConfig(
            emulator_launcher=config_classes.EmulatorLauncherConfig(
                emulator_console_port=console_port,
                adb_port=console_port + 1,
                grpc_port=grpc_port,
            ),
            adb_controller=config_classes.AdbControllerConfig(adb_path=adb_path),
        ),
    )
    android_env_instance = load(config)
    return AndroidWorldController(android_env_instance)

def _get_env(
        console_port: int, adb_path: str, grpc_port: int
    ) -> interface.AsyncEnv:
    """Creates an AsyncEnv by connecting to an existing Android environment."""
    controller = get_controller(
        console_port, adb_path, grpc_port
    )
    return interface.AsyncAndroidEnv(controller)

def load_and_setup_env(
        console_port: int = 5554,
        emulator_setup: bool = False,
        freeze_datetime: bool = True,
        adb_path: str = android_world_controller.DEFAULT_ADB_PATH,
        grpc_port: int = 8554,
    ) -> interface.AsyncEnv:
    """Create environment with `get_env()` and perform env setup and validation.

    Before running this, an emulator must be launched. For example:

    ```
    AVD_NAME=Pixel_6_API_33  # First create an AVD in Android Studio.
    ~/Android/Sdk/emulator/emulator -avd $AVD_NAME -no-snapshot -grpc 8554
    ```

    Args:
        console_port: The console port of the existing device. This can usually be
        retrieved by looking at the output of `adb devices`. In general, the first
        connected device is port 5554, the second is 5556, and so on.
        emulator_setup: Perform first-time app setup on the environment if True.
        freeze_datetime: Whether to freeze the datetime to a fixed time, October
        2023, to ensure consistent benchmarking.
        adb_path: The location of the adb binary.
        grpc_port: The port for gRPC communication with the emulator.

    Returns:
        An interactable Android environment.
    """
    env = _get_env(console_port, adb_path, grpc_port)
    setup_env(env, emulator_setup, freeze_datetime)
    return env
