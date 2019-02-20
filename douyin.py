# -*- coding: utf-8 -*-
import hashlib
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

class calcSig(object):
    key1 = '57218436'
    key2 = '15387264'
    rstr = 'efc84c17'

    def shuffle(self, p1, p2):
        p = ''
        p += p1[int(p2[0], 10) - 1]
        p += p1[int(p2[1], 10) - 1]
        p += p1[int(p2[2], 10) - 1]
        p += p1[int(p2[3], 10) - 1]
        p += p1[int(p2[4], 10) - 1]
        p += p1[int(p2[5], 10) - 1]
        p += p1[int(p2[6], 10) - 1]
        p += p1[int(p2[7], 10) - 1]
        return p.lower()

    # 生成 as和cp字段
    def ppp(self, u_md5, u_key1, u_key2):
        ascp = [0] * 36
        ascp[0] = 'a'
        ascp[1] = '1'
        for i in range(0, 8):
            ascp[2 * (i + 1)] = u_md5[i]
            ascp[2 * i + 3] = u_key2[i]
            ascp[2 * i + 18] = u_key1[i]
            ascp[2 * i + 1 + 18] = u_md5[i + 24]
        ascp[-2] = 'e'
        ascp[-1] = '1'

        return ''.join(ascp)

    # 解析url参数
    def parseURL(self, url):
        param_index = url.find('?')
        param = url[param_index + 1:]
        param_list = param.split('&')
        param_list.append('rstr='+self.rstr)
        param_list = sorted(param_list)
        result = ''
        for a in param_list:
            tmp = a.split('=')
            tmp[1] = tmp[1].replace('+', 'a')
            tmp[1] = tmp[1].replace(' ', 'a')
            result += tmp[1]
        return result

    # 计算md5
    def calcMD5(self, str_encode):
        m = hashlib.md5()
        m.update(str_encode.encode('utf-8'))
        return m.hexdigest()

    def work(self, url, curtime):
        url_param = self.parseURL(url)
        p_md5 = self.calcMD5(url_param)
        if curtime & 1:
            p_md5 = self.calcMD5(p_md5)
        hexTime = hex(curtime)[2:]
        aa = self.shuffle(hexTime, self.key1)
        bb = self.shuffle(hexTime, self.key2)
        sig = self.ppp(p_md5, aa, bb)
        return ('%s&as=%s&cp=%s' % (url, sig[:18], sig[18:]))
        # return (sig[:18], sig[18:])


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
  def outputtxt(self, content):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.send_header('Access-Control-Allow-Origin', '*')
    self.end_headers()
    self.wfile.write(bytes(content, "utf-8"))
  def do_POST(self):
    content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
    post_data = self.rfile.read(content_length) # <--- Gets the data itself
    # logging.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))
    # 接收到的数据
    url = post_data.decode('utf-8')
    # print(url)
    c = calcSig()
    t = int(time.time())
    # url = '/aweme/v1/user/following/list/?_rticket=1542283051266435909&ac=wifi&aid=1128&app_name=awemechannel=360&count=20device_brand=OnePlus&device_id=59479530042&device_platform=android&device_type=ONEPLUS%2BA5000&dpi=420&iid=51242560222&language=zh&manifest_version_code=169&max_time=1541202996&openudid=5514716858105890&os_api=27&os_version=8.1.0&resolution=1080%2A1920&retry_type=no_retry&ssmix=a&update_version_code=1692&user_id=83774364341&uuid=615720636968612&version_code=169&version_name=1.6.9'
    url = url + '&ts=' +str(t)
    # print(url)
    # print(c.work(url,t))
    self.outputtxt(c.work(url,t))

if __name__ == '__main__':
  # 启动服务器
  port = 8100
  print('starting server, port', port)
  # Server settings
  server_address = ('0.0.0.0', port)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()