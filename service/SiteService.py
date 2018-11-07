import pymysql.cursors
import time
from module.Site import Site


class SiteService(object):
    def __init__(self):
        self.site_db = Site()

    def batch_add_site(self, site_array):
        """
            # 批量添加网站
            # site_array 网站数组
            # [
            # {
            #   "title":"网站标题",
            #   "domain":"网站域名（不可重复）",
            #   "keyword":"keyword",
            #   "description:"description",
            #   "server_id":"对应的服务器id"
            # },
            # {}
            # ]
        """
        connection = pymysql.connect(host='120.76.232.162',
                                     user='root',
                                     password='lcn@123',
                                     db='site_group',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                for site in site_array:
                    domain = str(site['domain']).replace('http://', '').replace('https://', '')
                    # Read a single record
                    sql = "SELECT * FROM `site` WHERE `domain`=%s LIMIT 1"
                    cursor.execute(sql, domain)
                    result = cursor.fetchone()
                    # print(result)
                    if result is None:
                        # 不存在，添加
                        web_path = domain.replace('.', '_')
                        sql = 'insert into site(title,web_path,template_id,server_id,`domain`,keyword,description,article_ids,state,create_time) value(%s, %s,(select id from site_template WHERE type=0 order by rand() LIMIT 1),%s, %s, %s, %s, (select id from article order by rand() LIMIT 1),%s, %s)'
                        cursor.execute(sql, (
                            str(site['title']), web_path, str(site['server_id']), domain, str(site['keyword']),
                            str(site['description']), 0, int(time.time())))
                        # 保存
                        connection.commit()
                        print("添加成功{%s}" % site['title'])
        finally:
            connection.close()

    # 获取要发布的网站
    def get_site_and_server(self, site_id):
        connection = pymysql.connect(host='120.76.232.162',
                                     user='root',
                                     password='lcn@123',
                                     db='site_group',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT site.*,servers.id as serverId,servers.host,servers.port,servers.user_name,servers.user_pwd,servers.nginx_config_path,servers.web_site_path FROM `site` left join `servers` on servers.id=site.server_id WHERE site.`id`=%s LIMIT 1"
                cursor.execute(sql, site_id)
                site = cursor.fetchone()
                return site

        finally:
            connection.close()

    def get_site_list(self):
        """
        获取所有网站列表
        :return:
        """
        return self.site_db.get_site_list()

    def add_single(self, site_model):
        """
        添加单个网站
        :param site_model:
        :return:
        """
        print("添加网站service｛%s｝" % site_model['title'])
        return self.site_db.add_single(site_model)

    def get_site_template_info(self, site_id):
        """
        获取网站（关联site_template表）
        :param site_id:
        :return:
        """
        return self.site_db.get_site_template_info(site_id)

    def get_site_server_info(self, site_id):
        """
        获取网站（关联servers表）
        :param site_id:
        :return:
        """
        return self.site_db.get_site_server_info(site_id)

    def get_site_content(self, site_id):
        """
        获取网站内容（包括site_template、article）仅限单页面类型的网站
        :param site_id:
        :return:
        """
        return self.site_db.get_site_content(site_id)

    def get_site_content_list(self):
        """
        获取网站内容（包括site_template、article）仅限单页面类型的网站
        :param :
        :return:
        """
        return self.site_db.get_site_content_list()

    def update_generated_state(self, site_id):
        """
        更新网站生成状态
        :param site_id:
        :return:
        """
        return self.site_db.update_generated_state(site_id)

    def update_released_state(self, site_id):
        """
        更新网站发布状态
        :param site_id:
        :return:
        """
        return self.site_db.update_released_state(site_id)
