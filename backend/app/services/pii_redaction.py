"""
PII Redaction Service

Automatically detects and redacts personally identifiable information (PII)
from trace data before storage. Uses Microsoft Presidio with spaCy NER
for enhanced entity recognition.

Supports detection of:
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers (SSN)
- IP addresses
- Person names (via spaCy NER)
- Locations/Addresses (via spaCy NER)
- Organizations (via spaCy NER)
- API keys and tokens
- Dates of birth
- Medical record numbers (HIPAA)
- Custom patterns per organization
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
import re
import json
import logging
import hashlib

try:
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RedactionRule:
    """Custom redaction rule for an organization."""
    entity_type: str
    pattern: str
    replacement: str = "<REDACTED>"
    score: float = 0.85
    enabled: bool = True
    description: str = ""


@dataclass
class RedactionConfig:
    """Configuration for PII redaction per organization."""
    org_id: str
    enabled: bool = True

    # Entity types to detect
    detect_email: bool = True
    detect_phone: bool = True
    detect_credit_card: bool = True
    detect_ssn: bool = True
    detect_ip_address: bool = True
    detect_person: bool = True
    detect_location: bool = True
    detect_organization: bool = True
    detect_url: bool = True
    detect_api_keys: bool = True
    detect_jwt: bool = True

    # HIPAA compliance
    hipaa_mode: bool = False
    detect_medical_record: bool = False
    detect_health_plan: bool = False
    detect_dob: bool = False

    # GDPR compliance
    gdpr_mode: bool = False
    anonymize_names: bool = False
    pseudonymize: bool = False  # Use consistent replacements

    # Custom rules
    custom_rules: List[RedactionRule] = field(default_factory=list)

    # Audit settings
    audit_enabled: bool = True
    log_redacted_count: bool = True
    log_entity_types: bool = True


@dataclass
class RedactionAuditEntry:
    """Audit log entry for a redaction operation."""
    timestamp: datetime
    org_id: str
    trace_id: Optional[str]
    entities_found: int
    entity_types: Dict[str, int]
    fields_redacted: List[str]
    config_hash: str  # Hash of config used


class PIIRedactorEnhanced:
    """
    Enhanced PII detection and redaction engine with spaCy NER,
    configurable rules, and audit logging.

    Usage:
        >>> config = RedactionConfig(org_id="org_123", hipaa_mode=True)
        >>> redactor = PIIRedactorEnhanced(config)
        >>> data = {"email": "user@example.com", "message": "Call John at 555-1234"}
        >>> redacted, audit = redactor.redact_dict(data, trace_id="trace_456")
        >>> print(redacted)
        {"email": "<EMAIL>", "message": "Call <PERSON> at <PHONE_NUMBER>"}
    """

    def __init__(self, config: Optional[RedactionConfig] = None, language: str = "en"):
        """
        Initialize enhanced PII redactor.

        Args:
            config: Redaction configuration (uses defaults if not provided)
            language: Language code for NLP model (default: en)
        """
        self.config = config or RedactionConfig(org_id="default")
        self.language = language
        self.audit_log: List[RedactionAuditEntry] = []
        self._pseudonym_cache: Dict[str, str] = {}

        # Initialize Presidio with spaCy
        if PRESIDIO_AVAILABLE:
            self._init_presidio()
        else:
            logger.warning("Presidio not available, using regex-only fallback")
            self.analyzer = None
            self.anonymizer = None

        # Build custom patterns
        self._build_custom_patterns()

    def _init_presidio(self):
        """Initialize Presidio analyzer with spaCy NER engine."""
        try:
            # Try to use spaCy model
            if SPACY_AVAILABLE:
                try:
                    nlp_config = {
                        "nlp_engine_name": "spacy",
                        "models": [{"lang_code": self.language, "model_name": "en_core_web_lg"}]
                    }
                    provider = NlpEngineProvider(nlp_configuration=nlp_config)
                    nlp_engine = provider.create_engine()
                    self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
                    logger.info("Initialized Presidio with spaCy en_core_web_lg")
                except Exception as e:
                    # Fall back to smaller model
                    try:
                        nlp_config = {
                            "nlp_engine_name": "spacy",
                            "models": [{"lang_code": self.language, "model_name": "en_core_web_sm"}]
                        }
                        provider = NlpEngineProvider(nlp_configuration=nlp_config)
                        nlp_engine = provider.create_engine()
                        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
                        logger.info("Initialized Presidio with spaCy en_core_web_sm")
                    except Exception:
                        self.analyzer = AnalyzerEngine()
                        logger.info("Initialized Presidio with default engine")
            else:
                self.analyzer = AnalyzerEngine()
                logger.info("Initialized Presidio without spaCy")

            self.anonymizer = AnonymizerEngine()

            # Add custom recognizers for HIPAA
            if self.config.hipaa_mode:
                self._add_hipaa_recognizers()

        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            self.analyzer = None
            self.anonymizer = None

    def _add_hipaa_recognizers(self):
        """Add HIPAA-specific pattern recognizers."""
        if not self.analyzer:
            return

        # Medical Record Number pattern
        mrn_pattern = PatternRecognizer(
            supported_entity="MEDICAL_RECORD_NUMBER",
            patterns=[
                Pattern("MRN", r"\b(MRN|MR#?|Medical Record)\s*:?\s*([A-Z0-9]{6,12})\b", 0.7),
                Pattern("MRN_NUM", r"\b[A-Z]{2,3}[0-9]{6,9}\b", 0.5),
            ]
        )
        self.analyzer.registry.add_recognizer(mrn_pattern)

        # Health Plan ID
        health_plan_pattern = PatternRecognizer(
            supported_entity="HEALTH_PLAN_ID",
            patterns=[
                Pattern("HPID", r"\b(Health Plan|Insurance)\s*ID\s*:?\s*([A-Z0-9]{9,15})\b", 0.7),
            ]
        )
        self.analyzer.registry.add_recognizer(health_plan_pattern)

        # Date of Birth variations
        dob_pattern = PatternRecognizer(
            supported_entity="DATE_OF_BIRTH",
            patterns=[
                Pattern("DOB", r"\b(DOB|Date of Birth|Birth ?Date)\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b", 0.9),
                Pattern("DOB_TEXT", r"\b(born|birthday)\s+(?:on\s+)?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b", 0.7),
            ]
        )
        self.analyzer.registry.add_recognizer(dob_pattern)

    def _build_custom_patterns(self):
        """Build custom regex patterns for PII detection."""
        self.custom_patterns = {
            "API_KEY": [
                r"(?i)(api[_-]?key|apikey|api[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
                r"(?i)(ag_live_[a-zA-Z0-9]{32})",  # OverseeX API keys
                r"(?i)(ag_test_[a-zA-Z0-9]{32})",  # OverseeX test API keys
                r"(?i)(sk-[a-zA-Z0-9]{48})",  # OpenAI API keys
                r"(?i)(sk-proj-[a-zA-Z0-9\-_]{48,})",  # OpenAI project keys
                r"(?i)(anthropic-[a-zA-Z0-9]{32,})",  # Anthropic keys
            ],
            "JWT_TOKEN": [
                r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
            ],
            "AWS_KEY": [
                r"(?i)(AKIA[0-9A-Z]{16})",
                r"(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
            ],
            "STRIPE_KEY": [
                r"(?i)(sk_live_[a-zA-Z0-9]{24,})",
                r"(?i)(sk_test_[a-zA-Z0-9]{24,})",
                r"(?i)(pk_live_[a-zA-Z0-9]{24,})",
                r"(?i)(pk_test_[a-zA-Z0-9]{24,})",
            ],
            "GITHUB_TOKEN": [
                r"(?i)(ghp_[a-zA-Z0-9]{36})",
                r"(?i)(gho_[a-zA-Z0-9]{36})",
                r"(?i)(github_pat_[a-zA-Z0-9_]{22,})",
            ],
        }

        # Add custom rules from config
        for rule in self.config.custom_rules:
            if rule.enabled:
                if rule.entity_type not in self.custom_patterns:
                    self.custom_patterns[rule.entity_type] = []
                self.custom_patterns[rule.entity_type].append(rule.pattern)

    def _get_enabled_entities(self) -> List[str]:
        """Get list of enabled entity types based on config."""
        entities = []

        if self.config.detect_email:
            entities.append("EMAIL_ADDRESS")
        if self.config.detect_phone:
            entities.append("PHONE_NUMBER")
        if self.config.detect_credit_card:
            entities.append("CREDIT_CARD")
        if self.config.detect_ssn:
            entities.append("US_SSN")
        if self.config.detect_ip_address:
            entities.append("IP_ADDRESS")
        if self.config.detect_person:
            entities.append("PERSON")
        if self.config.detect_location:
            entities.append("LOCATION")
        if self.config.detect_organization:
            entities.append("ORG")
        if self.config.detect_url:
            entities.append("URL")

        # HIPAA entities
        if self.config.hipaa_mode:
            if self.config.detect_medical_record:
                entities.append("MEDICAL_RECORD_NUMBER")
            if self.config.detect_health_plan:
                entities.append("HEALTH_PLAN_ID")
            if self.config.detect_dob:
                entities.append("DATE_OF_BIRTH")

        return entities

    def _get_operators(self) -> Dict[str, OperatorConfig]:
        """Get anonymization operators based on config."""
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<CREDIT_CARD>"}),
            "US_SSN": OperatorConfig("replace", {"new_value": "<SSN>"}),
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
            "ORG": OperatorConfig("replace", {"new_value": "<ORG>"}),
            "URL": OperatorConfig("replace", {"new_value": "<URL>"}),
            "API_KEY": OperatorConfig("replace", {"new_value": "<API_KEY>"}),
            "JWT_TOKEN": OperatorConfig("replace", {"new_value": "<TOKEN>"}),
            "AWS_KEY": OperatorConfig("replace", {"new_value": "<AWS_KEY>"}),
            "STRIPE_KEY": OperatorConfig("replace", {"new_value": "<STRIPE_KEY>"}),
            "GITHUB_TOKEN": OperatorConfig("replace", {"new_value": "<GITHUB_TOKEN>"}),
            "MEDICAL_RECORD_NUMBER": OperatorConfig("replace", {"new_value": "<MRN>"}),
            "HEALTH_PLAN_ID": OperatorConfig("replace", {"new_value": "<HEALTH_PLAN>"}),
            "DATE_OF_BIRTH": OperatorConfig("replace", {"new_value": "<DOB>"}),
        }

        # Add custom rule operators
        for rule in self.config.custom_rules:
            if rule.enabled:
                operators[rule.entity_type] = OperatorConfig(
                    "replace", {"new_value": rule.replacement}
                )

        return operators

    def _generate_pseudonym(self, entity_type: str, original: str) -> str:
        """Generate consistent pseudonym for an entity."""
        cache_key = f"{entity_type}:{original}"
        if cache_key in self._pseudonym_cache:
            return self._pseudonym_cache[cache_key]

        # Generate hash-based pseudonym
        hash_val = hashlib.sha256(original.encode()).hexdigest()[:8]
        pseudonym = f"<{entity_type}_{hash_val}>"

        self._pseudonym_cache[cache_key] = pseudonym
        return pseudonym

    def redact_text(
        self,
        text: str,
        return_analysis: bool = False,
        trace_id: Optional[str] = None
    ) -> str:
        """
        Redact PII from a text string.

        Args:
            text: Text to redact
            return_analysis: If True, return analysis results instead of redacted text
            trace_id: Optional trace ID for audit logging

        Returns:
            Redacted text or analysis results
        """
        if not self.config.enabled:
            return text

        if not text or not isinstance(text, str):
            return text

        results = []

        # Analyze with Presidio if available
        if self.analyzer and PRESIDIO_AVAILABLE:
            entities = self._get_enabled_entities()
            presidio_results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=entities
            )
            results.extend(presidio_results)

        # Add custom pattern matches
        for entity_type, patterns in self.custom_patterns.items():
            # Check if this entity type is enabled via config
            if entity_type == "API_KEY" and not self.config.detect_api_keys:
                continue
            if entity_type == "JWT_TOKEN" and not self.config.detect_jwt:
                continue

            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    # Avoid overlapping with existing results
                    if not any(
                        r.start <= match.start() < r.end or
                        r.start < match.end() <= r.end
                        for r in results
                    ):
                        results.append(
                            RecognizerResult(
                                entity_type=entity_type,
                                start=match.start(),
                                end=match.end(),
                                score=0.95
                            )
                        )

        if return_analysis:
            return results

        # Anonymize detected entities
        if not results:
            return text

        if self.anonymizer and PRESIDIO_AVAILABLE:
            operators = self._get_operators()

            # Handle pseudonymization
            if self.config.pseudonymize:
                for result in results:
                    original = text[result.start:result.end]
                    pseudonym = self._generate_pseudonym(result.entity_type, original)
                    operators[result.entity_type] = OperatorConfig(
                        "replace", {"new_value": pseudonym}
                    )

            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators
            )
            return anonymized.text
        else:
            # Fallback: simple replacement
            sorted_results = sorted(results, key=lambda x: x.start, reverse=True)
            for result in sorted_results:
                replacement = f"<{result.entity_type}>"
                text = text[:result.start] + replacement + text[result.end:]
            return text

    def redact_dict(
        self,
        data: Dict[str, Any],
        max_depth: int = 10,
        trace_id: Optional[str] = None
    ) -> tuple[Dict[str, Any], Optional[RedactionAuditEntry]]:
        """
        Recursively redact PII from dictionary values.

        Args:
            data: Dictionary to redact
            max_depth: Maximum recursion depth
            trace_id: Optional trace ID for audit logging

        Returns:
            Tuple of (redacted dictionary, audit entry)
        """
        if not self.config.enabled:
            return data, None

        if max_depth <= 0:
            return data, None

        if not isinstance(data, dict):
            return data, None

        entity_counts: Dict[str, int] = {}
        fields_redacted: List[str] = []

        def redact_value(value: Any, path: str, depth: int) -> Any:
            if depth <= 0:
                return value

            if isinstance(value, str):
                # Get analysis first
                results = self.redact_text(value, return_analysis=True)
                if results:
                    fields_redacted.append(path)
                    for r in results:
                        entity_counts[r.entity_type] = entity_counts.get(r.entity_type, 0) + 1
                return self.redact_text(value)
            elif isinstance(value, dict):
                return {
                    k: redact_value(v, f"{path}.{k}", depth - 1)
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                return [
                    redact_value(item, f"{path}[{i}]", depth - 1)
                    for i, item in enumerate(value)
                ]
            else:
                return value

        redacted = {
            key: redact_value(value, key, max_depth)
            for key, value in data.items()
        }

        # Create audit entry
        audit_entry = None
        if self.config.audit_enabled and (entity_counts or fields_redacted):
            config_hash = hashlib.md5(
                json.dumps(self.config.__dict__, default=str).encode()
            ).hexdigest()[:12]

            audit_entry = RedactionAuditEntry(
                timestamp=datetime.utcnow(),
                org_id=self.config.org_id,
                trace_id=trace_id,
                entities_found=sum(entity_counts.values()),
                entity_types=entity_counts if self.config.log_entity_types else {},
                fields_redacted=fields_redacted,
                config_hash=config_hash
            )
            self.audit_log.append(audit_entry)

        return redacted, audit_entry

    def redact_trace_data(
        self,
        trace_data: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> tuple[Dict[str, Any], Optional[RedactionAuditEntry]]:
        """
        Redact PII from trace data (input_data, output_data, metadata).

        Args:
            trace_data: Trace data dictionary
            trace_id: Optional trace ID for audit logging

        Returns:
            Tuple of (redacted trace data, audit entry)
        """
        if not self.config.enabled:
            return trace_data, None

        redacted_trace = trace_data.copy()
        all_entity_counts: Dict[str, int] = {}
        all_fields_redacted: List[str] = []

        # Redact input_data
        if "input_data" in redacted_trace:
            if isinstance(redacted_trace["input_data"], dict):
                redacted, audit = self.redact_dict(redacted_trace["input_data"], trace_id=trace_id)
                redacted_trace["input_data"] = redacted
                if audit:
                    for k, v in audit.entity_types.items():
                        all_entity_counts[k] = all_entity_counts.get(k, 0) + v
                    all_fields_redacted.extend([f"input_data.{f}" for f in audit.fields_redacted])
            elif isinstance(redacted_trace["input_data"], str):
                redacted_trace["input_data"] = self.redact_text(redacted_trace["input_data"])

        # Redact output_data
        if "output_data" in redacted_trace:
            if isinstance(redacted_trace["output_data"], dict):
                redacted, audit = self.redact_dict(redacted_trace["output_data"], trace_id=trace_id)
                redacted_trace["output_data"] = redacted
                if audit:
                    for k, v in audit.entity_types.items():
                        all_entity_counts[k] = all_entity_counts.get(k, 0) + v
                    all_fields_redacted.extend([f"output_data.{f}" for f in audit.fields_redacted])
            elif isinstance(redacted_trace["output_data"], str):
                redacted_trace["output_data"] = self.redact_text(redacted_trace["output_data"])

        # Redact metadata
        if "metadata" in redacted_trace and isinstance(redacted_trace["metadata"], dict):
            redacted, audit = self.redact_dict(redacted_trace["metadata"], trace_id=trace_id)
            redacted_trace["metadata"] = redacted
            if audit:
                for k, v in audit.entity_types.items():
                    all_entity_counts[k] = all_entity_counts.get(k, 0) + v
                all_fields_redacted.extend([f"metadata.{f}" for f in audit.fields_redacted])

        # Redact error_message
        if "error_message" in redacted_trace and isinstance(redacted_trace["error_message"], str):
            redacted_trace["error_message"] = self.redact_text(redacted_trace["error_message"])

        # Create combined audit entry
        audit_entry = None
        if self.config.audit_enabled and (all_entity_counts or all_fields_redacted):
            config_hash = hashlib.md5(
                json.dumps(self.config.__dict__, default=str).encode()
            ).hexdigest()[:12]

            audit_entry = RedactionAuditEntry(
                timestamp=datetime.utcnow(),
                org_id=self.config.org_id,
                trace_id=trace_id,
                entities_found=sum(all_entity_counts.values()),
                entity_types=all_entity_counts if self.config.log_entity_types else {},
                fields_redacted=all_fields_redacted,
                config_hash=config_hash
            )

        return redacted_trace, audit_entry

    def analyze_trace_data(self, trace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze trace data for PII without redacting.

        Returns list of detected PII entities with locations.

        Args:
            trace_data: Trace data to analyze

        Returns:
            List of detected entities with metadata
        """
        findings = []

        def analyze_value(value: Any, path: str):
            if isinstance(value, str):
                results = self.redact_text(value, return_analysis=True)
                if results:
                    for result in results:
                        findings.append({
                            "field": path,
                            "entity_type": result.entity_type,
                            "start": result.start,
                            "end": result.end,
                            "score": result.score,
                            "text": value[result.start:result.end]
                        })
            elif isinstance(value, dict):
                for key, val in value.items():
                    analyze_value(val, f"{path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    analyze_value(item, f"{path}[{i}]")

        analyze_value(trace_data, "trace")
        return findings

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        entries = self.audit_log[-limit:]
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "org_id": e.org_id,
                "trace_id": e.trace_id,
                "entities_found": e.entities_found,
                "entity_types": e.entity_types,
                "fields_redacted": e.fields_redacted,
                "config_hash": e.config_hash,
            }
            for e in entries
        ]

    def clear_audit_log(self):
        """Clear the audit log."""
        self.audit_log.clear()


