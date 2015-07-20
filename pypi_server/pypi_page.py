from collections import namedtuple
import re
import fnmatch
import html5lib


AnchorTag = namedtuple('HrefTag', ['href', 'name'])

def get_hrefs_from_html(html, exp=None, match_type=None):
    """
    exp is None: return all hrefs
    match_type: 
            'reg_exp': regular expresion match,
            'fnmatch': unix path match
    """
    parser = html5lib.parse(html, namespaceHTMLElements=False)
    if isinstance(exp, basestring) and match_type == 'reg_exp':
    	reg_exp =  re.compile(exp)

    for anchor in parser.findall('.//a[@href]'):
        href = anchor.get('href')
        name = anchor.text
        if exp is None:
            yield AnchorTag(href, name)
            continue
        if match_type == 'reg_exp' and reg_exp.match(name):
           yield AnchorTag(href, name)
        if match_type == 'fnmatch' and fnmatch.fnmatch(name, exp):
            yield AnchorTag(href, name)