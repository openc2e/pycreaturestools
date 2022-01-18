import os
import sys

from creaturestools.mngmusic import *


def main():
    input_filename = sys.argv[1]
    filename_root = os.path.basename(os.path.splitext(input_filename)[0])
    output_directory = filename_root

    script, samples = read_mng_file(input_filename)

    try:
        os.makedirs(output_directory)
    except FileExistsError:
        pass

    script_filename = os.path.join(output_directory, filename_root + ".mng.txt")
    print("Writing {!r}".format(script_filename))
    with open(script_filename, "w") as f:
        f.write(script)

    for name, data in samples.items():
        wav_filename = os.path.join(output_directory, name + ".wav")
        print("Writing {!r}".format(wav_filename))
        with open(wav_filename, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    main()
