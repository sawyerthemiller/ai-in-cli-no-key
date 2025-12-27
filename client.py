import socket
import sys
import os

SERVER_IP = "localhost"
PORT = 19

INSTRUCTION = (
    "you should answer plainly, not using too advanced language, "
    "and also use no formatting, lists, bold, etc. you may however use new lines. "
    "this is a one-time instruction that should not be referenced or repeated in the response.\n\n"
)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def send_prompt(prompt):
    full_prompt = INSTRUCTION + prompt
    if not full_prompt.endswith('\n'):
        full_prompt += '\n'

    with socket.create_connection((SERVER_IP, PORT), timeout=120) as sock:
        sock.sendall(full_prompt.encode('utf-8'))
        
        # prevent hanging
        try:
            sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        response = b''
        while True:
            part = sock.recv(4096)
            if not part:
                break
            response += part
    return response.decode('utf-8')

def print_blue(text):
    BLUE = "\033[94m"
    RESET = "\033[0m"
    print(f"{BLUE}{text}{RESET}")

def main():
    if len(sys.argv) < 2:
        clear_screen()
        print()
        print()
        user_prompt = input("enter prompt: ")
    else:
        user_prompt = " ".join(sys.argv[1:])

    clear_screen()
    print()
    print()
    print("waiting on server...")

    answer = send_prompt(user_prompt)

    clear_screen()
    print()
    print()
    print("answer:")
    print()
    print("-" * 40)
    print_blue(answer)
    print("-" * 40)

    input("\npress enter to exit...")
    clear_screen()

if __name__ == "__main__":
    main()