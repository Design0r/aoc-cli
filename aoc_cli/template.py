from pathlib import Path

with open(Path(__file__).parent.parent / "inputs/REPLACE_DAY.txt") as f:
    file = f.read().strip()


def part_1() -> None:
    result = None
    print(f"Day REPLACE_DAY_NUM, Part 1: {result}")


def part_2() -> None:
    result = None
    print(f"Day REPLACE_DAY_NUM, Part 2: {result}")


if __name__ == "__main__":
    part_1()
    part_2()
