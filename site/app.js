(() => {
  "use strict";

  const form = document.getElementById("founding-form");
  const errorBox = document.getElementById("form-error");
  const successBox = document.getElementById("success-message");
  const copyButton = document.getElementById("copy-button");

  const requiredIds = [
    "email",
    "company",
    "role",
    "integration",
    "workflow",
    "failure",
    "sample",
    "pilot-interest",
    "consent"
  ];

  const get = (id) => document.getElementById(id);
  const clean = (value) => String(value || "").replace(/[\u0000-\u001f\u007f]/g, " ").trim();

  function validate() {
    let firstInvalid = null;
    const problems = [];

    requiredIds.forEach((id) => {
      const field = get(id);
      const invalid = field.type === "checkbox" ? !field.checked : !clean(field.value);
      field.setAttribute("aria-invalid", invalid ? "true" : "false");
      if (invalid && !firstInvalid) firstInvalid = field;
    });

    const email = clean(get("email").value);
    const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (email && !validEmail) {
      get("email").setAttribute("aria-invalid", "true");
      firstInvalid ||= get("email");
      problems.push("Enter a valid work email.");
    }

    if (clean(get("website").value)) {
      problems.push("Submission could not be prepared.");
    }

    if (firstInvalid) {
      problems.unshift("Complete all required fields and consent to email contact.");
      firstInvalid.focus();
    }

    errorBox.textContent = [...new Set(problems)].join(" ");
    return problems.length === 0;
  }

  function responseText() {
    return [
      "RESONANCE Opportunity Truth Founding List",
      "",
      `Work email: ${clean(get("email").value)}`,
      `Company/project: ${clean(get("company").value)}`,
      `Role: ${clean(get("role").value)}`,
      `Preferred integration: ${clean(get("integration").value)}`,
      `Hardest pre-trade failure: ${clean(get("failure").value)}`,
      `Public/sandbox example: ${clean(get("sample").value)}`,
      `Pilot interest: ${clean(get("pilot-interest").value)}`,
      "",
      "Agent/trading workflow:",
      clean(get("workflow").value),
      "",
      "Consent: I consent to being contacted by email about RESONANCE Verify discovery, evidence updates and the paper-only pilot.",
      "",
      "No credentials, private keys, balances, signing permissions or production secrets are included."
    ].join("\n");
  }

  function mailtoUrl() {
    const company = clean(get("company").value) || "Founding List";
    const subject = `Opportunity Truth Founding List — ${company}`;
    return `mailto:safal0645@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(responseText())}`;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    successBox.hidden = true;
    if (!validate()) return;

    successBox.hidden = false;
    window.location.href = mailtoUrl();
  });

  copyButton.addEventListener("click", async () => {
    successBox.hidden = true;
    if (!validate()) return;

    try {
      await navigator.clipboard.writeText(responseText());
      successBox.hidden = false;
      successBox.querySelector("strong").textContent = "Responses copied.";
      successBox.querySelector("span").textContent = "Paste them into an email to safal0645@gmail.com with the subject Opportunity Truth Founding List.";
    } catch (_error) {
      errorBox.textContent = "Clipboard access was blocked. Use the email button instead.";
    }
  });

  form.addEventListener("input", (event) => {
    const field = event.target;
    if (field && field.matches("input, textarea, select")) {
      field.removeAttribute("aria-invalid");
      errorBox.textContent = "";
      successBox.hidden = true;
    }
  });
})();
