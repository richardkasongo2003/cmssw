from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import mimetypes
import cgi
import argparse

class Serv(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        
        try:
            file_path = self.path[1:]

            with open(file_path, 'rb') as file:
                file_to_open = file.read()

            mime_type, _ = mimetypes.guess_type(file_path)

            self.send_response(200)
            if mime_type:
                self.send_header("Content-type", mime_type)
            self.end_headers()

            self.wfile.write(file_to_open)
        
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("File not found", 'utf-8'))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f"Internal server error: {str(e)}", 'utf-8'))

    def do_POST(self):
        if self.path == '/upload':
            content_type, pdict = cgi.parse_header(self.headers.get('content-type'))
            if content_type == 'multipart/form-data':
                fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                if 'dataFile' in fs:
                    file_item = fs['dataFile']
                    file_path = os.path.join('.', 'uploaded_data.js')
                    with open(file_path, 'wb') as f:
                        f.write(file_item.file.read())
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes("File uploaded successfully", 'utf-8'))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(bytes("No file uploaded", 'utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(bytes("Invalid content type", 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=Serv, port=65432):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a simple HTTP server.')
    parser.add_argument('--port', type=int, default=65432, help='Port to serve on (default: 65432)')
    args = parser.parse_args()

    run(port=args.port)
