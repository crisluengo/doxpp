"""
Admonition extension for Python-Markdown
========================================

Adds rST-style admonitions. Inspired by [rST][] feature with the same name.

[rST]: http://docutils.sourceforge.net/docs/ref/rst/directives.html#specific-admonitions  # noqa

See <https://Python-Markdown.github.io/extensions/admonition>
for documentation.

Original code Copyright [Tiago Serafim](https://www.tiagoserafim.com/).

All changes Copyright The Python Markdown Project

License: [BSD](https://opensource.org/licenses/bsd-license.php)

Further changes by Cris Luengo, to adapt generated HTML to m.css
 - Instead of `<div>` we use `<aside>`
 - Instead of `<p class="admonition-title">Title</p>` we use `<h4>Title</h4>`
 - Class name for the <aside> is "m-note". We add an additional class depending on the admonition type
"""

import markdown
import xml.etree.ElementTree as etree
import re


class AdmonitionExtension(markdown.extensions.Extension):
    """ Admonition extension for Python-Markdown. """

    def extendMarkdown(self, md):
        """ Add Admonition to Markdown instance. """
        md.registerExtension(self)

        md.parser.blockprocessors.register(AdmonitionProcessor(md.parser), 'admonition', 105)


class AdmonitionProcessor(markdown.blockprocessors.BlockProcessor):

    CLASSNAME1 = 'm-note'
    CLASSNAME2 = 'm-block'
    RE = re.compile(r'(?:^|\n)!!! ?([\w\-]+(?: +[\w\-]+)*)(?: +"(.*?)")? *(?:\n|$)')

    def __init__(self, parser):
        """Initialization."""

        super().__init__(parser)

        self.current_sibling = None
        self.content_indention = 0

    def get_sibling(self, parent, block):
        """Get sibling admonition.

        Retrieve the appropriate sibling element. This can get tricky when
        dealing with lists.

        """

        # We already acquired the block via test
        if self.current_sibling is not None:
            sibling = self.current_sibling
            block = block[self.content_indent:]
            self.current_sibling = None
            self.content_indent = 0
            return sibling, block

        sibling = self.lastChild(parent)

        if sibling is None or (sibling.get('class', '').find(self.CLASSNAME1) == -1 and
                               sibling.get('class', '').find(self.CLASSNAME2) == -1):
            sibling = None
        else:
            # If the last child is a list and the content is indented sufficient
            # to be under it, then the content's sibling is in the list.
            last_child = self.lastChild(sibling)
            indent = 0
            while last_child:
                if (
                    sibling and block.startswith(' ' * self.tab_length * 2) and
                    last_child and last_child.tag in ('ul', 'ol', 'dl')
                ):

                    # The expectation is that we'll find an <li> or <dt>.
                    # We should get it's last child as well.
                    sibling = self.lastChild(last_child)
                    last_child = self.lastChild(sibling) if sibling else None

                    # Context has been lost at this point, so we must adjust the
                    # text's indentation level so it will be evaluated correctly
                    # under the list.
                    block = block[self.tab_length:]
                    indent += self.tab_length
                else:
                    last_child = None

            if not block.startswith(' ' * self.tab_length):
                sibling = None

            if sibling is not None:
                self.current_sibling = sibling
                self.content_indent = indent

        return sibling, block

    def test(self, parent, block):

        if self.RE.search(block):
            return True
        else:
            return self.get_sibling(parent, block)[0] is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end():]  # removes the first line
        else:
            sibling, block = self.get_sibling(parent, block)

        block, theRest = self.detab(block)

        if m:
            klass, title = self.get_class_and_title(m)
            div = etree.SubElement(parent, 'aside')
            div.set('class', klass)
            if title:
                p = etree.SubElement(div, 'h4')
                p.text = title
        else:
            # Sibling is a list item, but we need to wrap it's content should be wrapped in <p>
            if sibling.tag in ('li', 'dd') and sibling.text:
                text = sibling.text
                sibling.text = ''
                p = etree.SubElement(sibling, 'p')
                p.text = text

            div = sibling

        self.parser.parseChunk(div, block)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)

    def get_class_and_title(self, match):
        klass, title = match.group(1).lower(), match.group(2)
        list = klass.split()
        type = list[0] if list else ''
        klass = list[1:]
        if self.CLASSNAME1 not in klass and self.CLASSNAME2 not in klass:
            klass = [self.CLASSNAME1] + klass
        if type == 'see':
            def_title = 'See also'
            type = 'm-default'
        elif type == 'note':
            def_title = 'Note'
            type = 'm-primary'
        elif type == 'attention':
            def_title = 'Attention'
            type = 'm-info'
        elif type == 'warning':
            def_title = 'Warning'
            type = 'm-warning'
        elif type == 'bug':
            def_title = 'Bug'
            type = 'm-danger'
        elif type in ['literature', 'author', 'authors', 'copyright', 'version', 'since', 'date']:
            def_title = type.capitalize()
            type = 'm-default'
        elif type == 'pre':
            def_title = 'Precondition'
            type = 'm-success'
        elif type == 'post':
            def_title = 'Postcondition'
            type = 'm-success'
        elif type == 'invariant':
            def_title = 'Invariant'
            type = 'm-success'
        elif type == 'par':
            def_title = None
            type = 'm-frame'
        elif type == 'aside':
            def_title = None
            type = 'm-dim'
        else:
            def_title = type.capitalize()
        klass = ' '.join(klass + [type])
        if title is None:
            # no title was provided
            title = def_title
        elif title == '':
            # an explicit blank title should not be rendered
            # e.g.: `!!! warning ""` will *not* render `p` with a title
            title = None
        return klass, title


def makeExtension(**kwargs):  # pragma: no cover
    return AdmonitionExtension(**kwargs)
