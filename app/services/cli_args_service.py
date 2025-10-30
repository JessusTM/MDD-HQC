import sys
from pathlib import Path
import argparse

class CliArgs:
    def read_cli_args(self):
        parser              = argparse.ArgumentParser(add_help=False)
        parser.add_argument("-i", "--input", required=True)
        args                = parser.parse_args()
        inputPath : Path    = Path(args.input)
        if not inputPath.exists() : sys.exit(1)
        return inputPath
