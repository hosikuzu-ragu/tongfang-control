import os
import subprocess
import platform

os_type = platform.system()

if os_type == "Windows":
    import wmi


def buffer_to_int(buffer):
    # Get rid of brackets and commas so we can parse the hexadecimals.
    for text in ['{', '}']:
        buffer = buffer.replace(text, '')

    hex_string_array = buffer.split(', ')

    # The buffer returned from ACPI is backwards and must be reversed.
    hex_string_array.reverse()

    # Parse each hexadecimal and convert to a bytearray
    byte_array = bytearray([int(item, 16) for item in hex_string_array])

    # Finally, convert the bytearray to an integer
    return int.from_bytes(byte_array, byteorder='big')


wmi_connection = None

event_names = {
    1: "OSD_CAPSLOCK",
    2: "OSD_NUMLOCK",
    3: "OSD_SROLLOCK",
    4: "OSD_TPON",
    5: "OSD_TPOFF",
    6: "OSD_SILENTON",
    7: "OSD_SILENTOFF",
    8: "OSD_WLANON",
    9: "OSD_WLANOFF",
    10: "OSD_WINMAXON",
    11: "OSD_WINMAXOFF",
    12: "OSD_BTON",
    13: "OSD_BTOFF",
    14: "OSD_RFON",
    15: "OSD_RFOFF",
    16: "OSD_3GON",
    17: "OSD_3GOFF",
    18: "OSD_WEBCAMON",
    19: "OSD_WEBCAMOFF",
    20: "OSD_BRIGHTNESSUP",
    21: "OSD_BRIGHTNESSDOWN",
    26: "OSD_RADIOON",
    27: "OSD_RADIOOFF",
    49: "OSD_POWERSAVEON",
    50: "OSD_POWERSAVEOFF",
    52: "OSD_MENU",
    53: "OSD_MUTE",
    54: "OSD_VOLUMEDOWN",
    55: "OSD_VOLUMEUP",
    56: "OSD_OSD_MENU_2",
    57: "OSD_BREATH_LED_ON",
    58: "OSD_BREATH_LED_OFF",
    59: "OSD_KB_LED_LEVEL0",
    60: "OSD_KB_LED_LEVEL1",
    61: "OSD_KB_LED_LEVEL2",
    62: "OSD_KB_LED_LEVEL3",
    63: "OSD_KB_LED_LEVEL4",
    64: "OSD_WINKEY_LOCK",
    65: "OSD_WINKEY_UNLOCK",
    66: "OSD_MENU_JP",
    144: "OSD_CAMERAON",
    145: "OSD_CAMERAOFF",
    164: "OSD_AIRPLANEMODE",
    167: "OSD_FANBOOST_UPDATE",
    169: "OSD_LCD_SW",
    170: "OSD_FAN_OVER_TEMP",
    171: "OSD_MyBat_ACUpdate",
    172: "OSD_MyBat_HPOff",
    173: "OSD_Fan_DOWN_TEMP",
    174: "OSD_Battery_Alert",
    175: "TimAP_HaierLB_Sw",
    165: "WinKey_Update",
    176: "OSD_FanModeSwitch",
    177: "OSD_KEYBOARD_BRIGHTNESS_DOWN",
    178: "OSD_KEYBOARD_BRIGHTNESS_UP",
}

OfficeMode_Tau_Default = 56
OfficeMode_PL1_Default = 5
OfficeMode_PL2_Default = 5
OfficeMode_PL4_Default = 5


def init():
    global wmi_connection
    if os_type == "Windows":
        moniker = 'root/WMI:AcpiTest_MULong.InstanceName="ACPI\\\\PNP0C14\\\\1_1"'
        wmi_connection = wmi.WMI(moniker=moniker)
        # wmi_connection = wmi.WMI(namespace="WMI").AcpiTest_MULong(InstanceName="ACPI\\PNP0C14\\1_1")
        # wmi_connection = wmi.WMI(namespace="WMI").query("SELECT * FROM AcpiTest_MULong WHERE InstanceName = 'ACPI\\PNP0C14\\1_1'")
        return wmi_connection

        # watcher = wmi.WMI(namespace="WMI").AcpiTest_EventULong.watch_for()
        # while True:
        #     event = watcher()
        #     event_id = event.ULong
        #     name = "Unknown"
        #     if event_id in event_names:
        #         name = event_names[event_id]
        #     print(event_id, name)


