#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.request import urlopen

f = urlopen('http://sample.scraping-book.com/dp')
f.read()
print(f.getheader('Content-Type'))

