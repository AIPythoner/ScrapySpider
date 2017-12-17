# -*- coding: utf-8 -*-
import hashlib
import re

def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    match_obj = re.match(".*?(\d+).*", text)
    if match_obj:
        num = int(match_obj.group(1))
    else:
        num = 0
    return num





















