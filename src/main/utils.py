def flatten(l: list):
    """Flattens a list of lists."""
    if False in [type(item) is list for item in l]:
        raise ValueError("Expected all items to be of type `list`")

    return [sub_item for item in l for sub_item in item]