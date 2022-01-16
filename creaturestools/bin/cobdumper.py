import argparse
import os
import sys

from creaturestools.cobs import *
from creaturestools.sprites import *


def main():
    opts = argparse.ArgumentParser()
    opts.add_argument("file")
    # TODO: argument to convert images
    args = opts.parse_args()

    cob_filename = args.file
    # TODO: warn if it doesn't end in .COB?

    filename_root = os.path.basename(os.path.splitext(cob_filename)[0])
    output_directory = filename_root

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    if is_cob2_file(cob_filename):
        blocks = read_cob2_file(cob_filename)

        def my_filename_filter(name, data):
            if name.lower().endswith(".s16"):
                data = io.BytesIO(data)
                image = stitch_to_sheet(read_s16_file(data))
                output_name = os.path.join(
                    output_directory, os.path.splitext(name)[0] + ".png"
                )
                print("* Writing {!r}".format(output_name))
                image.save(output_name)
            else:
                output_name = os.path.join(output_directory, name)
                print("* Writing {!r}".format(output_name))
                with open(output_name, "wb") as f:
                    f.write(data)
            return name

        source = generate_cob2_source(blocks, my_filename_filter)
        output_name = os.path.join(output_directory, filename_root + ".cob2.txt")
        print("* Writing {!r}".format(output_name))
        with open(output_name, "wb") as f:
            f.write(source.encode())
        # print(source)

    else:
        neighbor_filenames = os.listdir(os.path.dirname(cob_filename))
        rcb_filename = None
        for n in neighbor_filenames:
            root, ext = os.path.splitext(n.lower())
            if root == filename_root.lower() and ext.lower() == ".rcb":
                rcb_filename = os.path.join(os.path.dirname(cob_filename), n)
                break

        cob = read_cob1_file(cob_filename)
        if rcb_filename:
            print("* Found RCB file: {}".format(rcb_filename))
            rcb = read_cob1_file(rcb_filename)
        else:
            print("* Couldn't find RCB file")
            rcb = False

        def my_filename_filter(name, data):
            if not name.lower().endswith(".spr"):
                raise NotImplementedError(name)
            data = io.BytesIO(data)
            image = read_spr_file(data)[0]
            output_name = os.path.join(
                output_directory, os.path.splitext(name)[0] + ".png"
            )
            print("* Writing {}".format(output_name))
            image.save(output_name)
            return name

        s = generate_caos2cob1_source(cob, rcb, my_filename_filter)
        caos2cob_filename = os.path.join(output_directory, cob.name + ".cos")
        print("* Writing {}".format(caos2cob_filename))
        with open(caos2cob_filename, "wb") as f:
            f.write((s.strip() + "\n").encode("ascii"))

        print(s.strip())


if __name__ == "__main__":
    main()
