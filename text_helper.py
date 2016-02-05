import string
import unicodedata
import sys
import Stemmer

import html_helper

stemmer = Stemmer.Stemmer('en')

punctuationTable = dict.fromkeys(i for i in xrange(sys.maxunicode)
                                 if unicodedata.category(unichr(i)).startswith('P'))


def prepare_text(text):
    text = unicode(text)
    text = html_helper.strip_tags(text)
    text = ' '.join(text.splitlines())
    text = text.translate(punctuationTable)
    words = [stemmer.stemWord(word) for word in text.split(' ') if word]
    text = string.join(words, ' ')
    return text

