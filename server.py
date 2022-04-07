import socket
import threading
from Users import Users
from ClientHandler import ClientHandler


class Server(socket.socket):
    """ Class for the server that listens to client connections
        The server is inherited from the socket class
        A new thread is created for each client connection

    Attributes:
        host (str): The hostname of the server
        port (int): The port number of the server
        DB (Users): The database of users

    Args:
        socket ([type]): [description]

    """     

    def __init__(self, host, port):
        """
            Initialize the server and bind it to the host and port

        Args:
            host (str): The hostname of the server
            port (int): The port number of the server

        Raises:
            IOException: If the server cannot be created

        """

        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.bind((host, port))
        self.listen(5)
        print(f"Server listening on http://{host}:{port}")
        
        self.DB = Users()

        self.start()

    def start(self):
        """Start the server and listen for connections
           Create a new thread for each client connection and create a new instance of the ClientHandler class
        
        Raises:
            IOException: If the client gets disconnected
        """


        while True:
            try:
                conn, addr = self.accept()
                conn.setblocking(True)
                print("Client connected:" + addr[0])

                new_thread = threading.Thread(target=ClientHandler(conn, self.DB).handle, args=[
                    conn, addr], daemon=True)

                new_thread.start()
            except Exception as e:
                print (e)
                break

        self.close()


# Run main
if __name__ == "__main__":
    Server("localhost", 8080)
