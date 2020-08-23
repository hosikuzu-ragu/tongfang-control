from tongfang_control.acpi import AcpiController
from tongfang_control.ecspec import *
from enum import Enum

# TODO: Find out what ApExit, LB10NoKey and LB10KeyPress are and if they are supported


class LightBarColor(Enum):
    Red = 0
    Green = 1
    Blue = 2


# Maps color levels to PWM values
lightbar_color_values = {
    LightBarColor.Red: [0, 4, 8, 12, 16, 20, 24, 28, 32, 36],
    LightBarColor.Green: [0, 4, 8, 12, 16, 20, 24, 28, 32, 36],
    LightBarColor.Blue: [0, 4, 8, 12, 16, 20, 24, 28, 32, 36],
}


class LightBarController(AcpiController):

    colors = {
        LightBarColor.Red: 0,
        LightBarColor.Green: 0,
        LightBarColor.Blue: 0
    }

    def get_color_value(self, color: LightBarColor, brightness: int):
        # Brightness is between 0 and 255.
        range = len(lightbar_color_values[color])
        level = int((brightness/256) * range)
        return lightbar_color_values[color][level]

    def set_oem_service_new(self, on_off, welcome_mode, r, g, b):
        num = None
        if (on_off == 1):
            if (welcome_mode == 1):
                num = self.acpi.combine_bits([32, 1, 0, 0, 0, 0, 0, 0])
            else:
                num = self.acpi.combine_bits([33, r, g, b, 0, 0, 0, 0])
        else:
            num = self.acpi.combine_bits([32, 0, 0, 0, 0, 0, 0, 0])
        self.acpi.write_bios_ram(num)

    def set_color_level(self, color, addr: int, brightness: int):
        level = self.get_color_value(color, brightness)
        # Level must be between 0 and 36.
        self.acpi.write_ecram(addr, level)
        self.colors[color] = level

    def set_color(self, r: int, g: int, b: int):
        # All brightness values must be between 0 and 255.
        if r is not None:
            self.set_color_level(
                LightBarColor.Red, ADDR_REDBAR_CONTROL_BYTE, r)
        if g is not None:
            self.set_color_level(LightBarColor.Green,
                                 ADDR_GREENBAR_CONTROL_BYTE, g)
        if b is not None:
            self.set_color_level(LightBarColor.Blue,
                                 ADDR_BLUEBAR_CONTROL_BYTE, b)

        # FIXME: Save lightbar settings to BIOS
        self.set_oem_service_new(
            1, 0,
            self.colors[LightBarColor.Red],
            self.colors[LightBarColor.Green],
            self.colors[LightBarColor.Blue]
        )

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
