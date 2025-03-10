import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import threading
import socket
import json
import rsa

SERVER_HOST = '127.0.0.1'  # Change to your server's IP if needed
SERVER_PORT = 5000

class ChatLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Chat display area
        self.chat_history = Label(text="Chat History:\n", size_hint=(1, 0.8))
        self.add_widget(self.chat_history)
        
        # Text input for new messages
        self.text_input = TextInput(hint_text="Type your message here", size_hint=(1, 0.1))
        self.add_widget(self.text_input)
        
        # Send button
        self.send_button = Button(text="Send", size_hint=(1, 0.1))
        self.send_button.bind(on_press=self.send_message)
        self.add_widget(self.send_button)
        
        # Generate client's RSA key pair (512 bits for demo)
        self.client_pub, self.client_priv = rsa.newkeys(512)
        self.server_pub = None  # Will be set after key exchange
        
        # Connect to the server socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((SERVER_HOST, SERVER_PORT))
        except Exception as e:
            self.update_chat(f"Connection error: {e}")
            return
        
        # Start background threads for key exchange and listening for messages
        threading.Thread(target=self.initialize_keys, daemon=True).start()
        threading.Thread(target=self.listen_to_server, daemon=True).start()
    
    def initialize_keys(self):
        """Handles the initial key exchange without blocking the UI."""
        try:
            data = self.sock.recv(4096).decode('utf8')
            for line in data.splitlines():
                msg = json.loads(line)
                if msg.get("type") == "server_pubkey":
                    server_pub_pem = msg.get("data")
                    self.server_pub = rsa.PublicKey.load_pkcs1(server_pub_pem.encode('utf8'))
                    # Now send our public key to the server
                    client_pub_pem = self.client_pub.save_pkcs1().decode('utf8')
                    out_msg = {"type": "pubkey", "data": client_pub_pem}
                    self.sock.sendall((json.dumps(out_msg) + "\n").encode('utf8'))
                    # Inform UI that connection is ready
                    Clock.schedule_once(lambda dt: self.update_chat("Connected to server!"))
                    break
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_chat("Error during key exchange: " + str(e)))
    
    def listen_to_server(self):
        """Continuously listens for messages from the server."""
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode('utf8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    msg = json.loads(line)
                    if msg.get("type") == "msg":
                        encrypted_hex = msg.get("data")
                        encrypted_bytes = bytes.fromhex(encrypted_hex)
                        try:
                            plain_text = rsa.decrypt(encrypted_bytes, self.client_priv).decode('utf8')
                            # Safely update UI from the background thread
                            Clock.schedule_once(lambda dt, text=plain_text: self.update_chat(text))
                        except Exception as e:
                            print("Error decrypting message:", e)
            except Exception as e:
                print("Error receiving data:", e)
                break
    
    def update_chat(self, message):
        """Updates the chat history."""
        self.chat_history.text += "\n" + message

    def send_message(self, instance):
        """Encrypts and sends a message to the server."""
        message_text = self.text_input.text.strip()
        if message_text and self.server_pub:
            try:
                # Encrypt the message using the server's public key
                encrypted = rsa.encrypt(message_text.encode('utf8'), self.server_pub)
                out_msg = {"type": "msg", "data": encrypted.hex()}
                self.sock.sendall((json.dumps(out_msg) + "\n").encode('utf8'))
                self.text_input.text = ""
            except Exception as e:
                self.update_chat("Error sending message: " + str(e))
        else:
            self.update_chat("Not connected to server or empty message.")

class ChatApp(App):
    def build(self):
        return ChatLayout()

if __name__ == '__main__':
    ChatApp().run()
