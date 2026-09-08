# Privacy

Metrora has two deliberately different surfaces.

## Hosted product demo

The public Streamlit deployment is a read-only demonstration. It uses bundled synthetic data and
does not expose file upload, cloud connection, mapping changes, provider recommendation import, or
external AI controls. The hosting provider may still process normal service information such as IP
addresses, browser details, and operational logs under its own terms and privacy practices.

Do not submit confidential information through bug reports, screenshots, URLs, or other public
project channels.

## Desktop application

The desktop app performs its analytical work locally. By default, application data is stored under
`%LOCALAPPDATA%\Metrora` on Windows, including the DuckDB database, non-secret connection profiles,
decision records, and local diagnostic logs. Closing Metrora and deleting that folder removes its
local application state.

Metrora does not include application telemetry and does not store cloud passwords, access keys,
API tokens, or service-account files in its own connection profiles. Cloud SDKs and command-line
tools may maintain authentication caches outside Metrora; those remain governed by the provider's
tools and your operating-system account.

Data leaves the local application only after an explicit user action:

- a cloud refresh reads billing exports through the configured provider SDK;
- an optional S3 export writes the selected canonical dataset to the configured bucket; or
- an optional desktop AI request sends the calculated fact pack to the configured HTTPS provider.

The application files are not independently encrypted. Use an access-controlled Windows account,
device encryption such as BitLocker, least-privilege cloud roles, and approved organizational data
handling practices for sensitive billing data.

## Logs and support material

Local crash and service logs may contain exception messages and local file paths. Review and redact
them before sharing. Screenshots and exported reports may contain billing values or identifiers;
treat them with the same controls as the source data.

This notice describes the current reference implementation and should be reviewed again before any
multi-user or commercial deployment.
