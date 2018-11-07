from module.DbBase import DbBase

"""
服务器（servers表）module
"""


class Server(DbBase):

    def get_list(self, state):
        """
        获取所有有效的服务器list
        :param sql:sql语句，注意防注入
        :param dict_mark:是否以字典形式返回，默认为False
        :param args:传入参数
        :return:结果集
        """
        sql = "SELECT * FROM servers WHERE state=%s"
        result = self.db.execute_query(sql, True, state)
        return result

    def get_all(self):
        sql = "SELECT * FROM servers "
        result = self.db.execute_query(sql)
        return result

    def get_single(self, id):
        """
        根据id获取服务器
        :param id:
        :return:
        """
        sql = "SELECT * FROM servers WHERE id=%s"

        result = self.db.execute_query_single(sql, False, id)
        return result
