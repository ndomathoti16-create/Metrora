"""Streamlined file and cloud billing-source management for the workspace."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime
from html import escape
from typing import TYPE_CHECKING

from ..connections import (
    AwsS3BillingConnector,
    AwsS3ExportConfig,
    AzureBlobBillingConnector,
    AzureBlobExportConfig,
    CloudConnectionError,
    ConnectionProfile,
    ConnectionStore,
    GcpBigQueryBillingConnector,
    GcpBigQueryExportConfig,
)
from .ingestion_view import activate_loaded_table, render_ingestion_view

if TYPE_CHECKING:
    from ..config import Settings


def _store(settings: Settings) -> ConnectionStore:
    return ConnectionStore(settings.data_dir / "state" / "connections.json")


def _connector_for(profile: ConnectionProfile):
    if profile.provider == "aws":
        return AwsS3BillingConnector(AwsS3ExportConfig(**profile.settings))
    if profile.provider == "azure":
        return AzureBlobBillingConnector(AzureBlobExportConfig(**profile.settings))
    if profile.provider == "gcp":
        return GcpBigQueryBillingConnector(GcpBigQueryExportConfig(**profile.settings))
    raise CloudConnectionError(f"Unsupported provider {profile.provider!r}.")


def _install_sync_result(result, profile: ConnectionProfile) -> int:
    import streamlit as st

    profile_data, _, _ = activate_loaded_table(result.loaded_table)
    st.session_state["active_connection_id"] = profile.connection_id
    st.session_state["connection_sync"] = {
        "provider": result.provider,
        "source_uri": result.source_uri,
        "object_count": result.object_count,
        "total_bytes": result.total_bytes,
        "latest_modified": result.latest_modified.isoformat(),
        "synced_at": result.synced_at.isoformat(),
    }
    return int(profile_data.row_count)


def _sync_profile(settings: Settings, profile: ConnectionProfile) -> bool:
    import streamlit as st

    store = _store(settings)
    try:
        result = _connector_for(profile).sync_latest()
        row_count = _install_sync_result(result, profile)
    except (CloudConnectionError, ValueError) as exc:
        message = str(exc)
        store.record_sync(profile, status="Needs attention", message=message)
        st.error(message)
        return False

    store.record_sync(
        profile,
        status="Ready",
        message=(f"Imported {row_count:,} rows from {result.object_count:,} export file(s)."),
        source_uri=result.source_uri,
        row_count=row_count,
    )
    st.success(
        f"{result.provider} sync complete: {row_count:,} rows imported and sent through "
        "Metrora's mapping, reconciliation, and quality checks."
    )
    return True


def _find_or_create_profile(
    settings: Settings,
    *,
    name: str,
    provider: str,
    provider_settings: dict,
    refresh_on_open: bool,
) -> ConnectionProfile:
    store = _store(settings)
    candidate = ConnectionProfile.create(
        name=name,
        provider=provider,
        settings=provider_settings,
        refresh_on_open=refresh_on_open,
    )
    for existing in store.list():
        if (
            existing.provider == provider
            and existing.name.casefold() == name.strip().casefold()
            and existing.settings == candidate.settings
        ):
            profile = replace(existing, refresh_on_open=refresh_on_open)
            store.save(profile)
            return profile
    store.save(candidate)
    return candidate


def _finish_connection(settings: Settings, profile: ConnectionProfile) -> None:
    import streamlit as st

    from .navigation import set_workspace_route

    with st.spinner("Finding and validating the latest complete billing export..."):
        ready = _sync_profile(settings, profile)
    if ready:
        set_workspace_route("Home", scenario_id=None)
        st.rerun()


def _render_saved_connections(settings: Settings) -> None:
    import streamlit as st

    store = _store(settings)
    try:
        profiles = store.list()
    except ValueError as exc:
        st.error(str(exc))
        return
    if not profiles:
        return

    st.markdown("### Saved connections")
    st.caption(
        "Saved profiles contain locations and identity selectors only. Metrora never stores "
        "cloud passwords, access keys, tokens, or service-account files."
    )
    for profile in sorted(profiles, key=lambda item: item.updated_at, reverse=True):
        provider_label = {
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "Google Cloud",
        }.get(profile.provider, profile.provider.title())
        last_sync = "Not synced yet"
        if profile.last_sync_at:
            try:
                last_sync = (
                    datetime.fromisoformat(profile.last_sync_at)
                    .astimezone()
                    .strftime("%b %d, %Y at %I:%M %p")
                )
            except ValueError:
                last_sync = profile.last_sync_at
        refresh_label = "On open" if profile.refresh_on_open else "Manual"
        st.markdown(
            '<div class="metrora-connection-row">'
            f"<div><span>{escape(provider_label)}</span><strong>{escape(profile.name)}</strong>"
            f"<small>{escape(profile.last_status)} · {escape(last_sync)}</small></div>"
            f"<div><span>Refresh</span><strong>{refresh_label}</strong>"
            f"<small>{escape(profile.last_message or 'Ready to connect')}</small></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        sync_column, remove_column, spacer = st.columns([1, 1, 3.5])
        with sync_column:
            if st.button(
                "Sync latest",
                key=f"sync_connection_{profile.connection_id}",
                width="stretch",
            ):
                _finish_connection(settings, profile)
        with remove_column:
            if st.button(
                "Remove",
                key=f"remove_connection_{profile.connection_id}",
                width="stretch",
            ):
                store.delete(profile.connection_id)
                if st.session_state.get("active_connection_id") == profile.connection_id:
                    st.session_state.pop("active_connection_id", None)
                    st.session_state.pop("connection_sync", None)
                st.rerun()
        del spacer


def _render_aws_form(settings: Settings) -> None:
    import streamlit as st

    st.markdown("### Connect AWS billing exports")
    st.write(
        "Point Metrora at an AWS Data Exports or CUR 2.0 S3 prefix. It uses your current "
        "AWS SSO profile, environment credentials, or IAM role and never stores a secret."
    )
    with st.form("aws_connection_form"):
        left, right = st.columns(2, gap="large")
        with left:
            name = st.text_input("Connection name", value="AWS billing export")
            bucket = st.text_input("S3 bucket", placeholder="company-finops-exports")
            prefix = st.text_input("Export prefix", placeholder="billing/cur2")
        with right:
            region = st.text_input("AWS region", value=settings.aws_region)
            profile_name = st.text_input(
                "AWS profile (optional)",
                placeholder="finops-readonly",
                help="Leave blank for the default credential chain or an attached IAM role.",
            )
            refresh = st.checkbox("Refresh this source when Metrora opens", value=True)
        with st.expander("Advanced security check", expanded=False):
            owner = st.text_input(
                "Expected bucket owner (optional)",
                placeholder="123456789012",
                help="Prevents syncing from a same-named bucket in another AWS account.",
            )
        submitted = st.form_submit_button("Connect and import latest", type="primary")
    if submitted:
        try:
            config = AwsS3ExportConfig(
                bucket=bucket,
                prefix=prefix,
                region=region,
                profile_name=profile_name or None,
                expected_bucket_owner=owner or None,
            )
            profile = _find_or_create_profile(
                settings,
                name=name or "AWS billing export",
                provider="aws",
                provider_settings=asdict(config),
                refresh_on_open=refresh,
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _finish_connection(settings, profile)


def _render_azure_form(settings: Settings) -> None:
    import streamlit as st

    st.markdown("### Connect Azure cost exports")
    st.write(
        "Use a recurring Azure Cost Management export in Blob Storage. Metrora signs in "
        "through Azure CLI, Visual Studio, or managed identity using Entra ID and RBAC."
    )
    with st.form("azure_connection_form"):
        left, right = st.columns(2, gap="large")
        with left:
            name = st.text_input("Connection name", value="Azure cost export")
            account_url = st.text_input(
                "Storage account URL",
                placeholder="https://companycosts.blob.core.windows.net",
            )
        with right:
            container = st.text_input("Blob container", placeholder="cost-management")
            prefix = st.text_input("Export prefix", placeholder="daily/amortized")
            refresh = st.checkbox("Refresh this source when Metrora opens", value=True)
        submitted = st.form_submit_button("Connect and import latest", type="primary")
    if submitted:
        try:
            config = AzureBlobExportConfig(
                account_url=account_url,
                container=container,
                prefix=prefix,
            )
            profile = _find_or_create_profile(
                settings,
                name=name or "Azure cost export",
                provider="azure",
                provider_settings=asdict(config),
                refresh_on_open=refresh,
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _finish_connection(settings, profile)


def _render_gcp_form(settings: Settings) -> None:
    import streamlit as st

    st.markdown("### Connect Google Cloud Billing")
    st.write(
        "Query a standard Cloud Billing export in BigQuery through Application Default "
        "Credentials. Credits are included in the imported effective-cost value."
    )
    with st.form("gcp_connection_form"):
        left, right = st.columns(2, gap="large")
        with left:
            name = st.text_input("Connection name", value="Google Cloud billing")
            project_id = st.text_input("Google Cloud project ID")
            dataset = st.text_input("BigQuery dataset", placeholder="billing_export")
        with right:
            table = st.text_input("Billing table", value="gcp_billing_export_v1_*")
            lookback = st.number_input(
                "History to import (days)", min_value=7, max_value=366, value=120
            )
            refresh = st.checkbox("Refresh this source when Metrora opens", value=True)
        submitted = st.form_submit_button("Connect and import latest", type="primary")
    if submitted:
        try:
            config = GcpBigQueryExportConfig(
                project_id=project_id,
                dataset=dataset,
                table=table,
                lookback_days=int(lookback),
            )
            profile = _find_or_create_profile(
                settings,
                name=name or "Google Cloud billing",
                provider="gcp",
                provider_settings=asdict(config),
                refresh_on_open=refresh,
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        _finish_connection(settings, profile)


def maybe_refresh_active_connection(settings: Settings) -> None:
    """Refresh one saved cloud source once when a blank desktop workspace opens."""
    import streamlit as st

    if st.session_state.get("connection_refresh_checked"):
        return
    st.session_state["connection_refresh_checked"] = True
    if st.session_state.get("loaded_table") is not None:
        return
    try:
        profile = _store(settings).active()
    except ValueError as exc:
        st.session_state["connection_refresh_error"] = str(exc)
        return
    if profile is None or not profile.refresh_on_open:
        return
    try:
        result = _connector_for(profile).sync_latest()
        row_count = _install_sync_result(result, profile)
        _store(settings).record_sync(
            profile,
            status="Ready",
            message=f"Automatically imported {row_count:,} rows when Metrora opened.",
            source_uri=result.source_uri,
            row_count=row_count,
        )
    except (CloudConnectionError, ValueError) as exc:
        _store(settings).record_sync(
            profile,
            status="Needs attention",
            message=str(exc),
        )
        st.session_state["connection_refresh_error"] = str(exc)


def render_connections_view(settings: Settings) -> None:
    """Render one source hub for files and secure provider-managed exports."""
    import streamlit as st

    st.markdown(
        """
        <div class="metrora-automation-note">
            <strong>Exports stay provider-managed.</strong>
            <span>AWS, Azure, or Google Cloud schedules the billing export. Metrora reads the
            latest complete result with a least-privilege identity and refreshes the trusted
            model without storing cloud credentials.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if error := st.session_state.pop("connection_refresh_error", None):
        st.warning(f"Automatic refresh needs attention: {error}")

    _render_saved_connections(settings)
    st.markdown("### Add a data source")
    file_tab, aws_tab, azure_tab, gcp_tab = st.tabs(
        ["Upload a file", "AWS", "Azure", "Google Cloud"]
    )
    with file_tab:
        render_ingestion_view(settings, include_mapping=False)
    with aws_tab:
        _render_aws_form(settings)
    with azure_tab:
        _render_azure_form(settings)
    with gcp_tab:
        _render_gcp_form(settings)

    st.markdown("### Identity and permissions")
    st.markdown(
        """
        - **AWS:** `s3:ListBucket` on the export prefix and `s3:GetObject` on its files.
        - **Azure:** Storage Blob Data Reader on the export container.
        - **Google Cloud:** BigQuery Job User on the project and Data Viewer on the dataset.

        Metrora is read-only. It does not create, resize, stop, or delete cloud resources.
        """
    )
