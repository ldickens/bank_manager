from csv import reader


def parse_csv(file: str) -> list[list[str]]:
    data = []
    if not file:
        raise TypeError("No file selected")
    with open(file, newline="", mode="r") as f:
        parse = reader(f, dialect="excel")
        for line in parse:
            data.append(line)

    return data
