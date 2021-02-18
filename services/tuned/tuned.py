import logging
from collections import namedtuple

import aiohttp

logger = logging.getLogger(__name__)

Execution = namedtuple('Execution',
                       'token name exchange symbol timeframe profit mdd wins trades side position_profit position_amount')


async def get_execution(token):
    """
    shogun binance spot eth MLrBQvKWNJpyNcEXkonrLHlzxjVtse
    shogun bitmex eth IUzkUkyLIiXyhLCoYseiDErhXBHYzg
    """
    payload = [{
        "operationName": "GetSharedExecution",
        "variables": {
            "query": {"numberOfResults": 20},
            "filters": [],
            "sort": {"sortKey": "CREATION_DATE", "sortDirection": "DESC"},
            "shareToken": token
        },
        "query": "query GetSharedExecution($shareToken: ID!) {\n  sharedExecution(shareToken: $shareToken) {\n    ...SharedExecutionData\n    __typename\n  }\n}\n\nfragment SharedExecutionData on SharedExecution {\n  shareToken\n  name\n  exchange\n  currencyPair\n  candleSize\n  measurements {\n    ...MeasurementData\n    __typename\n  }\n  __typename\n}\n\nfragment MeasurementData on Measurements {\n  absoluteProfit\n  avgBarsInTrade\n  numberOfTrades\n  maxDrawdown\n  percentProfitableTrades\n  profitability\n  profitFactor\n  buyHoldRatio\n  avgTradePrice\n  avgPositionPrice\n  lastTick\n  positionProfitLoss\n  avgMonthlyProfit\n  avgWinMonth\n  avgLoseMonth\n  percProfitableMonths\n  positionAbsoluteProfit\n  positionAmount\n  positionProfitLoss\n  balance\n  riskScore\n  __typename\n}\n"
    }]

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.tuned.com/graphql', json=payload) as response:
            if response.status != 200:
                logger.error(response)
                return None

            r = await response.json()
            result = r[0]['data']['sharedExecution']
            logger.debug(result)

            if result is None:
                # may return 200 but empty result
                logger.error(response)
                return None
            if result['measurements']['positionAmount'] == 'NaN':
                pos_amount = None
                pos_profit = None
                side = None
            else:
                pos_amount = float(result['measurements']['positionAmount'])
                pos_profit = float(result['measurements']['positionProfitLoss'])
                side = 'buy' if pos_amount > 0 else 'sell'

            return Execution(
                **{
                    'token': result['shareToken'],
                    'name': result['name'],
                    'exchange': result['exchange'],
                    'symbol': result['currencyPair'],
                    'timeframe': result['candleSize'],
                    'profit': round(float(result['measurements']['profitability']) * 100, 2),
                    'mdd': round(float(result['measurements']['maxDrawdown']) * 100, 2),
                    'wins': round(float(result['measurements']['percentProfitableTrades']) * 100, 2),
                    'trades': int(result['measurements']['numberOfTrades']),
                    'side': side,
                    'position_profit': pos_profit,
                    'position_amount': pos_amount,
                }
            )
