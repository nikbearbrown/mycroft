"""
config.py
=========
Agentic AML Compliance Workflow — Developer Configuration
US Equities · OFAC/BSA/FinCEN

Single file covering:
  1. LLMConfig     — which LLM provider and model to use
  2. call_llm()    — provider-agnostic LLM call used by every agent
  3. Data source configs — connection settings per source
  4. PipelineConfig     — root config object, passed to build_orchestrator()
  5. GLEIFLEIDatabase   — concrete LEI implementation (GLEIF public API)
  6. build_orchestrator() — updated factory that wires config to dependencies

QUICK START (development — runs immediately, no infrastructure required):
  from config import PipelineConfig, build_orchestrator
  import os
  os.environ["ANTHROPIC_API_KEY"] = "your-key-here"
  orchestrator = build_orchestrator(PipelineConfig.development())

PRODUCTION:
  Set environment variables (see section headers below), then:
  orchestrator = build_orchestrator(PipelineConfig.from_env())

Dependencies:
  pip install anthropic>=0.25 httpx>=0.27 pydantic>=2.0
  pip install openai>=1.0  # only if using openai_compatible provider
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# 1. LLM CONFIGURATION
# ─────────────────────────────────────────────────────────────

@dataclass
class LLMConfig:
    """
    Which LLM provider and model to use across the entire pipeline.

    Supported providers:
      "anthropic"         — Anthropic Claude (default, recommended for compliance)
      "openai"            — OpenAI GPT-4o and variants
      "gemini"            — Google Gemini
      "openai_compatible" — Any OpenAI-compatible endpoint:
                            Azure OpenAI, Groq, Together AI, local Ollama, etc.

    Environment variables (used by from_env() and development()):
      ANTHROPIC_API_KEY   — required for anthropic provider
      OPENAI_API_KEY      — required for openai provider
      GEMINI_API_KEY      — required for gemini provider
      LLM_PROVIDER        — "anthropic" | "openai" | "gemini" | "openai_compatible"
      LLM_MODEL           — model name override
      LLM_BASE_URL        — base URL for openai_compatible provider
      LLM_API_KEY         — API key for openai_compatible provider

    Model guidance by provider:
      anthropic:          claude-sonnet-4-6 (default) · claude-opus-4-6 (higher quality)
      openai:             gpt-4o (default) · gpt-4o-mini (faster/cheaper) · o3-mini
      gemini:             gemini-2.0-flash (default) · gemini-1.5-pro · gemini-2.5-pro
      openai_compatible:  use the model name your endpoint expects
    """
    # [DEV] CHOOSE YOUR LLM PROVIDER ─────────────────────────────────────────
    # "anthropic"         — Anthropic Claude (ANTHROPIC_API_KEY)
    # "openai"            — OpenAI GPT (OPENAI_API_KEY)
    # "gemini"            — Google Gemini (GEMINI_API_KEY)
    # "openai_compatible" — Azure, Groq, Ollama, etc. (requires base_url)
    # ─────────────────────────────────────────────────────────────────────────
    provider: Literal["anthropic", "openai", "gemini", "openai_compatible"] = "anthropic"

    # [DEV] CHOOSE YOUR MODEL ─────────────────────────────────────────────────
    # Anthropic: "claude-sonnet-4-6" (default) | "claude-opus-4-6" (higher quality)
    # OpenAI:    "gpt-4o" (default)            | "gpt-4o-mini"     | "o3-mini"
    # Gemini:    "gemini-2.0-flash" (default)  | "gemini-1.5-pro"  | "gemini-2.5-pro"
    # ─────────────────────────────────────────────────────────────────────────
    model: str = "claude-sonnet-4-6"

    api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )

    # [DEV] REQUIRED for openai_compatible provider ───────────────────────────
    # Set to the base URL of your endpoint. Examples:
    #   Azure OpenAI:  "https://<resource>.openai.azure.com/"
    #   Groq:          "https://api.groq.com/openai/v1"
    #   Ollama local:  "http://localhost:11434/v1"
    # Leave as None for anthropic, openai, and gemini providers.
    # ─────────────────────────────────────────────────────────────────────────
    base_url: str | None = None
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Loads LLM config from environment variables.
        Auto-detects provider from available API keys if LLM_PROVIDER is not set.
        """
        provider = os.environ.get("LLM_PROVIDER", "").strip()

        # Auto-detect provider from whichever API key is present
        if not provider:
            if os.environ.get("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.environ.get("OPENAI_API_KEY"):
                provider = "openai"
            elif os.environ.get("GEMINI_API_KEY"):
                provider = "gemini"
            else:
                provider = "anthropic"  # Default — will fail with clear error at build_client()

        # Resolve API key and default model per provider
        if provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY", "")
            default_model = "gpt-4o"
        elif provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY", "")
            default_model = "gemini-2.0-flash"
        elif provider == "openai_compatible":
            api_key = os.environ.get("LLM_API_KEY", "")
            default_model = "gpt-4o"
        else:  # anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            default_model = "claude-sonnet-4-6"

        return cls(
            provider=provider,  # type: ignore[arg-type]
            model=os.environ.get("LLM_MODEL", default_model),
            api_key=api_key,
            base_url=os.environ.get("LLM_BASE_URL") or None,
        )

    def build_client(self) -> Any:
        """
        Returns a configured LLM client.
        The client is passed to call_llm() — it is never used directly by agents.
        """
        if self.provider == "anthropic":
            import anthropic
            if not self.api_key:
                raise ValueError(
                    "LLMConfig.api_key is empty. "
                    "Set the ANTHROPIC_API_KEY environment variable."
                )
            return anthropic.Anthropic(api_key=self.api_key)

        elif self.provider == "openai":
            from openai import OpenAI
            if not self.api_key:
                raise ValueError(
                    "LLMConfig.api_key is empty for openai provider. "
                    "Set the OPENAI_API_KEY environment variable."
                )
            return OpenAI(api_key=self.api_key)

        elif self.provider == "gemini":
            if not self.api_key:
                raise ValueError(
                    "LLMConfig.api_key is empty for gemini provider. "
                    "Set the GEMINI_API_KEY environment variable."
                )
            # Return a lightweight holder — the SDK is imported lazily in call_llm()
            return _GeminiClientHolder(api_key=self.api_key, model=self.model)

        elif self.provider == "openai_compatible":
            from openai import OpenAI
            if not self.base_url:
                raise ValueError(
                    "LLMConfig.base_url is required for openai_compatible provider. "
                    "Example for Azure: 'https://<resource>.openai.azure.com/' "
                    "Example for Ollama: 'http://localhost:11434/v1'"
                )
            return OpenAI(api_key=self.api_key or "none", base_url=self.base_url)

        # [DEV] ADD NEW PROVIDER HERE ─────────────────────────────────────────
        # To support a provider not listed above, add an elif branch here.
        # Install the provider's SDK, instantiate its client, and return it.
        # Then add a matching branch in call_llm() below so agents can call it.
        # Example:
        #   elif self.provider == "cohere":
        #       import cohere
        #       return cohere.Client(api_key=self.api_key)
        # ─────────────────────────────────────────────────────────────────────
        else:
            raise ValueError(
                f"Unsupported LLM provider: '{self.provider}'. "
                "Supported values: 'anthropic', 'openai', 'gemini', 'openai_compatible'."
            )


class _GeminiClientHolder:
    """
    Lightweight holder for Gemini config.
    The actual google-generativeai SDK is imported lazily inside call_llm()
    so that the SDK is not required if the gemini provider is not used.
    """
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model


# ─────────────────────────────────────────────────────────────
# 2. PROVIDER-AGNOSTIC LLM CALL
# ─────────────────────────────────────────────────────────────

def call_llm(
    client: Any,
    config: LLMConfig,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 500,
) -> str:
    """
    Provider-agnostic LLM call used by every agent in the pipeline.
    Called by Agent.run() — agents never touch the client directly.

    Returns the model's response as a plain string.
    Raises the provider's native exception on failure (the orchestrator
    catches these as part of mid-pipeline error handling).

    Adding a new provider:
      Add an elif branch here. The rest of the pipeline needs no changes.
    """
    if config.provider == "anthropic":
        response = client.messages.create(
            model=config.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text.strip()

    elif config.provider == "openai":
        response = client.chat.completions.create(
            model=config.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    elif config.provider == "gemini":
        # client is _GeminiClientHolder — configure SDK and instantiate model here
        import google.generativeai as genai
        import google.generativeai.types as genai_types

        genai.configure(api_key=client.api_key)
        model = genai.GenerativeModel(
            model_name=client.model,
            system_instruction=system_prompt,
            generation_config=genai_types.GenerationConfig(
                max_output_tokens=max_tokens,
            ),
        )
        response = model.generate_content(user_prompt)
        return response.text.strip()

    elif config.provider == "openai_compatible":
        response = client.chat.completions.create(
            model=config.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    # [DEV] ADD NEW PROVIDER CALL HERE ────────────────────────────────────────
    # Add an elif branch matching the provider name you added in build_client().
    # Map the provider's response format to a plain string and return it.
    # Example:
    #   elif config.provider == "cohere":
    #       response = client.chat(model=config.model, message=user_prompt,
    #                              preamble=system_prompt, max_tokens=max_tokens)
    #       return response.text.strip()
    # ─────────────────────────────────────────────────────────────────────────
    else:
        raise ValueError(f"Unsupported provider in call_llm: {config.provider}")


# ─────────────────────────────────────────────────────────────
# 3. DATA SOURCE CONFIGURATIONS
# ─────────────────────────────────────────────────────────────

@dataclass
class LEISourceConfig:
    """
    GLEIF LEI database connection settings.

    use_stub=False  → calls the real GLEIF public REST API (no key needed)
    use_stub=True   → returns fixture data, no network calls

    The GLEIF API is free for low-volume use. No API key required for
    development. Set gleif_api_key for production rate limit guarantees.

    Environment variables:
      GLEIF_API_KEY   — optional, increases rate limits
    """
    gleif_api_key: str | None = field(
        default_factory=lambda: os.environ.get("GLEIF_API_KEY")
    )
    timeout_seconds: float = 5.0
    use_stub: bool = False  # GLEIF is public — stub off by default


@dataclass
class KYCSourceConfig:
    """
    Internal KYC records system connection settings.

    use_stub=True by default — you must implement the adapter to your
    institution's KYC system before setting this to False.
    See data_sources.py: KYCStore interface.

    Environment variables:
      KYC_SYSTEM_URL   — base URL of your KYC system REST API
      KYC_API_KEY      — service account API key
    """
    base_url: str = field(
        default_factory=lambda: os.environ.get("KYC_SYSTEM_URL", "")
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("KYC_API_KEY", "")
    )
    timeout_seconds: float = 5.0
    # [DEV] FLIP TO FALSE WHEN YOUR KYC ADAPTER IS READY ─────────────────────
    # Keeping this True uses StubKYCStore (returns clean fixture data).
    # When your adapter is implemented (see ADAPTER PATTERN below),
    # set use_stub=False so the pipeline uses real KYC records.
    # ─────────────────────────────────────────────────────────────────────────
    use_stub: bool = True


@dataclass
class SanctionsSourceConfig:
    """
    OFAC SDN / Consolidated Sanctions database connection settings.

    use_stub=False and use_local_list=True is recommended for production:
      - Download the OFAC SDN XML list on startup
      - Cache locally for sub-millisecond query time
      - Refresh on a scheduled interval (see staleness_threshold_hours)

    use_stub=True: returns clean result for all LEIs — for development only.

    Environment variables:
      OFAC_API_KEY             — optional, for OFAC REST API (alternative to local list)
      OFAC_LOCAL_LIST_PATH     — path to cached SDN XML file (default: data/ofac_sdn.xml)
      OFAC_STALENESS_HOURS     — max age of cached list before raising DataSourceStaleError
    """
    ofac_api_key: str = field(
        default_factory=lambda: os.environ.get("OFAC_API_KEY", "")
    )
    use_local_list: bool = True
    local_list_path: str = field(
        default_factory=lambda: os.environ.get("OFAC_LOCAL_LIST_PATH", "data/ofac_sdn.xml")
    )
    # [DEV] SET STALENESS THRESHOLD ───────────────────────────────────────────
    # OFAC updates the SDN list multiple times per week.
    # 24 hours is a reasonable default for compliance purposes.
    # Your compliance policy and legal counsel determine the actual value.
    # ─────────────────────────────────────────────────────────────────────────
    staleness_threshold_hours: int = int(
        os.environ.get("OFAC_STALENESS_HOURS", "24")
    )
    timeout_seconds: float = 5.0
    # [DEV] FLIP TO True ONLY FOR DEVELOPMENT ─────────────────────────────────
    # Sanctions check is CRITICAL — do not run in production with use_stub=True.
    # The stub returns "no match" for every LEI, bypassing the entire check.
    # ─────────────────────────────────────────────────────────────────────────
    use_stub: bool = False


@dataclass
class TXHistorySourceConfig:
    """
    Internal transaction history system connection settings.

    use_stub=True by default — you must implement the adapter to your
    institution's transaction history system before setting this to False.
    See data_sources.py: TransactionHistoryStore interface.

    Environment variables:
      TX_HISTORY_URL       — base URL of your transaction history REST API
      TX_HISTORY_API_KEY   — service account API key
      TX_LOOKBACK_MONTHS   — lookback window (default: 24)
    """
    base_url: str = field(
        default_factory=lambda: os.environ.get("TX_HISTORY_URL", "")
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("TX_HISTORY_API_KEY", "")
    )
    # [DEV] SET LOOKBACK PERIOD ───────────────────────────────────────────────
    # 24 months is the BSA/AML standard for typology analysis.
    # Your compliance policy governs the actual lookback window.
    # ─────────────────────────────────────────────────────────────────────────
    default_lookback_months: int = int(
        os.environ.get("TX_LOOKBACK_MONTHS", "24")
    )
    timeout_seconds: float = 10.0
    # [DEV] FLIP TO FALSE WHEN YOUR TX HISTORY ADAPTER IS READY ──────────────
    use_stub: bool = True


# ─────────────────────────────────────────────────────────────
# 4. ROOT PIPELINE CONFIGURATION
# ─────────────────────────────────────────────────────────────

@dataclass
class PipelineConfig:
    """
    Root configuration object. Build once at startup, pass to build_orchestrator().

    ── QUICK START ──────────────────────────────────────────────────────
    Development (stubs for KYC + TX, real GLEIF API, stub sanctions):

        import os
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
        config = PipelineConfig.development()
        orchestrator = build_orchestrator(config)

    Production:

        # Set all env vars (see each config class above), then:
        config = PipelineConfig.from_env()
        orchestrator = build_orchestrator(config)
    ─────────────────────────────────────────────────────────────────────
    """
    llm: LLMConfig = field(default_factory=LLMConfig)
    lei: LEISourceConfig = field(default_factory=LEISourceConfig)
    kyc: KYCSourceConfig = field(default_factory=KYCSourceConfig)
    sanctions: SanctionsSourceConfig = field(default_factory=SanctionsSourceConfig)
    tx_history: TXHistorySourceConfig = field(default_factory=TXHistorySourceConfig)

    @classmethod
    def development(cls) -> "PipelineConfig":
        """
        Development preset.

        What runs for real:
          ✓ LLM calls (requires ANTHROPIC_API_KEY)
          ✓ GLEIF LEI API (free public API, no key needed)

        What uses stubs (no external calls):
          ✗ KYC records   → returns a clean CURRENT/LOW-RISK fixture
          ✗ OFAC SDN      → returns a clean no-match fixture
          ✗ TX history    → returns a clean 47-trade fixture

        Override specific LEIs in stubs for test scenarios:
            config = PipelineConfig.development()
            orchestrator = build_orchestrator(config)
            # ...then swap orchestrator.prefetcher.sanctions_db._fixtures[lei] = ...
        """
        return cls(
            llm=LLMConfig.from_env(),
            lei=LEISourceConfig(use_stub=False),       # Real GLEIF — no key needed
            kyc=KYCSourceConfig(use_stub=True),
            sanctions=SanctionsSourceConfig(use_stub=True),
            tx_history=TXHistorySourceConfig(use_stub=True),
        )

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        """Load all settings from environment variables."""
        return cls(
            llm=LLMConfig.from_env(),
            lei=LEISourceConfig(),
            kyc=KYCSourceConfig(),
            sanctions=SanctionsSourceConfig(),
            tx_history=TXHistorySourceConfig(),
        )


# ─────────────────────────────────────────────────────────────
# 5. GLEIF CONCRETE IMPLEMENTATION
# ─────────────────────────────────────────────────────────────
# This is the only concrete data source implementation provided.
# It targets the GLEIF public REST API — free, no auth required for
# low volume, production-grade. Use it as a template for your other
# adapters (KYC, OFAC, TX history).

from data_sources import (
    DataSourceAuthError,
    DataSourceError,
    DataSourceTimeout,
    DataSourceUnavailable,
    LEIDatabase,
    LEIRecord,
    StubLEIDatabase,
    StubKYCStore,
    StubSanctionsDatabase,
    StubTransactionHistoryStore,
)


class GLEIFLEIDatabase(LEIDatabase):
    """
    Concrete LEI database implementation using the GLEIF public REST API.

    GLEIF endpoint: GET https://api.gleif.org/api/v1/lei-records/{lei}
    Response: JSON:API format. Key paths documented inline below.

    Rate limits:
      Unauthenticated: ~60 requests/minute
      With API key:    Higher — contact GLEIF for current limits

    httpx is used for its clean timeout handling. If you prefer requests:
        import requests
        resp = requests.get(url, headers=headers, timeout=self.timeout)
    """

    _BASE_URL = "https://api.gleif.org/api/v1"

    def __init__(self, cfg: LEISourceConfig):
        self._cfg = cfg

    def query(self, lei: str) -> LEIRecord:
        import httpx

        headers = {"Accept": "application/vnd.api+json"}
        if self._cfg.gleif_api_key:
            headers["X-Api-Key"] = self._cfg.gleif_api_key

        url = f"{self._BASE_URL}/lei-records/{lei}"
        logger.debug(f"GLEIFLEIDatabase: querying {url}")

        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=self._cfg.timeout_seconds,
                follow_redirects=True,
            )
        except httpx.TimeoutException:
            raise DataSourceTimeout(
                "LEI-DB",
                f"GLEIF API did not respond within {self._cfg.timeout_seconds}s. "
                f"LEI queried: {lei}",
            )
        except httpx.ConnectError as e:
            raise DataSourceUnavailable("LEI-DB", f"GLEIF API unreachable: {e}")

        if response.status_code == 401:
            raise DataSourceAuthError(
                "LEI-DB", "GLEIF API returned 401 — check your GLEIF_API_KEY."
            )

        if response.status_code == 404:
            # LEI not in GLEIF — valid response, not an error
            return LEIRecord(
                lei=lei,
                legal_name="",
                jurisdiction="",
                entity_status="INACTIVE",
                registration_status="ISSUED",
                last_updated=datetime.now(timezone.utc),
                found=False,
            )

        if response.status_code != 200:
            raise DataSourceError(
                "LEI-DB",
                f"GLEIF API returned HTTP {response.status_code} for LEI {lei}.",
            )

        try:
            body = response.json()
            attrs = body["data"]["attributes"]
            entity = attrs["entity"]
            registration = attrs["registration"]

            # Parent entity: present only if a direct parent relationship exists
            parent_lei: str | None = None
            relationships = body["data"].get("relationships", {})
            direct_parent = relationships.get("directParent", {}).get("data")
            if direct_parent:
                parent_lei = direct_parent.get("id")
                # Fetching the parent name would require a second API call.
                # For MVP, log the parent LEI and leave the name to the
                # investigation agent to note.

            return LEIRecord(
                lei=lei,
                legal_name=entity["legalName"]["name"],
                jurisdiction=entity.get("jurisdiction", ""),
                entity_status=entity.get("status", "ACTIVE"),
                registration_status=registration.get("status", "ISSUED"),
                parent_lei=parent_lei,
                parent_legal_name=None,  # Requires second GLEIF call — omit for MVP
                last_updated=datetime.fromisoformat(
                    registration.get("lastUpdateDate", datetime.now(timezone.utc).isoformat())
                ).replace(tzinfo=timezone.utc),
                found=True,
            )

        except (KeyError, ValueError) as e:
            raise DataSourceError(
                "LEI-DB",
                f"GLEIF API response could not be parsed: {e}. "
                f"Response excerpt: {str(response.text)[:200]}",
            )


# ─────────────────────────────────────────────────────────────
# ADAPTER PATTERN FOR YOUR OTHER THREE SOURCES
# ─────────────────────────────────────────────────────────────
# KYC, OFAC, and TX history are institution-specific.
# Use this pattern to build your adapters. One class per source,
# one __init__ that accepts the relevant *Config object, one method
# that maps your system's response to the Pydantic schema.
#
# [DEV] IMPLEMENT THESE THREE ADAPTERS ────────────────────────
# Each adapter replaces a stub in build_orchestrator().
# Steps:
#   1. Copy the skeleton below.
#   2. Rename the class (e.g. YourKYCAdapter).
#   3. Replace the httpx.get() call with your system's API call.
#   4. Map your response fields to the Pydantic model.
#   5. Set use_stub=False in the relevant *SourceConfig.
# ─────────────────────────────────────────────────────────────
#
# Example skeleton (copy, rename, fill in):
#
# from data_sources import KYCStore, KYCRecord
# import httpx
#
# class YourKYCAdapter(KYCStore):
#     def __init__(self, cfg: KYCSourceConfig):
#         self._cfg = cfg
#
#     def query(self, lei: str) -> KYCRecord:
#         try:
#             resp = httpx.get(
#                 f"{self._cfg.base_url}/kyc/{lei}",
#                 headers={"Authorization": f"Bearer {self._cfg.api_key}"},
#                 timeout=self._cfg.timeout_seconds,
#             )
#         except httpx.TimeoutException:
#             raise DataSourceTimeout("KYC", f"KYC system timed out for LEI {lei}")
#         except httpx.ConnectError as e:
#             raise DataSourceUnavailable("KYC", str(e))
#
#         data = resp.json()
#         return KYCRecord(
#             lei=lei,
#             entity_name=data["entity_name"],
#             kyc_status=data["status"],          # map your system's values to the enum
#             risk_tier=data["risk_tier"],         # map to: LOW / MEDIUM / HIGH / PROHIBITED
#             last_review_date=date.fromisoformat(data["last_review"]),
#             # ... map remaining fields from KYCRecord in data_sources.py
#         )


# ─────────────────────────────────────────────────────────────
# 6. UPDATED build_orchestrator() — REPLACES THE VERSION IN orchestrator.py
# ─────────────────────────────────────────────────────────────

def build_orchestrator(config: PipelineConfig, deps: dict | None = None):  # type: ignore[return]
    """
    Constructs the AMLOrchestrator with all dependencies wired from config.

    This replaces the build_orchestrator() in orchestrator.py.
    Import from config.py instead:

        from config import PipelineConfig, build_orchestrator

    deps (optional dict): override specific dependency implementations.
    Used by main.py to inject dev/test implementations without changing config.
    Keys: "review_queue", "settlement_api", "audit_log", "escalation_queue"

    Example:
        orchestrator = build_orchestrator(config, deps={
            "review_queue": DevHumanReviewQueue(),
            "audit_log": DevAuditLog(),
        })
    """
    deps = deps or {}
    # Import here to avoid circular import at module load time
    from orchestrator import (
        AMLOrchestrator,
        Agent,
        AuditLog,
        EscalationQueue,
        HumanReviewQueue,
        SettlementAPI,
    )
    from investigation_prefetch import (
        InvestigationPrefetcher,
        INVESTIGATION_AGENT_SYSTEM_PROMPT,
    )
    import orchestrator as _orch_module

    # Build LLM client and inject into the orchestrator module
    llm_client = config.llm.build_client()
    _orch_module.llm = llm_client
    _orch_module.llm_config = config.llm

    # Build data source implementations based on config
    lei_db = (
        StubLEIDatabase()
        if config.lei.use_stub
        else GLEIFLEIDatabase(config.lei)
    )
    kyc_store = StubKYCStore() if config.kyc.use_stub else _require_impl("KYCStore", config.kyc)
    sanctions_db = StubSanctionsDatabase() if config.sanctions.use_stub else _require_impl("SanctionsDatabase", config.sanctions)
    tx_store = StubTransactionHistoryStore() if config.tx_history.use_stub else _require_impl("TransactionHistoryStore", config.tx_history)

    prefetcher = InvestigationPrefetcher(
        lei_db=lei_db,
        kyc_store=kyc_store,
        sanctions_db=sanctions_db,
        tx_store=tx_store,
    )

    CITATION_INSTRUCTION = (
        "When citing a source, use the format [SOURCE: SOURCE_NAME] "
        "immediately after the claim. Use only recognized source names: "
        "LEI-DB, KYC-RECORDS, OFAC-SDN, OFAC-CONSOL, FINCEN-314A, "
        "TX-HISTORY-24M, AML-TAXONOMY, POLICY-LIB, TRADE-DATA."
    )

    agents = [
        Agent(
            name="triage_agent",
            system_prompt=(
                "You are a trade reconciliation and triage agent for a US institutional "
                "equity trading desk operating under BSA/AML compliance requirements. "
                "Confirm the trade fields. Characterize the AML flag type and confidence level. "
                "Assign a risk level (LOW / MED / HIGH). "
                "State precisely what the investigation agent must check. "
                "Write in plain paragraphs. Exactly 3 paragraphs. "
                "No markdown, no bullet points, no bold text."
            ),
            max_tokens=450,
            permissions=["read:trade_data", "read:aml_taxonomy"],
            llm_config=config.llm,
            llm_client=llm_client,
        ),
        Agent(
            name="investigation_agent",
            system_prompt=INVESTIGATION_AGENT_SYSTEM_PROMPT,
            max_tokens=550,
            permissions=["read:accumulated_context"],
            llm_config=config.llm,
            llm_client=llm_client,
        ),
        Agent(
            name="reasoning_agent",
            system_prompt=(
                "You are a compliance audit agent preparing a regulatory reasoning chain "
                "under BSA/AML requirements for FinCEN audit purposes. "
                "Generate a numbered reasoning chain for this investigation. "
                "Each step must name the specific evidence examined and the finding it produced. "
                "Minimum 3 steps. Maximum 7 steps. "
                "Plain text. No markdown. "
                + CITATION_INSTRUCTION
            ),
            max_tokens=450,
            permissions=["read:accumulated_context", "read:policy_lib"],
            llm_config=config.llm,
            llm_client=llm_client,
        ),
        Agent(
            name="report_agent",
            system_prompt=(
                "You are a compliance reporting agent. "
                "Produce a formal exception report for compliance officer review. "
                "Use EXACTLY these four section labels on their own lines, in this order:\n"
                "FLAG SUMMARY\n"
                "INVESTIGATION FINDINGS\n"
                "REGULATORY ASSESSMENT\n"
                "RECOMMENDED ACTION\n\n"
                "FLAG SUMMARY: 2 sentences. "
                "INVESTIGATION FINDINGS: 3 sentences. "
                "REGULATORY ASSESSMENT: 2 sentences. "
                "RECOMMENDED ACTION: 1 sentence beginning exactly with 'Recommend:'\n\n"
                "No markdown. No bullet points. Plain text only."
            ),
            max_tokens=500,
            permissions=["read:accumulated_context", "read:report_template"],
            llm_config=config.llm,
            llm_client=llm_client,
        ),
    ]

    return AMLOrchestrator(
        agents=agents,
        prefetcher=prefetcher,
        review_queue=deps.get("review_queue") or HumanReviewQueue(),       # [DEV] Replace with concrete implementation
        settlement_api=deps.get("settlement_api") or SettlementAPI(),       # [DEV] Replace with concrete implementation
        audit_log=deps.get("audit_log") or AuditLog(),                     # [DEV] Replace with concrete implementation
        escalation_queue=deps.get("escalation_queue") or EscalationQueue(), # [DEV] Replace with concrete implementation
    )


def _require_impl(name: str, cfg: Any) -> Any:
    """
    Raises a clear error when a non-stub implementation is expected but not yet provided.
    Guides the developer to the right place to add their adapter.
    """
    raise NotImplementedError(
        f"No concrete implementation found for '{name}'. "
        f"Config has use_stub=False but no adapter class has been registered. "
        f"Build your adapter following the pattern in config.py "
        f"(see 'ADAPTER PATTERN FOR YOUR OTHER THREE SOURCES'), "
        f"then replace this call with your implementation. "
        f"Config: {cfg}"
    )
