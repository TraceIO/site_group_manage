from module.DbBase import DbBase

"""
网站模版（site_template表）module
"""


class SiteTemplate(DbBase):

    def get_template_list(self, state, template_type):
        sql = "SELECT * FROM `site_template` WHERE state = %s  and `type`=%s"
        result = self.db.execute_query(sql, True, (state, template_type))
        return result
