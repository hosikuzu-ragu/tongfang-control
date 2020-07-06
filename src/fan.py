from enum import Enum
from acpi import AcpiController

OfficeMode_Tau_Default = 56
OfficeMode_PL1_Default = 5
OfficeMode_PL2_Default = 5
OfficeMode_PL4_Default = 5


class FanMode(Enum):
    # Intelligently adjusts the fan speed proportionally to temperatures.
    Intelligent = 0
    # Enables fan boost and pushes the fan to it's maximum speed.
    FullSpeed = 1
    # Allows for setting custom speeds either globally or per temperature range.
    Custom = 2


class FanController(AcpiController):
    def set_mode(self, mode: int):
        """Changes the preset fan mode.

        Args:
            mode (FanMode): The fan's mode. 0 is the default intelligent energy mode, 1 is full speed and 2 is custom.
        """

        if not isinstance(mode, FanMode):
            # TODO: Improve error message
            raise TypeError(
                'Invalid fan mode "{0}". Mode must be an instance of the FanMode Enum'.format(mode))

        if mode == FanMode.Intelligent:
            self.acpi.write_ecram(1873, 0)
        elif mode == FanMode.FullSpeed:
            self.acpi.write_ecram(1873, 64)
        elif mode == FanMode.Custom:
            self.acpi.write_ecram(1873, 160)

    def set_boost(self, enabled):
        self.acpi.set_flag(1873, 64, enabled)

    def set_speed(self, level: int):
        """Manually sets the fans speed.

        Warning: Turning off the fans could permanently damage the computer.

        To reset the fans speed, use `set_fan_mode`.

        Args:
            level (integer): Fan speed level from 0-7 with 0 being off.
        """
        self.set_mode(FanMode.Custom)

        # if (get_fan_isupport()):
        #     set_office_mode_advanced_min_speed(0);
        #     set_office_mode_advanced_min_temp(55);
        #     set_office_mode_advanced_extra_speed(8);
        # set_fan_pwm(1, 1)
        # set_fan_pwm(2, 2)
        # set_fan_pwm(3, 3)
        # set_fan_pwm(4, 4)
        # set_fan_pwm(5, 5)

        self.acpi.write_ecram(1873, 128 + level)

    def get_fan_isupport(self):
        data = self.acpi.read_ecram(1858)
        return (data & 32) == 32

    def set_pwm(self, level, speed):
        self.acpi.write_ecram(1858 + level, speed)

    def set_pl_value(self, pl, value):
        self.acpi.write_ecram(1923, value)

    def set_tau_value(self, value):
        # FIXME: Implement
        # XtuCLI.exe -t -id 66 -v value
        print("tau")

    def set_pl124_tau(self, pl1, pl2, pl4, tau):
        # TODO: This messes with voltage so I'm going to leave it for now
        # self.set_pl_value(0, pl1)
        # self.set_pl_value(1, pl2)
        # self.set_pl_value(2, pl4)
        # self.set_tau_value(tau)
        print("set_pl124_tau", pl1, pl2, pl4, tau)

    def set_office_mode_advanced_min_speed(self, speed):
        # standard PWM levels are [0,1,2,3,4,5]
        # giving byte speeds of [0,60,80,100,120,140]
        self.acpi.write_ecram(1950, speed)

    def set_office_mode_advanced_min_temp(self, temp):
        self.acpi.write_ecram(1951, temp)

    def set_office_mode_advanced_extra_speed(self, level):
        self.acpi.write_ecram(1952, level)

    def set_custom_fan_curve(self, l1, l2, l3, l4, l5, eco=True, dc=True, loudness_level=None):
        """
        L1 67 < 59 degrees
        L2 77 59-65 degrees
        L3 87 66-72 degrees
        L4 97 73 degrees
        L5 107 74-78 degrees
        Anything higher is automatic

        Notes:
        - Minimum speed seems to be overwritten by L1.
        - Not sure what minimum temperature does.
        - For PWM values to apply, extra speed must be zero.
        """
        # These are PWM values. (0-5)
        self.set_mode(FanMode.Custom)

        # TODO: Only check this once
        if (self.get_fan_isupport()):
            if loudness_level is not None:
                if loudness_level == 1:
                    # slow
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 5
                elif loudness_level == 2:
                    # middle
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 10
                elif loudness_level == 3:
                    # fast
                    min_speed = 0
                    fan_min_temp = 70
                    fan_extra_speed = 5
                elif loudness_level == 4:
                    # custom (doesn't exist in GamingCenter)
                    min_speed = 20
                    fan_min_temp = 55
                    fan_extra_speed = 0
            else:
                min_speed = 0
                fan_min_temp = 55
                fan_extra_speed = 5
            # Do this in all set fan speed functions
            self.set_office_mode_advanced_min_speed(min_speed)
            self.set_office_mode_advanced_min_temp(fan_min_temp)
            self.set_office_mode_advanced_extra_speed(fan_extra_speed)

        # ~~It seems like this does nothing when the fan has isupport~~
        # These only apply when extra speed is 0
        self.set_pwm(1, l1)
        self.set_pwm(2, l2)
        self.set_pwm(3, l3)
        self.set_pwm(4, l4)
        self.set_pwm(5, l5)

        if eco:
            if dc:
                self.set_pl124_tau(0, 0, 0, OfficeMode_Tau_Default)
            else:
                self.set_pl124_tau(25, 25, OfficeMode_PL4_Default,
                                   OfficeMode_Tau_Default)
        else:
            if dc:
                self.set_pl124_tau(0, 0, 0, OfficeMode_Tau_Default)
            else:
                self.set_pl124_tau(OfficeMode_PL1_Default, OfficeMode_PL2_Default,
                                   OfficeMode_PL4_Default, OfficeMode_Tau_Default)

    def print_fan_pwm_values(self):
        for level in [1, 2, 3, 4, 5]:
            data = self.acpi.read_ecram(1858+level)
            print("L"+str(level), data)

    def check_turbo_mode_support(self):
        data = self.acpi.read_ecram(1183)
        return (data >> 1 & 1) == 1

    def get_speed(self):
        return self.acpi.read_ecram(0x1804)

    def get_temp(self):
        return self.acpi.read_ecram(0x043e)
