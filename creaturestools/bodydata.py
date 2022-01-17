from creaturestools._io_utils import *
from creaturestools._simplelexer import *


def read_att_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        s = decode_creatures_string(f.read())

    t = simplelexer(s)
    p = 0
    while p < len(t) and t[p][0] in ("whitespace", "newline"):
        p += 1

    # parse one line
    lines = []

    while True:
        line = []

        while p < len(t) and t[p][0] in ("whitespace", "newline"):
            p += 1

        if t[p][0] != "integer":
            break

        while True:
            while t[p][0] == "whitespace":
                p += 1
                continue

            if t[p][0] == "eoi":
                break
            if t[p][0] == "newline":
                p += 1
                break

            if t[p][0] != "integer":
                raise Exception(
                    "Expected first integer in pair, but got {}".format(t[p])
                )
            x = int(t[p][1])
            p += 1
            # if t[p][0] != 'whitespace':
            #     raise Exception("Expected whitespace after first integer in pair, but got {}".format(t[p]))
            # p += 1
            #
            # if t[p][0] != 'integer':
            #     raise Exception("Expected second integer in pair, but got {}".format(t[p]))
            # y = int(t[p][1])
            # p += 1
            # print(x, y)
            line.append(x)

        if line:
            if len(line) % 2 != 0:
                raise Exception(
                    "Expected even number of integers on line, but got {}".format(line)
                )
            line = [tuple(line[i : i + 2]) for i in range(0, len(line), 2)]
            if lines and len(line) != len(lines[0]):
                raise Exception(
                    "Expected same number of coordinates as first line {}, but got {}".format(
                        lines[0], line
                    )
                )
            lines.append(line)

    notes = ""
    while t[p][0] != "eoi":
        notes += t[p][1]
        p += 1
    notes = notes.strip()

    return (lines, notes)