def acpi_call(data):
    if os_type == "Linux":
        # FIXME: Catch errors
        acpi_method = "\_SB.AMW0.WMBC"  # AcpiTest_MULong
        instance = 0
        method = 4  # GetSetULong
        command = "echo '{0} {1} {2} {3}' | sudo tee /proc/acpi/call".format(
            acpi_method, instance, method, data)
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(command, shell=True, stdout=FNULL)

        response = subprocess.check_output(
            "sudo cat /proc/acpi/call", shell=True)
        # Remove trailing newline and convert to string
        response = response[:-1].decode('utf-8')
        response = buffer_to_int(response)
        return response
    elif os_type == "Windows":
        response = wmi_connection.GetSetULong(data)[0]
        return response
    else:
        raise Exception("Unsupported operating system: {0}".format(os_type))


def read_ecram(address, byte=True):
    data = acpi_call(0x10000000000 + address)
    if byte:
        data = data & 255
    return data


def write_ecram(address, value):
    return acpi_call(0x0000000000000000 + (value << 16) + address)


def set_light_color_level(addr, brightness):
    # Level must be between 0 and 36.
    level = int((brightness/255) * 36)
    write_ecram(addr, level)


def set_light_color(r, g, b):
    # All brightness values must be between 0 and 255.
    if r is not None:
        set_light_color_level(1865, r)
    if g is not None:
        set_light_color_level(1866, g)
    if b is not None:
        set_light_color_level(1867, b)


def set_flag(address, flag, enabled):
    """
    By default, when a flag is enabled, it's bit is set to 1.
    """
    data = read_ecram(address)
    if enabled:
        write_ecram(address, data | flag)
    else:
        write_ecram(address, data & (255 - flag))


def set_light_bar_flag(flag, enabled):
    set_flag(1864, flag, enabled)


def set_light_power_save_mode(enabled):
    set_light_bar_flag(2, enabled)


def set_light_bar_mode(enabled):
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

    set_light_bar_flag(4, not enabled)


def set_breathing_light_mode(enabled):
    set_light_bar_flag(8, not enabled)


def set_colorful_light_mode(enabled):
    set_light_bar_flag(128, enabled)


def toggle_win_key_mode():
    data = read_ecram(1895, False)
    write_ecram(1895, 1 + (data & 254))


def set_win_key_enabled(enabled):
    status = read_ecram(1896)
    if enabled:
        if status & 1 == 1:
            toggle_win_key_mode()
    else:
        if status & 1 == 0:
            toggle_win_key_mode()


def supports_silent_mode():
    data = read_ecram(1115)
    return (data & 1) == 1


def toggle_silent_mode():
    # Apparently not supported by my laptop
    data = read_ecram(1895)
    write_ecram(1895, 8 + (data & 247))


def toggle_touchpad():
    # FIXME: This doesn't work
    data = read_ecram(1885)
    write_ecram(1885, 4 + (data & 251))


def set_fan_mode(mode):
    """Changes the preset fan mode.

    Args:
        mode (integer): The fans mode. 0 is the default intelligent energy mode, 1 is full speed.
    """
    data = read_ecram(1873)
    if mode == 0:
        # Intelligent energy mode
        write_ecram(1873, 0)
    elif mode == 1:
        # Full speed
        write_ecram(1873, 64)
    elif mode == 2:
        # Custom speeds for different temperatures
        write_ecram(1873, 160)


def set_fan_boost(enabled):
    set_flag(1873, 64, enabled)


def set_fan_speed(level):
    """Manually sets the fans speed.

    Warning: Turning off the fans could permanently damage the computer.

    To reset the fans speed, use `set_fan_mode`.

    Args:
        level (integer): Fan speed level from 0-7 with 0 being off.
    """
    set_fan_mode(2)

    # if (get_fan_isupport()):
    #     set_office_mode_advanced_min_speed(0);
    #     set_office_mode_advanced_min_temp(55);
    #     set_office_mode_advanced_extra_speed(8);
    # set_fan_pwm(1, 1)
    # set_fan_pwm(2, 2)
    # set_fan_pwm(3, 3)
    # set_fan_pwm(4, 4)
    # set_fan_pwm(5, 5)

    write_ecram(1873, 128 + level)


def set_fan_speed_for_temperature_level(level, speed):
    """
    Speeds from 0-200
    """
    write_ecram(1857 + level, speed)


def set_custom_fan_curve(l0, l1, l2, l3, l4, l5, l6):
    """
    Make sure to call set_fan_mode(2) afterwards.
    """
    # L0 and L1 Don't seem to do anything on my laptop
    # L0 40 degree (Might not exist)
    set_fan_speed_for_temperature_level(0, l0)

    # # L1 45 degree
    set_fan_speed_for_temperature_level(1, l1)

    # L2 50 degree
    set_fan_speed_for_temperature_level(2, l2)

    # L3 55 degree
    set_fan_speed_for_temperature_level(3, l3)

    # L4 60 degree
    set_fan_speed_for_temperature_level(4, l4)

    # L5 65 degree
    set_fan_speed_for_temperature_level(5, l5)

    # Up to 70 degrees
    # L6 70 degree
    set_fan_speed_for_temperature_level(6, l6)


