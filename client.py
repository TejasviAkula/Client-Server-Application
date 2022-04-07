import socket
def main():
    """
        Main function for client side
        - Cretes a socket
        - Connects to the server
        - Listens for initial message from server
        
        While the client is connected to the server:

        - Prompts user for command input
        - Sends command to server
        - Listens for response from server
        - Prints response to screen

    Connection can be closed by typing 'exit' in the command prompt.

    """
    # Create a socket object
    s = socket.socket()

    # connect to the server on localhost 8080
    s.connect(('localhost', 8080))

    # Receive data from the server
    message = s.recv(4096)
    print(message.decode())

    # Create main loop
    while True:
        # Get user input
        command = input("> ")

        if command == "exit":
            # Quit the program
            break

        # Send the command to the server
        s.send(command.encode("utf-8"))

        # Receive the response from the server
        message = s.recv(4096)
        print(message.decode())

    # close the connection
    s.close()


if __name__ == '__main__':
  main()