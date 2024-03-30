#
# Copyright (C) 2024
# Christophe Vu-Brugier <cvubrugier@fastmail.fm>
#
# SPDX-License-Identifier: MIT
#

import hashlib
from typing import Self

import requests
from bs4 import BeautifulSoup
from ebooklib import epub

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
TIMEOUT = 5


class Article:
    """
    Encapsulates an article downloaded from Mediapart
    """

    title: str
    author: str
    content: str

    def __init__(self, title: str, author: str, content: str):
        self.title = title
        self.author = author
        self.content = content

    @classmethod
    def from_file(cls, filename: str) -> Self:
        """
        Build article from file
        """
        with open(filename, encoding="utf-8") as fd:
            full_content = fd.read()
            title, author, content = cls._extract(full_content)
            return cls(title, author, content)

    @classmethod
    def from_url(cls, url: str, session_id: str) -> Self:
        """
        Build article from URL
        """
        full_content = cls._download(url, session_id)
        title, author, content = cls._extract(full_content)
        return cls(title, author, content)

    @staticmethod
    def _download(url: str, session_id: str) -> str:
        headers = {
            "User-Agent": USER_AGENT,
        }
        cookies = {
            "MPSESSID": session_id,
        }
        resp = requests.get(url=url, headers=headers, cookies=cookies, timeout=TIMEOUT)
        if not resp.ok:
            msg = f"failed to download {url}"
            raise RuntimeError(msg)
        return resp.text

    @staticmethod
    def _extract(content: str) -> tuple[str, str, str]:
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string
        title = title.removesuffix(" | Mediapart")

        author = soup.find("meta", attrs={"name": "author"})
        author = author.get("content")

        body = soup.find("div", class_="news__body__center__article")
        for h2 in body.find_all("h2"):
            if h2.contents[0] == "Écouter l\N{RIGHT SINGLE QUOTATION MARK}article":
                h2.extract()
        for fig in body.find_all("figure"):
            fig.extract()
        for aside in body.find_all("aside"):
            aside.extract()
        for span_hidden in body.find_all("span", attrs={"aria-hidden": "true"}):
            span_hidden.extract()

        content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="author" content="{author}">
</head>
<body>
<article>
<header>
<h1>{title}</h1>
<address>Par <a rel="author" href="https://www.mediapart.fr/">{author}</a></address>
</header>
{body}
</article>
</body>
</html>"""
        return str(title), str(author), str(content)

    def save(self, filename: str) -> None:
        """
        Save article to EPUB file
        """
        book = epub.EpubBook()
        identifier = hashlib.sha3_256(self.title.encode()).hexdigest()
        book.set_identifier(identifier)
        book.set_language("fr")
        book.set_direction("ltr")
        book.set_title(self.title)
        book.add_metadata("DC", "publisher", "Mediapart")
        book.add_author(self.author)
        c1 = epub.EpubHtml(
            title="article",
            file_name="article.html",
            lang="fr",
        )
        c1.set_content(self.content)
        book.add_item(c1)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.toc = [
            c1,
        ]
        book.spine = [
            c1,
        ]
        epub.write_epub(filename, book)
