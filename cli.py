import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="BASH stdlib linter")
    parser.add_argument("-r", "--rebuild", action="store_true", help="Rebuild the cache from documentation")
    parser.add_argument("--check", nargs="+", help="Check the specified shell script files")
    return parser, parser.parse_args()
