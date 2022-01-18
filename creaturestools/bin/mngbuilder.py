import os
import sys

from creaturestools.mngmusic import *


def main():
    input_filename = sys.argv[1]
    filename_root = os.path.basename(os.path.splitext(input_filename)[0])
    if filename_root.lower().endswith(".mng"):
        filename_root = filename_root[: -len(".mng")]
    filename_dirname = os.path.dirname(input_filename)
    output_filename = filename_root + ".mng"

    with open(input_filename) as f:
        script = f.read()

    def myfileloaderfunc(name):
        filename = os.path.join(filename_dirname, name)
        child_filename = os.path.join(filename_dirname, filename_root, name)
        if not os.path.exists(filename) and os.path.exists(child_filename):
            filename = child_filename
        print("Loading {!r}".format(filename))
        with open(filename, "rb") as f:
            return f.read()

    write_mng_file(output_filename, script, myfileloaderfunc)
    print("Writing {!r}".format(output_filename))


if __name__ == "__main__":
    main()
