from swagger.swagger import swagger

HOST_NAME = "0.0.0.0"
PORT = 8080

app = swagger.app

if __name__ == '__main__':
    print(f"Server started http://{HOST_NAME}:{PORT}")
    app.run(host=HOST_NAME, port=PORT, debug=True, threaded=True)