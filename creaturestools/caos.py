def format_c1_caos(script):
    DEDENT_WORDS = ("else", "endi", "endm", "ever", "next", "repe", "retn", "untl")
    INDENT_WORDS = (
        "doif",
        "else",
        "enum",
        "iscr",
        "loop",
        "reps",
        "rscr",
        "scrp",
        "subr",
    )

    commands = script.split(",")
    ret = ""
    indent = 0
    for command in commands:
        word = command.strip().split(" ")[0].lower()
        last_word = command.strip().split(" ")[-1].lower()
        if word in DEDENT_WORDS:
            indent -= 1
            # TODO: error if we went below 0?
        if word == "subr":
            ret += "\n"
        ret += "  " * indent + command.strip() + "\n"
        if word in INDENT_WORDS and last_word not in DEDENT_WORDS:
            indent += 1
    return ret


def format_c2_caos(script):
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
            "etch",
            "iscr",
            "loop",
            "reps",
            "rscr",
            "scrp",
            "subr",
        ):
            indent += 1
    return ret
