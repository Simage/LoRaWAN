import argparse
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "--file", "-f", type=argparse.FileType("r"), default=None, help="file to output"
)
parser.add_argument(
    "--delay", "-d", type=int, default=0, help="increase output verbosity"
)
args = parser.parse_args()

for line in args.file:
    sys.stdout.write(line)
    sys.stdout.flush()
    if args.delay:
        time.sleep(args.delay)
