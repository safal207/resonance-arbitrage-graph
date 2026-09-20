# External Verification & Upstream Review Record

This page tracks external engineering evidence connected to the work behind RESONANCE and related reliability research.

The entries are intentionally separated by evidence strength. An independent reproduction is not treated as equivalent to an upstream discussion, and an accepted technical correction is not presented as a merged framework change.

## Evidence levels

| Level | Meaning |
| --- | --- |
| **A — Independent reproduction** | A third party independently obtains public artifacts, runs the verification path, and reports reproducible results. |
| **B — External technical review** | A third party checks a technical claim or mapping against code/artifacts and adopts or confirms corrections. |
| **C — Upstream technical influence** | A technical distinction or boundary raised in an upstream issue is explicitly accepted or incorporated into the next design/test iteration. This is not a framework merge or product adoption claim. |

---

## A — Independent reproduction

### CrewAI #5802 — public RESONANCE evidence bundles

**Context:** CrewAI issue [#5802](https://github.com/crewAIInc/crewAI/issues/5802) discusses retry/idempotency failure boundaries for effectful tools.

Two public RESONANCE evidence bundles were offered as a bounded external comparison:

- [successful observation bundle](https://github.com/safal207/resonance-arbitrage-graph/blob/34e99b59424924a50f5e35966bfd531d16eb1e2b/docs/evidence/wallet-watch-pr85/recent-resume-20260906/README.md)
- [incomplete-retrieval control](https://github.com/safal207/resonance-arbitrage-graph/blob/4cc66497c2e32221d3a726cd78b247cda57873b1/docs/evidence/wallet-watch-pr85/resume-20260906/README.md)

External contributor `@azender1` reported that both downloaded archives matched their published SHA-256 manifests and both offline verifiers passed at the pinned source commit.

The external classification preserved the intended claim boundary:

- successful package → `OBSERVED_EVENT_ONLY`;
- failed retrieval → `INCOMPLETE_RETRIEVAL / UNCERTAIN`;
- `event.event_id` remained an external chain/log identity rather than being promoted into a pre-dispatch logical-action or payment-intent ID.

The reviewer also reported that their narrow adapter plus four boundary tests left their complete local suite at `153/153`.

**External record:** [azender1 comparison](https://github.com/crewAIInc/crewAI/issues/5802#issuecomment-5743395182)

**What this supports:** reproducible bundle integrity, offline verification, and conservative classification by an external party.

**What it does not support:** independent network completeness, real payment execution, LangGraph/CrewAI framework correctness, fresh-worker crash recovery, or a general exactly-once guarantee.

---

## B — External technical review

### x402 #3379 — field provenance and cross-artifact seams

**Context:** x402 issue [#3379](https://github.com/x402-foundation/x402/issues/3379) explores externally verifiable evidence around paid agent work and receipt composition.

During the receipt/claim schema mapping discussion, `@safal207` checked the claim column against the current `holistis/tokenizen` implementation and identified six evidence-grade corrections, including:

- the provenance link pointed to the wrong repository/PR;
- `computeClaimId` covers the full normalized `ClaimContent`;
- `priorClaimId` is asserted while later completeness analysis is derived;
- `externalRefs.disputeContext` is an unverified citation;
- `evidenceHash` is a signed hash binding, not independent evidence verification;
- `receipt.stdout_sha256` and `claim.delivered` answer different propositions and should be described as a coverage gap/no cross-binding rather than a logical contradiction.

**Correction record:** [safal207 review](https://github.com/x402-foundation/x402/issues/3379#issuecomment-5731487483)

`@goun7` then reported that all six corrections were applied and independently checked against the pinned implementation commit. The resulting map was updated with an auditable diff rather than silently changed.

**External confirmation:** [goun7 verification and applied corrections](https://github.com/x402-foundation/x402/issues/3379#issuecomment-5731942887)

A later FIELD-PROVENANCE pass caused one additional correction on the receipt/claim map: `evidenceHash` was relabeled **asserted** after the reviewer concluded that treating it as even a limited derived field overclaimed what a stranger can recompute from the claim bytes.

**Follow-up confirmation:** [FIELD-PROVENANCE review](https://github.com/x402-foundation/x402/issues/3379#issuecomment-5734280155)

A remaining seam was then stated explicitly: two independently valid artifacts do not by themselves prove that they belong to the same purchase; settlement and party binding still need to be resolved and joined.

**Seam record:** [cross-artifact settlement binding](https://github.com/x402-foundation/x402/issues/3379#issuecomment-5735610802)

**What this supports:** externally reviewed provenance reasoning and corrections that materially changed a public schema/evidence map.

**What it does not support:** x402 adoption, a merged x402 protocol change, proof that the composed artifacts describe the same settlement, or end-to-end settlement/delivery correctness.

---

## C — Upstream technical influence

### LangGraph #7417 — UNKNOWN vs CONFLICT at recovery boundaries

**Context:** LangGraph issue [#7417](https://github.com/langchain-ai/langgraph/issues/7417) documents a replay/recovery boundary involving long-running tool work, checkpoints, and repeated execution.

A public local recovery A/B reported:

- baseline: two node entries / two external effects;
- guarded path: two node entries / one external effect;
- missing receipt on first recovery: fail closed, later return prior;
- receipt digest mismatch: remain unknown and do not redispatch;
- authority revoked after target commit: read-only reconciliation and return prior.

The author explicitly limited the claim to a deterministic local LangGraph + SQLite process-restart fixture rather than LangGraph Cloud or global exactly-once behavior.

**External experiment:** [Pushkard17 recovery A/B](https://github.com/langchain-ai/langgraph/issues/7417#issuecomment-5692967829)

After reviewing that result, `@safal207` identified a useful semantic distinction: a missing authoritative receipt and a present-but-mismatched receipt should not collapse into the same state. The suggestion was to distinguish:

- `UNKNOWN` — authoritative receipt not visible yet;
- `MISMATCH / CONFLICT` — a receipt exists but does not bind to the intended action/digest.

Both remain non-authorizing.

**Technical review:** [safal207 UNKNOWN vs CONFLICT comment](https://github.com/langchain-ai/langgraph/issues/7417#issuecomment-5699415522)

`@Pushkard17` explicitly accepted the distinction and stated that the implementation/test path would separate `UNKNOWN` from `CONFLICT`, keep both non-authorizing, and test delayed visibility separately from contradictory evidence.

**Accepted follow-up:** [Pushkard17 response](https://github.com/langchain-ai/langgraph/issues/7417#issuecomment-5701980916)

**What this supports:** a concrete upstream reliability distinction was reviewed, accepted, and carried into the next stated implementation/test direction.

**What it does not support:** a LangGraph framework merge, LangGraph Cloud validation, formal maintainer endorsement of RESONANCE, or proof of global exactly-once execution.

---

## Why this record exists

The goal is not to count comments or logos. The useful signal is whether technical claims survive contact with independent readers, reproducible artifacts, source inspection, and explicit counterexamples.

A strong evidence trail should make four things easy to distinguish:

```text
what was observed
what was independently recomputed
what was only asserted
what remains unknown
```

That separation is the common thread across the three cases above.
