def main(issues) -> str:
    # We extract the URL field of an issue's metadata JSON
    urls = list(map(lambda x: x["url"], issues))
    return urls
