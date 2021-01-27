r"""
mdx_math_svg

Python-Markdown extension to render equations as embedded SVG.
No MathJax, no images. Real vector drawings.

The Markdown syntax recognized is:
```
$Equation$, \(Equation\)

$$
  Display Equations
$$

\[
  Display Equations
\]

\begin{align}
  Display Equations
\end{align}
```


Copyright 2021 by Cris Luengo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.


Based on:

- Extension logic, recognizing Markdown syntax:
  Arithmatex from PyMdown Extensions <https://github.com/facelessuser/pymdown-extensions>
  Copyright 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>
  MIT license.

- Converting LaTeX into SVG:
  latex2svg
  Copyright 2017, Tino Wagner
  MIT license.

- Tweaking the output of latex2svg for embedding into HTML5, and use of cache:
  latex2svgextra from m.css <https://github.com/mosra/m.css>
  Copyright 2017, 2018, 2019, 2020 Vladimír Vondruš <mosra@centrum.cz>
  MIT license.
"""

# Import statements for the Markdown extension component
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown import util as md_util
import xml.etree.ElementTree as ET

# Other import statements
import os
import sys
import subprocess
import shlex
import re
import copy
import html
import pickle
from tempfile import TemporaryDirectory
from ctypes.util import find_library
from hashlib import sha1


# -------------------------------------------------------
# Code below adapted from latex2svg and latex2svgextra
# -------------------------------------------------------

# TODO dvisvgm 2.2.2 was changed to "avoid scientific notation of floating
#      point numbers" (https://github.com/mgieseki/dvisvgm/blob/3facb925bfe3ab47bf40d376d567a114b2bee3a5/NEWS#L90),
#      meaning the default precision (6) is now used for the decimal points, so
#      you'll often get numbers like 194.283203, which is a bit too much
#      precision. Could be enough to have 4 decimal points max, but that would
#      be too little for <2.2.2, where it would mean you get just 194.28. We
#      need to detect the version somehow and then apply reasonable precision
#      based on that.
# TODO The --relative option should reduce the size of the SVG a bit. Does
#      this work with older versions too?

params = {
    'fontsize': 1,  # em (in the sense used by CSS)
    'template': r"""
\documentclass[12pt,preview]{standalone}
{{ preamble }}
\begin{document}
\begin{preview}
{{ code }}
\end{preview}
\end{document}
""",
    'preamble': r"""
\usepackage[utf8x]{inputenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{newtxtext}
\usepackage{newtxmath}
""",
    'latex_cmd': 'latex -interaction nonstopmode -halt-on-error',
    'dvisvgm_cmd': 'dvisvgm --no-fonts --exact',
    'libgs': None,
}

if not hasattr(os.environ, 'LIBGS') and not find_library('gs'):
    if sys.platform == 'darwin':
        # Fallback to homebrew Ghostscript on macOS
        homebrew_libgs = '/usr/local/opt/ghostscript/lib/libgs.dylib'
        if os.path.exists(homebrew_libgs):
            params['libgs'] = homebrew_libgs
    if not params['libgs']:
        print('Warning: libgs not found')


def _latex2svg(latex, working_directory):
    document = (params['template']
                .replace('{{ preamble }}', params['preamble'])
                .replace('{{ code }}', latex))

    with open(os.path.join(working_directory, 'code.tex'), 'w') as f:
        f.write(document)

    # Run LaTeX and create DVI file
    try:
        ret = subprocess.run(shlex.split(params['latex_cmd'] + ' code.tex'),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=working_directory, encoding='utf-8')
        if ret.returncode:
            # LaTeX prints errors on stdout instead of stderr (stderr is empty),
            # so print stdout instead
            print(ret.stdout)
            print('\n\n\nAttempting to compile the following:\n\n\n')
            print(document)
        ret.check_returncode()
    except FileNotFoundError:
        raise RuntimeError('latex not found')

    # Add LIBGS to environment if supplied
    env = os.environ.copy()
    if params['libgs']:
        env['LIBGS'] = params['libgs']

    # Convert DVI to SVG
    try:
        ret = subprocess.run(shlex.split(params['dvisvgm_cmd']+' code.dvi'),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=working_directory, env=env, encoding='utf-8')
        if ret.returncode:
            print(ret.stderr)
        ret.check_returncode()
    except FileNotFoundError:
        raise RuntimeError('dvisvgm not found')

    with open(os.path.join(working_directory, 'code.svg'), 'r') as f:
        svg = f.read()

    # Parse dvisvgm output for alignment
    def get_measure(output, name):
        regex = r'\b{}=([0-9.e-]+)pt'.format(name)
        match = re.search(regex, output)
        if match:
            return float(match.group(1))
        else:
            return None
    depth = get_measure(ret.stderr, 'depth')  # This is in pt

    return svg, depth


