from core.request import FactoryClient

if __name__ == '__main__':
    test_address = '0x7e5ce10826ee167de897d262fcc9976f609ecd2b'

    f = FactoryClient()
    result = f.sync_request(
        namespace='/address',
        payload={
            'address': test_address,
            'currency': 'usd',
            'portfolio_fields': 'all'
        },
        scope='transactions'
    )
    print(result)
