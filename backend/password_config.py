# Password configuration file
# Administrators can modify these settings as needed

# Minimum password length
MIN_LENGTH = 10

# Maximum password length
MAX_LENGTH = 50

# Whether to require at least one uppercase letter
REQUIRE_UPPERCASE = True

# Whether to require at least one lowercase letter
REQUIRE_LOWERCASE = True

# Whether to require at least one number
REQUIRE_NUMBERS = True

# Whether to require at least one special character
REQUIRE_SPECIAL_CHARS = True

# Allowed special characters
SPECIAL_CHARS = "!@#$%^&*()_-+=<>?/[]{}|"

# Password history - number of previous passwords to check against
# User cannot reuse any of their last N passwords
PASSWORD_HISTORY_LENGTH = 3

# Maximum number of failed login attempts before account is locked
MAX_LOGIN_ATTEMPTS = 3

# List of common passwords that are not allowed (dictionary passwords)
DISALLOWED_PASSWORDS = [
    "password",
    "123456",
    "12345678",
    "qwerty",
    "abc123",
    "111111",
    "123123",
    "admin",
    "welcome",
    "password123",
    "admin123",
    "letmein",
    "monkey",
    "1234567",
    "sunshine",
    "iloveyou",
    "trustno1",
    "princess",
    "123456789",
    "987654321",
    "mypassword",
    "football",
    "000000",
    "qwerty123",
    "dragon",
    "baseball",
    "superman",
    "password1",
    "internet",
    "service",
    "provider"
]