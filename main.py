import os
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            self._extracted_from_do_GET_6(200, 'index.html')
        elif path == '/message':
            self._extracted_from_do_GET_6(200, 'message.html')
        else:
            self._extracted_from_do_GET_6(404, 'error.html')

    # TODO Rename this here and in `do_GET`
    def _extracted_from_do_GET_6(self, arg0, arg1):
        self._extracted_from_do_POST_2(arg0, 'Content-type', 'text/html')
        with open(arg1, 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_params = parse_qs(post_data)

            username = post_params.get('username', [''])[0]
            message = post_params.get('message', [''])[0]

            send_to_socket_server(username, message)

            self._extracted_from_do_POST_2(302, 'Location', '/message')

    # TODO Rename this here and in `_extracted_from_do_GET_6` and `do_POST`
    def _extracted_from_do_POST_2(self, arg0, arg1, arg2):
        self.send_response(arg0)
        self.send_header(arg1, arg2)
        self.end_headers()


def send_to_socket_server(username, message):
    message_data = {
        'username': username,
        'message': message
    }
    message_json = json.dumps(message_data).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(message_json, ('127.0.0.1', 5000))


def socket_server_thread():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(('127.0.0.1', 5000))
        while True:
            data, addr = server_socket.recvfrom(1024)
            data = data.decode('utf-8')
            message_data = json.loads(data)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            storage_data = {
                timestamp: {
                    'username': message_data['username'],
                    'message': message_data['message']
                }
            }

            with open('storage/data.json', 'r') as storage_file:
                existing_data = json.load(storage_file)

            existing_data.update(storage_data)

            with open('storage/data.json', 'w') as storage_file:
                json.dump(existing_data, storage_file, indent=2)


def setup_storage():
    if not os.path.exists('storage'):
        os.makedirs('storage')

    if not os.path.exists('storage/data.json'):
        with open('storage/data.json', 'w') as storage_file:
            json.dump({}, storage_file)


def main():
    setup_storage()

    http_server = HTTPServer(('0.0.0.0', 4000), RequestHandler)
    http_thread = threading.Thread(target=http_server.serve_forever)

    socket_thread = threading.Thread(target=socket_server_thread)

    http_thread.start()
    socket_thread.start()

    try:
        http_thread.join()
        socket_thread.join()
    except KeyboardInterrupt:
        http_server.shutdown()


if __name__ == '__main__':
    main()
