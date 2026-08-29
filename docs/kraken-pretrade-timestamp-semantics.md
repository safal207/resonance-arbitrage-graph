# Kraken PreTrade timestamp semantics

## Why this contract exists

Corpus Campaign 001 exposed a provenance mistake in the original Kraken
PreTrade adapter.

Kraken returns `publication_ts` on each bid or ask level. Kraken documents that
field as the time that **the price level** was last updated and published. It is
not documented as the publication time of the complete REST snapshot returned
to this client.

Official field reference:

- https://docs.kraken.com/api/docs/rest-api/get-pre-trade/

The original adapter selected the older top bid/ask `publication_ts`, labelled
the whole snapshot `exchange_published`, and used that time as the snapshot
freshness clock. A stable top level could therefore make a newly fetched public
snapshot appear tens of seconds old.

## Correct causal distinction

```text
observed_at_ms
  = when RESONANCE received the current public REST snapshot

source_timestamp_ms
  = when the preserved Kraken price level was last updated and published

snapshot freshness
  !=
price-level age
```

Kraken PreTrade snapshots with level timestamps use:

```text
timestamp_class = client_observed_level_update
freshness_reference_ms = observed_at_ms
source_timestamp_ms = oldest preserved top-level publication_ts
```

The level timestamp remains inside canonical market, rolling-window, replay and
corpus evidence. Changing or removing it changes the evidence digest. It simply
no longer claims to be the publication time of the complete snapshot.

The existing `exchange_published` class is unchanged. It remains appropriate
for a source that supplies an exchange timestamp for the complete snapshot and
continues to use `source_timestamp_ms` conservatively for freshness.

## Campaign boundary

Campaign 001 evidence is not retroactively reinterpreted. Its `UNKNOWN ->
REJECT` results remain a valid record of the measurement policy used at the
time.

Any measurement-corrected campaign must use a new dedicated corpus and bind its
own timestamp semantics, rolling-window policy, verifier policy, costs and
quality gate.

## Safety boundary

This change affects public-data provenance and paper verification only. It adds
no credentials, orders, signing, transfers, wallet control, live capital or
automatic policy promotion.
