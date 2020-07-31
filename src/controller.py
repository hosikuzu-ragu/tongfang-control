from acpi import BaseAcpiController
from ecspec import *
from fan import FanController
from lightbar import LightBarController


class TongfangController():
    def __init__(self):
        self.acpi = BaseAcpiController()
        self.fan = FanController(self.acpi)
        self.lightbar = LightBarController(self.acpi)

    def trigger(self, flag: TriggerByteFlag):
        self.acpi.set_flag(ADDR_TRIGGER_BYTE, flag.value, True)

    def check_status(self, flag: StatusByteOneFlag) -> bool:
        flag = flag.value
        return self.acpi.get_flag(ADDR_STATUS_BYTE, flag)

    def toggle_win_key_mode(self):
        self.trigger(TriggerByteFlag.WinLock_Trigger)

    def set_win_key_enabled(self, enabled):
        currently_enabled = self.check_status(StatusByteOneFlag.WinLock)
        if enabled:
            if currently_enabled:
                self.toggle_win_key_mode()
        else:
            if not currently_enabled:
                self.toggle_win_key_mode()

    def supports_silent_mode(self):
        return self.acpi.get_flag(ADDR_SILENTMODE_STATUS_BYTE, 1)

    def toggle_silent_mode(self):
        # Apparently not supported by my laptop
        self.trigger(TriggerByteFlag.SilentMode_Trigger)

    def toggle_touchpad(self):
        # FIXME: This doesn't work
        self.acpi.set_flag(ADDR_TRIGGER_BYTE2, 4)
