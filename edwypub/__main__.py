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
    parser.add_argument("url", nargs="+", help="set URL of article to convert to EPUB")
    parser.add_argument("--session", required=True, help="set Mediapart session identifier")
    args = parser.parse_args()
    for url in args.url:
        article = Article.from_url(url, args.session)
        basename = url.rsplit("/", 1)[-1]
        filename = f"{basename[:40]}.epub"
        article.save(filename)
        logging.info(filename)


if __name__ == "__main__":
    sys.exit(main())
