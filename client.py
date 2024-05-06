import asyncio
import json
import websockets
import ssl

async def main():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Ignore certificate verification (for self-signed certificates)

    async with websockets.connect(
        'wss://localhost:8765',  # Replace with your server's WebSocket URL
        ssl=ssl_context,
    ) as websocket:
        while True:
            data = await websocket.recv()
            print("Received:", data)

if __name__ == "__main__":
    asyncio.run(main())