# Legacy PIIRedactor for backward compatibility
class PIIRedactor(PIIRedactorEnhanced):
    """Legacy PII redactor - wraps enhanced version with default config."""

    def __init__(self, language: str = "en"):
        super().__init__(config=None, language=language)

    def redact_dict(self, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """Backward compatible redact_dict that returns only the data."""
        redacted, _ = super().redact_dict(data, max_depth)
        return redacted

    def redact_trace_data(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatible redact_trace_data that returns only the data."""
        redacted, _ = super().redact_trace_data(trace_data)
        return redacted


# Global instances
_redactor_instance: Optional[PIIRedactor] = None
_org_redactors: Dict[str, PIIRedactorEnhanced] = {}


def get_redactor() -> PIIRedactor:
    """
    Get or create global PIIRedactor instance.

    Returns:
        PIIRedactor singleton instance
    """
    global _redactor_instance
    if _redactor_instance is None:
        _redactor_instance = PIIRedactor()
    return _redactor_instance


def get_org_redactor(org_id: str, config: Optional[RedactionConfig] = None) -> PIIRedactorEnhanced:
    """
    Get or create organization-specific redactor.

    Args:
        org_id: Organization ID
        config: Optional redaction config (uses defaults if not provided)

    Returns:
        PIIRedactorEnhanced instance for the organization
    """
    global _org_redactors

    if org_id not in _org_redactors:
        if config is None:
            config = RedactionConfig(org_id=org_id)
        _org_redactors[org_id] = PIIRedactorEnhanced(config)

    return _org_redactors[org_id]


def update_org_config(org_id: str, config: RedactionConfig):
    """Update configuration for an organization's redactor."""
    global _org_redactors
    _org_redactors[org_id] = PIIRedactorEnhanced(config)


def redact_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to redact PII from dictionary.

    Args:
        data: Data to redact

    Returns:
        Redacted data
    """
    redactor = get_redactor()
    return redactor.redact_dict(data)


def redact_trace(trace_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to redact PII from trace data.

    Args:
        trace_data: Trace data to redact

    Returns:
        Redacted trace data
    """
    redactor = get_redactor()
    return redactor.redact_trace_data(trace_data)
