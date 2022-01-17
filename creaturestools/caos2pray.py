from creaturestools._simplelexer import *
from creaturestools.praysource import *


def _escape(s):
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _caos2pray_lex_line(line):
    t = simplelexer(line)
    p = 0

    while t[p][0] == "whitespace":
        p += 1

    if ("equals", "=") in t:
        tagname = t[p][1]
        p += 1
        while t[p][0] == "whitespace" and t[p + 1][0] == "word":
            tagname += t[p][1] + t[p + 1][1]
            p += 2
        while t[p][0] == "whitespace":
            p += 1

        if not t[p][0] == "equals":
            raise Exception("Expected token of type '=', but got {}".format(t[p]))
        p += 1
        while t[p][0] == "whitespace":
            p += 1

        if t[p][0] == "integer":
            tagvalue = int(t[p][1])
        elif t[p][0] == "string":
            tagvalue = t[p][1]
        else:
            raise Exception(
                "Expected token of type 'number' or 'string', but got {}".format(t[p])
            )
        p += 1
        result = ("tag", tagname, tagvalue)

    else:
        if t[p][0] != "word":
            raise Exception("Expected token of type 'word', but got {}".format(t[p]))
        command = t[p][1]
        args = []
        p += 1
        while t[p][0] == "whitespace" and t[p + 1][0] in ("word", "string"):
            args.append(t[p + 1][1])
            p += 2
        result = ("command", command, args)

    while t[p][0] == "whitespace":
        p += 1
    if t[p][0] != "eoi":
        raise Exception("Expected end-of-input, but got {}".format(t[p]))

    return result


def parse_caos2pray_source_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        s = f.read().decode()
    lines = s.strip().split("\n")

    tag_blocks = []
    tag_values = {"Agent Type": 0}
    scripts = [s]
    dependencies = []
    file_blocks = []
    in_remove_script = False
    remove_script = None
    default_c3_name = None

    for line in lines:
        if not line.startswith("*#"):
            macro = line.strip().lower().split(" ")[0]
            if macro == "rscr":
                # TODO: better parsing?
                in_remove_script = True
                if not remove_script:
                    remove_script = ""
            if in_remove_script:
                remove_script += line + "\n"
            if macro in ("endm", "iscr", "scrp"):
                in_remove_script = False
            continue
        caos2prayline = line[len("*#") :]
        directive = _caos2pray_lex_line(caos2prayline)
        if directive[0] == "command":
            commandname = directive[1].lower()
            args = directive[2]
            if commandname == "pray-file":
                # ignore
                pass
            elif commandname == "ds-name":
                if len(args) != 1:
                    raise Exception("Expected single argument, but got {}".format(args))
                else:
                    default_c3_name = args[0]
                    tag_blocks.append(("DSAG", args[0]))
            elif commandname == "c3-name":
                if default_c3_name and len(args) == 0:
                    tag_blocks.append(("AGNT", default_c3_name))
                elif len(args) != 1:
                    raise Exception("Expected single argument, but got {}".format(args))
                else:
                    tag_blocks.append(("AGNT", args[0]))
            # elif commandname == 'wxyz-name': # TODO
            elif commandname == "depend":
                dependencies += args
            elif commandname == "inline":
                if len(args != 1):
                    raise NotImplementedError(
                        "Expected single argument to 'inline', but got {}".format(args)
                    )
                file_blocks += [a for a in args]
            elif commandname == "attach":
                dependencies += args
                file_blocks += [a for a in args]
            elif commandname == "link":
                scripts += [pathlib.Path(a) for a in args]
            elif commandname == "rscr":
                raise NotImplementedError("rscr")
        elif directive[0] == "tag":
            tagname = directive[1]
            tagvalue = directive[2]
            tagname = {
                "anim": "Agent Animation String",
                "anim file": "Agent Animation File",
                "desc": "Agent Description",
                # "anim start": "Agent Sprite First Image",
                # "anim img": "Agent Sprite First Image",
                # "anim image": "Agent Sprite First Image",
                # "first image": "Agent Sprite First Image",
                # "bioenergy": "Agent Bioenergy Value",
            }.get(tagname, tagname)
            if tagname in tag_values:
                raise ValueError("Got duplicate tag name {!r}".format(tagname))
            tag_values[tagname] = tagvalue
        else:
            assert False

    tag_values["Dependency Count"] = len(dependencies)
    for i, dep in enumerate(dependencies):
        tag_values["Dependency {}".format(i + 1)] = dep
        ext = dep.lower().split(".")[-1]
        if ext in ("wav", "mng"):
            depcategory = 1
        elif ext in ("c16", "s16"):
            depcategory = 2
        elif ext in ("gen", "gno"):
            depcategory = 3
        elif ext == "att":
            depcategory = 4
        # elif is_overlay_data:
        #     depcategory = 5
        elif ext == "blk":
            depcategory = 6
        elif ext == "catalogue":
            depcategory = 7
        else:
            raise NotImplementedError("File category for extension {!r}".format(ext))
        tag_values["Dependency Category {}".format(i + 1)] = depcategory

    tag_values["Script Count"] = len(scripts)
    for i, script in enumerate(scripts):
        tag_values["Script {}".format(i + 1)] = script

    if remove_script:
        tag_values["Remove script"] = remove_script

    tag_blocks = [
        (blocktype, blockname, tag_values) for (blocktype, blockname) in tag_blocks
    ]
    file_blocks = [
        ("FILE", filename, pathlib.Path(filename)) for filename in file_blocks
    ]

    return tag_blocks + file_blocks
