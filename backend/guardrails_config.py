"""
Guardrails Configuration for AI Contract Risk Detector
Customizable safety parameters and policies
"""

from typing import Dict, List, Any
from enum import Enum

class GuardrailConfig:
    """Configuration for guardrails system"""
    
    # Input validation settings
    MAX_TEXT_LENGTH = 100000  # 100KB
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx', '.txt', '.doc']
    MAX_REQUESTS_PER_MINUTE = 30
    MAX_CONCURRENT_ANALYSES = 5
    
    # Content filtering settings
    BLOCKED_PATTERNS = [
        # Malicious code injection
        r'(?i)(exec|eval|system|shell|cmd|powershell)\s*\(',
        r'(?i)(<script|javascript:|vbscript:|onload=|onerror=)',
        # SQL injection
        r'(?i)(union|select|insert|update|delete|drop|create)\s+',
        # Hate speech and discrimination
        r'(?i)(hate|kill|murder|terrorist|nazi|white supremacist)',
        # Illegal activities
        r'(?i)(illegal|fraud|money laundering|drug trafficking)',
        # Personal data requests
        r'(?i)(ssn|social security|credit card|bank account|password)',
        # Prompt injection attempts
        r'(?i)(ignore previous|forget everything|system prompt|jailbreak)',
    ]
    
    SENSITIVE_INFO_PATTERNS = [
        # Email addresses
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        # Phone numbers
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        # SSN patterns
        r'\b\d{3}-\d{2}-\d{4}\b',
        # Credit card patterns
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        # URLs with sensitive info
        r'https?://[^\s]*\b(password|token|key|secret)\b[^\s]*',
        # API keys
        r'\b[A-Za-z0-9]{20,}\b',
        # Private keys
        r'-----BEGIN [A-Z]+ KEY-----',
    ]
    
    # Output validation settings
    MAX_RESPONSE_LENGTH = 10000
    REQUIRED_DISCLAIMERS = [
        "This analysis is for informational purposes only and does not constitute legal advice.",
        "Please consult with a qualified legal professional before signing any contract.",
        "AI analysis may not capture all nuances of your specific situation."
    ]
    
    FORBIDDEN_OUTPUT_PATTERNS = [
        # Legal advice disclaimers that should be explicit
        r'(?i)(i am (a lawyer|an attorney)|legal advice)',
        # Financial guarantees
        r'(?i)(guaranteed|certain|definitely).{0,50}(win|succeed|profit)',
        # Medical advice
        r'(?i)(diagnose|prescribe|medical advice)',
        # Promises of AI infallibility
        r'(?i)(perfect|infallible|always correct)',
        # Harmful instructions
        r'(?i)(how to (hack|exploit|bypass|circumvent))',
    ]
    
    # Rate limiting settings
    RATE_LIMITS = {
        "default": 100,  # requests per minute
        "upload": 10,    # uploads per minute
        "analysis": 5,   # analyses per minute
        "chat": 30,      # chat requests per minute
    }
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "critical": 0.9
    }
    
    # Behavioral constraints
    SUSPICIOUS_PATTERNS = {
        "headers": [
            "X-Forwarded-Host",
            "X-Originating-IP", 
            "X-Remote-IP",
            "X-Remote-Addr"
        ],
        "user_agents": [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "scanner", "crawler", "bot", "spider"
        ],
        "paths": [
            "/admin", "/config", "/env", "/secret", "/backup",
            "/test", "/debug", "/.env", "/.git"
        ]
    }
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        ),
        "Permissions-Policy": (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        ),
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    # Monitoring settings
    MONITORING = {
        "log_slow_requests": 10.0,  # seconds
        "log_errors": True,
        "log_uploads": True,
        "audit_all_requests": True,
        "block_duration": 3600,  # seconds (1 hour)
    }
    
    @classmethod
    def get_blocked_patterns(cls) -> List[str]:
        """Get list of blocked content patterns"""
        return cls.BLOCKED_PATTERNS
    
    @classmethod
    def get_sensitive_patterns(cls) -> List[str]:
        """Get list of sensitive information patterns"""
        return cls.SENSITIVE_INFO_PATTERNS
    
    @classmethod
    def get_forbidden_output_patterns(cls) -> List[str]:
        """Get list of forbidden output patterns"""
        return cls.FORBIDDEN_OUTPUT_PATTERNS
    
    @classmethod
    def get_required_disclaimers(cls) -> List[str]:
        """Get list of required disclaimers"""
        return cls.REQUIRED_DISCLAIMERS
    
    @classmethod
    def get_rate_limit(cls, endpoint_type: str = "default") -> int:
        """Get rate limit for specific endpoint type"""
        return cls.RATE_LIMITS.get(endpoint_type, cls.RATE_LIMITS["default"])
    
    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        """Get security headers configuration"""
        return cls.SECURITY_HEADERS

class ComplianceStandards:
    """Compliance standards for different regions"""
    
    GDPR_REQUIREMENTS = {
        "data_processing": True,
        "user_consent": True,
        "right_to_erasure": True,
        "data_portability": True,
        "privacy_policy": True
    }
    
    HIPAA_REQUIREMENTS = {
        "phi_protection": True,
        "audit_logs": True,
        "access_controls": True,
        "encryption": True,
        "business_associate_agreement": True
    }
    
    SOX_REQUIREMENTS = {
        "financial_data_protection": True,
        "audit_trails": True,
        "retention_policy": True,
        "access_controls": True,
        "change_management": True
    }
    
    @classmethod
    def check_compliance(cls, standard: str) -> Dict[str, bool]:
        """Check compliance against specific standard"""
        standards_map = {
            "gdpr": cls.GDPR_REQUIREMENTS,
            "hipaa": cls.HIPAA_REQUIREMENTS,
            "sox": cls.SOX_REQUIREMENTS
        }
        return standards_map.get(standard.lower(), {})

class EthicalGuidelines:
    """Ethical guidelines for AI behavior"""
    
    GUIDELINES = {
        "transparency": {
            "disclose_ai_nature": True,
            "explain_limitations": True,
            "provide_confidence_scores": True
        },
        "fairness": {
            "avoid_bias": True,
            "equal_treatment": True,
            "no_discrimination": True
        },
        "accountability": {
            "log_decisions": True,
            "human_oversight": True,
            "appeal_mechanism": True
        },
        "privacy": {
            "minimize_data_collection": True,
            "protect_sensitive_info": True,
            "secure_storage": True
        },
        "safety": {
            "harm_prevention": True,
            "risk_assessment": True,
            "emergency_stop": True
        }
    }
    
    @classmethod
    def get_guideline(cls, category: str) -> Dict[str, bool]:
        """Get specific ethical guideline category"""
        return cls.GUIDELINES.get(category.lower(), {})
    
    @classmethod
    def validate_response(cls, response: str, category: str) -> Dict[str, Any]:
        """Validate response against ethical guidelines"""
        guidelines = cls.get_guideline(category)
        results = {}
        
        for principle, required in guidelines.items():
            if required:
                # Simple validation - in production, this would be more sophisticated
                if principle == "disclose_ai_nature":
                    results[principle] = "ai" in response.lower() or "assistant" in response.lower()
                elif principle == "explain_limitations":
                    results[principle] = "limitation" in response.lower() or "not perfect" in response.lower()
                else:
                    results[principle] = True  # Default to compliant
        
        return results

# Global configuration instance
guardrail_config = GuardrailConfig()
compliance_standards = ComplianceStandards()
ethical_guidelines = EthicalGuidelines()
