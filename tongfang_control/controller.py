from typing import Union
from tongfang_control.acpi import BaseAcpiController
from tongfang_control.ecspec import *
from tongfang_control.fan import FanController
from tongfang_control.lightbar import LightBarController


class TongfangController():
    def __init__(self):
        self.acpi = BaseAcpiController()
        self.fan = FanController(self.acpi)
        self.lightbar = LightBarController(self.acpi)

    def check_support(self, support_byte: int, flag: Union[SupportByteOneFlag, SupportByteTwoFlag, SupportByteThreeFlag]) -> bool:
        """Checks if a particular feature is supported. (This method doesn't work on all devices)

        Args:
            support_byte (int): The support byte to check. Can be 1,2 or 3.
            flag (Union[SupportByteOneFlag, SupportByteTwoFlag, SupportByteThreeFlag]): The feature to check

        Returns:
            bool: Whether the specified feature is supported
        """
        if support_byte == 1:
            addr = ADDR_SUPPORT_BYTE1
        elif support_byte == 2:
            addr = ADDR_SUPPORT_BYTE2
        elif support_byte == 3:
            addr = ADDR_SUPPORT_BYTE5
        else:
            raise ValueError("Invalid support byte")
        flag = flag.value
        return self.acpi.get_flag(addr, flag)

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
