from swagger.swagger import swagger
from flasgger import swag_from

HOST_NAME = "localhost"
PORT = 8080

app = swagger.app

if __name__ == '__main__':
    print(f"Server started http://{HOST_NAME}:{PORT}")
    app.run(host=HOST_NAME, port=PORT)
    