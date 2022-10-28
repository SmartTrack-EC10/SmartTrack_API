from swagger.swagger import swagger

HOST_NAME = "localhost"
PORT = 8080

app = swagger.app

if __name__ == '__main__':
    print(f"Server started http://{HOST_NAME}:{PORT}")
    app.run(host=HOST_NAME, port=PORT)
    