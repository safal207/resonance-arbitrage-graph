# Public market-data contracts

v0.2 only consumes unauthenticated, read-only market data.

## Binance Spot

- Public market-data base: `https://data-api.binance.vision`
- Best bid/ask endpoint: `GET /api/v3/ticker/bookTicker`
- Normalized fields: symbol, bid price/qty, ask price/qty
- The REST response does not include an exchange publication timestamp, so the adapter records a client-observed timestamp and labels it `client_observed`.

Official documentation:
- https://developers.binance.com/en/docs/products/spot/rest-api
- https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market

## Kraken Spot

- Public base: `https://api.kraken.com`
- Top-of-book endpoint: `GET /0/public/PreTrade`
- Normalized fields: symbol, base/quote assets, bid/ask price and quantity
- The response includes `publication_ts` on price levels; v0.2 conservatively uses the older of the top bid/ask publication timestamps as the quote freshness reference.

Official documentation:
- https://docs.kraken.com/api/docs/rest-api/get-pre-trade

## Safety boundary

No private key, API key, signed request, account endpoint, order endpoint, wallet endpoint, or fund-transfer endpoint is implemented in this layer.
