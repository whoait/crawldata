import re

_EXCESS_SPACES   = re.compile(r"(\s*&nbsp;)+\s*")
_EMPTY_TAGS      = re.compile(r"<(?P<tag>\w+)>\s*?</(?P=tag)>")
_EMPTY_PARAS     = re.compile(r"\s*(<p>\s*?</p>|<li>\s*?</li>)\s*", re.I)
_EXCESS_PARA_SPACES = re.compile(r"<(?P<tag>(p|li))>\s+", re.I)
_EXCESS_NEWLINES = re.compile(r"[\r\n]+")

def clean_html(html):
    if not html:
        return ''
    else:
        s = _EXCESS_SPACES.sub(" ", html.strip())
        s = _EMPTY_TAGS.sub("", s)
        s = _EMPTY_PARAS.sub("", s)
        s = _EXCESS_PARA_SPACES.sub(r"<\g<tag>>", s)
        s = _EXCESS_NEWLINES.sub("\n", s)
        return s

def clean_text(s):
    return re.sub(r"\s+", " ", s.strip())