def get_fan_isupport():
    data = read_ecram(1858)
    return (data & 32) == 32


def set_fan_pwm(level, speed):
    write_ecram(1858 + level, speed)


def set_pl_value(pl, value):
    write_ecram(1923, value)


def set_tau_value(value):
    # FIXME: Implement
    # XtuCLI.exe -t -id 66 -v value
    print("tau")


def set_pl124_tau(pl1, pl2, pl4, tau):
    # TODO: This messes with voltage so I'm going to leave it for now
    # set_pl_value(0, pl1)
    # set_pl_value(1, pl2)
    # set_pl_value(2, pl4)
    # set_tau_value(tau)
    print("set_pl124_tau", pl1, pl2, pl4, tau)


def set_office_mode_advanced_min_speed(speed):
    # standard PWM levels are [0,1,2,3,4,5]
    # giving byte speeds of [0,60,80,100,120,140]
    write_ecram(1950, speed)


def set_office_mode_advanced_min_temp(temp):
    write_ecram(1951, temp)


def set_office_mode_advanced_extra_speed(level):
    write_ecram(1952, level)


def set_custom_fan_curve2(l1, l2, l3, l4, l5, eco=True, dc=True, loudness_level=None):
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
    set_fan_mode(2)

    # TODO: Only check this once
    if (get_fan_isupport()):
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
        set_office_mode_advanced_min_speed(min_speed)
        set_office_mode_advanced_min_temp(fan_min_temp)
        set_office_mode_advanced_extra_speed(fan_extra_speed)

    # ~~It seems like this does nothing when the fan has isupport~~
    # These only apply when extra speed is 0
    set_fan_pwm(1, l1)
    set_fan_pwm(2, l2)
    set_fan_pwm(3, l3)
    set_fan_pwm(4, l4)
    set_fan_pwm(5, l5)

    if eco:
        if dc:
            set_pl124_tau(0, 0, 0, OfficeMode_Tau_Default)
        else:
            set_pl124_tau(25, 25, OfficeMode_PL4_Default,
                          OfficeMode_Tau_Default)
    else:
        if dc:
            set_pl124_tau(0, 0, 0, OfficeMode_Tau_Default)
        else:
            set_pl124_tau(OfficeMode_PL1_Default, OfficeMode_PL2_Default,
                          OfficeMode_PL4_Default, OfficeMode_Tau_Default)


def read_fan_temp_speeds():
    for level in [1, 2, 3, 4, 5]:
        data = read_ecram(1858+level)
        print("L"+str(level), data)


def check_turbo_mode_support():
    data = read_ecram(1183)
    return (data >> 1 & 1) == 1


def get_fan_speed():
    return read_ecram(0x1804)


def get_fan_temp():
    return read_ecram(0x043e)


init()

# set_light_color(48, 0, 89)

# FIXME: Disable silent mode on Windows. I toggled it once on Linux.
# toggle_silent_mode()
# Silent mode currently: Disabled

# set_fan_mode(0)
"""
Default fan curve is:
- 0, 0
- 1, 162
- 2, 60
- 3, 70
- 4, 80
- 5, 90
- 6, 100

0,162,60,70,80,90,100
"""
# read_fan_temp_speeds()
# set_custom_fan_curve(20, 20, 20, 20, 45, 75, 75)
# set_custom_fan_curve(200, 200, 200, 200, 200, 200, 200)
# set_custom_fan_curve(0, 162, 60, 70, 80, 90, 100)

# set_fan_mode(0)

# Loud
# set_custom_fan_curve2(60, 75, 90, 105, 120)
# Middle
# set_custom_fan_curve2(60, 72, 85, 98, 110)
# Quiet
# set_custom_fan_curve2(60, 70, 80, 90, 100)

# set_fan_mode(2)
# write_ecram(1857, 1)
# write_ecram(1858, 162)
# set_custom_fan_curve2(60, 80, 100, 120, 140, loudness_level=1)
# set_custom_fan_curve2(67, 77, 87, 97, 107, loudness_level=4)
set_fan_mode(0)

print("Fan mode:", read_ecram(1873))
read_fan_temp_speeds()
print("Pl1:", read_ecram(1840))
print("Pl2:", read_ecram(1841))
print("Pl4:", read_ecram(1842))
print("ISupport:", get_fan_isupport())
print("Min speed:", read_ecram(1950))
print("Min temp:", read_ecram(1951))
print("Extra speed:", read_ecram(1952))

while True:
    print("Speed: {0} RPM".format(get_fan_speed()), ",",
          "Temp: {0}°C".format(get_fan_temp()))

# dev = os.open("/dev/tuxedo_cc_wmi", os.O_RDWR)
# os.write(dev, bytes(0x04))
# print(os.read(dev, 16))
