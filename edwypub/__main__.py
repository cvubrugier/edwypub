#
# Copyright (C) 2024
# Christophe Vu-Brugier <cvubrugier@fastmail.fm>
#
# SPDX-License-Identifier: MIT
#

import argparse
import logging
import sys

from edwypub.core import Article


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="edwypub",
        description="Convert articles from Mediapart to EPUB e-books.",
    )
    parser.add_argument("url", nargs="+", help="set URL of article to convert to EPUB (can be a local file)")
    parser.add_argument("--session", help="set Mediapart session identifier")
    args = parser.parse_args()
    for url in args.url:
        article = Article.from_url(url, args.session) if url.startswith("https://") else Article.from_file(url)
        basename = url.rsplit("/", 1)[-1]
        basename = basename.rstrip(".html")
        filename = f"{basename[:40]}.epub"
        article.save(filename)
        logging.info(filename)


if __name__ == "__main__":
    sys.exit(main())
