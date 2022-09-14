# -*- coding: utf-8 -*-
"""Markdown Subscript Extension

Extends the Python-Markdown library to support subscript text.

Given the text:
    The molecular composition of water is H~2~O.
Will output:
    <p>The molecular composition of water is H<sub>2</sub>O.</p>

:website: https://github.com/jambonrose/markdown_subscript_extension
:copyright: Copyright 2014-2018 Andrew Pinkham, Copyright 2022 Cris Luengo
:license: Simplified BSD, see LICENSE for details.
"""

from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor

# match ~, at least one character that is not ~, and ~ again
SUBSCRIPT_RE = r"()\~(.*?)\~"


def makeExtension(*args, **kwargs):
    """Inform Markdown of the existence of the extension."""
    return SubscriptExtension(*args, **kwargs)


class SubscriptExtension(Extension):
    """Extension: text between ~ characters will be subscripted."""

    def extendMarkdown(self, md):
        """Insert 'subscript' pattern before 'not_strong' pattern."""
        md.inlinePatterns.register(SimpleTagInlineProcessor(SUBSCRIPT_RE, "sub"), "subscript", 75)
