import matplotlib.animation as animation
import matplotlib.pyplot as plt
import datetime as dt
from tongfang_control.controller import TongfangController


def graph_sensors(controller: TongfangController, sensors, sensor_names):

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xg = {}
    yg = {}

    # Format plot
    # plt.xticks(rotation=45, ha='right')
    # plt.subplots_adjust(bottom=0.30)
    plt.title('Sensors')
    plt.ylabel('Temperature (deg C)')

    # This function is called periodically from FuncAnimation
    def animate(i, xg, yg):

        ax.clear()

        # print("===")
        for sensor in sensors:
            # Read sensor data
            value = controller.acpi.read_ecram(sensor, byte=False)

            if sensor not in xg:
                xg[sensor] = []
            if sensor not in yg:
                yg[sensor] = []
            xs = xg[sensor]
            ys = yg[sensor]

            # Add x and y to lists
            # xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
            xs.append(i)
            ys.append(value)

            # Limit x and y lists to 20 items
            xs = xs[-30:]
            ys = ys[-30:]

            # Draw x and y lists
            label = sensor_names[sensor] if sensor in sensor_names else sensor
            # print(label, ys)
            ax.plot(xs, ys, label=label)

        plt.legend()

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xg, yg), interval=10)
    plt.show()


def discover_sensors():
    sensors = [
        6148,  # 0b1100000000100 71 -> 69 :: Fan speed
        6173,  # 0b1100000011101 23296 -> 23040
        6174,  # 0b1100000011110 601 -> 603
        6175,  # 0b1100000011111 23298 -> 24066
        6176,  # 0b1100000100000 169 -> 32
        1086,  # 0b10000111110 67 -> 63 :: Fan temp
        1096,  # 0b10001001000 7358 -> 4286
        1097,  # 0b10001001001 30 -> 14
        1099,  # 0b10001001011 14337 -> 6913
        1100,  # 0b10001001100 55 -> 27
        1119,  # 0b10001011111 1024 -> 512
        1120,  # 0b10001100000 23044 -> 17922
        1121,  # 0b10001100001 17754 -> 17734
        1123,  # 0b10001100011 3845 -> 3333
        # 1124,  # 0b10001100100 64271 -> 782
        1125,  # 0b10001100101 251 -> 3
        1131,  # 0b10001101011 3875 -> 3363
        # 1132,  # 0b10001101100 62223 -> 58893
        1133,  # 0b10001101101 243 -> 230
    ]

    # 800,000,000

    sensor_names = {
        6148: 'Fan speed',
        1086: 'Fan temp',
        1133: 'CPU freq 1',
        1125: 'CPU freq 2',
        1124: 'CPU freq 3 (follows 1132)',
        1132: 'CPU freq 4 (follows 1124)',
        1123: 'follows 6173',
        6173: 'follows 1123',
    }

    # graph_sensors(tongfang, sensors, sensor_names)

    # prev_values = {}
    # for start in [0x1804, 0x043e]:
    #     for i in range(2):
    #         for i in range(128):
    #             addr = start + i
    #             value = tongfang.acpi.read_ecram(addr, byte=False)
    #             if addr in prev_values:
    #                 prev_value = prev_values[addr]
    #                 if prev_value != value:
    #                     print(addr, bin(addr), prev_value, "->", value)
    #             prev_values[addr] = value
    #         print("completed run")
