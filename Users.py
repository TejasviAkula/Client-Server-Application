
class Users:

    def __init__(self, db='./db/users.csv'):
        """Class Users

            Attributes:
                users (list): A list of all users

            Methods:
                register(username, password): Registers a new user
                login(username, password): Logs in a user
        """
        self.db = db

        # Load all users from the database
        self.users = []

        with open(self.db, 'r') as f:
            for line in f.readlines():
                username, password = line.strip('\n').split(',')
                self.users.append(User(username, password))

    def register(self, username, password):
        """Registers a new user and saves it to the database

        Args:
            username (str): The username of the new user
            password (str): The password of the new user

        Raises:
            Exception: If the username already exists

        Returns:
            User: The new user

        # Test registering a new username
        >>> users = Users("./db/test-users.csv")
        >>> users.flush()
        >>> users.register('test', 'test') # doctest: +ELLIPSIS
        <Users.User object at ...

        # Test registering an existing username
        >>> Users("./db/test-users.csv").register('test', 'test') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: User already exists

        """

        # Check if the username is already taken
        for user in self.users:
            if user.username == username:
                raise Exception('Username already taken')

        # Create a new user
        new_user = User(username, password)
        self.users.append(new_user)

        # Save the new user to the database
        self.save()

        return new_user

    def login(self, username, password):
        """ Logs in a user 

        Args:
            username (str): The username of the user
            password (str): The password of the user

        Raises:
            Exception: If the username does not exist
            Exception: If the password is incorrect

        Returns:
            User: The user that was logged in

        # Test logging in a user

        >>> users = Users("./db/test-users.csv")
        >>> users.users = [User('test', 'test')]
        >>> users.login('test', 'test') # doctest: +ELLIPSIS
        <Users.User object at ...

        # Test logging in a user with an incorrect password
        >>> users.login('test', 'wrong') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: Incorrect password

        # Test logging in a non-existing user
        >>> users.login('wrong', 'test') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        Exception: User does not exist

        """

        # Check that the user exists
        for user in self.users:
            # Find the user
            if user.username == username:
                # Check that the password is correct
                if user.password == password:
                    return user
                else:
                    raise Exception('Incorrect password')

        # If the user doesn't exist, raise an exception
        raise Exception('User does not exist')

    def save(self):
        """Saves the database to file

           Args:
                None

            Returns:
                None

        # Test saving the database

        >>> users = Users("./db/test-users.csv")
        >>> users.flush()
        >>> users.users = [User('test', 'test')]
        >>> users.save()
        >>> users = Users("./db/test-users.csv")
        >>> users.users[0].username == 'test'
        True

        """

        # Save all users to the database
        with open(self.db, 'w') as f:
            for user in self.users:
                f.write(user.username + ',' + user.password + '\n')

    def flush(self):
        """Flushes the database both locally and on file

        Warning:
            This will delete all users in the database, only use in testing

        """

        with open(self.db, 'w') as f:
            f.write('')

        self.users = []


class User:
    def __init__(self, username, password):
        """Class User
        Just a class to hold a username and password for a user that is logged in or in the database

        Attributes:
            username (str): The username of the user
            password (str): The password of the user

        Methods:
            None
        """
        self.username = username
        self.password = password

    def __str__(self):
        return 'User(' + self.username + ',' + self.password + ')'
