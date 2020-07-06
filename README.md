# Tongfang Unofficial Control Center

An open-source cross-platform control centre for controlling various features of Tongfang-based laptops' such as RGB lighting and fan speed. Developed for the GK5CP0Z but will likely work with similar models (GK5CN5Z, GK5CN6Z, GK5CQ7Z etc.).

This software was primarily developed for Linux since no first-class control centers existed. If you are using Windows, this software is currently no better than the standard Gaming Center applications offered by various vendors such as Eluktronics. In the future, certain features will be added that are not supported by the OEM software such as fan speed readings and temperature curves.

This is project was started before [Tuxedo Computer's control center](https://github.com/tuxedocomputers/tuxedo-control-center) was discovered. It basically does what this control center does but seems to control fan speed in userspace rather than using the builtin fan speed settings. It also doesn't yet support RGB lighting control. If you have a Clevo laptop, consider using it instead. This project may be merged into that in the future if Tuxedo Computer's is interested.

## Supported devices

- Tongfang gaming laptops: GK5CN5Z / GK5CN6Z / GK5CQ7Z / GK5CP0Z (Barebone)
- Wootbook Ultra 2060 (GK5CP0Z)
- Aftershock Apex 15 RTX 2060 (GK5CP0Z)
- llegear Onyx Laptop RTX 2060 (GK5CP0Z)

Various Clevo, Mechrevo, Eluktronics, XMG, Avell and Aftershock laptops that use the same chassis probably also work.

## Usage

This project is still in heavily development and  is not ready for daily usage.

For developers, you will need the `wmi` Python package if on Windows and the `acpi-call-dkms` kernel module if on Linux.

## Related projects

- [Tuxedo Control Center](https://github.com/tuxedocomputers/tuxedo-control-center) - Control center for Tuxedo laptops with support for fan speed adjustment using profiles. Works with Tongfang and Clevo laptops that use the Uniwill OEM interface. ([See the driver for more](https://github.com/tuxedocomputers/tuxedo-cc-wmi)).
- [tuxedo-cc-wmi](https://github.com/tuxedocomputers/tuxedo-cc-wmi) - Kernel driver for interacting with Tongfang and Clevo laptops WMI interfaces. Supports changing fan speed and mode as well as reading current fan speed and temperature.
- [avell-unofficial-control-center](https://github.com/rodgomesc/avell-unofficial-control-center) - Driver to control laptop RGB keyboards that use the ITE Device(8291) controller (such as Tongfang gaming laptops).
- [Notebook Review forum thread on Tongfang laptops](http://forum.notebookreview.com/threads/tongfang-gk5cn5z-gk5cn6z-gk5cq7z-gk5cp0z.815943/) - Contains hacks, tips, tricks, guides and reviews on and, drivers and software for Tongfang laptops.
- [gk5cn6z_rgb_control](https://github.com/ehntoo/gk5cn6z_rgb_control/) - RGB control for GK5CN6Z laptops.
- [https://github.com/ehntoo/gk5cn6z_wmi](gk5cn6z_wmi) - Kernel module to add backlight brightness support to Tongfang GK5CN6z (and possibly related) laptops. Contains lots of helpful links on how to debug the ACPI and WMI calls necessary to control Tongfang laptops.
- [Rev.Center2-FanManager](https://github.com/lKinderBueno/Rev.Center2-FanManager), [Rev.Center2-Keyboard](https://github.com/lKinderBueno/Rev.Center2-Keyboard), [Rev.Center2-Main-LedBar](https://github.com/lKinderBueno/Rev.Center2-Main-LedBar) - Alternative gaming control center. Very useful for figuring out what calls must be made.

## History

This is a brief rundown of how this project was developed.

Figured out I needed to write to ACPI using WMI.

The WMI class is `AcpiTest_MULong` and the instance is `PNP0C14\1_1`.

Figured out GUID of `AcpiTest_MULong` is `ABBC0F6F-8EA1-11d1-00A0-C90629100000` by
checking
<https://github.com/microsoft/Windows-driver-samples/blob/6c1981b8504329521343ad00f32daa847fa6083a/wmi/wmiacpi/acpimof.mof>
where we can also see the documentation for the class.

```
[WMI,
 Dynamic,
 Provider("WmiProv"),
 Locale("MS\\0x409"),
 Description("Class used to operate methods on a ULong"),
 guid("{ABBC0F6F-8EA1-11d1-00A0-C90629100000}")
]
class AcpiTest_MULong
{
    [key, read]
     string InstanceName;
    [read] boolean Active;

    [WmiMethodId(1),
     Implemented,
     read, write,
     Description("Return the contents of a ULong")
    ] void GetULong([out, Description("Ulong Data")] uint32 Data);

    [WmiMethodId(2),
     Implemented,
     read, write,
     Description("Set the contents of a ULong")
    ] void SetULong([in, Description("Ulong Data")] uint32 Data);

    [WmiMethodId(3),
     Implemented,
     read, write,
     Description("Generate an event containing ULong data")
    ] void FireULong([in, Description("WMI requires a parameter")] uint32 Hack);
};
```

Also <https://github.com/ehntoo/gk5cn6z_wmi/blob/master/gk5cn6z_wqba.mof>:

```
[WMI,
 Dynamic,
 Provider("WmiProv"),
 Locale("MS\\0x409"),
 Description("Class used to operate methods on a ULong"),
 guid("{ABBC0F6F-8EA1-11d1-00A0-C90629100000}")
]
class AcpiTest_MULong {
  [key, read] String InstanceName;
  [read] Boolean Active;

  [WmiMethodId(1),
   Implemented,
   read, write,
   Description("Return the contents of a ULong")
  ] void GetULong([out, Description("Ulong Data")] uint32 Data);

  [WmiMethodId(2),
   Implemented,
   read, write,
   Description("Set the contents of a ULong")
  ] void SetULong([in, Description("Ulong Data")] uint32 Data);

  [WmiMethodId(3),
   Implemented,
   read, write,
   Description("Generate an event containing ULong data")
  ] void FireULong([in, Description("WMI requires a parameter")] uint32 Hack);

  [WmiMethodId(4),
   Implemented,
   read, write,
   Description("Get and Set the contents of a ULong")
  ] void GetSetULong(
    [in, Description("Ulong Data")] uint64 Data,
    [out, Description("Ulong Data")] uint32 Return
  );

  [WmiMethodId(5),
   Implemented,
   read, write,
   Description("Get and Set the contents of a ULong for Dollby button")
  ] void GetButton([in, Description("Ulong Data")] uint64 Data, [out, Description("Ulong Data")] uint32 Return);
};
```

Correlated this with output of `fwts wmi -` (See
<https://wiki.ubuntu.com/Kernel/Reference/WMI>):

```
\_SB_.AMW0._WDG (6 of 10)
  GUID: ABBC0F6F-8EA1-11D1-00A0-C90629100000
  WMI Method:
    Flags          : 0x02 (Method)
    Object ID      : BC
    Instance       : 0x0a
FAILED [LOW] WMIMultipleMethod: Test 1, GUID
ABBC0F6F-8EA1-11D1-00A0-C90629100000 has multiple associated methods WMBC
defined, this is a firmware bug that leads to ambiguous behaviour.
```

Based on the documentation for `AcpiTest_MULong`, we know that there is a string
(instanceName) and three methods with IDs 1, 2 and 3.

After finding , I decided to start messing around with ACPI calls using `sudo
apt install acpi-call-dkms`.

The first on I tried was a simple query to get the current value of the light
bar.

The Driver is `\_SB_.AMW0._WDG`, the unsigned integer for the light bar is
`1895UL`. The address to read is thus `0x10000000000 + 1895UL = 1099511629671`.

The method is `WMBC`, method id is `GetSetULong`. Then we need
an instance, not sure which to use though so I tested with 0.

`WMBC` methods take three arguments: ulong instance index, method ID,

| Method | Instance index | Method ID | Input data    |
| ------ | -------------- | --------- | ------------- |
| WMBC   | 0              | 4         | 1099511629671 |

Should instance be `WMBC`?

Before running, [debug using apciexec](https://wiki.ubuntu.com/Kernel/Reference/ACPITricksAndTips#acpiexec).
From debugging, we can tell that the method to call is `\_SB.AMW0.WMBC`.

Debug command:

```
execute _SB.AMW0.WMBC 0 4 <value>
```

So the full call is:

```bash
echo '\_SB.AMW0.WMBC 0 4 1099511629640' | sudo tee /proc/acpi/call
sudo cat /proc/acpi/call
```

I then debugged the responses of reading data from the driver on Windows;

| Prop name | Prop   | Prop address  | State     | Return (uint) | Return (byte) | notes                             |
| --------- | ------ | ------------- | --------- | ------------- | ------------- | --------------------------------- |
| Lightbar  | 1864UL | 1099511629640 | Enabled   | 3081          | 9             |                                   |
|           | 1864UL | 1099511629640 | Enabled   | 1033          | 9             | bitwise or = 41                   |
|           | 1864UL | 1099511629640 | Disabled  | 1037          | 13            | flipped and converted to byte = 0 |
| Fan       | 1873UL | 1099511629649 | Game mode | 27808         | 160           |                                   |

The unsigned integer responses are converted to bytes using this C# code

```csharp
(byte) (Convert.ToUInt64(data) & (ulong) byte.MaxValue)
```

I then compared these responses to those on Linux to figure out how to convert the buffers from the Linux ACPI calls to the unsigned integers returned on Windows.

| Prop name | Command                          | State     | Return                                                                                                                                                                                                                                           |
| --------- | -------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Lightbar  | \_SB.AMW0.WMBC 0 4 1099511629640 | Enabled   | {0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} |
| Fan       | \_SB.AMW0.WMBC 0 4 1099511629649 | Game mode | {0xa0, 0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00} |
