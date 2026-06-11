class UserProfile:
    """
    Represents a user profile with basic identification details.
    """
    def __init__(self, username: str, email_address: str, age: int):
        self.username = username
        self.email_address = email_address
        self.age = age

    def is_adult(self) -> bool:
        """Determines if the user is 18 years or older."""
        return self.age >= 18

    def __str__(self):
        return f"User: {self.username} ({self.email_address})"
