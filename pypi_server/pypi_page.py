from collections import namedtuple
import re
import html5lib


AnchorTag = namedtuple('HrefTag', ['link', 'name'])

def get_hrefs(html, exp, match_type='reg_exp'):
    parser = html5lib.parse(self.html, 
            namespaceHTMLElements=False)
    if isinstance(reg_exp, basestring):
    	if match_type == 'reg_exp':
    		reg_exp =  re.compile(reg_exp)
    	if match_type == 'glob':
    		match_exp = ''
    for anchor in parser.findall('.//a[@href]'):
            href = anchor.get('href')
            name = anchor.text
            if reg_exp.match(name):
               yield AnchorTag(href, name)