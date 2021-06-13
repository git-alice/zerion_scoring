from functools import reduce
import numpy as np
import time
from scipy.interpolate import interp1d

from .request import FactoryClient


def transactions_parsing(address):
    chunks = []
    i = 0

    while True:
        f = FactoryClient('../settings.yaml')
        data = f.sync_request(
            namespace='/address',
            payload={
                'address': address,
                'currency': 'usd',
                'portfolio_fields': 'all',
                'transactions_offset': i
            },
            scope='transactions'
        )
        chunks.append(data)
        i += 50

        time.sleep(0.1)  # 0_o

        if len(data) < 50:
            break

    return reduce(lambda acc, arr: acc + arr, chunks, [])


def charts_parsing(address):
    f = FactoryClient('../settings.yaml')
    charts = f.sync_request(
        namespace='/address',
        payload={
            'address': address,
            'currency': 'usd',
            'portfolio_fields': 'all',
            'charts_type': 'y',
        },
        scope='charts'
    )
    charts = np.array(charts['others'])
    return charts


def wallet_price_by_timestamps(address, timestamps):
    charts = charts_parsing(address)
    available_timestamps, available_wallet_prices = charts[:, 0], charts[:, 1]
    func = interp1d(available_timestamps, available_wallet_prices, bounds_error=False)
    return func(timestamps)