# dvisvgm 1.9.2 (on Ubuntu 16.04) doesn't specify the encoding part. However
# that version reports broken "depth", meaning inline equations are not
# vertically aligned properly, so it can't be made to work 100% correct anyway.
_patch_src = re.compile(r"""<\?xml version='1\.0'( encoding='UTF-8')?\?>
<!-- This file was generated by dvisvgm \d+\.\d+\.\d+ -->
<svg height='(?P<height>[^']+)pt' version='1.1' viewBox='(?P<viewBox>[^']+)' width='(?P<width>[^']+)pt' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
""")

# dvisvgm 2.6 has a different order of attributes. According to the changelog,
# the SVGs can be now hashed, which hopefully means that the output won't
# change every second day again. Hopefully.
_patch26_src = re.compile(r"""<\?xml version='1\.0' encoding='UTF-8'\?>
<!-- This file was generated by dvisvgm \d+\.\d+\.\d+ -->
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='(?P<width>[^']+)pt' height='(?P<height>[^']+)pt' viewBox='(?P<viewBox>[^']+)'>
""")

# version ignored by all UAs, safe to drop https://stackoverflow.com/a/18468348
_patch_dst = r"""<svg{attribs} style="width: {width:.3f}em; height: {height:.3f}em;{style}" viewBox="{viewBox}">
<title>
{formula}
</title>
"""

# Cache for rendered equations (source formula sha1 -> svg).
# _cache[1] is a counter (the "age") used to track which latex equations were used this time around.
# Unused equations can be pruned from the cache.
# The cache version should be bumped if the format of the cache is changed, cache files
# with an different version number can be discarded.
_cache_version = 0

def _empty_cache():
    return {
        'version': _cache_version,
        'age': 0,
        'fontsize': params['fontsize'],
        'data': {}
    }

_cache = _empty_cache()


# Counter to ensure unique IDs for multiple SVG elements on the same page.
# Reset back to zero on start of a new page for reproducible behavior.
counter = 0
_unique_src = re.compile(r"""(?P<name> id|xlink:href)='(?P<ref>#?)(?P<id>g\d+-\d+|page\d+)'""")
_unique_dst = r"""\g<name>='\g<ref>eq{counter}-\g<id>'"""


_remove_svg_header = re.compile(r"""<\?xml version='1\.0'( encoding='UTF-8')?\?>
<!-- This file was generated by dvisvgm \d+\.\d+\.\d+ -->
""")

#_remove_svg_namespace = re.compile(r"(xmlns='http://www.w3.org/2000/svg')|(xmlns:xlink='http://www.w3.org/1999/xlink')")
_remove_svg_namespace = re.compile(r"xmlns='http://www.w3.org/2000/svg'")


