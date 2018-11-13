import datetime
import random
import time
import os
import json

# from celery import Celery
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import pymysql.cursors
from jinja2 import Environment, FileSystemLoader
import paramiko
from core.Publisher import Publisher

from core.Generator import Generator

from flask_celery import make_celery
from service.SiteService import SiteService
from service.ServerService import ServerService
from service.SiteTemplateService import SiteTemplateService
from utils.regex_utils import re_web_url

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/1',
    CELERY_RESULT_BACKEND='redis://localhost:6379/7'
)
celery = make_celery(app)
celery.conf.update(app.config)


@app.route('/')
def hello_world():
    # return 'Hello World!'
    print("耗时的请求")
    result = long_time_def.delay()
    print(result.result)
    # result.wait()  # 65

    return redirect("/manage/login")
    # return Response(json.dumps(result), mimetype='application/json')


@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({'Location': url_for('taskstatus', task_id=task.id), "code": 202})


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task()
def add_together(a, b):
    return a + b


@celery.task()
def long_time_def():
    for _ in range(10000):
        for j in range(10000):
            i = 1
    return 'hello'


# 后台登录
@app.route('/manage/login', methods=['POST', 'GET'])
def manage_login():
    if request.method == "GET":
        print("后台登录GET")
        user = {'username': 'Miguel'}
        return render_template('/manage/login.html', title='Home', user=user)
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        print("后台登录POST｛%s,%s｝" % (username, password))
        return redirect("/manage/home")


# 管理后台首页
@app.route('/manage/home', methods=['POST', 'GET'])
def manage_home():
    return render_template('/manage/index.html', username='Richie')


@app.route('/manage/site_list', methods=['POST', 'GET'])
def manage_site_list():
    """
    网站列表
    :return:
    """
    site_service = SiteService()
    site_list = site_service.get_site_list()
    # print(site_list)

    return render_template('/manage/site_list.html', site_list=site_list)


@app.route('/manage/site_add', methods=['POST', 'GET'])
def manage_site_add():
    """
    添加网站（单个添加）
    :return:
    """
    if request.method == "GET":
        server_service = ServerService()
        servers = server_service.get_list(1)
        site_template_service = SiteTemplateService()
        templates = site_template_service.get_template_list(1, 0)
        print(templates)

        return render_template('/manage/site_add.html', title='Home', servers=servers, templates=templates)
    if request.method == "POST":
        title = request.form.get('title')
        server_id = request.form.get('server')
        keyword = request.form.get('keyword')
        domain = str(request.form.get('domain')).replace('http://', '').replace('https://', '')
        template = int(request.form.get('template'))
        description = request.form.get('description')
        web_path = domain.replace('.', '_')
        article_ids = str(request.form.get('content_id')).replace(',', "")
        # site service
        site_service = SiteService()
        site = {
            "title": title,
            "server_id": server_id,
            "web_path": web_path,
            "template_id": template,
            "domain": domain,
            "keyword": keyword,
            "description": description,
            "article_id": article_ids
        }

        site_service.add_single(site)
        print("添加网站POST｛%s,%s,%s,%s,%s｝" % (title, domain, template, keyword, description))

        return redirect("/manage/site_list")


# 批量添加网站
@app.route('/manage/site_add_batch', methods=['POST', 'GET'])
def manage_site_add_batch():
    """
    批量添加网站
    :return:
    """
    if request.method == "GET":
        server_service = ServerService()
        servers = server_service.get_list(1)

        return render_template('/manage/site_add_batch.html', servers=servers)
    if request.method == "POST":
        server_id = request.form.get('server')
        domain = request.form.get('domain')
        title = request.form.get('title')
        keyword = request.form.get('keyword')
        description = request.form.get('description')
        domain_array = str(domain).splitlines()
        title_array = str(title).splitlines()
        keyword_array = str(keyword).splitlines()
        desc_array = str(description).splitlines()

        site_array = []

        for index, d_url in enumerate(domain_array):
            a = re_web_url(d_url)
            if a is not None:
                print(d_url)
                site = {
                    "domain": d_url,
                    "title": title_array[index],
                    "keyword": keyword_array[index],
                    "description": desc_array[index],
                    "server_id": server_id
                }
                site_array.append(site)

        # 插入数据库
        # site service
        site_service = SiteService()
        site_service.batch_add_site(site_array)
        return redirect("/manage/site_list")


# 生成html
@app.route("/manage/site_generate/<int:id>", methods=['POST'])
def manage_site_generate(id):
    """
    生成html（单个生成）
    :param id:
    :return:
    """
    json_result = {}  # 返回的json result
    # site service
    site_service = SiteService()
    site = site_service.get_site_content(id)
    if site:
        if site['template_type'] is None:
            json_result = {
                "code": 500,
                "msg": "网站没有指定模版"
            }
            return Response(json.dumps(json_result), mimetype='application/json')
        if site['article_content'] is None:
            json_result = {
                "code": 502,
                "msg": "没有指定网站内容"
            }
            return Response(json.dumps(json_result), mimetype='application/json')

        # 开始生成
        PATH = os.path.dirname(os.path.abspath(__file__))
        generator = Generator()
        generator.generator_html(site, PATH)

        # 更新站点状态
        site_service.update_generated_state(id)

        json_result = {
            "code": 0,
            "msg": "SUCCESS"
        }
        return Response(json.dumps(json_result), mimetype='application/json')
    else:
        json_result = {
            "code": 404,
            "msg": "网站不存在"
        }
        return Response(json.dumps(json_result), mimetype='application/json')


