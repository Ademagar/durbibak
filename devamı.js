async def main():
    await api.authorize('FMewJFZjWVU6LZm')
    api.subscribeToBalance()
    api.events.on("balance", (res) => {
        const balance = res.balance;
        console.log(balance);
    });
    # Read market data
    candles = []
    api.getTickHistory("R_50", { end: 'latest', count: 5, "style": "candles", "subscribe": 1 });
    api.events.on("candles", async (res) => {
        candles = res.candles;
        identifyCandlePatternBullishEngulfing(candles);
    });
    api.events.on("ohlc", async (res) => {
        ohlc = res.ohlc;
        if (ohlc.epoch % 60 === 0) {
            # console.log(ohlc);
            # Append New Candle to list
            candles.push({
                epoch: ohlc.epoch,
                open: ohlc.open,
                high: ohlc.high,
                low: ohlc.low,
                close: ohlc.close,
            });
            # Remove Unwanted candles
            if (len(candles) > 10): candles.pop()
            if (identifyCandlePatternBullishEngulfing(candles)) {
                # Place Order
                param = {}
                param.amount = 1
                param.basis = 'payout'
                param.contract_type = "CALL"
                param.currency = 'USD'
                param.duration = 2
                param.duration_unit = 'm'
                param.symbol = "R_50"
                max = 1
                this.api.buyContractParams(param, max).then(console.log).catch(console.error)
            }
        }
    });
main().then(console.log).catch(console.error);