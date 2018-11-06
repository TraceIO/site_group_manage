import pymysql.cursors
import time


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
##
##
# 批量添加网站
def batch_add_site(site_array):
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
                    cursor.execute(sql, (str(site['title']),web_path, str(site['server_id']), domain, str(site['keyword']), str(site['description']),  0, int(time.time())))
                    # 保存
                    connection.commit()
                    print("添加成功{%s}" % site['title'])
    finally:
        connection.close()
