import asyncio
from live_api import LiveApi
import pandas as pd
import numpy as np
from numpy import mean
import math

api = LiveApi()

async def candleDetails(candle):
    open = candle['open']
    high = candle['high']
    low = candle['low']
    close = candle['close']
    # Avoid dojo candles
    if open == close or high == low:
        return
    type = ''
    if open > close:
        type = "BEARISH"
    elif open < close:
        type = "BULLISH"
    bodySize = abs(open - close)
    upperBodySize = open > close ? high - open : high - close
    lowerBodySize = open > close ? close - low : open - low
    candleSize = high - low
    return {
        "type": type,
        "bodySize": bodySize,
        "upperBodySize": upperBodySize,
        "lowerBodySize": lowerBodySize
    }

async def identifyCandlePatternBullishEngulfing(candles):
    candles = candles.sort_values(by=['epoch'])
    direction = candles['close'].iloc[-1] - candles['close'].iloc[0]
    if direction > 0:
        firstCandle = candles.iloc[-1]
        secondCandle = candles.iloc[-2]
        secondCandleSummary = candleDetails(secondCandle)
        if secondCandleSummary['type'] == "BEARISH":
            firstCandleSummary = candleDetails(firstCandle)
            if firstCandleSummary['type'] == "BULLISH":
                if firstCandleSummary['bodySize'] > secondCandleSummary['bodySize']:
                    print("yeah we found it")
                    return True
        return False

async def main():
    await api.authorize('YOUR_API_KEY')
    api.subscribe_to_balance()
    api.events.on("balance", (res) => {
        const balance = res.balance;
        console.log(balance);
    });
    # Read market data
    candles = pd.DataFrame(columns=['epoch', 'open', 'high', 'low', 'close'])
    api.getTickHistory("R_50", { end: 'latest', count: 5, "style": "candles", "subscribe": 1 });
    api.events.on("candles", async (res) => {
        candles = res.candles;
        identifyCandlePatternBullishEngulfing(candles);
    });
    api.events.on("ohlc", async (res) => {
        ohlc = res.ohlc;
        if ohlc['epoch'] % 60 == 0:
            # print(ohlc)
            # Append New Candle to list
            candles = candles.append({
                'epoch': ohlc['epoch'],
                'open': ohlc['open'],
                'high': ohlc['high'],
                'low': ohlc['low'],
                'close': ohlc['close'],
            }, ignore_index=True)
            # Remove Unwanted candles
            if candles.shape[0] > 10:
                candles = candles.iloc[1:]
            if identifyCandlePatternBullishEngulfing(candles):
                # Place Order
                param = {}
                param['amount'] = 1
                param['basis'] = 'payout'
                param['contract_type'] = "CALL"
                param['currency'] = 'USD'
                param['duration'] = 2