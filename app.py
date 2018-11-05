import datetime
import time
import os
import json
from flask import Flask, render_template, Response, request, redirect
import pymysql.cursors
from jinja2 import Environment, FileSystemLoader
import paramiko

app = Flask(__name__)


@app.route('/')
def hello_world():
    # return 'Hello World!'
    return redirect("/manage/login")


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


# 网站列表
@app.route('/manage/site_list', methods=['POST', 'GET'])
def manage_site_list():
    site_list = {}
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
                sql = "SELECT site.*,servers.name,servers.host,site_template.type,site_template.title as template_title FROM `site` left join `servers` on servers.id = site.server_id left join `site_template` on site_template.id = site.template_id LIMIT 0,10"
                cursor.execute(sql)
                site_list = cursor.fetchall()

                print(site_list)
    finally:
        connection.close()

    return render_template('/manage/site_list.html', title='Home', site_list=site_list)


# 添加网站
@app.route('/manage/site_add', methods=['POST', 'GET'])
def manage_site_add():
    if request.method == "GET":
        servers = {}
        templates = {}
        connection = pymysql.connect(host='120.76.232.162',
                                     user='root',
                                     password='lcn@123',
                                     db='site_group',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # 查询服务器
                server_sql = "SELECT * FROM `servers` WHERE state = 1"
                cursor.execute(server_sql)
                servers = cursor.fetchall()
                # 查询模版
                template_sql = "SELECT * FROM `site_template` WHERE state = 1  and type=0"
                cursor.execute(template_sql)
                templates = cursor.fetchall()

        finally:
            connection.close()

        return render_template('/manage/site_add.html', title='Home', servers=servers, templates=templates)
    if request.method == "POST":
        title = request.form.get('title')
        server_id = request.form.get('server')
        keyword = request.form.get('keyword')
        domain = str(request.form.get('domain')).replace('http://', '').replace('https://', '')
        template = int(request.form.get('template'))
        description = request.form.get('description')
        web_path = domain.replace('.', '_')
        article_ids = request.form.get('content_id')

        print("添加网站POST｛%s,%s,%s,%s,%s｝" % (title, domain, template, keyword, description))
        # Connect to the database
        connection = pymysql.connect(host='120.76.232.162',
                                     user='root',
                                     password='lcn@123',
                                     db='site_group',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM `site` WHERE `domain`=%s LIMIT 1"
                cursor.execute(sql, domain)
                result = cursor.fetchone()
                print(result)
                if result is None:
                    # 添加站点
                    sql = "INSERT INTO `site` (`title`, `web_path`,`template_id`, `domain`,`keyword`, `description`,`state`, `create_time`,`article_ids`,`server_id`) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (
                        str(title), str(web_path), template, str(domain), str(keyword), str(description), 0,
                        int(time.time()), str(article_ids), str(server_id)))

                    # connection is not autocommit by default. So you must commit to save
                    # your changes.
                    connection.commit()

                else:
                    print("存在")
                    return redirect("/manage/site_add")

        finally:
            connection.close()

        return redirect("/manage/site_list")


# 生成html
@app.route("/manage/site_generate/<int:id>")
def manage_site_generate(id):
    site = {}
    # Connect to the database
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
                sql = "SELECT site.*,site_template.type as template_type,site_template.path as template_path FROM `site` left join `site_template` on site_template.id = site.template_id WHERE site.`id`=%s LIMIT 1"
                cursor.execute(sql, id)
                site = cursor.fetchone()
                print(site)
                if site is None:
                    print("网站不存在")
                    return redirect("/manage/site_list")
                elif site['template_type'] is None:
                    print("网站模版不存在")
                    return redirect("/manage/site_list")
                else:
                    article = {}
                    # 读取内容
                    if site['type'] == 0:
                        article_sql = "SELECT * FROM `article` WHERE `id`=%s LIMIT 1"
                        cursor.execute(article_sql, str(site['article_ids']).replace(',', ''))
                        article = cursor.fetchone()

                    print("开始生成网站：%s，%s" % (id, site['title']))

                    # 开始生成网站
                    PATH = os.path.dirname(os.path.abspath(__file__))
                    template_path = os.path.join(PATH, 'static/template/' + str(site['template_path']))

                    # 初始化模版
                    TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                                       loader=FileSystemLoader(template_path),
                                                       trim_blocks=False)

                    # 创建网站生成的目录
                    targetDir = os.path.join(PATH, 'output/' + site['web_path'])
                    # 拷贝模版中的样式及图片文件
                    copyFiles(template_path, targetDir)
                    print("拷贝模版中的样式及图片文件成功")

                    if site['template_type'] == 0:
                        # 单页面网站生成html
                        # 读取html模版并赋值，
                        html = TEMPLATE_ENVIRONMENT.get_template('index.html').render(site=site, article=article)

                        # 生成网站
                        fname = targetDir + "/index.html"
                        with open(fname, 'w') as f:
                            # html.render()
                            f.write(html)

                        # 生成nginx conf
                        # conf = ''
                        confFile = open(os.path.join(PATH, 'static/template/nginx.conf'))
                        webConf = confFile.read().replace('{{domain}}', site['domain']).replace('{{webpath}}',
                                                                                                site['web_path'])
                        # print(webConf)
                        # 生成nginx配置文件
                        with open(targetDir + "/" + site['web_path'] + ".conf", 'w') as f:
                            f.write(webConf)

                    # 更新网站状态为：已生成
                    sql = "UPDATE site SET is_generated=1 WHERE id=" + str(id)
                    cursor.execute(sql)

                    # connection is not autocommit by default. So you must commit to save
                    # your changes.
                    connection.commit()

    finally:
        connection.close()

    return Response(json.dumps(site), mimetype='application/json')


