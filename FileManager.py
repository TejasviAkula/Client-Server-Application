import os
from datetime import datetime


class FileManager():
    def __init__(self, username):
        """class FileManager

        Args:
            username (str): The username of the current user

        Attributes:
            user_directory (str): The directory of the user
            wd (str): The current working directory
            current_file (File): The current file that is open

        # Test that the user directory is created and the user is in the root directory

        >>> fm = FileManager("john")
        >>> fm.wd
        '.'

        >>> os.path.exists(fm.user_directory) 
        True

        """

        self.user_directory = os.path.join(
            "root", "usr", username)
        self.wd = "."  # Current working directory

        self.current_file = None

        # Initialize user's directory if it does not exist
        if not os.path.exists(self.user_directory):
            os.makedirs(self.user_directory)

    def get_current_wd(self):
        """
            Get the current working directory

            Returns:
                str: The current working directory

            >>> fm = FileManager("john")
            >>> fm.get_current_wd()
            'root\\\\usr\\\\john\\\\.'

        """
        return os.path.join(
            self.user_directory, self.wd)

    def list(self):
        """ List the files in the current working directory

        Returns:
            list: A list of files in the current working directory

        >>> fm = FileManager("john") 
        >>> fm.list() # doctest: +ELLIPSIS
        'Name                          Size                          ...

        """
        files = os.listdir(self.get_current_wd())
        width = 30
        response = f"{'Name':{width}}{'Size':{width}}{'Created':{width}}"
        response += "\n" + "-" * width * 3 + "\n"

        for f in files:
            # If file is a directory, add a '/' to the end of the name
            if os.path.isfile(os.path.join(self.get_current_wd(), f)):
                # Get the size of the directory from os
                size = os.path.getsize(os.path.join(self.get_current_wd(), f))

                # Get the creation date of the directory
                created = os.path.getctime(
                    os.path.join(self.get_current_wd(), f))

                # Add to the list of files
                response += f"{f:{width}}{str(size) + 'B':{width}}{str(datetime.fromtimestamp(created)):{width}}\n"
            elif os.path.isdir(os.path.join(self.get_current_wd(), f)):
                # Get size of file
                response += f"{f+'/'    }\n"

        return response

    def change_folder(self, name):
        """ Change the current working directory

        Args:
            name (str): The name of the directory to change to

        Returns:
            str: The new current working directory

        Raises:
            Exception: If the directory does not exist
            Exception: If the user is already in the root directory and tries to go up

        >>> fm = FileManager("john")

        # Try to change to a directory that does not exist

        >>> fm.change_folder("non-existent") # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: Directory does not exist

        # Try to change to go up from the root directory
        >>> fm.change_folder("..") # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: Already in root


        # Change to a directory that exists
        >>> if not os.path.exists(os.path.join(fm.get_current_wd(), "test")):  os.makedirs(os.path.join(fm.get_current_wd(), "test"))

        >>> fm.change_folder("test")
        'root\\\\test'


        """
        if name == "..":
           # can't go outside the user's folder
            if self.wd == ".":
                raise Exception("Already in root")
            else:
                self.wd = os.path.split(self.wd)[0]

        else:
            # Check if the directory exists
            if os.path.exists(os.path.join(self.get_current_wd(), name)):
                self.wd = os.path.join(self.wd, name)
            else:
                raise Exception("Directory does not exist")

        # Replace first '.' with root
        return self.wd.replace(".", "root", 1)

    def read_file(self, name):
        """
            Read the next 100 characters of 
                - The current file if it is open
                - The given file if it is not open

            Closes the file if no name is given

            Args:
                name (str): The name of the file to read

            Returns:
                str: The next 100 characters of the file

            Raises:
                Exception: If the file does not exist
                Exception: If no name is given and no file is open

            # Test a file that does not exist
            >>> fm = FileManager("john")
            >>> fm.read_file("file") # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ...
            Exception: File does not exist

            # Test to close a file that is not open

            >>> fm.read_file(None) # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ...
            Exception: No file open

            #! We don't test valid file read here because it is tested in the File class

        """
        if name is None:
            if self.current_file == None:
                raise Exception("No file open")

            # Destroy the file instance
            self.current_file = None
            return "File closed"

        # Check if the file exists and is a file
        if not os.path.exists(os.path.join(self.get_current_wd(), name)):
            raise Exception("File does not exist")

        # If no file is open or the request file is not the current file create new file instance
        if self.current_file is None or self.current_file.name != name:
            # Open the file
            self.current_file = File(name, self.get_current_wd())

        # Read the next 100 characters
        return self.current_file.read()

    def write_file(self, name, input):
        """Write content to a file

        Args:   
            name (str): The name of the file to write to
            input (str): The content to write to the file

        Returns:
            str: The name of the file that was written to

        # Test to write to a file that does not exist
        >>> fm = FileManager("john")

        >>> fm.write_file("important", "something important ") 
        'Successfully wrote to file important'

        # Test appending to a file that does  exist
        >>> fm.write_file("important", "more stuff")
        'Successfully wrote to file important'

        >>> open(os.path.join(fm.get_current_wd(), "important"), "r").read()
        'something important \\nmore stuff'

        >>> os.remove("root/usr/john/important") # remove file after test

        """

        fd = None

        # If the file does not exist, create it and if input is empty clear the contents of the file
        if not os.path.exists(os.path.join(self.get_current_wd(), name)) or input is None:
            fd = open(os.path.join(self.get_current_wd(), name), "w")

        else:
            fd = open(os.path.join(self.get_current_wd(), name), "a")
            fd.write("\n")

        fd.write(input if input is not None else "")
        fd.close()

        # Ensures that the file is reopened when the next read is called
        if self.current_file is not None and self.current_file.name == name:
            self.current_file = None

        return "Successfully wrote to file " + name

    def create_folder(self, folder_name):
        """ Create a new folder

        Args:
            folder_name (str): The name of the folder to create

        Returns:
            str: The name of the folder that was created

        Raises:
            Exception: If the folder already exists

        # Test to create a folder that already exists
        >>> fm = FileManager("john")
        >>> if not os.path.exists(os.path.join(fm.get_current_wd(), "test")):  os.makedirs(os.path.join(fm.get_current_wd(), "test"))
        >>> fm.create_folder("test") # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: Folder already exists

        # Test to create a folder that does not exist
        >>> fm.create_folder("test2")
        'Successfully created folder test2'

        # Clean up
        >>> os.rmdir(os.path.join(fm.get_current_wd(), "test2"))


        """
        if os.path.exists(os.path.join(self.get_current_wd(), folder_name)):
            raise Exception("Folder already exists")

        os.makedirs(os.path.join(self.get_current_wd(), folder_name))

        return "Successfully created folder " + folder_name


class File():
    """
        Class to represent a file

        Args:
            name (str): The name of the file
            cwd (str): The current working directory of the user

        Attributes:
            name (str): The name of the file
            file_path (str): The absolute path to the file
            offset (int): The current read offset of the file
            read_length (int): The length of content to read each time
    """

    def __init__(self, name, cwd):

        self.name = name
        self.file_path = os.path.join(cwd, name)

        self.offset = 0
        self.read_length = 100

    def read(self):
        """
            Read the next 100 characters of the file

            Returns:
                str: The next 100 characters of the file or EOF if the file is empty

            Raises:
                Exception: If the file does not exist

        #? Test to read file content
        >>> open("root/usr/john/important", "w").write("something important") 
        19
        >>> f = File("important", "root/usr/john")
        >>> f.read()
        'something important'

        #? Test to read EOF
        >>> open("root/usr/john/important", "w").write("")
        0
        >>> f = File("important", "root/usr/john")
        >>> f.read()
        'EOF'

        #? Clean up
        >>> os.remove("root/usr/john/important")

        """
        # read the next 100 characters from the current offset
        with open(self.file_path, "r") as f:
            f.seek(self.offset)
            response = f.read(self.read_length)
            self.offset += self.read_length
            return response if response != "" else "EOF"
