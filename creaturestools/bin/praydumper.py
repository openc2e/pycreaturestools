import os
import sys

from creaturestools.pray import *


def main():
    input_filename = sys.argv[1]
    filename_root = os.path.basename(os.path.splitext(input_filename)[0])
    output_directory = filename_root

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    def filenamefilter(relative_filename, data):
        output_filename = os.path.join(output_directory, relative_filename)
        print(f"Writing {output_filename}")
        with open(output_filename, "wb") as f:
            f.write(data)
        return relative_filename

    blocks = read_pray_file(input_filename)

    pray_source = pray_to_pray_source(blocks, filenamefilter)

    output_filename = os.path.join(output_directory, filename_root + ".pray.txt")
    print(f"Writing {output_filename}")
    with open(output_filename, "wb") as f:
        f.write(pray_source.encode("utf-8"))  # I guess?


if __name__ == "__main__":
    main()
