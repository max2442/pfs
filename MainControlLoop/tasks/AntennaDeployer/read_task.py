from MainControlLoop.lib.drivers.AntennaDeployer import AntennaDeployer
from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, ErrorFlag, StateField


class AntennaDeployerReadTask:
    CLEAR_BUFFER_TIMEOUT = 30

    def __init__(self, antenna_deployer: AntennaDeployer, state_field_registry: StateFieldRegistry):
        self.antenna_deployer: AntennaDeployer = antenna_deployer
        self.state_field_registry: StateFieldRegistry = state_field_registry
        self.buffer: list = []
        self.last_message: str = ""

    def execute(self):
        current_time: float = self.state_field_registry.get(StateField.TIME)
        if current_time - last_message_time > self.CLEAR_BUFFER_TIMEOUT:
            self.buffer = []

        next_byte: bytes = self.antenna_deployer.read()
        self.last_message = ""

        if next_byte is False:
            # Antenna Deployer Hardware Fault
            self.state_field_registry.raise_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)
            return

        self.state_field_registry.drop_flag(ErrorFlag.ANTENNA_DEPLOYER_FAILURE)

        if len(next_byte) == 0:
            return

        if next_byte == '\n'.encode('utf-8'):
            message: str = ""
            while len(self.buffer) > 0:
                buffer_byte: bytes = self.buffer.pop(0)
                message += buffer_byte.decode('utf-8')

            self.last_message = message
#            self.state_field_registry.update(StateField.APRS_LAST_MESSAGE_TIME, current_time)
            return

        self.buffer.append(next_byte)
