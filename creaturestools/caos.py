def format_c1_caos(script):
    commands = script.split(",")
    ret = ""
    indent = 0
    for command in commands:
        word = command.strip().split(" ")[0].lower()
        if word in ("else", "endi", "endm", "ever", "next", "repe", "retn", "untl"):
            indent -= 1
            # TODO: error if we went below 0?
        if word == "subr":
            ret += "\n"
        ret += "  " * indent + command.strip() + "\n"
        if word in (
            "doif",
            "else",
            "enum",
            "iscr",
            "loop",
            "reps",
            "rscr",
            "scrp",
            "subr",
        ):
            indent += 1
    return ret
