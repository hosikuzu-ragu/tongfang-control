import argparse
from enum import Enum
from tongfang_control.acpi import AcpiException
from tongfang_control.controller import TongfangController
from tongfang_control.ecspec import *
from tongfang_control.fan import FanMode, LoudnessLevel
from time import sleep


def display_status(controller):
    output = ""
    output += "Fan speed: {0} RPM".format(controller.fan.get_speed())
    output += ", Temp: {0}°C".format(controller.fan.get_temp())
    print(output)


def monitor(controller):
    while True:
        display_status(controller)
        sleep(2)


class ArgTypeMixin(Enum):
    @classmethod
    def argtype(cls, s: str) -> Enum:
        try:
            return cls[s]
        except KeyError:
            raise argparse.ArgumentTypeError(
                f"{s!r} is not a valid {cls.__name__}")

    def __str__(self):
        return self.name


class FanLoudnessArg(ArgTypeMixin, Enum):
    silent = 4
    quiet = LoudnessLevel.Quiet
    medium = LoudnessLevel.Middle
    loud = LoudnessLevel.Loud


class FanModeArg(ArgTypeMixin, Enum):
    intelligent = FanMode.Intelligent
    boost = FanMode.Boost
    custom = FanMode.Custom


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    try:
        parser = argparse.ArgumentParser(
            description="CLI version of Tongfang laptop's gaming centers.")
        parser.add_argument(
            "-fl", "--fan-loudness", type=FanLoudnessArg.argtype, choices=FanLoudnessArg, help="Set the fan's loudness",)
        parser.add_argument(
            "-fm", "--fan-mode", type=FanModeArg.argtype, choices=FanModeArg, help="Set the fan mode")
        parser.add_argument(
            "-m", "--monitor", action="store_true", help="Monitor fan speeds and CPU temperatures")
        parser.add_argument(
            "-lc", "--lightbar-color", type=int, nargs=3, help="Set color of the lightbar by providing the red, green and blue values in that order. E.g. '--lightbar-color 48 0 89'")
        parser.add_argument(
            "-lb", "--lightbar-breathing", type=str2bool, help="Set whether the lightbar will 'breath' when the laptop is charging")
        parser.add_argument(
            "-lcf", "--lightbar-colorful", type=str2bool, help="Set the lightbar to a colorful rainbow colors mode")
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enables verbose logging"
        )
        parsed = parser.parse_args()

        tongfang = TongfangController()

        if parsed.lightbar_color is not None:
            colors = parsed.lightbar_color
            valid = all(color >= 0 and color < 256 for color in colors)
            if valid:
                tongfang.lightbar.set_color(*colors)
            else:
                raise Exception(
                    "Invalid lightbar color {0}. Arguments must be red, green and blue color values in the range [0-255].".format(colors))

        if parsed.lightbar_breathing is not None:
            tongfang.lightbar.set_breathing_mode(parsed.lightbar_breathing)
            if parsed.verbose:
                print("Set lightbar breathing mode to {0}".format(
                    parsed.lightbar_breathing))

        if parsed.lightbar_colorful is not None:
            tongfang.lightbar.set_colorful_mode(parsed.lightbar_colorful)
            if parsed.verbose:
                print("Set lightbar colorful mode to {0}".format(
                    parsed.lightbar_colorful))

        if parsed.fan_mode is not None:
            tongfang.fan.set_mode(parsed.fan_mode.value)
            if parsed.verbose:
                print("Set fan mode to {0}".format(
                    parsed.fan_mode))

        if parsed.fan_loudness is not None:
            loudness = parsed.fan_loudness.value
            if isinstance(loudness, FanMode):
                tongfang.fan.set_loudness(loudness_level=loudness-1)
                if parsed.verbose:
                    print("Set fan loudness to {0}".format(
                        LoudnessLevel(loudness-1).name))
            else:
                # Extra quiet (in theory)
                tongfang.fan.set_custom_fan_curve(
                    20, 20, 45, 60, 75, loudness_level=LoudnessLevel.Custom)
                if parsed.verbose:
                    print("Set fan loudness to Extra quiet")

        if parsed.monitor:
            monitor(tongfang)
    except AcpiException as e:
        print("Error: {0}".format(e))


if __name__ == "__main__":
    main()
