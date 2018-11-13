import paramiko
import datetime
import os


class Publisher(object):

    # sftp上传到服务器
    def sftp_put(self, remote_dir, local_dir, site_id, server_host, server_port, user_name, user_pwd,
                 nginx_config_path):
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
        sftp.put(local_dir + '/' + site_id + '.conf', nginx_config_path + site_id + '.conf')
        # # 将result.txt 下载到本地
        # sftp.get('/tmp/result.txt', '~/yours.txt')
        transport.close()
