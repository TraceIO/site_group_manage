import re


def re_web_url(url):
    addr_regex = re.compile(r'''(
   (http://|https://)?
   ([a-z1-9A-Z]+\.)?
   ([a-z1-9A-Z]+)
   (\.com|\.cn|\.org|\.com\.cn|\.net|\.net\.cn|\.cc|\.tv|\.vip|\.xin|\.top|\.info)
   )''', re.VERBOSE)  # 匹配网址，

    match = addr_regex.match(url)
    return match
    # matchs = []
    # for groups in addr_regex.findall(response):
    #     matchs.append(groups[0])
    # if len(matchs) == 0:
    #     print('没有网址')
    # return matchs
