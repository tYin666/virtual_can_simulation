import argparse
import time
from datetime import datetime


def parse_speed(value: str) -> int:
    try:
        speed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("speed must be an integer") from error
    if not 0 <= speed <= 240:
        raise argparse.ArgumentTypeError("speed must be between 0 and 240 km/h")
    return speed


def parse_positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be an integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def parse_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("count must be an integer") from error
    if count < 0:
        raise argparse.ArgumentTypeError("count must be zero or greater")
    return count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Console-only vehicle speed ECU simulator")
    parser.add_argument("--speed", type=parse_speed, default=72, help="simulated vehicle speed in km/h (0-240)")
    parser.add_argument("--interval-ms", type=parse_positive_int, default=500, help="time between updates in milliseconds")
    parser.add_argument("--count", type=parse_count, default=10, help="number of updates; use 0 to stream until interrupted")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sequence = 0
    print("CAN Speed Lab | console simulation | no CAN hardware", flush=True)
    try:
        while args.count == 0 or sequence < args.count:
            sequence += 1
            timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
            print(
                f"{timestamp} | SIMULATED BUS | ECU-A -> DISPLAY | "
                f"VEH_SPEED | {args.speed} km/h | seq={sequence:04d}",
                flush=True,
            )
            if args.count == 0 or sequence < args.count:
                time.sleep(args.interval_ms / 1000)
    except KeyboardInterrupt:
        print("Simulation stopped.", flush=True)


if __name__ == "__main__":
    main()