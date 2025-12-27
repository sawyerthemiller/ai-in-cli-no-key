import socket
import time
import os
from playwright.sync_api import sync_playwright

SERVER_IP = "localhost"
PORT = 19
USER_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def run_server():
    # only one print at startup
    clear_screen()
    print()
    print()
    print(f"server started on {PORT}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="msedge",
            headless=False,
            args=["--no-sandbox"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://chatgpt.com")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((SERVER_IP, PORT))
        server.listen(1)

        while True:
            conn, _ = server.accept()
            
            try:
                data = b''
                while True:
                    packet = conn.recv(4096)
                    if not packet: break
                    data += packet
                
                prompt_text = data.decode('utf-8')
                if not prompt_text: continue
                print ()
                print()
                print("our time is now")

                # new chat
                try:
                    page.click('[data-testid="create-new-chat-button"]', timeout=1000)
                except:
                    page.keyboard.press("Control+Shift+O")
                
                time.sleep(0.5)

                # input
                input_selector = '#prompt-textarea'
                page.wait_for_selector(input_selector)
                page.fill(input_selector, prompt_text)
                page.keyboard.press("Enter")

                # wait for the "stop generating" button to show
                # this ensures we don't scrape before it even starts
                try:
                    page.wait_for_selector('button[aria-label="Stop generating"]', state='visible', timeout=5000)
                except:
                    pass # proceed if it failed (maybe response was instant)

                # wait for the "stop generating" button to gone
                # This ensures we wait until it is fully done.
                try:
                    page.wait_for_selector('button[aria-label="Stop generating"]', state='hidden', timeout=60000)
                except:
                    pass
                
                # small safety buffer to let the DOM settle
                time.sleep(0.5)

                # scrape
                responses = page.query_selector_all('.markdown')
                reply = responses[-1].inner_text() if responses else ""

                conn.sendall(reply.encode('utf-8'))
                print()
                print()
                print("sent data to client")
            
            except Exception:
                pass # silent error handling
            
            finally:
                conn.close()

if __name__ == "__main__":
    run_server()