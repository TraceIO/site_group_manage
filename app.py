import time
import os
import json
from flask import Flask, render_template, Response, request, redirect
import pymysql.cursors
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


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


@app.route('/manage/home', methods=['POST', 'GET'])
def manage_home():
    return render_template('/manage/index.html', title='Home')


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
                sql = "SELECT * FROM `site` LIMIT 0,10"
                cursor.execute(sql)
                site_list = cursor.fetchall()

                print(site_list)
    finally:
        connection.close()

    return render_template('/manage/site_list.html', title='Home', site_list=site_list)


@app.route('/manage/site_add', methods=['POST', 'GET'])
def manage_site_add():
    if request.method == "GET":
        return render_template('/manage/site_add.html', title='Home')
    if request.method == "POST":
        title = request.form.get('title')
        keyword = request.form.get('keyword')
        domain = str(request.form.get('domain')).replace('http://', '').replace('https://', '')
        template = int(request.form.get('template'))
        description = request.form.get('description')
        web_path = domain.replace('.', '_')

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

                with connection.cursor() as cursor:
                    # Read a single record
                    sql = "SELECT * FROM `site` WHERE `domain`=%s LIMIT 1"
                    cursor.execute(sql, domain)
                    result = cursor.fetchone()
                    print(result)
                    if result is None:
                        # Create a new record
                        sql = "INSERT INTO `site` (`title`, `web_path`,`template_id`, `domain`,`keyword`, `description`,`state`, `create_time`) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)"
                        cursor.execute(sql, (
                            str(title), str(web_path), template, str(domain), str(keyword), str(description), 0,
                            int(time.time())))

                        # connection is not autocommit by default. So you must commit to save
                        # your changes.
                        connection.commit()
                    else:
                        print("存在")
                        return redirect("/manage/site_add")

        finally:
            connection.close()

        return redirect("/manage/site_list")


@app.route("/manage/site_generate/<int:id>")
def manage_site_generate(id):
    print(id)
    t = {}
    # t['id'] = id
    # t['title'] = 'aaaa'
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
                sql = "SELECT * FROM `site` WHERE `id`=%s LIMIT 1"
                cursor.execute(sql, id)
                site = cursor.fetchone()
                print(site)
                if site is None:
                    print("不存在")
                    return redirect("/manage/site_list")
                else:
                    print("存在")
                    t = site
                    site_id = site['template_id']
                    # 开始生成网站
                    PATH = os.path.dirname(
                        os.path.abspath(__file__))  # + '/static/template/' + str(site_template) + '/'
                    template_path = os.path.join(PATH, 'static/template/' + str(site_id))

                    # 初始化模版
                    TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                                       loader=FileSystemLoader(template_path),
                                                       trim_blocks=False)

                    # 创建网站生成的目录
                    targetDir = os.path.join(PATH, 'output/' + site['web_path'])
                    copyFiles(template_path, targetDir)
                    print("拷贝模版中的样式及图片文件成功")
                    if site_id == 1:
                        # 读取html模版并赋值，
                        html = TEMPLATE_ENVIRONMENT.get_template('index.html').render(title=site['title'])

                        # 生成网站
                        fname = targetDir + "/index.html"
                        with open(fname, 'w') as f:
                            # html.render()
                            f.write(html)

    finally:
        connection.close()

    return Response(json.dumps(t), mimetype='application/json')


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


if __name__ == '__main__':
    app.run()