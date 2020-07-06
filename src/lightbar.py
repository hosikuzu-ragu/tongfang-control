from acpi import AcpiController


class LightBarController(AcpiController):

    def set_color_level(self, addr: int, level: int):
        # Level must be between 0 and 36.
        level = int((level/255) * 36)
        self.acpi.write_ecram(addr, level)

    def set_color(self, r: int, g: int, b: int):
        # All brightness values must be between 0 and 255.
        if r is not None:
            self.set_color_level(1865, r)
        if g is not None:
            self.set_color_level(1866, g)
        if b is not None:
            self.set_color_level(1867, b)

    def set_flag(self, flag, enabled):
        self.acpi.set_flag(1864, flag, enabled)

    def set_power_save_mode(self, enabled):
        self.set_flag(2, enabled)

    def set_mode(self, enabled):
        # Alternate way that doesn't work. It might apparently be isKeyPress and not isLightBarOn
        # data = read_ecram(1864)
        # print(data)
        # if enabled:
        #     write_ecram(1864, data | 32)
        # else:
        #     write_ecram(1864, data | 16)

        # Alternate way to toggle [nonfunctional]
        # data = read_ecram(1895)
        # write_ecram(1895, 2 + (data & 253))

        self.set_flag(4, not enabled)

    def set_breathing_mode(self, enabled):
        self.set_flag(8, not enabled)

    def set_colorful_mode(self, enabled):
        self.set_flag(128, enabled)
