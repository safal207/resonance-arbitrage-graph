# Founding-list form intake

Status: interim production intake for PLF discovery; awaiting one-time recipient activation.

## Current path

```text
explicit visitor submit
→ FormSubmit HTTPS processor
→ optional anti-spam check
→ delivery to safal0645@gmail.com
→ thank-you page
→ manual discovery coding
```

The static GitHub Pages site cannot persist requests by itself. This integration replaces the fragile `mailto:`-only path while preserving copy/email fallback.

## Data collected

- work email;
- company/project;
- role;
- preferred integration;
- bounded workflow description;
- hardest pre-trade failure;
- public/sandbox sample availability;
- pilot interest;
- explicit consent statement and submission timestamp;
- source page, `ref`, `utm_source`, `utm_medium`, and `utm_campaign`.

Never collect credentials, keys, balances, signing permissions, account identifiers, private strategy code, or production secrets.

## Processor boundary

FormSubmit delivers the submission by email and documents a recoverable archive retained for up to 30 days. Gmail is the working record; the processor archive is not treated as the canonical CRM.

The page discloses the external processor before submission. Nothing is transmitted before the visitor presses Submit. The page contains no analytics tracker.

## Reliability controls

- native HTTPS POST;
- required-field and email validation;
- explicit consent;
- honeypot;
- processor anti-spam challenge;
- 60-second client-side exact-duplicate guard;
- absolute source and thank-you URLs;
- UTM/ref attribution;
- copy/email fallback;
- deployment validation that fails if the endpoint or disclosure disappears.

## Activation boundary

FormSubmit requires one confirmation email for a new recipient/form. Direct curl, AJAX, and a standard headless Chromium probe were all stopped by the provider's Cloudflare human-verification gate. No bypass was attempted.

Activation therefore requires one normal human-browser submission from the live page, followed by the confirmation link sent to `safal0645@gmail.com`. Until both actions complete, the page must not be described as a confirmed automatic intake channel; the copy/email fallback remains available.

After activation, submit one clearly labelled system test and verify that it arrives in Gmail before directing broader PLF traffic to the form.

## Replacement gate

Replace this interim processor with a first-party endpoint, durable database, authenticated admin view, server-side rate limiting, and notification retries when either condition is met:

1. ten genuine submissions have been received; or
2. the first paid design-partner pilot is agreed.

The replacement must preserve consent evidence, attribution, exportability, and email fallback.
