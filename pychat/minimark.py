"""
    MiniMark
    ========
    Micro markdown environment:

        - **bold text**
        - *italic text*
        - `code block`
        - \"\"\"quotation\"\"\"
        - http://hyper.li/nk
        - line
          break
"""

import re

def _compile_links(md):
    md = re.sub("((https?:\/\/)?([\da-z-][\da-z\.-]*[\da-z-])\.([a-z\.]{2,6})([\/\w\.-]*)*\/?)", r"<a href='\1'>\1</a>", md)
    return md

def _compile_bold(md):
    md = re.sub("\*\*(.*?)\*\*", r"<strong>\1</strong>", md)
    return md

def _compile_italic(md):
    md = re.sub("\*(.*?)\*", r"<em>\1</em>", md)
    return md

def _compile_bit(md):
    md = re.sub("\*\*\*(.*?)\*\*\*", r"<em><strong>\1</strong></em>", md)
    return md

def _compile_code(md):
    md = re.sub("\`(.*?)\`", r"<code>\1</code>", md)
    return md

def _compile_quote(md):
    md = re.sub("\"\"\"(.*?)\"\"\"", r"<q>\1</q>", md)
    return md

def _compile_breaks(md):
    md = md.replace("\r\n", "\n")
    md = md.replace("\r", "\n")
    md = md.replace("\n", "<br>")
    while "<br><br>" in md:
        md = md.replace("<br><br>", "<br>")
    md = md.replace("<br>", "<br>\n")
    return md

def compile(md):
    md = _compile_breaks(md)
    md = _compile_quote(md)
    md = _compile_links(md)
    md = _compile_code(md)
    md = _compile_bit(md)
    md = _compile_bold(md)
    md = _compile_italic(md)
    return md
