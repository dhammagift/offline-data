"""Standalone page for any web server: wraps the artifact page (viewer/page.html) in a full HTML document.

usage: make_page.py   (writes viewer/index.html next to it)
"""
import os
here = os.path.dirname(os.path.abspath(__file__))
page = open(os.path.join(here, 'page.html'), encoding='utf-8').read()
cut = page.index('<style>')  # <title>, <meta>, <link> of the page go into <head>
head = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>[hidden]{display:none!important}img{max-width:100%}</style>\n' + page[:cut] + '</head><body>\n')
with open(os.path.join(here, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(head + page[cut:] + '\n</body></html>\n')
