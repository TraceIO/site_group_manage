"""
Description: DB工具类
@author: WangLeAi
@date: 2018/9/18
"""
from utils.PropertiesUtil import prop
from DBUtils.PooledDB import PooledDB
import importlib

"""
单例模式
"""


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


"""
DBUtils数据库连接池管理帮助类
采用单例模式，不会造成重复实例化
"""


@singleton
class DbPoolUtil(object):

    def __init__(self, config_file='database.properties'):
        """
        初始化
        :param config_file:  配置文件地址
        """
        properties_dic = prop.get_config_dict(config_file)

        config = {
            'host': properties_dic['host_mysql'],
            'port': int(properties_dic['port_mysql']),
            'database': properties_dic['database_mysql'],
            'user': properties_dic['user_mysql'],
            'password': properties_dic['password_mysql'],
            'charset': properties_dic['charset_mysql']
        }
        db_creator = importlib.import_module("pymysql")
        self.__pool = PooledDB(db_creator, maxcached=50, maxconnections=1000, maxusage=1000, **config)

    def execute_query(self, sql, dict_mark=True, args=()):
        """
        执行查询语句，获取结果
        :param sql:sql语句，注意防注入
        :param dict_mark:是否以字典形式返回，默认为False
        :param args:传入参数
        :return:结果集
        """
        result = []
        conn = self.__pool.connection()
        cur = conn.cursor()
        try:
            if dict_mark:
                cur.execute(sql, args)
                # name为description的第一个内容，表示为字段名
                fields = [desc[0] for desc in cur.description]
                rst = cur.fetchall()
                if rst:
                    result = [dict(zip(fields, row)) for row in rst]
            else:
                cur.execute(sql, args)
                result = cur.fetchall()
        except Exception as e:
            print('异常信息:' + str(e))
        cur.close()
        conn.close()
        return result

    def execute_query_single(self, sql, dict_mark=True, args=()):
        """
        执行查询语句，获取单行结果
        :param sql:sql语句，注意防注入
        :param dict_mark:是否以字典形式返回，默认为False
        :param args:传入参数
        :return:结果集
        """
        result = []
        conn = self.__pool.connection()
        cur = conn.cursor()
        try:
            if dict_mark:
                cur.execute(sql, args)
                # name为description的第一个内容，表示为字段名
                fields = [desc[0] for desc in cur.description]
                rst = cur.fetchone()
                if rst:
                    result = dict(zip(fields, rst))
            else:
                cur.execute(sql, args)
                result = cur.fetchone()
        except Exception as e:
            print('异常信息:' + str(e))
        cur.close()
        conn.close()
        return result

    def execute_update(self, sql, args=()):
        """
        执行增删改语句
        :param sql:sql语句，注意防注入
        :param args:传入参数
        :return:影响行数,mysql和sqlite有返回值
        """
        conn = self.__pool.connection()
        cur = conn.cursor()
        count = 0
        try:
            result = cur.execute(sql, args)
            conn.commit()
            count = result

        except Exception as e:
            print('异常信息:' + str(e))
            conn.rollback()
        cur.close()
        conn.close()
        return count

    def execute_proc(self, proc_name, args=()):
        """
        执行存储过程，mysql适用
        :param proc_name:存储过程/函数名
        :param args:参数
        :return:result为结果集，args_out为参数最终结果（用于out，顺序与传参一致）
        """
        result = ()
        args_out = ()
        conn = self.__pool.connection()
        cur = conn.cursor()
        try:
            cur.callproc(proc_name, args)
            result = cur.fetchall()
            if args:
                sql = "select " + ",".join(["_".join(["@", proc_name, str(index)]) for index in range(len(args))])
                cur.execute(sql)
                args_out = cur.fetchone()
            conn.commit()
        except Exception as e:
            print('异常信息:' + str(e))
            conn.rollback()
        cur.close()
        conn.close()
        return result, args_out
