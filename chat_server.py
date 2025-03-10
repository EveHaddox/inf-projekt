import socket
import threading
import json
import rsa

# Generate server RSA key pair (512 bits for demonstration; use larger keys in practice)
server_pub, server_priv = rsa.newkeys(512)

HOST = '0.0.0.0'
PORT = 5000

# Dictionary to keep track of connected clients and their public keys
clients = {}  # { client_socket: client_public_key }
lock = threading.Lock()

def broadcast(message_text):
    """Encrypts the plain text message for each client and sends it."""
    with lock:
        for client_sock, client_pub in list(clients.items()):
            try:
                encrypted = rsa.encrypt(message_text.encode('utf8'), client_pub)
                out_msg = {"type": "msg", "data": encrypted.hex()}
                client_sock.sendall((json.dumps(out_msg) + "\n").encode('utf8'))
            except Exception as e:
                print("Error sending to client:", e)
                client_sock.close()
                del clients[client_sock]

def handle_client(client_sock, addr):
    print(f"New connection from {addr}")
    try:
        # Send server's public key to the client
        server_pub_pem = server_pub.save_pkcs1().decode('utf8')
        init_msg = {"type": "server_pubkey", "data": server_pub_pem}
        client_sock.sendall((json.dumps(init_msg) + "\n").encode('utf8'))
        
        # Wait for client to send its public key
        data = client_sock.recv(4096).decode('utf8')
        if not data:
            client_sock.close()
            return
        for line in data.splitlines():
            msg = json.loads(line)
            if msg.get("type") == "pubkey":
                client_pub_pem = msg.get("data")
                client_pub = rsa.PublicKey.load_pkcs1(client_pub_pem.encode('utf8'))
                with lock:
                    clients[client_sock] = client_pub
                break
        
        # Listen for encrypted messages from the client
        buffer = ""
        while True:
            data = client_sock.recv(4096).decode('utf8')
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
                    try:
                        encrypted_bytes = bytes.fromhex(encrypted_hex)
                        # Decrypt using the server's private key
                        plain_text = rsa.decrypt(encrypted_bytes, server_priv).decode('utf8')
                        print(f"Received message from {addr}: {plain_text}")
                        # Broadcast the plain text to all clients
                        broadcast(plain_text)
                    except Exception as e:
                        print("Error decrypting message:", e)
    except Exception as e:
        print("Error handling client:", e)
    finally:
        with lock:
            if client_sock in clients:
                del clients[client_sock]
        client_sock.close()
        print(f"Connection closed {addr}")

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print("Server listening on", (HOST, PORT))
    
    try:
        while True:
            client_sock, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_sock.close()

if __name__ == '__main__':
    main()
