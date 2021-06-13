import numpy as np
import pandas as pd


# === Transactions ===

def get_price(changes_dict, deg=18):
    stock_price = changes_dict['price']
    value = changes_dict['value']
    if (stock_price is None) or (value is None):
        return np.nan
    order_price = (value / 10 ** deg) * stock_price
    return order_price


def income_outcome(changes):
    income = 0
    outcome = 0
    for change in changes:
        deg = change['asset']['decimals']
        if change['direction'] == 'in':
            income += get_price(change, deg)
        elif change['direction'] == 'out':
            outcome += get_price(change, deg)
    return income, outcome


def preprocess_transaction(transaction, type_of_deal, mined_at, hash_tr):
    if 'changes' in transaction:
        changes = transaction['changes']
    else:
        return None

    income, outcome = income_outcome(changes)

    fee = transaction['fee']
    if fee is not None:
        fee_price = get_price(fee)
    else:
        fee_price = np.nan

    df = pd.DataFrame(data={'timestamp': mined_at,
                            'type': type_of_deal,
                            'from': transaction['address_from'],
                            'to': transaction['address_to'],
                            'income': income,
                            'outcome': outcome,
                            'fee': fee_price},
                      index=[hash_tr])
    return df


def preprocess_transactions(transactions):
    chunks = []
    transaction_types = ['send', 'receive', 'trade', 'claim', 'authorize', 'withdraw', 'deposit',
                         'borrow', 'repay', 'stake', 'unstake', 'deployment', 'execution']
    for transaction in transactions:
        if transaction['type'] in transaction_types:
            chunk = \
                preprocess_transaction(transaction, transaction['type'], transaction['mined_at'], transaction['hash'])
            chunks.append(chunk)

    return chunks
