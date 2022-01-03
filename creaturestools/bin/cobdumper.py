import os
import sys

from PIL import Image

import creaturestools.cobs
from creaturestools.caos import format_c1_caos


def main():
    cob_filename = sys.argv[1]
    # TODO: warn if it doesn't end in .COB?

    filename_root = os.path.basename(os.path.splitext(cob_filename)[0])
    neighbor_filenames = os.listdir(os.path.dirname(cob_filename))
    rcb_filename = None
    for n in neighbor_filenames:
        root, ext = os.path.splitext(n.lower())
        if root == filename_root.lower() and ext.lower() == ".rcb":
            rcb_filename = os.path.join(os.path.dirname(cob_filename), n)
            break

    cob = creaturestools.cobs.read_cob1_file(cob_filename)
    if rcb_filename:
        rcb = creaturestools.cobs.read_cob1_file(rcb_filename)
    else:
        rcb = False

    sprite_filename = filename_root + ".png"
    print("* Writing {}".format(sprite_filename))
    cob.sprite.save(sprite_filename)

    caos2cob_filename = filename_root + ".cos"
    print("* Writing {}".format(caos2cob_filename))

    s = ""
    s += "** CAOS2Cob\n"
    s += "*# C1-Name {!r}\n".format(cob.name)
    s += "*# Cob File = {!r}\n".format(filename_root + ".cob")
    s += "*# Quantity Available = {}\n".format(cob.quantity_available)
    s += "*# Quantity Used = {}\n".format(cob.quantity_used)
    s += "*# Sprinkle = {}\n".format(str(cob.sprinkle).lower())
    s += "*# Expiry Date = {}-{}-{}\n".format(*cob.expiration_date)
    s += "*# Thumbnail = {!r}\n".format(sprite_filename)
    s += "*# Description = {!r}\n".format(cob.description)
    s += "\n"
    for install_script in cob.install_scripts:
        s += format_c1_caos("iscr," + install_script)
        s += "\n"
    for object_script in cob.object_scripts:
        s += format_c1_caos(object_script)
        s += "\n"
    if rcb:
        for install_script in rcb.install_scripts:
            s += format_c1_caos("rscr," + install_script)
            s += "\n"

    print(s.strip())
    with open(caos2cob_filename, "wb") as f:
        f.write((s.strip() + "\n").encode("ascii"))


if __name__ == "__main__":
    main()
