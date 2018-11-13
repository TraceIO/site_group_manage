from module.DbBase import DbBase
import time

"""
网站（site表）module
"""


class Site(DbBase):

    def get_site_list(self):
        """
        获取所有网站列表
        :return:
        """
        sql = "SELECT site.*,servers.name,servers.host,site_template.type,site_template.title as template_title FROM `site` left join `servers` on servers.id = site.server_id left join `site_template` on site_template.id = site.template_id ORDER BY site.id desc LIMIT 0,10 "
        result = self.db.execute_query(sql)
        return result

    def add_single(self, site_model):
        """
        添加单个网站
        :param site_model:
        :return:
        """
        sql = "INSERT INTO `site` (`title`, `web_path`,`template_id`, `domain`,`keyword`, `description`,`state`, `create_time`,`article_id`,`server_id`) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)"
        # cursor.execute(sql, (
        #                 str(title), str(web_path), template, str(domain), str(keyword), str(description), 0,
        #                 int(time.time()), str(article_ids), str(server_id)))
        self.db.execute_update(sql, (
            site_model['title'], site_model['web_path'], site_model['template_id'], site_model['domain'],
            site_model['keyword'], site_model['description'], 0, int(time.time()), site_model['article_id'],
            site_model['server_id']))

    def get_site_template_info(self, site_id):
        """
        获取网站（关联site_template表）
        :param site_id:
        :return:
        """
        sql = "SELECT site.*,site_template.type as template_type,site_template.path as template_path FROM `site` left join `site_template` on site_template.id = site.template_id WHERE site.`id`=%s LIMIT 1"
        return self.db.execute_query_single(sql, True, site_id)

    def get_site_server_info(self, site_id):
        """
        获取网站（关联servers表）
        :param site_id:
        :return:
        """
        sql = "SELECT site.*,servers.id as serverId,servers.host,servers.port,servers.user_name,servers.user_pwd,servers.nginx_config_path,servers.web_site_path FROM `site` left join `servers` on servers.id=site.server_id WHERE site.`id`=%s LIMIT 1"
        return self.db.execute_query_single(sql, True, site_id)

    def get_site_content(self, site_id):
        """
        获取网站内容（包括site_template、article）仅限单页面类型的网站
        :param site_id:
        :return:
        """
        sql = "SELECT site.*,st.`path` as template_path,st.`type` as template_type,a.title as article_title,a.`content` as article_content FROM site  left join site_template st on st.id = site.`template_id`  left join article a on a.id = site.`article_id` where site.id = %s LIMIT 1"
        return self.db.execute_query_single(sql, True, site_id)

    def get_site_content_list(self):
        """
        获取网站内容（包括site_template、article）仅限单页面类型的网站
        :param :
        :return:
        """
        sql = "SELECT site.*,st.`path` as template_path,st.`type` as template_type,a.title as article_title,a.`content` as article_content FROM site  left join site_template st on st.id = site.`template_id`  left join article a on a.id = site.`article_id` where site.is_generated = 0 LIMIT 100"
        return self.db.execute_query(sql)

    def update_generated_state(self, site_id):
        """
        更新网站生成状态
        :param site_id:
        :return:
        """
        sql = "UPDATE site SET is_generated=1 WHERE id=%s"
        return self.db.execute_update(sql, site_id)

    def update_released_state(self, site_id):
        """
        更新网站发布状态
        :param site_id:
        :return:
        """
        sql = "UPDATE site SET is_released=1 WHERE id=%s"
        return self.db.execute_update(sql, site_id)
