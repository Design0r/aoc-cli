from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
import httpx
from html.parser import HTMLParser


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.is_article = False
        self.article_content = []

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.is_article = True

    def handle_endtag(self, tag):
        if tag == "article":
            self.is_article = False

    def handle_data(self, data):
        if self.is_article:
            self.article_content.append(data)


def get_latest_aoc_year() -> int:
    dt = datetime.now()
    year = dt.year
    month = dt.month

    return year - 1 if month < 12 else year


def parse_args() -> Namespace:
    latest_aoc_year = get_latest_aoc_year()

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    download_parser = subparsers.add_parser(
        "download", help="Download an Advent of Code Puzzle"
    )
    download_parser.add_argument(
        "path",
        type=str,
        help="The Path in which the inputs and samples will be created",
    )
    download_parser.add_argument(
        "-d",
        "--day",
        required=True,
        type=int,
        help="The Advent of Code day to download, a number between 1 and 25",
    )
    download_parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=latest_aoc_year,
        help=f"The Advent of Code year to download from, a number between 2015 and {latest_aoc_year}",
    )

    submit_parser = subparsers.add_parser(
        "submit", help="Submit your solution to Advent of Code"
    )
    submit_parser.add_argument("solution", type=int, help="The solution to submit")
    submit_parser.add_argument(
        "-d",
        "--day",
        required=True,
        type=int,
        help="The Advent of Code day to submit, a number between 1 and 25",
    )
    submit_parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=latest_aoc_year,
        help=f"The Advent of Code year to submit to, a number between 2015 and {latest_aoc_year}",
    )
    submit_parser.add_argument(
        "-p",
        "--part",
        required=True,
        type=int,
        help="The Advent of Code part you want to submit. Number 1 or 2",
    )

    cookie_parser = subparsers.add_parser(
        "cookie", help="Set and get your Advent of Code Session Cookie"
    )
    cookie_parser.add_argument(
        "cookie",
        type=str,
        nargs="?",
        help="set your session Cookie, if empty prints your active one",
    )

    return parser.parse_args()


def check(expression, error: str):
    if not expression:
        raise SystemExit(error)


def check_args(args: Namespace):
    latest_aoc_year = get_latest_aoc_year()
    if args.command == "download":
        check(args.day <= 25, f"Expected a Day between 1 and 25, got: {args.day}")
        check(
            2015 <= args.year <= latest_aoc_year,
            f"Expected a Year between 2015 and {latest_aoc_year}, got: {args.year}",
        )

    elif args.command == "submit":
        check(
            args.part
            in {
                1,
                2,
            },
            f"Expected Part Number to be 1 or 2, got: {args.part}",
        )
        check(args.day <= 25, f"Expected a Day between 1 and 25, got: {args.day}")
        check(
            2015 <= args.year <= latest_aoc_year,
            f"Expected a Year between 2015 and {latest_aoc_year}, got: {args.year}",
        )


def get_cookie() -> dict[str, str]:
    path = Path(__file__).parent / "cookies.txt"
    path.touch(exist_ok=True)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        text = 'Expected a Valid Session Cookie, use "aoc cookie --help" for more info'
        raise SystemExit(text)

    cookies = {}
    key, value = content.split("=")
    cookies[key] = value

    return cookies


def set_cookie(args: Namespace) -> str:
    if args.cookie.startswith("session="):
        cookie = args.cookie
    else:
        cookie = f"session={args.cookie}"

    with open(Path(__file__).parent / "cookies.txt", "w", encoding="utf-8") as f:
        f.write(cookie)

    return cookie


def get_input(args: Namespace) -> str:
    url = f"http://adventofcode.com/{args.year}/day/{args.day}/input"
    response = httpx.get(
        url,
        cookies=get_cookie(),
        follow_redirects=True,
    )

    return response.text


def submit_solution(args: Namespace) -> None:
    data = {"level": args.part, "answer": args.solution}
    url = f"https://adventofcode.com/{args.year}/day/{args.day}/answer"
    r = httpx.post(url, data=data, cookies=get_cookie())

    parser = ArticleParser()
    parser.feed(r.text)
    print("".join(parser.article_content).strip())


def create_project_structure(args: Namespace, input_text: str) -> None:
    base_path = Path(args.path)
    base_path.mkdir(exist_ok=True)
    input_path = base_path / "inputs"
    sample_path = base_path / "samples"
    src_path = base_path / "src"

    input_path.mkdir(exist_ok=True)
    sample_path.mkdir(exist_ok=True)
    src_path.mkdir(exist_ok=True)

    left_pad = args.day if len(str(args.day)) == 2 else f"0{args.day}"
    txt_file = f"day_{left_pad}.txt"

    # Generate Input File
    with open(input_path / txt_file, "w", encoding="utf-8") as f:
        f.write(input_text)

    # Generate Sample File
    (sample_path / txt_file).touch(exist_ok=True)

    # Generate Python File
    python_file = src_path / f"day_{left_pad}.py"
    if python_file.exists():
        return

    with open(Path(__file__).parent / "template.py", "r", encoding="utf-8") as f:
        template = (
            f.read()
            .strip()
            .replace("REPLACE_DAY_NUM", str(left_pad))
            .replace("REPLACE_DAY", f"day_{left_pad}")
        )

    with open(python_file, "w", encoding="utf-8") as f:
        f.write(template)


def main() -> int:
    args = parse_args()
    check_args(args)

    if args.command == "download":
        aoc_input = get_input(args)
        create_project_structure(args, aoc_input)

    elif args.command == "submit":
        submit_solution(args)

    elif args.command == "cookie":
        if args.cookie:
            print(set_cookie(args))
        else:
            print(f"session={get_cookie().get('session')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
