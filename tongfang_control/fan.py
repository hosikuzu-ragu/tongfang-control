from enum import Enum
from tongfang_control.acpi import AcpiController
from tongfang_control.ecspec import *

OfficeMode_Tau_Default = 56
OfficeMode_PL1_Default = 5
OfficeMode_PL2_Default = 5
OfficeMode_PL4_Default = 5


class FanMode(Enum):
    # Intelligently adjusts the fan speed proportionally to temperatures.
    Intelligent = FAN_MODE_NORMAL
    # Enables fan boost and pushes the fan to it's maximum speed.
    Boost = FAN_MODE_BOOST
    # Allows for setting custom speeds either globally or per temperature range.
    Custom = FAN_MODE_CUSTOMIZE


class LoudnessLevel(Enum):
    Quiet = 0
    Middle = 1
    Loud = 2
    Custom = 3


# TODO: Add method to read default PWM level values
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
            self.acpi.write_ecram(ADDR_MAFAN_CONTROL_BYTE,
                                  MyFanCTLByteFlag.Normal_Mode.value)
        elif mode == FanMode.Boost:
            self.acpi.write_ecram(ADDR_MAFAN_CONTROL_BYTE,
                                  MyFanCTLByteFlag.FanBoost_Mode.value)
        elif mode == FanMode.Custom:
            self.acpi.write_ecram(ADDR_MAFAN_CONTROL_BYTE,
                                  MyFanCTLByteFlag.User_Fan_HiMode.value)

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

        # TODO: Implement User_Fan_Level1 -> 5
        self.acpi.write_ecram(ADDR_MAFAN_CONTROL_BYTE,
                              MyFanCTLByteFlag.User_Fan_Mode.value + level)
        # FIXME: Make this work by writing to 6148 (fan speed) instead

    def get_fan_isupport(self) -> bool:
        return self.acpi.get_flag(ADDR_SUPPORT_BYTE5, 32)

    def set_pwm(self, level: int, speed: int):
        # Address is ADDR_MYFAN2_L1_PWM -> ADDR_MYFAN2_L5_PWM
        self.acpi.write_ecram(1858 + level, speed)

    def set_pl_value(self, pl, value: int):
        if pl == 1:
            self.acpi.write_ecram(ADDR_PL1_SETTING_VALUE, value)
        elif pl == 2:
            self.acpi.write_ecram(ADDR_PL2_SETTING_VALUE, value)
        elif pl == 4:
            self.acpi.write_ecram(ADDR_PL4_SETTING_VALUE, value)

    def set_tau_value(self, value: int):
        # FIXME: Implement
        # XtuCLI.exe -t -id 66 -v value
        print("tau")

    def set_pl124_tau(self, pl1: int, pl2: int, pl4: int, tau: int):
        # TODO: This messes with voltage so I'm going to leave it disabled for now
        # self.set_pl_value(1, pl1)
        # self.set_pl_value(2, pl2)
        # self.set_pl_value(4, pl4)
        # self.set_tau_value(tau)
        print("set_pl124_tau", pl1, pl2, pl4, tau)

    def set_min_speed(self, speed: int):
        # standard PWM levels are [0,1,2,3,4,5]
        # giving byte speeds of [0,60,80,100,120,140]
        self.acpi.write_ecram(ADDR_MYFANI_MIN_SPEED, speed)

    def set_min_temp(self, temp: int):
        self.acpi.write_ecram(ADDR_MYFANI_MIN_TEMP, temp)

    def set_extra_speed(self, level: int):
        self.acpi.write_ecram(ADDR_MYFANI_EXTRA_SPEED, level)

    def set_custom_fan_curve(self, l1: int, l2: int, l3: int, l4: int, l5: int, eco=True, dc=True, loudness_level: LoudnessLevel = None):
        # TODO: Merge this with set_speed
        """
        Anything higher is automatic

        Notes:
        - Minimum speed seems to be overwritten by L1.
        - Not sure what minimum temperature does.
        - For PWM values to apply, extra speed must be zero.

        Args:
            l1 (int): Speed at < 59 degrees
            l2 (int): Speed at 59-65 degrees
            l3 (int): Speed at 66-72 degrees
            l4 (int): Speed at 73 degrees
            l5 (int): Speed at 74-78 degrees
            loudness_level (int): 
        """
        # These are PWM values. (0-5)
        self.set_mode(FanMode.Custom)

        # TODO: Only check this once
        if (self.get_fan_isupport()):
            if loudness_level is not None:
                if loudness_level == LoudnessLevel.Quiet:
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 5
                elif loudness_level == LoudnessLevel.Middle:
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 10
                elif loudness_level == LoudnessLevel.Loud:
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 15
                elif loudness_level == LoudnessLevel.Custom:
                    # Note: this doesn't exist in GamingCenter
                    min_speed = 0
                    fan_min_temp = 55
                    fan_extra_speed = 0
            else:
                min_speed = 0
                fan_min_temp = 55
                fan_extra_speed = 5
            # Do this in all set fan speed functions
            self.set_min_speed(min_speed)
            self.set_min_temp(fan_min_temp)
            self.set_extra_speed(fan_extra_speed)

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

    def set_loudness(self, loudness_level: LoudnessLevel):
        self.set_custom_fan_curve(60, 70, 80, 90, 100, loudness_level)

    def get_fan_pwm_values(self):
        values = []
        for level in [1, 2, 3, 4, 5]:
            value = self.acpi.read_ecram(1858+level)
            values.append(value)
        return values

    def check_turbo_mode_support(self):
        data = self.acpi.read_ecram(ADDR_BIOS_INFO_3_BYTE)
        return (data >> 1 & 1) == 1

    def get_speed(self):
        return self.acpi.read_ecram(Sensors.Speed.value)

    def get_temp(self):
        return self.acpi.read_ecram(Sensors.Temp.value)
