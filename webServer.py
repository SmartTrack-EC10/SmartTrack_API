import sys, cgi
from http.server import HTTPServer
from routes.server import PythonServer

HOST_NAME = "localhost"
PORT = 8080

if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    print(f"Server started http://{HOST_NAME}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped successfully")
        sys.exit(0)