def latex2svg(latex):
    """Convert LaTeX to SVG using dvisvgm.

    Uses settings in the dict mdx_math_svg.params.

    Uses a cache. mdx_math_svg.load_cache(file) will load cached data
    from file, and mdx_math_svg.save_cache(file) will save the current
    cache to disk. Use these commands at the start and end of your
    session.

    Parameters
    ----------
    latex : str
        LaTeX code to render.

    Returns
    -------
    svg : str
       SVG data.
    """
    global _cache

    # Find latex code in cache
    hash = sha1(latex.encode('utf-8')).digest()
    if hash in _cache['data']:
        svg = _cache['data'][hash][1]
        #print('Found the following LaTeX in the cache:', latex)
    else:
        # It's not in the cache: compute SVG
        with TemporaryDirectory() as tmpdir:
            #print('Rendering the following LaTeX:', latex)
            svg, depth = _latex2svg(latex, tmpdir)

        # Patch SVG
        pt2em = params['fontsize'] / 10  # Unfortunately, 12pt(==1em) font is not 1em.
        if latex.startswith(r'\('):  # Inline
            style = ' vertical-align: -{:.3f}em;'.format(depth * pt2em)
        else:
            style = ''
        def repl(match):
            return _patch_dst.format(
                width=float(match.group('width')) * pt2em,
                height=float(match.group('height')) * pt2em,
                style=style,
                viewBox=match.group('viewBox'),
                attribs='',
                formula=html.escape(latex))
        # There are two incompatible preambles, if the first fails try the second
        svg, found = _patch_src.subn(repl, svg)
        if not found:
            svg, found = _patch26_src.subn(repl, svg)
            assert found

    # Put svg in cache, note that if it was already there, we're just updating the counter
    _cache['data'][hash] = (_cache['age'], svg)

    # Make element IDs unique
    global counter
    counter += 1
    svg = _unique_src.sub(_unique_dst.format(counter=counter), svg)

    return svg


def load_cache(file):
    """Loads cached SVG data. Use at the start of a session to avoid
    repeating renderings done in the previous session.
    """
    global _cache

    try:
        with open(file, 'rb') as f:
            _cache = pickle.load(f)
            if not _cache or not isinstance(_cache, dict) or \
                    'version' not in _cache or _cache['version'] != _cache_version or \
                    'fontsize' not in _cache or _cache['fontsize'] != params['fontsize']:
                # Reset the cache if not valid or not expected version
                # If font size changes, we also need to flush the cache
                _cache = _empty_cache()
            else:
                # Otherwise bump cache age
                _cache['age'] += 1
    except FileNotFoundError:
        _cache = _empty_cache()


def save_cache(file):
    """Saves cached SVG data. Use at the end of a session so they
    can be recovered in your next session.
    """
    global _cache

    # Don't save any file if there is nothing
    if not _cache['data']:
        return

    # Prune entries that were not used
    cache_to_save = _cache.copy()
    cache_to_save['data'] = {}
    for hash, entry in _cache['data'].items():
        if entry[0] != _cache['age']:
            continue
        cache_to_save['data'][hash] = entry

    with open(file, 'wb') as f:
        pickle.dump(cache_to_save, f)


# -------------------------------------------------------
# Code below adapted from Arithmatex
# -------------------------------------------------------

def _escape_chars(md, echrs):
    """
    Add chars to the escape list.
    Don't just append as it modifies the global list permanently.
    Make a copy and extend **that** copy so that only this Markdown
    instance gets modified.
    """

    escaped = copy.copy(md.ESCAPED_CHARS)
    for ec in echrs:
        if ec not in escaped:
            escaped.append(ec)
    md.ESCAPED_CHARS = escaped


class InlineMathSvgPattern(InlineProcessor):
    """MathSvg inline pattern handler."""

    ESCAPED_BSLASH = '%s%s%s' % (md_util.STX, ord('\\'), md_util.ETX)

    def __init__(self, pattern, config, md):
        """Initialize."""

        self.inline_class = config.get('inline_class', '')

        InlineProcessor.__init__(self, pattern, md)

    def handleMatch(self, m, data):
        """Handle inline content."""

        # Handle escapes
        escapes = m.group(1)
        if not escapes:
            escapes = m.group(4)
        if escapes:
            return escapes.replace('\\\\', self.ESCAPED_BSLASH), m.start(0), m.end(0)

        # Handle LaTeX
        latex = m.group(3)
        if not latex:
            latex = m.group(6)
        latex = r'\(' + latex + r'\)'
        svg = latex2svg(latex)

        el = ET.Element('span', {'class': self.inline_class})
        el.text = self.md.htmlStash.store(svg)

        return el, m.start(0), m.end(0)


