def generate_diff(old, new):
    i_old = i_new = 0
    diff = []
    if old == "":
        old = []
    else:
        old = old.split("\n")
    if new == "":
        new = []
    else:
        new = new.split("\n")
    if old == []:
        return [[1, n] for n in new]
    if new == []:
        return [[-1, o] for o in old]
    while i_new < len(new):
        old1 = old[i_old]
        new1 = new[i_new]
        if old1 == new1:
            diff.append([0, old1])
            i_old += 1
        else:
            if new1 in old[i_old:]:
                while new1 != old1:
                    old1 = old[i_old]
                    diff.append([-1, old1])
                    i_old += 1
                del diff[-1]
                i_old -= 1
                continue
            elif old1 in new[i_new:]:
                diff.append([1, new1])
            else:
                diff.append([1, new1])
                diff.append([-1, old1])
                i_old += 1
        if i_old >= len(old):
            i_new += 1
            while i_new < len(new):
                new1 = new[i_new]
                diff.append([1, new1])
                i_new += 1
        i_new += 1
    if i_old < len(old):
        while i_old < len(old):
            old1 = old[i_old]
            diff.append([-1, old1])
            i_old += 1
    return diff
