import socketio
import asyncio
from core.client_utils import connect_to_socket


class FactoryClient:
    def __init__(self):
        self.CONNECTED_TO_SOCKET = False
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.result = None

    async def async_request(self, namespace, payload, scope):
        @self.sio.event(namespace=namespace)
        async def connect():
            global CONNECTED_TO_SOCKET
            print(f'Connected to {namespace} namespace!')
            self.CONNECTED_TO_SOCKET = True

        # Initiate the connection with the websocket
        await connect_to_socket(self.sio, namespace=namespace)

        # Wait until the connection is established
        while not self.CONNECTED_TO_SOCKET:
            await asyncio.sleep(0)

        # Request address information
        await self.sio.emit('subscribe', {
            'scope': ['portfolio', 'assets', 'deposits', 'loans', 'staked-assets', 'locked-assets', 'charts'],
            'payload': payload
        }, namespace=namespace)

        @self.sio.on(f'received address {scope}', namespace=namespace)
        def received_address_portfolio(data):
            print('Address portfolio is received')
            self.result = data['payload'][scope]

        # Wait until all information about the address is received
        while self.result is None:
            await asyncio.sleep(0)

        return self.result

    def sync_request(self, namespace, payload, scope):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_request(namespace, payload, scope))