# 生成html
@app.route("/manage/site_generate_batch")
def manage_site_generate_batch():
    if request.method == "GET":
        site = {}
        connection = pymysql.connect(host='120.76.232.162',
                                     user='root',
                                     password='lcn@123',
                                     db='site_group',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # 查询服务器
                server_sql = "SELECT COUNT(0) AS count FROM `site` WHERE is_generated = 0"
                cursor.execute(server_sql)
                site = cursor.fetchone()

        finally:
            connection.close()

        return render_template('/manage/site_generate_batch.html', site_count=site['count'])


# 启动批量生成后台运行
@app.route('/manage/site_generate_batch_start', methods=['POST'])
def manage_site_generate_batch_start():
    task = site_generate_task.apply_async()
    return jsonify({'Location': url_for('site_generate_status', task_id=task.id), "code": 202})


# 后台程序状态查询
@app.route('/manage/site_generate_status/<task_id>')
def site_generate_status(task_id):
    task = site_generate_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


# 批量生成html 后台程序
@celery.task(bind=True)
def site_generate_task(self):
    site_service = SiteService()
    site_list = site_service.get_site_content_list()
    # print(site_list)

    PATH = os.path.dirname(os.path.abspath(__file__))
    generator = Generator()

    count = 0
    for index, site in enumerate(site_list):

        if site['template_type'] is not None and site['article_content'] is not None:
            # 有模版，有内容，开始生成

            generator.generator_html(site, PATH)

            # 更新站点状态
            site_service.update_generated_state(site['id'])
            count = count + 1

        self.update_state(state='PROGRESS',
                          meta={'current': index, 'total': len(site_list),
                                'status': "OK"})
        time.sleep(1)

    return {'current': len(site_list), 'total': len(site_list), 'status': 'Task completed!',
            'result': count}


# 网站资讯内容弹窗
@app.route("/manage/site_content_iframe")
def manage_site_content_iframe():
    template_type = request.args.get('t', '2')
    print(template_type)
    content_list = {}

    connection = pymysql.connect(host='120.76.232.162',
                                 user='root',
                                 password='lcn@123',
                                 db='site_group',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT id,title FROM `article` LIMIT 0,10"
                cursor.execute(sql)
                content_list = cursor.fetchall()

                # print(site_list)
    finally:
        connection.close()

        # content_list.append(obj)

    return render_template('/manage/site_content_iframe.html', list=content_list, template=int(template_type))


# 发布网站(单个)
@app.route("/manage/site_publish/<int:id>", methods=['POST'])
def manage_site_publish(id):
    print("发布网站%s", str(id))
    site_service = SiteService()

    site = site_service.get_site_server_info(id)
    if site is None:
        # print("网站不存在")
        json_result = {
            "code": 404,
            "msg": "网站不存在"
        }
        return Response(json.dumps(json_result), mimetype='application/json')
    elif site['host'] is None:
        # print("服务器不存在")
        json_result = {
            "code": 500,
            "msg": "服务器不存在"
        }
        return Response(json.dumps(json_result), mimetype='application/json')

    # remote_dir = "/var/www/%s/" % site['web_path']
    remote_dir = site['web_site_path'] + site['web_path'] + "/"

    PATH = os.path.dirname(os.path.abspath(__file__))
    local_dir = os.path.join(PATH, 'output/%s/' % site['web_path'])

    # 发布网站到服务器 （上传网站、上传nginx conf）
    publisher = Publisher()
    publisher.sftp_put(remote_dir, local_dir, site['web_path'], site['host'], site['port'],
                       site['user_name'],
                       site['user_pwd'],
                       site['nginx_config_path'])

    # 更新网站状态为：已生成
    site_service.update_released_state(id)

    json_result = {
        "code": 0,
        "msg": "SUCCESS"
    }
    return Response(json.dumps(json_result), mimetype='application/json')
    # Connect to the database
    # connection = pymysql.connect(host='120.76.232.162',
    #                              user='root',
    #                              password='lcn@123',
    #                              db='site_group',
    #                              charset='utf8mb4',
    #                              cursorclass=pymysql.cursors.DictCursor)
    #
    # try:
    #     with connection.cursor() as cursor:
    #         # Read a single record
    #         sql = "SELECT site.*,servers.id as serverId,servers.host,servers.port,servers.user_name,servers.user_pwd,servers.nginx_config_path,servers.web_site_path FROM `site` left join `servers` on servers.id=site.server_id WHERE site.`id`=%s LIMIT 1"
    #         cursor.execute(sql, id)
    #         site = cursor.fetchone()
    #         # print(site)
    #         if site is None:
    #             print("网站不存在")
    #             return redirect("/manage/site_list")
    #         elif site['serverId'] is None:
    #             print("服务器不存在")
    #             return redirect("/manage/site_list")
    #         else:
    #             print("开始发布%s" % site['title'])
    #
    #             # remote_dir = "/var/www/%s/" % site['web_path']
    #             remote_dir = site['web_site_path'] + site['web_path']
    #
    #             PATH = os.path.dirname(os.path.abspath(__file__))
    #             local_dir = os.path.join(PATH, 'output/%s' % site['web_path'])
    #
    #             # 发布网站到服务器 （上传网站、上传nginx conf）
    #             publisher = Publisher()
    #             publisher.sftp_put(remote_dir, local_dir, site['web_path'], site['host'], site['port'],
    #                                site['user_name'],
    #                                site['user_pwd'])
    #
    #             # 更新发布状态
    #             # 更新网站状态为：已生成
    #             sql = "UPDATE site SET is_released=1 WHERE id=" + str(id)
    #             cursor.execute(sql)
    #             connection.commit()
    #
    # finally:
    #     connection.close()

    # 更新网站状态为：已生成
    # sql = "UPDATE site SET is_generated=1 WHERE id=" + str(id)
    # cursor.execute(sql)
    #
    # # connection is not autocommit by default. So you must commit to save
    # # your changes.
    # connection.commit()

    # site = {
    #     "t": "adsfs"
    # }

    # return Response(json.dumps(site), mimetype='application/json')


# sftp上传到服务器
# def sftp_put(remote_dir, local_dir, site_id, server_host, server_port, user_name, user_pwd):
#     # 连接服务器
#     transport = paramiko.Transport((server_host, server_port))
#     transport.connect(username=user_name, password=user_pwd)
#     sftp = paramiko.SFTPClient.from_transport(transport)
#
#     print('upload file start %s ' % datetime.datetime.now())
#
#     # remote_dir = "/var/www/www_hwz_cc/"
#
#     # PATH = os.path.dirname(os.path.abspath(__file__))
#     # local_dir = os.path.join(PATH, 'output/www_hwz_cc')
#
#     for root, dirs, files in os.walk(local_dir):
#         print('[%s][%s][%s]' % (root, dirs, files))
#
#         for filespath in files:
#             local_file = os.path.join(root, filespath)
#             print(11, '[%s][%s][%s][%s]' % (root, filespath, local_file, local_dir))
#
#             a = local_file.replace(local_dir, '').replace('\\', '/').lstrip('/')
#
#             print('01', a, '[%s]' % remote_dir)
#
#             remote_file = os.path.join(remote_dir, a).replace('\\', '/')
#
#             print(22, remote_file)
#             try:
#                 sftp.put(local_file, remote_file)
#             except Exception as e:
#
#                 sftp.mkdir(os.path.split(remote_file)[0])
#
#                 sftp.put(local_file, remote_file)
#
#                 print("66 upload %s to remote %s" % (local_file, remote_file))
#
#         for name in dirs:
#
#             local_path = os.path.join(root, name)
#
#             print(0, local_path, local_dir)
#
#             a = local_path.replace(local_dir, '').replace('\\', '/').lstrip('/')
#
#             print(1, a)
#
#             print(1, remote_dir)
#             # remote_path = os.path.join(remote_dir, a).replace('\\', '/')
#
#             remote_path = remote_dir + a
#
#             print(33, remote_path)
#
#             try:
#                 sftp.mkdir(remote_path)
#                 print(44, "mkdir path %s" % remote_path)
#             except Exception as e:
#
#                 print(55, e)
#     print('77,upload file success %s ' % datetime.datetime.now())
#     # 上传conf文件到nginx/conf.d
#     #
#     #
#     # # 将resutl.txt 上传至服务器 /tmp/result.txt
#     sftp.put(local_dir + '/' + site_id + '.conf', '/etc/nginx/conf.d/' + site_id + '.conf')
#     # # 将result.txt 下载到本地
#     # sftp.get('/tmp/result.txt', '~/yours.txt')
#     transport.close()


# 模版管理
@app.route("/manage/template_list")
def template_list():
    template_list = {}
    connection = pymysql.connect(host='120.76.232.162',
                                 user='root',
                                 password='lcn@123',
                                 db='site_group',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `site_template` LIMIT 0,10"
            cursor.execute(sql)
            template_list = cursor.fetchall()

            # print(site_list)
    finally:
        connection.close()

    return render_template('/manage/template_list.html', list=template_list)


# 服务管理
@app.route("/manage/server_list")
def server_list():
    server_list = {}
    connection = pymysql.connect(host='120.76.232.162',
                                 user='root',
                                 password='lcn@123',
                                 db='site_group',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `servers` LIMIT 0,10"
            cursor.execute(sql)
            server_list = cursor.fetchall()

            # print(site_list)
    finally:
        connection.close()

    return render_template('/manage/server_list.html', list=server_list)


if __name__ == '__main__':
    # app.run(debug=True, threaded=True)
    app.run(debug=True)
