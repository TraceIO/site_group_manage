from module.DbPoolUtil import DbPoolUtil

"""
DB基类
"""


class DbBase(object):
    def __init__(self):
        self.db = DbPoolUtil()
