# Advent of Code CLI

A CLI written in Python to Download new Advent of Code Puzzles and Submit your Solutions.

## Installation

1. Clone the Repo
2. pip install the cli

```shell

cd aoc-cli
pip install .
```

## Usage

1. Set yout Advent of code Session Cookie

   ```shell
   aoc cookie <Your Cookie>
   ```

2. Dowload a Puzzle

   ```shell
   aoc download <Path> --day <Day> --year <Year>
   ```

- Example:

  ```shell
  aoc download advent-of-code/ --day 1 --year 2023
  ```

3. Submit your Solution

   ```shell
   aoc submit <Solution> --day <Day> --year <Year> --part <Part>
   ```

- Example:

  ```shell
  aoc submit 9823 --day 1 --year 2023 --part 1
  ```

4. Further Help

   ```shell
   aoc --help
   ```
