from dataclasses import dataclass, field
from drafter import *
import secrets
from datetime import datetime

set_website_title("Unlocked")
set_site_information(
    author="Ryan Simpkins",
    description="Encrypt and Decrypt messages using random keys.",
    sources="",
    planning=[],
    links=["https://github.com/your-username/your-repository"]
)
hide_debug_information()
set_website_framed(False)

# Encryption Records
@dataclass
class EncryptionRecord:
    original_message: str
    encrypted_message: str
    encryption_key: str
    date_created: str


# State
@dataclass
class State:
    current_message: str = ""
    current_key: str = ""
    current_encrypted: str = ""
    current_decrypted: str = ""
    error_message: str = ""
    history: list[EncryptionRecord] = field(default_factory=list)


# Home Page
@route
def index(state: State) -> Page:
    return Page(
        state,
        [
            Header("Welcome To Unlocked!"),
            Text("Encrypt and Decrypt messages using random keys."),
            Button("Encrypt a Message", "encrypt_page"),
            Button("Decrypt a Message", "decrypt_page"),
            Button("View Encryption History", "history_page"),
            Button("Help", "help_page")
        ]
    )


# Encryption Page
@route
def encrypt_page(state: State) -> Page:
    return Page(
        state,
        [
            Header("Encrypt a Message"),
            Text("Enter your message below:"),
            TextBox("message", state.current_message),
            Button("Generate Key", "generate_key"),
            Text("Your key: " + state.current_key),
            Button("Encrypt", "encrypt_message"),
            Text("Encrypted message: " + state.current_encrypted),
            Text(state.error_message),
            Button("Home", "index")
        ]
    )


# Decryption Page
@route
def decrypt_page(state: State) -> Page:
    return Page(
        state,
        [
            Header("Decrypt a Message"),
            Text("Enter your encrypted message:"),
            TextBox("encrypted_message", state.current_encrypted),
            Text("Enter your encryption key:"),
            TextBox("entered_key", state.current_key),
            Button("Decrypt", "decrypt_message"),
            Text("Original message: " + state.current_decrypted),
            Text(state.error_message),
            Button("Home", "index")
        ]
    )


# History Page
@route
def history_page(state: State) -> Page:
    history_display = []

    if len(state.history) == 0:
        history_display.append(
            Text("No Previous Encryption Records.")
        )
    else:
        for record in state.history:
            history_display.append(
                Text("Original Message: " + record.original_message)
            )
            history_display.append(
                Text("Encrypted Message: " + record.encrypted_message)
            )
            history_display.append(
                Text("Date: " + record.date_created)
            )

    return Page(
        state,
        [
            Header("Encryption History"),
            *history_display,
            Button("Home", "index")
        ]
    )


# Help Page
@route
def help_page(state: State) -> Page:
    return Page(
        state,
        [
            Header("How To Use Unlocked!"),
            Header("Step 1: Encrypt"),
            Text("Enter your message and generate a random key."),
            Header("Step 2: Save Your Key"),
            Text("Keep your key someplace safe."),
            Header("Step 3: Decrypt"),
            Text("Enter your encrypted message and the key."),
            Header("Step 4: Receive Your Original Message"),
            Text("Click decrypt to recover your original message."),
            Button("Home", "index")
        ]
    )


# Generate a Random Key
def generate_random_key() -> str:
    return str(secrets.randbelow(25) + 1)


# Generate Key Route
@route
def generate_key(state: State, message: str) -> Page:
    state.current_message = message
    state.current_key = generate_random_key()
    state.error_message = ""
    state.current_encrypted = ""

    return encrypt_page(state)


# Encrypting Text Helper Function
def encrypt_text(message: str, key: str) -> str:
    shift = int(key)
    encrypted = ""

    for character in message:
        if character.isalpha():
            if character.isupper():
                base = ord("A")
            else:
                base = ord("a")

            new_character = chr(
                (ord(character) - base + shift) % 26 + base
            )
            encrypted += new_character
        else:
            encrypted += character

    return encrypted


# Encrypt Message Route
@route
def encrypt_message(state: State, message: str) -> Page:
    state.current_message = message

    if state.current_message == "":
        state.error_message = "*ERROR: Please enter a message.*"

    elif state.current_key == "":
        state.error_message = "*ERROR: Please generate a key first.*"

    else:
        state.current_encrypted = encrypt_text(
            state.current_message,
            state.current_key
        )

        state.error_message = ""

        record = EncryptionRecord(
            state.current_message,
            state.current_encrypted,
            state.current_key,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        state.history.append(record)

    return encrypt_page(state)


# Decrypting Text Helper Function
def decrypt_text(message: str, key: str) -> str:
    reverse_key = 26 - int(key)

    return encrypt_text(message, str(reverse_key))


# Decrypt Message Route
@route
def decrypt_message(
    state: State,
    encrypted_message: str,
    entered_key: str
) -> Page:

    state.current_encrypted = encrypted_message
    state.current_key = entered_key

    if encrypted_message == "" or entered_key == "":
        state.error_message = "*ERROR:Please enter a message and a key.*"

    else:
        try:
            state.current_decrypted = decrypt_text(
                encrypted_message,
                entered_key
            )
            state.error_message = ""

        except ValueError:
            state.error_message = "*ERROR: Your key must be a number.*"

    return decrypt_page(state)

assert_state(index(State()), State())

start_server(State())
