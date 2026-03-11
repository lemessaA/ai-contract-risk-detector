"""
Guardrails System for AI Contract Risk Detector
Comprehensive safety mechanisms for LLM-based contract analysis
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level classification for content"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GuardrailAction(Enum):
    """Actions to take when guardrails are triggered"""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    SANITIZE = "sanitize"

@dataclass
class GuardrailResult:
    """Result of guardrail check"""
    triggered: bool
    action: GuardrailAction
    risk_level: RiskLevel
    message: str
    sanitized_content: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class InputGuardrails:
    """Input validation and filtering mechanisms"""
    
    def __init__(self):
        self.max_text_length = 100000  # 100KB max
        self.max_file_size_mb = 10
        self.allowed_languages = ['en', 'es', 'fr', 'de', 'it', 'pt']
        self.blocked_patterns = self._initialize_blocked_patterns()
        self.sensitive_info_patterns = self._initialize_sensitive_patterns()
    
    def _initialize_blocked_patterns(self) -> List[re.Pattern]:
        """Initialize patterns for blocked content"""
        patterns = [
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
        ]
        return [re.compile(pattern) for pattern in patterns]
    
    def _initialize_sensitive_patterns(self) -> List[re.Pattern]:
        """Initialize patterns for sensitive information"""
        patterns = [
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
        ]
        return [re.compile(pattern) for pattern in patterns]
    
    def validate_text_input(self, text: str, context: str = "general") -> GuardrailResult:
        """
        Validate text input against multiple safety criteria
        
        Args:
            text: Input text to validate
            context: Context of the input (question, contract, etc.)
            
        Returns:
            GuardrailResult with validation outcome
        """
        if not text or not text.strip():
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                message="Empty input is not allowed"
            )
        
        # Length check
        if len(text) > self.max_text_length:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                message=f"Text exceeds maximum length of {self.max_text_length} characters"
            )
        
        # Blocked content check
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                return GuardrailResult(
                    triggered=True,
                    action=GuardrailAction.BLOCK,
                    risk_level=RiskLevel.HIGH,
                    message="Input contains prohibited content",
                    details={"matched_pattern": pattern.pattern}
                )
        
        # Sensitive information check
        sensitive_matches = []
        for pattern in self.sensitive_info_patterns:
            matches = pattern.findall(text)
            if matches:
                sensitive_matches.extend(matches)
        
        if sensitive_matches:
            sanitized_text = self._sanitize_sensitive_info(text)
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.SANITIZE,
                risk_level=RiskLevel.MEDIUM,
                message="Input contains sensitive information that has been sanitized",
                sanitized_content=sanitized_text,
                details={"sensitive_count": len(sensitive_matches)}
            )
        
        return GuardrailResult(
            triggered=False,
            action=GuardrailAction.ALLOW,
            risk_level=RiskLevel.LOW,
            message="Input passed all validation checks"
        )
    
    def _sanitize_sensitive_info(self, text: str) -> str:
        """Sanitize sensitive information from text"""
        sanitized = text
        
        for pattern in self.sensitive_info_patterns:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized
    
    def validate_file_upload(self, filename: str, file_size: int, content_type: str) -> GuardrailResult:
        """
        Validate file upload parameters
        
        Args:
            filename: Name of uploaded file
            file_size: Size in bytes
            content_type: MIME type of file
            
        Returns:
            GuardrailResult with validation outcome
        """
        # File size check
        size_mb = file_size / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                message=f"File size ({size_mb:.1f}MB) exceeds maximum allowed size ({self.max_file_size_mb}MB)"
            )
        
        # File extension check
        allowed_extensions = ['.pdf', '.docx', '.txt', '.doc']
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if f'.{file_ext}' not in allowed_extensions:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.HIGH,
                message=f"File type .{file_ext} is not allowed"
            )
        
        # Filename check for suspicious patterns
        suspicious_patterns = [
            r'\.exe$', r'\.bat$', r'\.cmd$', r'\.scr$', r'\.vbs$',
            r'(?i)(virus|malware|trojan|backdoor|exploit)'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename):
                return GuardrailResult(
                    triggered=True,
                    action=GuardrailAction.BLOCK,
                    risk_level=RiskLevel.CRITICAL,
                    message="Filename contains suspicious patterns"
                )
        
        return GuardrailResult(
            triggered=False,
            action=GuardrailAction.ALLOW,
            risk_level=RiskLevel.LOW,
            message="File upload validation passed"
        )

class OutputGuardrails:
    """Output sanitization and behavioral constraints"""
    
    def __init__(self):
        self.max_response_length = 10000
        self.forbidden_content = self._initialize_forbidden_content()
        self.required_disclaimers = self._initialize_disclaimers()
    
    def _initialize_forbidden_content(self) -> List[re.Pattern]:
        """Initialize patterns for forbidden output content"""
        patterns = [
            # Legal advice disclaimers that should be explicit
            r'(?i)(i am (a lawyer|an attorney)|legal advice)',
            # Financial guarantees
            r'(?i)(guaranteed|certain|definitely).{0,50}(win|succeed|profit)',
            # Medical advice (not relevant but good practice)
            r'(?i)(diagnose|prescribe|medical advice)',
            # Promises of AI infallibility
            r'(?i)(perfect|infallible|always correct)',
        ]
        return [re.compile(pattern) for pattern in patterns]
    
    def _initialize_disclaimers(self) -> List[str]:
        """Initialize required disclaimers for contract analysis"""
        return [
            "This analysis is for informational purposes only and does not constitute legal advice.",
            "Please consult with a qualified legal professional before signing any contract.",
            "AI analysis may not capture all nuances of your specific situation."
        ]
    
    def validate_output(self, output: str, context: str = "contract_analysis") -> GuardrailResult:
        """
        Validate and sanitize AI output
        
        Args:
            output: AI-generated output to validate
            context: Context of the output (analysis, chat, etc.)
            
        Returns:
            GuardrailResult with validation outcome
        """
        if not output:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.HIGH,
                message="Empty output generated"
            )
        
        # Length check
        if len(output) > self.max_response_length:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.SANITIZE,
                risk_level=RiskLevel.MEDIUM,
                message="Output too long, truncating",
                sanitized_content=output[:self.max_response_length]
            )
        
        # Forbidden content check
        for pattern in self.forbidden_content:
            if pattern.search(output):
                sanitized = self._sanitize_forbidden_content(output)
                return GuardrailResult(
                    triggered=True,
                    action=GuardrailAction.SANITIZE,
                    risk_level=RiskLevel.HIGH,
                    message="Output contains forbidden content, sanitized",
                    sanitized_content=sanitized
                )
        
        # Ensure required disclaimers for contract analysis
        if context == "contract_analysis":
            missing_disclaimers = []
            for disclaimer in self.required_disclaimers:
                if disclaimer.lower() not in output.lower():
                    missing_disclaimers.append(disclaimer)
            
            if missing_disclaimers:
                enhanced_output = output + "\n\n" + "\n".join(missing_disclaimers)
                return GuardrailResult(
                    triggered=True,
                    action=GuardrailAction.SANITIZE,
                    risk_level=RiskLevel.LOW,
                    message="Added required disclaimers",
                    sanitized_content=enhanced_output
                )
        
        return GuardrailResult(
            triggered=False,
            action=GuardrailAction.ALLOW,
            risk_level=RiskLevel.LOW,
            message="Output validation passed"
        )
    
    def _sanitize_forbidden_content(self, text: str) -> str:
        """Sanitize forbidden content from output"""
        sanitized = text
        
        # Replace problematic phrases
        replacements = {
            r'(?i)i am (a lawyer|an attorney)': 'I am an AI assistant',
            r'(?i)legal advice': 'informational guidance',
            r'(?i)(guaranteed|certain|definitely)': 'potentially',
            r'(?i)(perfect|infallible|always correct)': 'helpful'
        }
        
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized

class BehavioralGuardrails:
    """Behavioral constraints and ethical guidelines"""
    
    def __init__(self):
        self.max_requests_per_minute = 30
        self.max_concurrent_analyses = 5
        self.request_history = []
        self.active_analyses = set()
    
    def check_rate_limit(self, user_id: str = "anonymous") -> GuardrailResult:
        """Check if user exceeds rate limits"""
        import time
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        self.request_history = [
            req_time for req_time in self.request_history 
            if current_time - req_time < 60
        ]
        
        if len(self.request_history) >= self.max_requests_per_minute:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                message="Rate limit exceeded. Please try again later."
            )
        
        self.request_history.append(current_time)
        return GuardrailResult(
            triggered=False,
            action=GuardrailAction.ALLOW,
            risk_level=RiskLevel.LOW,
            message="Rate limit check passed"
        )
    
    def check_concurrent_analyses(self, analysis_id: str) -> GuardrailResult:
        """Check concurrent analysis limits"""
        if len(self.active_analyses) >= self.max_concurrent_analyses:
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                message="Too many concurrent analyses. Please wait for current analyses to complete."
            )
        
        self.active_analyses.add(analysis_id)
        return GuardrailResult(
            triggered=False,
            action=GuardrailAction.ALLOW,
            risk_level=RiskLevel.LOW,
            message="Concurrent analysis check passed"
        )
    
    def complete_analysis(self, analysis_id: str):
        """Mark analysis as complete"""
        self.active_analyses.discard(analysis_id)

class GuardrailsSystem:
    """Main guardrails system coordinating all safety mechanisms"""
    
    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.behavioral_guardrails = BehavioralGuardrails()
        self.logger = logging.getLogger(__name__)
    
    def validate_input(self, data: Any, input_type: str = "text", **kwargs) -> GuardrailResult:
        """
        Validate input using appropriate guardrails
        
        Args:
            data: Input data to validate
            input_type: Type of input (text, file, question)
            **kwargs: Additional parameters for validation
            
        Returns:
            GuardrailResult with validation outcome
        """
        try:
            if input_type == "text":
                return self.input_guardrails.validate_text_input(data, kwargs.get("context", "general"))
            elif input_type == "file":
                return self.input_guardrails.validate_file_upload(
                    kwargs.get("filename", ""),
                    kwargs.get("file_size", 0),
                    kwargs.get("content_type", "")
                )
            else:
                return GuardrailResult(
                    triggered=True,
                    action=GuardrailAction.BLOCK,
                    risk_level=RiskLevel.HIGH,
                    message=f"Unknown input type: {input_type}"
                )
        except Exception as e:
            self.logger.error(f"Input validation error: {str(e)}")
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.BLOCK,
                risk_level=RiskLevel.HIGH,
                message="Input validation system error"
            )
    
    def validate_output(self, output: str, context: str = "general") -> GuardrailResult:
        """
        Validate output using output guardrails
        
        Args:
            output: AI-generated output to validate
            context: Context of the output
            
        Returns:
            GuardrailResult with validation outcome
        """
        try:
            return self.output_guardrails.validate_output(output, context)
        except Exception as e:
            self.logger.error(f"Output validation error: {str(e)}")
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.SANITIZE,
                risk_level=RiskLevel.HIGH,
                message="Output validation system error",
                sanitized_content="System error occurred during output validation."
            )
    
    def check_behavioral_constraints(self, user_id: str = "anonymous", analysis_id: str = None) -> GuardrailResult:
        """
        Check behavioral constraints
        
        Args:
            user_id: User identifier for rate limiting
            analysis_id: Analysis ID for concurrent analysis tracking
            
        Returns:
            GuardrailResult with validation outcome
        """
        try:
            # Rate limiting
            rate_limit_result = self.behavioral_guardrails.check_rate_limit(user_id)
            if rate_limit_result.triggered:
                return rate_limit_result
            
            # Concurrent analysis check
            if analysis_id:
                concurrent_result = self.behavioral_guardrails.check_concurrent_analyses(analysis_id)
                if concurrent_result.triggered:
                    return concurrent_result
            
            return GuardrailResult(
                triggered=False,
                action=GuardrailAction.ALLOW,
                risk_level=RiskLevel.LOW,
                message="Behavioral constraints check passed"
            )
        except Exception as e:
            self.logger.error(f"Behavioral constraint error: {str(e)}")
            return GuardrailResult(
                triggered=True,
                action=GuardrailAction.WARN,
                risk_level=RiskLevel.MEDIUM,
                message="Behavioral constraint system error"
            )
    
    def process_with_guardrails(self, input_data: Any, processing_func, input_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        Process input through guardrails, processing function, and output guardrails
        
        Args:
            input_data: Input data to process
            processing_func: Function to process the data
            input_type: Type of input
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with processing result and guardrail information
        """
        # Input validation
        input_result = self.validate_input(input_data, input_type, **kwargs)
        
        if input_result.action == GuardrailAction.BLOCK:
            return {
                "success": False,
                "error": input_result.message,
                "guardrail_triggered": True,
                "risk_level": input_result.risk_level.value
            }
        
        # Use sanitized input if needed
        processed_input = input_result.sanitized_content or input_data
        
        # Behavioral constraints
        behavioral_result = self.check_behavioral_constraints(
            kwargs.get("user_id", "anonymous"),
            kwargs.get("analysis_id")
        )
        
        if behavioral_result.action == GuardrailAction.BLOCK:
            return {
                "success": False,
                "error": behavioral_result.message,
                "guardrail_triggered": True,
                "risk_level": behavioral_result.risk_level.value
            }
        
        try:
            # Process the input
            result = processing_func(processed_input, **kwargs)
            
            # Output validation
            if isinstance(result, str):
                output_result = self.validate_output(result, kwargs.get("context", "general"))
                
                if output_result.action == GuardrailAction.BLOCK:
                    return {
                        "success": False,
                        "error": output_result.message,
                        "guardrail_triggered": True,
                        "risk_level": output_result.risk_level.value
                    }
                
                # Return sanitized output if needed
                final_output = output_result.sanitized_content or result
                
                return {
                    "success": True,
                    "result": final_output,
                    "guardrail_triggered": input_result.triggered or output_result.triggered,
                    "warnings": [
                        input_result.message for input_result in [input_result, output_result] 
                        if input_result.triggered and input_result.action == GuardrailAction.WARN
                    ]
                }
            
            return {
                "success": True,
                "result": result,
                "guardrail_triggered": input_result.triggered,
                "warnings": [input_result.message] if input_result.triggered and input_result.action == GuardrailAction.WARN else []
            }
            
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "guardrail_triggered": True,
                "risk_level": "high"
            }
        finally:
            # Clean up analysis tracking
            if kwargs.get("analysis_id"):
                self.behavioral_guardrails.complete_analysis(kwargs["analysis_id"])

# Global guardrails instance
guardrails_system = GuardrailsSystem()
