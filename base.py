"""Provider abstraction for fraud-intelligence integrations.

LINDA talks to fraud-reporting / intelligence services only through
FraudIntelligenceProvider. The demo uses MockFraudIntelligenceProvider.
SafaricomFraudIntelligenceProvider is a disabled placeholder for a
future, approved integration: no public Safaricom fraud-report API is
documented, so it refuses to run rather than pretend.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

# Report status model (shared with the frontend, see
# frontend/src/lib/status.ts).
DRAFT = "draft"
SUBMITTED_LOCALLY = "submitted_locally"
RECEIVED = "received_by_demo_service"
UNDER_REVIEW = "under_review_simulated"
CORROBORATED = "corroborated_simulated"
CONFIRMED = "confirmed_by_authorised_source"  # never emitted in demo
REJECTED = "rejected"
INCONCLUSIVE = "inconclusive"
FINAL_STATUSES = {CORROBORATED, CONFIRMED, REJECTED, INCONCLUSIVE}


class ProviderError(Exception):
    """Base class for provider failures."""


class ProviderUnavailable(ProviderError):
    """The service could not be reached. Safe to retry later."""


class ProviderNotConfigured(ProviderError):
    """Credentials, approval or a documented contract are missing."""


@dataclass
class OutboundReport:
    """Exactly what LINDA would share with an external provider.

    No raw device ID, name, contacts, PIN or OTP is ever included. The
    reporter reference is a salted hash that cannot be reversed.
    """

    report_ref: str
    report_type: str
    indicator_kind: str
    indicator: str
    category: str
    submitted_at: str
    reporter_reference: str
    notes: str | None = None
    message_excerpt: str | None = None
    linked_campaign_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SubmissionReceipt:
    provider: str
    provider_ref: str
    status: str
    simulated: bool
    message: str


@dataclass
class StatusUpdate:
    status: str
    detail: str
    simulated: bool
    at: datetime


@dataclass
class IntelligenceSignal:
    found: bool
    provider: str
    simulated: bool
    source_label: str
    signal_type: str | None = None
    campaign_hint: str | None = None
    confidence: float | None = None
    detail: str = ""
    checked_at: str | None = None


@dataclass
class ProviderDescription:
    id: str
    name: str
    kind: str
    mode: str  # simulated | disabled | live
    configured: bool
    simulated: bool
    summary: str
    documentation: list[dict[str, str]] = field(default_factory=list)
    authentication: str = ""
    approvals: str = ""
    data_sent: list[str] = field(default_factory=list)
    responses: str = ""
    errors_and_retries: str = ""
    rate_limits: str = ""
    when_unavailable: str = ""
    needs_approval_for: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReportContext:
    """Facts the provider may use when computing a status."""

    created_at: datetime
    linked_campaign_id: str | None
    distinct_reporters: int
    current_status: str
    now: datetime | None = None


class FraudIntelligenceProvider(ABC):
    id: str = "base"
    simulated: bool = True

    @abstractmethod
    def describe(self) -> ProviderDescription: ...

    @abstractmethod
    def submit_report(self, report: OutboundReport) -> SubmissionReceipt: ...

    @abstractmethod
    def poll_status(
        self, provider_ref: str, ctx: ReportContext
    ) -> list[StatusUpdate]:
        """Return status changes since ctx.current_status, in order."""

    @abstractmethod
    def lookup_indicator(
        self, kind: str, value: str, meta: dict[str, Any] | None = None
    ) -> IntelligenceSignal: ...

    @abstractmethod
    def health(self) -> dict[str, Any]: ...