# 复制文件
def copyFiles(sourceDir, targetDir):
    # 将模版里的样式文件拷贝到网站目录
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        print("文件名：%s" % sourceF)
        if os.path.isfile(sourceF) and f != ".DS_Store" and f.find('.html') < 0:

            if not os.path.exists(targetDir):
                os.makedirs(targetDir)

            if not os.path.exists(targetF) or (
                    os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                # 2进制文件   * l$ _  o- b2 ~" a

                open(targetF, "wb").write(open(sourceF, "rb").read())
                print(u"%s %s 复制完毕" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), targetF))

        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)


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


# 发布网站
@app.route("/manage/site_publish/<int:id>")
def manage_site_publish(id):
    print("发布网站%s", str(id))
    site = {}
    # Connect to the database
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
            cursor.execute(sql, id)
            site = cursor.fetchone()
            # print(site)
            if site is None:
                print("网站不存在")
                return redirect("/manage/site_list")
            elif site['serverId'] is None:
                print("服务器不存在")
                return redirect("/manage/site_list")
            else:
                print("开始发布%s" % site['title'])

                # remote_dir = "/var/www/%s/" % site['web_path']
                remote_dir = site['web_site_path'] + site['web_path']

                PATH = os.path.dirname(os.path.abspath(__file__))
                local_dir = os.path.join(PATH, 'output/%s' % site['web_path'])

                # 发布网站到服务器 （上传网站、上传nginx conf）
                sftp_put(remote_dir, local_dir, site['web_path'], site['host'], site['port'], site['user_name'],
                         site['user_pwd'])

                # 更新发布状态
                # 更新网站状态为：已生成
                sql = "UPDATE site SET is_released=1 WHERE id=" + str(id)
                cursor.execute(sql)
                connection.commit()

    finally:
        connection.close()

    # 更新网站状态为：已生成
    # sql = "UPDATE site SET is_generated=1 WHERE id=" + str(id)
    # cursor.execute(sql)
    #
    # # connection is not autocommit by default. So you must commit to save
    # # your changes.
    # connection.commit()

    site = {
        "t": "adsfs"
    }

    return Response(json.dumps(site), mimetype='application/json')


# sftp上传到服务器
def sftp_put(remote_dir, local_dir, site_id, server_host, server_port, user_name, user_pwd):
    # 连接服务器
    transport = paramiko.Transport((server_host, server_port))
    transport.connect(username=user_name, password=user_pwd)
    sftp = paramiko.SFTPClient.from_transport(transport)

    print('upload file start %s ' % datetime.datetime.now())

    # remote_dir = "/var/www/www_hwz_cc/"

    # PATH = os.path.dirname(os.path.abspath(__file__))
    # local_dir = os.path.join(PATH, 'output/www_hwz_cc')

    for root, dirs, files in os.walk(local_dir):
        print('[%s][%s][%s]' % (root, dirs, files))

        for filespath in files:
            local_file = os.path.join(root, filespath)
            print(11, '[%s][%s][%s][%s]' % (root, filespath, local_file, local_dir))

            a = local_file.replace(local_dir, '').replace('\\', '/').lstrip('/')

            print('01', a, '[%s]' % remote_dir)

            remote_file = os.path.join(remote_dir, a).replace('\\', '/')

            print(22, remote_file)
            try:
                sftp.put(local_file, remote_file)
            except Exception as e:

                sftp.mkdir(os.path.split(remote_file)[0])

                sftp.put(local_file, remote_file)

                print("66 upload %s to remote %s" % (local_file, remote_file))

        for name in dirs:

            local_path = os.path.join(root, name)

            print(0, local_path, local_dir)

            a = local_path.replace(local_dir, '').replace('\\', '/').lstrip('/')

            print(1, a)

            print(1, remote_dir)
            # remote_path = os.path.join(remote_dir, a).replace('\\', '/')

            remote_path = remote_dir + a

            print(33, remote_path)

            try:
                sftp.mkdir(remote_path)
                print(44, "mkdir path %s" % remote_path)
            except Exception as e:

                print(55, e)
    print('77,upload file success %s ' % datetime.datetime.now())
    # 上传conf文件到nginx/conf.d
    #
    #
    # # 将resutl.txt 上传至服务器 /tmp/result.txt
    sftp.put(local_dir + '/' + site_id + '.conf', '/etc/nginx/conf.d/' + site_id + '.conf')
    # # 将result.txt 下载到本地
    # sftp.get('/tmp/result.txt', '~/yours.txt')
    transport.close()


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
    app.run()
