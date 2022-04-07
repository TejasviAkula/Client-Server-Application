from FileManager import FileManager
from Users import Users

DEBUG = True

def debug(msg):
    """
        Prints a debug message if DEBUG is True
    Arguments:
        msg (string) -- The message to print
    """

    if DEBUG:
        print(msg)


class ClientHandler():
    """ Class that handles each client connection and and executes commands sent to the server by the client 

    Args:
        conn (socket): The socket connection to the client
        DB (Users): The database of users (default: Users() - creates a new database instance if not provided):
        conn (socket): The socket connection to the client 
        FileManager (FileManager): The file manager for the current user (initialized when the user logs in)
        user (User): The current logged in user user
        commands (dict): The commands that can be executed by the client including their help messages, handlers and required/optional arguments

    """
    def __init__(self, conn, DB=Users()):
        self.conn = conn
        self.DB = DB
        self.FileManager = None
        self.user = None

        self.commands = {
            "exit": {
                "help": "Exit the program",
                "method": self.exit,
                "arguments": []
            },
            "help": {
                "help": "Shows this message",
                "method": self.help,
                "arguments": []
            },

            "register": {
                "help": "Register a new user",
                "method": self.register,
                "arguments": [{
                    "name": "username", 'optional': False, "description": "The username for the new user"},
                    {
                    "name": "password", 'optional': False,
                    "description": "The password for the new user"
                }],

            },
            "login": {
                "help": "Login to your account",
                "method": self.login,
                "arguments": [{"name": "username", 'optional': False, "description": ""},
                              {"name": "password", 'optional': False, "description": ""}],


            },
            "list": {
                "help": "List all files in the current directory",
                "method": self.list,
                "arguments": []
            },
            "change_folder": {
                "help": "Change the current working directory",
                "method": self.change_folder,
                "arguments": [{"name": "folder_name", 'optional': False,
                               "description": "The name of the folder you want to change to"
                               }],
            },
            "read_file": {
                "help": "Reads 100 characters of the file from the last read position, starting from 0 for the first read of a new file",
                "method": self.read_file,
                "arguments": [{"name": "file_name", 'optional': True,
                               "description": "The name of the file to read. If not provided the currently open file's read offset will be reset"
                               }],
            },
            "write_file": {
                "help": "Write content to a given file. The file will be created if it does not already exist",
                "method": self.write_file,
                "arguments": [
                    {"name": "file_name", 'optional': False,
                        "description": "The name of the file to write to"},
                    {"name": "input", 'optional': True,
                        "description": "The content to write to the file. If not provided, the existing file will be cleared"}
                ],
            },
            "create_folder": {
                "help": "Create a new folder in the current directory",
                "method": self.create_folder,
                "arguments": [
                    {"name": "folder_name", 'optional': False,
                        "description": "The name of the new folder to create"}
                ],

            }

        }

    def handle(self, conn, addr):
        """Generic handler for each command sent to the server
           Ensures that command is not empty
           Calls the validated_command_execution method to execute the command

        Args:
            conn (socket): The socket connection to the client
            addr (tuple): The address of the client
        """
        conn.send(b"Welcome to the server! Please enter your command")

        while True:
            try:
                # receive command from client
                command = conn.recv(2048).decode().lower()

                if not command:
                    conn.send(b"No command was entered, try again")

                # Get response from handler method
                response = self.validated_command_execution(command)

                # send back response
                conn.send(response.encode("UTF-8"))

            except Exception as e:
                debug(e)
                try:
                    conn.send(b"Server error occurred")
                except IOError:  # client disconnected so can't send error message
                    break

        conn.close()
        print("Client disconnected:" + addr[0])

    def validated_command_execution(self, command):
        """Validates the command and executes it if:
            - The command is not empty
            - The command is a valid command
            - The command has the correct number of required arguments

        Args:
            command (str): The command to be executed (including arguments separated by spaces)

        Returns:
            str: The response from the executed command

        # Test valid command
        >>> ClientHandler(None).validated_command_execution("help") # doctest: +ELLIPSIS
        Available commands...

        # Test invalid command
        >>> ClientHandler(None).validated_command_execution("invalid_command") # doctest: +ELLIPSIS
        "Command not found, try again. Type 'help' to see possible commands"

        # Test invalid number of arguments
        >>> ClientHandler(None).validated_command_execution("register john") # doctest: +ELLIPSIS
        'The number of arguments is incorrect, please try again'

        # Test optional command
        >>> ClientHandler(None).validated_command_execution("read_file") # doctest: +ELLIPSIS
        'Error: You need to login before using this command'
        """

        command_string = command.split(" ")[0]
        input_arguments = command.split(" ")[1:]

        if command_string not in self.commands:
            return "Command not found, try again. Type 'help' to see possible commands"

        # Get the command object
        command_object = self.commands[command_string]
        all_arguments = command_object["arguments"]
        # Only non-optional arguments
        required_arguments = [
            arg for arg in all_arguments if not arg["optional"]]

        # Check if the number of arguments is correct
        if len(required_arguments) > 0 and len(
                required_arguments) > len(input_arguments):
            return "The number of arguments is incorrect, please try again"

        # Execute the command
        return command_object["method"](input_arguments)

    def register(self, arguments):
        """Register a new user  

        Args:
            arguments (list): The arguments for the command (required: 2)

        Returns:
            str: The response from the executed command
        """
        try:
            self.user = self.DB.register(arguments[0], arguments[1])
            return "Successfully registered"
        except Exception as e:
            return "Error: " + str(e)

    def login(self, arguments):
        """Login to user account and set current user

        Args:
            arguments (list): The arguments for the command (required: 2)

        Returns:
            str: The response from the executed command
        """

        try:
            self.user = self.DB.login(arguments[0], arguments[1])
            # intialize the file manager
            self.FileManager = FileManager(self.user.username)
            return "Successfully logged in"
        except Exception as e:
            return "Error: " + str(e)

    """
        Methods for reading and writing files -------------------------------------------------------------
    """

    def list(self, arguments):
        """List all files in the current directory

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command
        """

        try:
            self.ensure_user_is_logged_in()
            return self.FileManager.list()
        except Exception as e:
            return "Error: " + str(e)

    def change_folder(self, arguments):
        """Change the current working directory

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command
        """

        try:
            self.ensure_user_is_logged_in()
            cwd = self.FileManager.change_folder(arguments[0])
            return "Current directory changed to " + cwd
        except Exception as e:
            return "Error: " + str(e)

    def read_file(self, arguments):
        """Read the contents of a file

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command
        """

        try:
            self.ensure_user_is_logged_in()
            result = self.FileManager.read_file(
                arguments[0] if len(arguments) > 0 else None)

            return result
        except Exception as e:
            return "Error: " + str(e)

    def write_file(self, arguments):
        """ Write to a file

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command
        """

        file_name = arguments[0]
        input_string = arguments[1] if len(arguments) > 1 else None

        try:
            self.ensure_user_is_logged_in()
            return self.FileManager.write_file(file_name, input_string)
        except Exception as e:
            return "Error: " + str(e)

    def create_folder(self, arguments):
        """Create a new folder

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command
        """

        try:
            self.ensure_user_is_logged_in()
            return self.FileManager.create_folder(arguments[0])
        except Exception as e:
            return "Error: " + str(e)

    """
        Helper methods
    """

    def help(self, args):
        """Prints the available commands

        Args: 
            arguments (list): The arguments for the command (required: 0)

        Returns:
            str: The response from the executed command

        # Test valid command
        >>> ClientHandler(None).help([]) # doctest: +ELLIPSIS   
        Available commands...
        """

        res = ""
        res += "Available commands\n"
        res += "=" * 80 + "\n"

        try:
            for command, obj in self.commands.items():
                args_string = " ".join([
                    f"<{arg['name']}>" for arg in obj["arguments"]
                ])
                res += f"{command:15}{args_string:24}{obj['help']:50}\n"
                print(res)
                # Add arguments list with optional arguments
                for arg in obj["arguments"]:
                    opt = "[optional]" if arg["optional"] else ""
                    res += f"{' ' * 15}{'-'+arg['name']:12}{opt:12}{arg['description']:50}\n"
                res += "\n"

            return res

        except Exception as e:
            return "Error: " + str(e)

    def ensure_user_is_logged_in(self):
        """Ensure that the user is logged in

        Raises:
            Exception: If the user is not logged in

        # Test valid command

        >>> ClientHandler(None).ensure_user_is_logged_in() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: You need to login before using this command


        """
        if self.user is None:
            raise Exception("You need to login before using this command")

    def exit(self, arguments):
        """Exit the program and close the connection

        Args:
            arguments (list): The arguments for the command (required: 0)

        """        
        debug("Running exit handler")
        self.conn.send(b"Goodbye!")
        self.conn.close()
        return None
