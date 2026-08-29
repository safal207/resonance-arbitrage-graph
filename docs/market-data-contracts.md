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
- Kraken's raw Bitcoin asset code `XBT` is explicitly normalized to the cross-venue RESONANCE identity `BTC`; the raw exchange symbol (for example `XBT/USD`) remains preserved in `QuoteSnapshot.symbol` and source provenance.
- No fuzzy symbol matching is used. Asset aliases must be explicitly enumerated by the adapter, and any other metadata mismatch remains fail-closed.
- Kraken documents each level's `publication_ts` as the time that price level was last updated and published. It is not the acquisition time of the current REST response. A resting best level can remain current while that level timestamp grows old.
- The adapter therefore labels the normalized REST snapshot `client_observed` and uses its local observation time for hard snapshot freshness. It does not overload `source_timestamp_ms` with per-level update semantics.
- The exact source URL is preserved as both quote and metadata provenance.

Official documentation:
- https://docs.kraken.com/api/docs/rest-api/get-pre-trade

## Evidence binding

Market evidence binds each route edge to exactly one supplied quote snapshot by venue, asset direction, rate, top-of-book capacity, and quote age at the recorded evaluation time. A missing or ambiguous binding is rejected instead of producing a receipt.

The hard freshness reference must describe when the normalized snapshot was available to the verifier. Auxiliary venue timestamps with narrower meanings, such as the last update of one resting order-book level, must not be substituted for snapshot acquisition time.

## Safety boundary

No private key, API key, signed request, account endpoint, order endpoint, wallet endpoint, or fund-transfer endpoint is implemented in this layer.
