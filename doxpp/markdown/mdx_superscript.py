# -*- coding: utf-8 -*-
"""Markdown Superscript Extension

Extends the Python-Markdown library to support superscript text.

Given the text:
    2^10^ is 1024.
Will output:
    2<sup>10</sup> is 1024.

:website: https://github.com/jambonrose/markdown_superscript_extension
:copyright: Copyright 2014-2018 Andrew Pinkham, Copyright 2022 Cris Luengo
:license: Simplified BSD, see LICENSE for details.
"""

from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor

# match ^, at least one character that is not ^, and ^ again
SUPERSCRIPT_RE = r"()\^(.*?)\^"


def makeExtension(*args, **kwargs):
    """Inform Markdown of the existence of the extension."""
    return SuperscriptExtension(*args, **kwargs)


class SuperscriptExtension(Extension):
    """Extension: text between ^ characters will be superscripted."""

    def extendMarkdown(self, md):
        """Insert 'superscript' pattern before 'not_strong' pattern."""
        md.inlinePatterns.register(SimpleTagInlineProcessor(SUPERSCRIPT_RE, "sup"), "superscript", 74)
