from acpi import BaseAcpiController
from fan import FanController
from lightbar import LightBarController


class TongfangController():
    def __init__(self):
        self.acpi = BaseAcpiController()
        self.fan = FanController(self.acpi)
        self.lightbar = LightBarController(self.acpi)

    def toggle_win_key_mode(self):
        data = self.acpi.read_ecram(1895, False)
        self.acpi.write_ecram(1895, 1 + (data & 254))

    def set_win_key_enabled(self, enabled):
        status = self.acpi.read_ecram(1896)
        if enabled:
            if status & 1 == 1:
                self.toggle_win_key_mode()
        else:
            if status & 1 == 0:
                self.toggle_win_key_mode()

    def supports_silent_mode(self):
        data = self.acpi.read_ecram(1115)
        return (data & 1) == 1

    def toggle_silent_mode(self):
        # Apparently not supported by my laptop
        data = self.acpi.read_ecram(1895)
        self.acpi.write_ecram(1895, 8 + (data & 247))

    def toggle_touchpad(self):
        # FIXME: This doesn't work
        data = self.acpi.read_ecram(1885)
        self.acpi.write_ecram(1885, 4 + (data & 251))
