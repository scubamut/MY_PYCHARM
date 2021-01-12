from datetime import datetime, timedelta, timezone,date
import pytz

from zipline import run_algorithm
from zipline.api import symbols, symbol, attach_pipeline, schedule_function, pipeline_output
from zipline.api import set_benchmark, set_slippage, set_commission, record, order, cancel_order
from zipline.api import get_open_orders, order_target_percent, order_target, get_datetime, set_benchmark
from zipline.utils.events import time_rules, date_rules
from zipline.finance import commission, slippage

import matplotlib.pyplot as plt

"""
Basic 60/40 Benchmark Portfolio based on monthly rebalancing
"""


def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    context.assets = [(symbol('IEF'), 0.40),  # bond etf
                      (symbol('QQQ'), 0.60)]  # Nasdaq etf

    context.first_rebalance = 0

    set_commission(commission.PerShare(cost=0.005, min_trade_cost=1))
    # Rebalance every month, at market open.
    schedule_function(my_rebalance,
                      date_rules.month_end(days_offset=0),
                      time_rules.market_open(minutes=1))


def my_rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    assets = context.assets

    if context.first_rebalance == 0:
        for asset in context.assets:
            if data.can_trade(asset[0]):
                order_target_percent(asset[0], asset[1])
                context.first_rebalance = 1
        return

    value = context.portfolio.portfolio_value
    asset = assets[0]
    bond_value = context.portfolio.positions[asset[0]].amount * \
                 data.current(asset[0], 'price')
    bonds = bond_value / value

    diff = abs(.40 - bonds) * 2.
    if diff >= .1:
        for asset in assets:
            order_target_percent(asset[0], asset[1])

    # print(diff, bonds, 1. - bonds)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    start = datetime(2000, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2020, 11, 1, 0, 0, 0, 0, pytz.utc)
    #     end = datetime.today().replace(tzinfo=timezone.utc)
    capital_base = 10000

    result = run_algorithm(start=start, end=end, initialize=initialize, \
                           capital_base=capital_base, \
                           # before_trading_start=before_trading_start,
                           # handle_data=handle_data,
                           bundle='etfs_bundle')


result.portfolio_value.plot()
plt.show()
pass