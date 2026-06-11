def process_data(d, t):
    """Processes input data based on a threshold."""
    r = []
    for x in d:
        if x > t:
            r.append(x * 2)
    return r
