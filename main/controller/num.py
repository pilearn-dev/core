def num2suff(x):
    if abs(x) >= 10**9:
        x = x / 10.0**9
        x = round(x, 1)
        if int(x) == x:
            x = int(x)
        return str(x).replace(".", ",") + "M"
    elif abs(x) >= 10**6:
        x = x / 10.0**6
        x = round(x, 1)
        if int(x) == x:
            x = int(x)
        return str(x).replace(".", ",") + "m"
    elif abs(x) >= 10**3:
        x = x / 10.0**3
        x = round(x, 1)
        print(x)
        if int(x) == x:
            x = int(x)
        return str(x).replace(".", ",") + "k"
    return x
