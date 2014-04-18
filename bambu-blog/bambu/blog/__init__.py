from django.conf import settings
from pyquery import PyQuery
from django.template.defaultfilters import truncatewords
from html2text import html2text
import string

__version__ = '0.2.3'
EXCERPT_LENGTH = getattr(settings, 'BLOG_EXCERPT_LENGTH', 30)

def plainify(html):
    doc = PyQuery('<body>%s</body>' % html)
    doc('img, audio, video, iframe, embed, object, script').remove()

    for a in doc('a, i, b, strong, em'):
        PyQuery(a).replaceWith(
            PyQuery(a).html()
        )

    for b in doc('blockquote'):
        PyQuery(b).replaceWith(
            PyQuery(b).html()
        )

    for a in doc('h1, h2, h3, h4, h5, h6'):
        PyQuery(a).replaceWith('<p>%s:</p>' % PyQuery(a).text())

    for p in doc('p'):
        t = (PyQuery(p).text() or '').strip()

        if not t:
            PyQuery(p).remove()
            continue

        if not t[-1] in string.punctuation:
            t += '. '

        if t.startswith('http:') or t.startswith('https:'):
            PyQuery(p).remove()

        if t.startswith('[') and t.endswith(']'):
            PyQuery(p).remove()

        PyQuery(p).html(t)

    for li in doc('li'):
        t = (PyQuery(li).text() or '').strip()
        if not t:
            PyQuery(li).remove()
            continue

        if not t[-1] in string.punctuation:
            t += '.'

        PyQuery(li).html(t)

    return html2text(
        doc.html()
    )

def excerpt(html, length = None):
    for tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        h = html.find('<%s' % tag)
        if h > -1:
            html = html[:h]

    doc = PyQuery('<body>%s</body>' % html)
    doc('img, audio, video, iframe, embed, object, script').remove()

    for a in doc('a, i, b, strong, em'):
        PyQuery(a).replaceWith(
            PyQuery(a).html()
        )

    for b in doc('blockquote'):
        PyQuery(b).replaceWith(
            '"%s"' % PyQuery(b).html()
        )

    for p in doc('p'):
        t = (PyQuery(p).text() or '').strip()

        if not t:
            PyQuery(p).remove()
            continue

        if not t[-1] in string.punctuation:
            t += '. '

        if t.startswith('http:') or t.startswith('https:'):
            PyQuery(p).remove()

        if t.startswith('[') and t.endswith(']'):
            PyQuery(p).remove()

        PyQuery(p).html(t)

    for li in doc('li'):
        t = (PyQuery(li).text() or '').strip()
        if not t:
            PyQuery(li).remove()
            continue

        if not t[-1] in string.punctuation:
            t += '.'

        PyQuery(li).html(t)

    excerpt = ''
    for p in doc('p'):
        if excerpt:
            excerpt += ' '

        excerpt += html2text(PyQuery(p).html())
        if len(excerpt.split()) >= 30:
            break

    if not length:
        length = EXCERPT_LENGTH

    return truncatewords(excerpt, length)
