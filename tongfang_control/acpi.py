import platform
import subprocess
os_type = platform.system()
if os_type == "Windows":
    import wmi

acpi_event_names = {
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


def kernel_module_loaded(module_name: str):
    """Checks if a kernel module is loaded."""
    lsmod_proc = subprocess.Popen(['lsmod'], stdout=subprocess.PIPE)
    grep_proc = subprocess.Popen(['grep', module_name],
                                 stdin=lsmod_proc.stdout, stdout=subprocess.DEVNULL)
    grep_proc.communicate()  # Block until finished
    return grep_proc.returncode == 0


class AcpiException(Exception):
    pass


class BaseAcpiController():
    wmi_test_ulong = None
    wmi_odm_demo = None

    def __init__(self):
        if os_type == "Windows":
            self.wmi_test_ulong = wmi.WMI(
                moniker='root/WMI:AcpiTest_MULong.InstanceName="ACPI\\\\PNP0C14\\\\1_1"')
            self.wmi_odm_demo = wmi.WMI(
                moniker='root/WMI:AcpiODM_Demo.InstanceName="ACPI\\\\PNP0C14\\\\2_0"')
        elif os_type == "Linux":
            # Make sure the necessary kernel module is loaded
            if not kernel_module_loaded("acpi_call"):
                raise AcpiException(
                    "The acpi-call-dkms kernel module is required to run this software. Try running 'sudo modprobe acpi_call'")

    def linux_acpi_call(self, acpi_method, instance, method, data):
        command = "echo '{0} {1} {2} {3}' | sudo tee /proc/acpi/call".format(
            acpi_method, instance, method, data)
        subprocess.check_call(command, shell=True,
                              stdout=subprocess.DEVNULL)

        # TODO: Avoid using sudo
        response = subprocess.check_output(
            "sudo cat /proc/acpi/call", shell=True)
        # Remove trailing newline and convert to string
        response = response[:-1].decode('utf-8')
        response = buffer_to_int(response)
        return response

    def watch_for_events(self):
        if os_type == "Windows":
            watcher = wmi.WMI(namespace="WMI").AcpiTest_EventULong.watch_for()
            while True:
                event = watcher()
                event_id = event.ULong
                event_name = "Unknown"
                if event_id in acpi_event_names:
                    event_name = acpi_event_names[event_id]
                print(event_id, event_name)
                # FIXME: Implement actual event handling
        elif os_type == "Linux":
            # FIXME: Implement Linux version
            print("Error: Linux event handling is not yet supported")
            return

    def write_bios_ram(self, data):
        # root\\WMI", "AcpiODM_Demo.InstanceName='ACPI\\PNP0C14\\2_0'
        #  "GetUlongEx7"
        if os_type == "Linux":
            acpi_method = "\_SB_.OTA0._WDG"  # AcpiODM_Demo
            instance = 0
            method = 7  # GetUlongEx7
            return self.linux_acpi_call(acpi_method, instance, method, data)
        elif os_type == "Windows":
            response = self.wmi_odm_demo.GetUlongEx7(data)[0]
            return response
        else:
            raise Exception(
                "Unsupported operating system: {0}".format(os_type))

    def getsetulong(self, data):
        # TODO: Make sure console errors are thrown
        if os_type == "Linux":
            acpi_method = "\_SB.AMW0.WMBC"  # AcpiTest_MULong
            instance = 0
            method = 4  # GetSetULong
            return self.linux_acpi_call(acpi_method, instance, method, data)
        elif os_type == "Windows":
            response = self.wmi_test_ulong.GetSetULong(data)[0]
            return response
        else:
            raise Exception(
                "Unsupported operating system: {0}".format(os_type))

    def read_ecram(self, address, byte=True):
        data = self.getsetulong(0x10000000000 + address)
        if byte:
            data = data & 255
        return data

    def write_ecram(self, address, value):
        return self.getsetulong(0x0000000000000000 + (value << 16) + address)

    def set_flag(self, address, flag, enabled):
        """
        By default, when a flag is enabled, it's bit is set to 1.
        """
        data = self.read_ecram(address)
        if enabled:
            self.write_ecram(address, data | flag)
        else:
            self.write_ecram(address, data & (255 - flag))

    def get_flag(self, address, flag) -> bool:
        return (self.read_ecram(address) & flag) == flag

    def combine_bits(self, bits: list):
        return int.from_bytes(bytes(bits), "little")


class AcpiController():
    acpi: BaseAcpiController = None

    def __init__(self, acpi: BaseAcpiController):
        self.acpi = acpi
