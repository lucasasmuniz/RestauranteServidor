import socket
import threading
import json

class ClientServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)

    def handle_client_connection(self, client_socket):
        request = client_socket.recv(4096).decode()
        headers, body = request.split('\r\n\r\n', 1)
        request_line = headers.splitlines()[0]
        method, path, _ = request_line.split()

        if method == "GET" and path == "/api/menu":
            response = self.get_menu_from_restaurant_server()
        elif method == "POST" and path == "/api/choose":
            choice_data = json.loads(body)
            choices = choice_data.get("choices", [])
            response = self.send_choices_to_restaurant_server(choices)
        elif method == "GET" and (path == "/" or path == "/index.html"):
            with open("app.html", "r") as file:
                html = file.read()
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
        elif method == "GET" and path == "/styles.css":
            with open("styles.css", "r") as file:
                css = file.read()
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n{css}"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

        client_socket.sendall(response.encode())
        client_socket.close()

    def get_menu_from_restaurant_server(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 9998))
        request = "GET /api/menu HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        client.send(request.encode())
        menu = client.recv(4096).decode()
        client.close()
        return menu

    def send_choices_to_restaurant_server(self, choices):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 9998))
        request_body = json.dumps({"choices": choices})
        request = (
            "POST /api/choose HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: " + str(len(request_body)) + "\r\n\r\n" +
            request_body
        )
        client.send(request.encode())
        response = client.recv(4096).decode()
        client.close()
        return response

    def run(self):
        print("Servidor TCP para cliente ouvindo na porta 9999...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Conexão aceita de {addr}")
            client_handler = threading.Thread(target=self.handle_client_connection, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    server = ClientServer()
    server.run()
