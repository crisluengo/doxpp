# -*- coding: utf-8 -*-
"""Markdown Subscript Extension

Extends the Python-Markdown library to support subscript text.

Given the text:
    The molecular composition of water is H~2~O.
Will output:
    <p>The molecular composition of water is H<sub>2</sub>O.</p>

:website: https://github.com/jambonrose/markdown_subscript_extension
:copyright: Copyright 2014-2018 Andrew Pinkham
:license: Simplified BSD, see LICENSE for details.
"""

from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagPattern

# match ~, at least one character that is not ~, and ~ again
SUBSCRIPT_RE = r"(\~)([^\~]+)\2"


def makeExtension(*args, **kwargs):  # noqa: N802
    """Inform Markdown of the existence of the extension."""
    return SubscriptExtension(*args, **kwargs)


class SubscriptExtension(Extension):
    """Extension: text between ~ characters will be subscripted."""

    def extendMarkdown(self, md, md_globals):  # noqa: N802
        """Insert 'subscript' pattern before 'not_strong' pattern."""
        md.inlinePatterns.add(
            "subscript", SimpleTagPattern(SUBSCRIPT_RE, "sub"), "<not_strong"
        )
