from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

class RequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """重写日志方法 - 禁用默认的访问日志"""
        # 完全禁用日志，注释掉下面这行
        pass

        # 或者自定义日志格式
        # print(f"[{self.log_date_time_string()}] {format % args}")

    # Handler for the GET requests
    def do_GET(self):

        # 解析URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # 根据路由执行不同操作
        if path == '/' or path == '/home':
            self.handle_home()
        elif path == '/api/start':
            self.handle_start()
        elif path == '/api/stop':
            self.handle_stop()
        else:
            self.handle_404()

    def send_json_response(self, status_code, response_data):
        """通用的JSON响应方法"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def handle_home(self):
        """处理首页请求"""
        response = {"message": "Welcome to SnowbreakAutoAssistant", "version": "2.0.6"}
        self.send_json_response(200, response)

    def handle_start(self):
        """处理启动请求"""
        response = {"action": "start", "result": "success", "message": "Assistant started"}
        self.send_json_response(200, response)

    def handle_stop(self):
        """处理停止请求"""
        response = {"action": "stop", "result": "success", "message": "Assistant stopped"}
        self.send_json_response(200, response)

    def handle_404(self):
        """处理404错误"""
        response = {"error": "Not Found", "message": "The requested resource was not found"}
        self.send_json_response(404, response)

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"SAA cli running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
