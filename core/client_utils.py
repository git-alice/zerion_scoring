import yaml


def load_settings(setting_path):
    with open(setting_path) as f:
        settings = yaml.safe_load(f)
    return settings['connection_settings']


async def connect_to_socket(sio, namespace, seetting_path):
    settings = load_settings(seetting_path)
    await sio.connect(
        f"{settings['URI']}/?api_token={settings['API_TOKEN']}",  # Request
        headers={'Origin': settings['ORIGIN']},
        namespaces=[namespace],  # Namespaces
        transports=['websocket']
    )