class BlockMathSvgProcessor(BlockProcessor):
    """MathSvg block pattern handler."""

    def __init__(self, pattern, config, md):
        """Initialize."""

        self.display_class = config.get('display_class', '')
        self.md = md

        self.match = None
        self.pattern = re.compile(pattern)

        BlockProcessor.__init__(self, md.parser)

    def test(self, parent, block):
        """Return 'True' for future Python Markdown block compatibility."""

        self.match = self.pattern.match(block) if self.pattern is not None else None
        return self.match is not None

    def run(self, parent, blocks):
        """Find and handle block content."""

        blocks.pop(0)

        escaped = False
        latex = self.match.group('math')
        if not latex:
            latex = self.match.group('math3')
        if not latex:
            latex = self.match.group('math2')
            escaped = True  # math2 includes the '\begin{env}' and '\end{env}'
        if not escaped:
            latex = r'\[' + latex + r'\]'
        svg = latex2svg(latex)

        el = ET.SubElement(parent, 'div', {'class': self.display_class})
        el.text = self.md.htmlStash.store(svg)

        return True


RE_SMART_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)(?!\s)((?:\\.|[^\\$])+?)(?<!\s)(?:\$))'
RE_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)((?:\\.|[^\\$])+?)(?:\$))'
RE_BRACKET_INLINE = r'(?:(?<!\\)((?:\\{2})+?)(?=\\\()|(?<!\\)(\\\()((?:\\[^)]|[^\\])+?)(?:\\\)))'

RE_DOLLAR_BLOCK = r'(?P<dollar>[$]{2})(?P<math>((?:\\.|[^\\])+?))(?P=dollar)'
RE_TEX_BLOCK = r'(?P<math2>\\begin\{(?P<env>[a-z]+\*?)\}(?:\\.|[^\\])+?\\end\{(?P=env)\})'
RE_BRACKET_BLOCK = r'\\\[(?P<math3>(?:\\[^\]]|[^\\])+?)\\\]'


class MathSvgExtension(Extension):
    """Adds MathSvg extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'inline_class': [
                [''],
                "Inline math is SVG wrapped in a <span> tag, this option adds a class name to it - Default: ''"
            ],
            'display_class': [
                [''],
                "Display math is SVG wrapped in a <div> tag, this option adds a class name to it - Default: ''"
            ],
            "smart_dollar": [True, "Use MathSvg's smart dollars - Default True"],
            "block_syntax": [
                ['dollar', 'square', 'begin'],
                'Enable block syntax: "dollar" ($$...$$), "square" (\\[...\\]), and '
                '"begin" (\\begin{env}...\\end{env}) - Default: ["dollar", "square", "begin"]'
            ],
            "inline_syntax": [
                ['dollar', 'round'],
                'Enable block syntax: "dollar" ($$...$$), "bracket" (\\(...\\)) '
                ' - Default: ["dollar", "round"]'
            ],
            "fontsize": [1, "Font size in em for rendering LaTeX equations - Default 1"]
        }

        super(MathSvgExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Extend the inline and block processor objects."""

        md.registerExtension(self)
        _escape_chars(md, ['$'])

        config = self.getConfigs()

        # Inline patterns
        allowed_inline = set(config.get('inline_syntax', ['dollar', 'round']))
        smart_dollar = config.get('smart_dollar', True)
        inline_patterns = []
        if 'dollar' in allowed_inline:
            inline_patterns.append(RE_SMART_DOLLAR_INLINE if smart_dollar else RE_DOLLAR_INLINE)
        if 'round' in allowed_inline:
            inline_patterns.append(RE_BRACKET_INLINE)
        if inline_patterns:
            inline = InlineMathSvgPattern('(?:%s)' % '|'.join(inline_patterns), config, md)
            md.inlinePatterns.register(inline, 'mathsvg-inline', 189.9)

        # Block patterns
        allowed_block = set(config.get('block_syntax', ['dollar', 'square', 'begin']))
        block_pattern = []
        if 'dollar' in allowed_block:
            block_pattern.append(RE_DOLLAR_BLOCK)
        if 'square' in allowed_block:
            block_pattern.append(RE_BRACKET_BLOCK)
        if 'begin' in allowed_block:
            block_pattern.append(RE_TEX_BLOCK)
        if block_pattern:
            block = BlockMathSvgProcessor(r'(?s)^(?:%s)[ ]*$' % '|'.join(block_pattern), config, md)
            md.parser.blockprocessors.register(block, "mathsvg-block", 79.9)

        # Configure latex2svg
        global params
        params['fontsize'] = config.get('fontsize', 1)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return MathSvgExtension(*args, **kwargs)
