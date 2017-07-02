#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from urllib.request import urlopen

f = urlopen('http://sample.scraping-book.com/dp')
# http ヘッダからエンコーディングを取得
encoding = f.info().get_content_charset(failobj='utf-8')
print('encoding: ', encoding, file=sys.stderr)

#デコード
text = f.read().decode(encoding)
#print(f.read())
#print(text)
print(f.info())

