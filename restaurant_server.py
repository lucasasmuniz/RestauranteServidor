import socket
import json
import threading

class RestaurantServer:
    def __init__(self, host='0.0.0.0', port=9998):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.menu = {
            1: ("Bolo de Rolo", 12.00),
            2: ("Cartola", 10.00),
            3: ("Carne de Sol com Queijo Coalho", 25.00),
            4: ("Feijoada Pernambucana", 30.00),
            5: ("Tapioca de Coco com Queijo Coalho", 10.00),
            6: ("Tapioca de Charque com Queijo Coalho", 12.00),
            7: ("Caldinho de Sururu", 15.00),
            8: ("Baião de Dois", 20.00),
            9: ("Cuscuz com Charque", 18.00),
            10: ("Cocada", 6.00),
            11: ("Café com Leite", 4.00),
            12: ("Caldo de Cana", 5.00),
            13: ("Guaraná Jesus", 6.00),
            14: ("Suco de Acerola", 7.00),
            15: ("Bebida de Mel de Engenho", 8.00),
            16: ("Tapioca de Frango com Catupiry", 12.00),
            17: ("Tapioca Romeu e Julieta", 12.00),
            18: ("Queijadinha", 5.00),
            19: ("Bolo Souza Leão", 14.00),
            20: ("Sarapatel", 22.00)
        }

    def generate_menu(self):
        menu_list = [{"id": item_id, "name": item_name, "price": item_price} for item_id, (item_name, item_price) in self.menu.items()]
        return menu_list

    def handle_client_connection(self, client_socket):
        try:
            request = client_socket.recv(4096).decode()
            headers, body = request.split('\r\n\r\n', 1)
            request_line = headers.splitlines()[0]
            method, path, _ = request_line.split()

            if method == 'GET' and path == '/api/menu':
                menu_list = self.generate_menu()
                response_body = json.dumps({"menu": menu_list})
                response = (
                    'HTTP/1.1 200 OK\r\n'
                    'Content-Type: application/json\r\n'
                    'Content-Length: ' + str(len(response_body)) + '\r\n\r\n' +
                    response_body
                )
                client_socket.send(response.encode())

            elif method == 'POST' and path == '/api/choose':
                choice_data = json.loads(body)
                choices = choice_data.get("choices", [])
                total = 0.0
                response_items = []

                for choice_id in choices:
                    if choice_id in self.menu:
                        item_name, item_price = self.menu[choice_id]
                        total += item_price
                        response_items.append(f"{item_name} - R${item_price:.2f}")

                if response_items:
                    response_message = "Você escolheu:\n" + "\n".join(response_items) + f"\nTotal: R${total:.2f}"
                else:
                    response_message = "Nenhuma escolha válida."

                response_body = json.dumps({"message": response_message})
                response = (
                    'HTTP/1.1 200 OK\r\n'
                    'Content-Type: application/json\r\n'
                    'Content-Length: ' + str(len(response_body)) + '\r\n\r\n' +
                    response_body
                )
                client_socket.send(response.encode())
            else:
                response_body = json.dumps({"message": "Requisição inválida."})
                response = (
                    'HTTP/1.1 400 Bad Request\r\n'
                    'Content-Type: application/json\r\n'
                    'Content-Length: ' + str(len(response_body)) + '\r\n\r\n' +
                    response_body
                )
                client_socket.send(response.encode())

        except Exception as e:
            error_response = {"message": f"Erro durante o processamento: {e}"}
            client_socket.send(json.dumps(error_response).encode())
        finally:
            client_socket.close()

    def run(self):
        print("Servidor TCP ouvindo na porta 9998...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Conexão aceita de {addr}")
            self.handle_client_connection(client_socket)

if __name__ == "__main__":
    server = RestaurantServer()
    server.run()
