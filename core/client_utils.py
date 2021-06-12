import yaml


def load_settings():
    with open('settings.yaml') as f:
        settings = yaml.safe_load(f)
    return settings['connection_settings']


async def connect_to_socket(sio, namespace):
    settings = load_settings()
    await sio.connect(
        f"{settings['URI']}/?api_token={settings['API_TOKEN']}",  # Request
        headers={'Origin': settings['ORIGIN']},
        namespaces=[namespace],  # Namespaces
        transports=['websocket']
    )
