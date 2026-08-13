# Public market-data contracts

v0.2 only consumes unauthenticated, read-only market data.

## Binance Spot

- Public market-data base: `https://data-api.binance.vision`
- Best bid/ask endpoint: `GET /api/v3/ticker/bookTicker`
- Pair metadata endpoint: `GET /api/v3/exchangeInfo?symbol=...`
- The adapter verifies the requested symbol against exchange-reported `baseAsset`, `quoteAsset`, trading status, and spot-trading availability before building graph edges.
- Pair metadata is cached per adapter process; the metadata URL is preserved in `QuoteSnapshot` and market evidence.
- Normalized quote fields: symbol, bid price/qty, ask price/qty
- `bookTicker` does not include an exchange publication timestamp, so the adapter records a client-observed timestamp and labels it `client_observed`.

Official documentation:
- https://developers.binance.com/en/docs/products/spot/rest-api
- https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general-endpoints
- https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market

## Kraken Spot

- Public base: `https://api.kraken.com`
- Top-of-book endpoint: `GET /0/public/PreTrade`
- Normalized fields: symbol, base/quote assets, bid/ask price and quantity
- The same response supplies pair metadata and per-level `publication_ts`; v0.2 conservatively uses the older of the top bid/ask publication timestamps as the quote freshness reference.
- The source URL is preserved as both quote and metadata provenance for this adapter.

Official documentation:
- https://docs.kraken.com/api/docs/rest-api/get-pre-trade

## Evidence binding

Market evidence binds each route edge to exactly one supplied quote snapshot by venue, asset direction, rate, top-of-book capacity, and quote age at the recorded evaluation time. A missing or ambiguous binding is rejected instead of producing a receipt.

## Safety boundary

No private key, API key, signed request, account endpoint, order endpoint, wallet endpoint, or fund-transfer endpoint is implemented in this layer.
