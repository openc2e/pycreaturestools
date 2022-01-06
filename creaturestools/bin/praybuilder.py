import argparse
import os
import sys

from creaturestools._io_utils import *
from creaturestools.exceptions import *
from creaturestools.pray import *
from creaturestools.praysource import *


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file")
    opts.add_argument("--output-file")
    args = opts.parse_args()

    input_filename = args.file
    if args.output_file:
        output_filename = args.output_file
    else:
        output_filename = os.path.splitext(os.path.basename(input_filename))[0]
        if output_filename.lower().endswith(".pray"):
            output_filename = output_filename[: -len(".pray")]
        output_filename += ".agents"

    def fileloaderfunc(filename):
        return read_entire_file(os.path.join(os.path.dirname(input_filename), filename))

    blocks = parse_pray_source_file(input_filename)
    for (block_type, block_name, data) in blocks:
        print(f'block {block_type} "{block_name}"')
    loadedblocks = pray_load_file_references(blocks, fileloaderfunc)

    print(f"Writing {output_filename}")
    write_pray_file(output_filename, loadedblocks)


if __name__ == "__main__":
    main()
