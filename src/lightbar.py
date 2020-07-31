from acpi import AcpiController
from ecspec import *

# TODO: Find out what ApExit, LB10NoKey and LB10KeyPress are and if they are supported


class LightBarController(AcpiController):

    def set_color_level(self, addr: int, level: int):
        # Level must be between 0 and 36.
        level = int((level/255) * 36)
        self.acpi.write_ecram(addr, level)

    def set_color(self, r: int, g: int, b: int):
        # All brightness values must be between 0 and 255.
        if r is not None:
            self.set_color_level(ADDR_REDBAR_CONTROL_BYTE, r)
        if g is not None:
            self.set_color_level(ADDR_GREENBAR_CONTROL_BYTE, g)
        if b is not None:
            self.set_color_level(ADDR_BLUEBAR_CONTROL_BYTE, b)

    def set_flag(self, flag: RGBLightBarCtrlByteFlag, enabled: bool):
        self.acpi.set_flag(ADDR_LIGHTBAR_CONTROL_BYTE, flag.value, enabled)

    def get_flag(self, flag: RGBLightBarCtrlByteFlag):
        return self.acpi.get_flag(ADDR_LIGHTBAR_CONTROL_BYTE, flag.value)

    def set_power_save_mode(self, enabled: bool):
        self.set_flag(RGBLightBarCtrlByteFlag.PowerSaveMode, enabled)

    def set_on_off(self, on: bool):
        self.set_flag(RGBLightBarCtrlByteFlag.Switch_S0, not on)

    def set_breathing_mode(self, enabled: bool):
        self.set_flag(RGBLightBarCtrlByteFlag.Switch_S3, not enabled)

    def set_colorful_mode(self, enabled: bool):
        self.set_flag(RGBLightBarCtrlByteFlag.WelcomeLightMode, enabled)

    def get_colorful_mode(self):
        return self.get_flag(RGBLightBarCtrlByteFlag.WelcomeLightMode)
