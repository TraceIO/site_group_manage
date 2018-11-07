import os
from jinja2 import Environment, FileSystemLoader
import time


class Generator(object):
    def generator_html(self, site, PATH):
        """
        生成网站html
        :param site:
        :param PATH:
        :return:
        """
        print("开始生成网站：%s，%s" % (site['id'], site['title']))
        # PATH = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(PATH, 'static/template/' + str(site['template_path']))

        # 初始化模版
        TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                           loader=FileSystemLoader(template_path),
                                           trim_blocks=False)

        # 创建网站生成的目录
        targetDir = os.path.join(PATH, 'output/' + site['web_path'])
        # 拷贝模版中的样式及图片文件
        self.copyFiles(template_path, targetDir)
        print("拷贝模版中的样式及图片文件成功")
        if site['template_type'] == 0:
            # 单页面网站生成html
            # 读取html模版并赋值，
            article = {
                "title": site['article_title'],
                "content": site['article_content']
            }

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

    # path 根目录
    def generator(self, site, article, PATH):
        print("开始生成网站：%s，%s" % (site['id'], site['title']))

        # 开始生成网站
        # PATH = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(PATH, 'static/template/' + str(site['template_path']))

        # 初始化模版
        TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                           loader=FileSystemLoader(template_path),
                                           trim_blocks=False)

        # 创建网站生成的目录
        targetDir = os.path.join(PATH, 'output/' + site['web_path'])
        # 拷贝模版中的样式及图片文件
        self.copyFiles(template_path, targetDir)
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

    # 复制文件
    def copyFiles(self, sourceDir, targetDir):
        # 将模版里的样式文件拷贝到网站目录
        for f in os.listdir(sourceDir):
            sourceF = os.path.join(sourceDir, f)
            targetF = os.path.join(targetDir, f)
            # print("文件名：%s" % sourceF)
            if os.path.isfile(sourceF) and f != ".DS_Store" and f.find('.html') < 0:

                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)

                if not os.path.exists(targetF) or (
                        os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                    # 2进制文件   * l$ _  o- b2 ~" a

                    open(targetF, "wb").write(open(sourceF, "rb").read())
                    # print(u"%s %s 复制完毕" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), targetF))

            if os.path.isdir(sourceF):
                self.copyFiles(sourceF, targetF)
