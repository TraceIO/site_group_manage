from module.DbBase import DbBase

"""
文章（article表）module
"""


class Article(DbBase):
    def get_site_list(self):
        sql = "SELECT * FROM article limit 10"
        result = self.db.execute_query(sql)
        return result
