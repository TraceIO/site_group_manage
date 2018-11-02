import os
import time

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




