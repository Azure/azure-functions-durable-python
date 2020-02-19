def main(value):
    int_value = int(value)
    if int_value == 6:
        raise Exception("Bad Request")

    return value
