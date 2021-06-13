import socketio
import asyncio
import random
import string
import time
from core.client_utils import connect_to_socket, async_connect_to_socket


class FactoryClient:
    def __init__(self, setting_path='settings.yaml'):
        self.CONNECTED_TO_SOCKET = False
        self.async_sio = socketio.AsyncClient(logger=False, engineio_logger=False, reconnection_delay=1,
                                              reconnection_delay_max=5, randomization_factor=3, ssl_verify=False)
        self.sync_sio = socketio.Client(logger=False, engineio_logger=False, reconnection_delay=1,
                                        reconnection_delay_max=5, randomization_factor=3, ssl_verify=False,
                                        request_timeout=2)
        self.result = None
        self.setting_path = setting_path

    def update_my_super_progress_bar(self, N=7, s='Что то происходит...'):
        print(f'\r{s} | ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=N)), end='')

    async def async_request(self, namespace, payload, scope):
        @self.async_sio.event(namespace=namespace)
        async def connect():
            # print(f'Connected to {namespace} namespace!')
            self.update_my_super_progress_bar(s='Connect')
            self.CONNECTED_TO_SOCKET = True

        # Initiate the connection with the websocket
        await async_connect_to_socket(self.async_sio, namespace=namespace, seetting_path=self.setting_path)

        # Wait until the connection is established
        if not self.CONNECTED_TO_SOCKET:
            await asyncio.sleep(5)

        # Request address information
        await self.async_sio.emit('subscribe', {
            'scope': [scope],
            'payload': payload
        }, namespace=namespace)

        @self.async_sio.on(f'received {namespace[1:]} {scope}', namespace=namespace)
        def received_address_portfolio(data):
            # print('Address portfolio is received')
            self.update_my_super_progress_bar(s='Wait')
            self.result = data['payload'][scope]

        # Wait until all information about the address is received
        while self.result is None:
            await asyncio.sleep(0)

        return self.result

    def sync_request(self, namespace, payload, scope):
        @self.sync_sio.event(namespace=namespace)
        def connect():
            self.update_my_super_progress_bar(s='Connect')
            self.CONNECTED_TO_SOCKET = True

        # Initiate the connection with the websocket
        connect_to_socket(self.sync_sio, namespace=namespace, seetting_path=self.setting_path)

        # Wait until the connection is established
        for _ in range(7):
            if not self.CONNECTED_TO_SOCKET:
                time.sleep(1)

        if not self.CONNECTED_TO_SOCKET:
            raise Exception('Блэд')

        # Request address information
        self.sync_sio.emit('subscribe', {
            'scope': [scope],
            'payload': payload
        }, namespace=namespace)

        @self.sync_sio.on(f'received {namespace[1:]} {scope}', namespace=namespace)
        def received_address_portfolio(data):
            # print('Address portfolio is received')
            self.update_my_super_progress_bar(s='Wait')
            self.result = data['payload'][scope]

        # # Wait until all information about the address is received
        while self.result is None:
            time.sleep(0)

        return self.result
