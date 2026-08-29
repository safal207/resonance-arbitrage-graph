from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_form_uses_explicit_https_submission_with_consent_and_fallbacks():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    js = (SITE / "app.js").read_text(encoding="utf-8")

    assert 'action="https://formsubmit.co/safal0645@gmail.com"' in html
    assert 'method="POST"' in html
    assert 'name="_honey"' in html
    assert 'name="_next" value="https://safal207.github.io/resonance-arbitrage-graph/thanks.html"' in html
    assert 'name="_replyto"' in html
    assert 'name="consent_statement"' in html
    assert 'id="consent" name="consent" value="Explicit consent granted" required' in html
    assert 'name="utm_source"' in html
    assert 'name="utm_medium"' in html
    assert 'name="utm_campaign"' in html
    assert 'name="source_page"' in html
    assert "up to 30 days" in html
    assert "No automatic data transmission before you press Submit" in html
    assert '_captcha=false' not in html

    assert "HTMLFormElement.prototype.submit.call(form)" in js
    assert "sessionStorage" in js
    assert "60_000" in js
    assert "mailto:safal0645@gmail.com" in js
    assert "navigator.clipboard" in js
    assert "submitted-at" in js


def test_thank_you_page_keeps_scope_boundary():
    html = (SITE / "thanks.html").read_text(encoding="utf-8")
    assert "Your request was submitted." in html
    assert "accepted your request for delivery to our Gmail" in html
    assert "not acceptance into a pilot" in html
    assert "not investment advice" in html
    assert "not a trading signal" in html
    assert "not a profitability claim" in html


def test_intake_docs_state_interim_processor_and_replacement_gate():
    docs = (ROOT / "docs" / "FORM_INTAKE.md").read_text(encoding="utf-8")
    assert "interim" in docs.lower()
    assert "FormSubmit" in docs
    assert "30 days" in docs
    assert "first-party" in docs
    assert "ten genuine submissions" in docs
    assert "human-browser submission" in docs
    assert "No bypass was attempted" in docs
