import string

from creaturestools._io_utils import decode_creatures_string


def simplelexer(s):
    if not isinstance(s, str):
        s = decode_creatures_string(s)

    p = 0
    tokens = []
    while True:
        basep = p
        # check for end of input
        if p >= len(s):
            tokens.append(("eoi", ""))
            break
        # whitespace
        elif s[p : p + 1] in (" ", "\t"):
            while p < len(s) and s[p : p + 1] in (" ", "\t"):
                p += 1
            tokens.append(("whitespace", s[basep:p]))
            continue
        # newlines
        elif s[p : p + 1] == "\r":
            p += 1
            if p >= len(s):
                raise Exception("Expected '\n' after '\r', but got end-of-input")
            elif s[p : p + 1] != "\n":
                raise Exception(
                    "Expected '\n' after '\r', but got {}".format(s[p : p + 1])
                )
            p += 1
            tokens.append(("newline", s[basep:p]))
            continue
        elif s[p : p + 1] == "\n":
            p += 1
            tokens.append(("newline", s[basep:p]))
            continue
        # words and integers
        elif s[p : p + 1] in string.ascii_letters + string.digits + "-_.":
            while (
                p < len(s)
                and s[p : p + 1] in string.ascii_letters + string.digits + "-_."
            ):
                p += 1
            if s[basep:p].isdigit():
                tokens.append(("integer", s[basep:p]))
            else:
                tokens.append(("word", s[basep:p]))
            continue
        # at-sign
        elif s[p : p + 1] == "@":
            p += 1
            tokens.append(("atsign", s[basep:p]))
            continue
        # equals
        elif s[p : p + 1] == "=":
            p += 1
            tokens.append(("equals", s[basep:p]))
            continue
        # question
        elif s[p : p + 1] == "?":
            p += 1
            tokens.append(("?", s[basep:p]))
            continue
        # strings
        elif s[p : p + 1] == '"':
            p += 1
            while True:
                if p >= len(s):
                    raise Exception("While parsing string, got unexpected EOI")
                elif s[p : p + 1] == "\\":
                    p += 2
                    continue
                elif s[p : p + 1] == '"':
                    p += 1
                    break
                else:
                    p += 1
            tokens.append(("string", s[basep + 1 : p - 1]))
            continue
        # TODO: comments
        # error
        raise Exception(
            "While parsing, got unexpected {!r}, preceded by {!r}".format(
                s[p], s[max(p - 10, 0) : p]
            )
        )
    return tokens


# def parse_pray_source_file(fname_or_stream):
#     with open_if_not_stream(fname_or_stream, "rb") as f:
#         s = f.read()
#     t = _lex_pray_source(s)
#     p = 0
#
#     def _any_whitespace():
#         nonlocal p
#         while p < len(t) and t[p][0] in ("whitespace", "newline", "comment"):
#             p += 1
#
#     def _some_whitespace():
#         if p < len(t) and t[p][0] not in ("whitespace", "newline", "comment"):
#             raise Exception("Expected whitespace, but got {}".format(t[p]))
#         _any_whitespace()
#
#     # read encoding marker
#     _any_whitespace()
#     if p >= len(t) or t[p] != ("string", "en-GB"):
#         raise Exception("Expected '\"en-GB\"', but got {}".format(t[p]))
#     p += 1
#
#     blocks = []
#
#     while True:
#         _any_whitespace()
#         # check eoi
#         if p >= len(t):
#             break
#         elif t[p][0] == "eoi":
#             break
#         # group block
#         elif t[p] == ("word", "group"):
#             p += 1
#             _some_whitespace()
#
#             # get block type
#             if p >= len(t) or t[p][0] != "word" or len(t[p][1]) != 4:
#                 raise Exception(
#                     "Expected 4-letter ASCII block type, but got {}".format(t)
#                 )
#             block_type = t[p][1]
#             p += 1
#             _some_whitespace()
#
#             # get block name
#             if p >= len(t) or t[p][0] != "string":
#                 raise Exception("Expected block name, but got {}".format(t))
#             block_name = t[p][1]
#             p += 1
#             _some_whitespace()
#
#             tags = {}
#             while True:
#                 # key name
#                 if p >= len(t):
#                     break
#                 elif t[p][0] == "string":
#                     key_name = t[p][1]
#                 else:
#                     break
#                 p += 1
#                 _some_whitespace()
#
#                 # key value
#                 if p >= len(t):
#                     raise Exception("Expected key value, got end-of-input")
#                 elif t[p][0] == "atsign":
#                     p += 1
#                     _some_whitespace()
#
#                     if p >= len(t):
#                         raise Exception("Expected key value, got end-of-input")
#                     elif t[p][0] != "string":
#                         raise Exception("Expected key value, got {}".format(t[p]))
#                     else:
#                         key_value = pathlib.Path(t[p][1])
#                 elif t[p][0] == "string":
#                     key_value = t[p][1]
#                 elif t[p][0] == "integer":
#                     key_value = int(t[p][1])
#                 else:
#                     break
#                 p += 1
#                 _some_whitespace()
#
#                 tags[key_name] = key_value
#
#             blocks.append((block_type, block_name, tags))
#
#         # inline block
#         elif t[p] == ("word", "inline"):
#             p += 1
#             _some_whitespace()
#
#             # get block type
#             if p >= len(t) or t[p][0] != "word" or len(t[p][1]) != 4:
#                 raise Exception(
#                     "Expected 4-letter ASCII block type, but got {}".format(t)
#                 )
#             block_type = t[p][1]
#             p += 1
#             _some_whitespace()
#
#             # get block name
#             if p >= len(t) or t[p][0] != "string":
#                 raise Exception("Expected block name, but got {}".format(t))
#             block_name = t[p][1]
#             p += 1
#             _some_whitespace()
#
#             # get inline source
#             if p >= len(t) or t[p][0] != "string":
#                 raise Exception("Expected inline filename, but got {}".format(t))
#             inline_filename = t[p][1]
#             p += 1
#             _some_whitespace()
#
#             blocks.append((block_type, block_name, pathlib.Path(inline_filename)))
#
#         # error
#         else:
#             raise Exception("Expected 'group' or 'inline', but got {}".format(t[p]))
#
#     return blocks
