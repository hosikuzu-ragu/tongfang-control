from controller import TongfangController


def main():
    tongfang = TongfangController()

    tongfang.lightbar.set_color(48, 0, 89)

    tongfang.acpi.watch_for_events()

    # while True:
    #     print("Speed: {0} RPM".format(tongfang.fan.get_speed()), ",",
    #           "Temp: {0}°C".format(tongfang.fan.get_temp()))


if __name__ == "__main__":
    main()
