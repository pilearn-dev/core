import difflib
def generate_diff(old, new):
    d = difflib.Differ()
    output = list(d.compare(old.splitlines(), new.splitlines()))

    lines = []
    for line in output:
        if line[0:2] == "  ":
            lines.append([0, line[2:]])
        elif line[0:2] == "- ":
            lines.append([-1, line[2:]])
        elif line[0:2] == "+ ":
            lines.append([1, line[2:]])

    return lines
