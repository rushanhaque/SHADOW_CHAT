# ShadowChat // BY RUSHAN HAQUE

ShadowChat is a secure, end-to-end encrypted messaging application with "Burn After Reading" capabilities.

## 🚀 Features
- **End-to-End Encryption**: Messages are encrypted on the client side.
- **Burn After Reading**: Rooms and messages can be wiped instantly.
- **WebSocket Real-time Communication**: Fast and responsive chat.
- **Ephemeral Rooms**: Links expire automatically.

---

## 🛠️ Requirements

- Python 3.8+
- [Optional] Redis (for persistent room management)

### Install Dependencies
Run the following command in your terminal:
```bash
pip install -r requirements.txt
```

---

## 🏃 How to Run (Direct Access)

1. Start the server:
   ```bash
   python server.py
   ```
2. The server will start on `http://localhost:8000`.
3. Open `http://localhost:8000` in your browser.

---

## 🌐 How to Run with Public Access (ngrok)

To share ShadowChat with friends over the internet, follow these steps:

### 1. Install ngrok
If you don't have ngrok, download it from [ngrok.com](https://ngrok.com/download) and sign up for a free account.

### 2. Connect your account
Run the following command with your auth token (found in your ngrok dashboard):
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 3. Start ShadowChat Server
Open a terminal and run:
```bash
python server.py
```

### 4. Start ngrok Tunnel
Open **another** terminal and run:
```bash
ngrok http 8000
```

### 5. Access the Public URL
- ngrok will provide a URL like `https://xxxx-xxxx-xxxx.ngrok-free.app`.
- Share this URL with your friends.
- They will be able to join your encrypted chat rooms using this link.

---

## 📂 Project Structure
- `server.py`: FastAPI backend handling WebSockets and room creation.
- `index.html`: The frontend application (HTML/CSS/JS).
- `requirements.txt`: List of Python libraries needed.

---

## ⚠️ Important Note
ShadowChat is designed for privacy. Ensure you use the `Burn Chat` button to wipe all traces of a conversation when finished.
