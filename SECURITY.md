# Security policy

## Supported version

Security fixes are applied to the latest published release and the current `main` branch. Older
portable builds should be replaced rather than treated as supported long-term versions.

## Report a vulnerability

Use GitHub's private vulnerability reporting option in this repository's **Security** tab. Do not
include exploit details, credentials, customer data, or billing exports in a public issue. If the
private form is unavailable, open a minimal issue requesting a private contact channel without
describing the vulnerability.

Include the affected version, operating system, reproduction conditions, impact, and the smallest
safe proof of concept. Reports made in good faith will be reviewed as time permits.

## Security boundaries

- The hosted demo is synthetic and read-only.
- The desktop app binds its local Streamlit service to `127.0.0.1` and opens it in a private desktop
  webview session.
- Saved cloud profiles contain locations and identity selectors, not passwords, tokens, access
  keys, or service-account contents.
- Cloud import sizes are bounded, including compressed payload expansion.
- Azure identity credentials are only used with canonical HTTPS Azure Blob Storage account URLs.
- Optional remote AI endpoints require HTTPS, except for explicit loopback development services.
- Financial values are calculated before any optional narrative request.

Users remain responsible for least-privilege IAM, endpoint security, credential rotation, device
encryption, backup controls, and validating exported reports before business use.

## Safe configuration

Never commit `.env`, Streamlit secrets, cloud credentials, private keys, real billing exports, or
customer identifiers. Verify release checksums, keep the desktop app current, and use synthetic or
anonymized data when reproducing a problem.
