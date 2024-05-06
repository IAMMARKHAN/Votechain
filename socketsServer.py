import asyncio
import json
import websockets
import ssl
from multiprocessing import Process, Queue

def read_json_and_put_into_queue(file_path, queue):
    while True:
        with open(file_path, 'r') as file:
            data = json.load(file)
            queue.put(data)

async def handle_connection(websocket, path, queue):
    while True:
        try:
            data = queue.get()
            await websocket.send(json.dumps(data))
            await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            break

async def main(file_path):
    queue = Queue()
    p = Process(target=read_json_and_put_into_queue, args=(file_path, queue))
    p.start()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    async with websockets.serve(
        lambda websocket, path: handle_connection(websocket, path, queue),
        "localhost",
        8765,
        ssl=ssl_context,
    ):
        await asyncio.Future()

if __name__ == "__main__":
    file_path = "data.json"
    asyncio.run(main(file_path))
