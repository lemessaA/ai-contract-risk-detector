#!/usr/bin/env python3
"""
Guardrails Testing Script
Comprehensive testing of safety mechanisms
"""

import asyncio
import json
import time
from typing import Dict, Any, List
from guardrails import guardrails_system, GuardrailAction, RiskLevel
from guardrails_config import guardrail_config, compliance_standards, ethical_guidelines

class GuardrailsTester:
    """Test suite for guardrails system"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_input_validation(self):
        """Test input validation guardrails"""
        print("\n=== Testing Input Validation ===")
        
        # Test 1: Empty input
        result = guardrails_system.validate_input("", "text")
        self.log_test(
            "Empty Input Blocking",
            result.triggered and result.action == GuardrailAction.BLOCK,
            f"Action: {result.action.value}, Message: {result.message}"
        )
        
        # Test 2: Malicious code injection
        malicious_input = "print('hack') + exec('system(\"rm -rf /\")')"
        result = guardrails_system.validate_input(malicious_input, "text")
        self.log_test(
            "Malicious Code Blocking",
            result.triggered and result.action == GuardrailAction.BLOCK,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
        
        # Test 3: SQL injection attempt
        sql_input = "SELECT * FROM users WHERE '1'='1' UNION SELECT password FROM admin"
        result = guardrails_system.validate_input(sql_input, "text")
        self.log_test(
            "SQL Injection Blocking",
            result.triggered and result.action == GuardrailAction.BLOCK,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
        
        # Test 4: Sensitive information detection
        sensitive_input = "Contact me at john.doe@email.com or call 555-123-4567"
        result = guardrails_system.validate_input(sensitive_input, "text")
        self.log_test(
            "Sensitive Info Detection",
            result.triggered and result.action == GuardrailAction.SANITIZE,
            f"Action: {result.action.value}, Sanitized: {result.sanitized_content is not None}"
        )
        
        # Test 5: Valid input
        valid_input = "This is a normal contract question about payment terms."
        result = guardrails_system.validate_input(valid_input, "text")
        self.log_test(
            "Valid Input Allowance",
            not result.triggered or result.action == GuardrailAction.ALLOW,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
    
    def test_file_validation(self):
        """Test file upload validation"""
        print("\n=== Testing File Validation ===")
        
        # Test 1: Suspicious filename
        result = guardrails_system.validate_input(
            "virus.exe",
            "file",
            filename="virus.exe",
            file_size=1024,
            content_type="application/octet-stream"
        )
        self.log_test(
            "Suspicious Filename Blocking",
            result.triggered and result.action == GuardrailAction.BLOCK,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
        
        # Test 2: Oversized file
        large_size = 15 * 1024 * 1024  # 15MB
        result = guardrails_system.validate_input(
            "contract.pdf",
            "file",
            filename="contract.pdf",
            file_size=large_size,
            content_type="application/pdf"
        )
        self.log_test(
            "Oversized File Blocking",
            result.triggered and result.action == GuardrailAction.BLOCK,
            f"Action: {result.action.value}, Message: {result.message}"
        )
        
        # Test 3: Valid file
        result = guardrails_system.validate_input(
            "contract.pdf",
            "file",
            filename="contract.pdf",
            file_size=1024 * 1024,  # 1MB
            content_type="application/pdf"
        )
        self.log_test(
            "Valid File Allowance",
            not result.triggered or result.action == GuardrailAction.ALLOW,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
    
    def test_output_validation(self):
        """Test output validation guardrails"""
        print("\n=== Testing Output Validation ===")
        
        # Test 1: Legal advice claim
        legal_advice_output = "As a lawyer, I can tell you that this contract is definitely binding."
        result = guardrails_system.validate_output(legal_advice_output, "contract_analysis")
        self.log_test(
            "Legal Advice Sanitization",
            result.triggered and result.action == GuardrailAction.SANITIZE,
            f"Action: {result.action.value}, Sanitized: {result.sanitized_content is not None}"
        )
        
        # Test 2: Guaranteed outcomes
        guarantee_output = "This contract will guarantee you win the case and make $1M profit."
        result = guardrails_system.validate_output(guarantee_output, "contract_analysis")
        self.log_test(
            "Guarantee Claims Sanitization",
            result.triggered and result.action == GuardrailAction.SANITIZE,
            f"Action: {result.action.value}"
        )
        
        # Test 3: Missing disclaimers
        no_disclaimer_output = "This contract looks good overall."
        result = guardrails_system.validate_output(no_disclaimer_output, "contract_analysis")
        self.log_test(
            "Disclaimer Addition",
            result.triggered and result.action == GuardrailAction.SANITIZE,
            f"Action: {result.action.value}, Has disclaimers: {'legal advice' in (result.sanitized_content or '')}"
        )
        
        # Test 4: Valid output with disclaimers
        valid_output = "This analysis is for informational purposes only and does not constitute legal advice."
        result = guardrails_system.validate_output(valid_output, "contract_analysis")
        self.log_test(
            "Valid Output Allowance",
            not result.triggered or result.action == GuardrailAction.ALLOW,
            f"Action: {result.action.value}, Risk: {result.risk_level.value}"
        )
    
    def test_behavioral_constraints(self):
        """Test behavioral constraints"""
        print("\n=== Testing Behavioral Constraints ===")
        
        # Test 1: Rate limiting
        user_id = "test_user"
        
        # Clear any existing rate limits
        guardrails_system.behavioral_guardrails.request_history = []
        
        # Make requests up to limit
        for i in range(guardrail_config.MAX_REQUESTS_PER_MINUTE + 1):
            result = guardrails_system.check_behavioral_constraints(user_id)
            if i < guardrail_config.MAX_REQUESTS_PER_MINUTE:
                self.log_test(
                    f"Rate Limit Check {i+1}",
                    not result.triggered or result.action == GuardrailAction.ALLOW,
                    f"Request {i+1}: {result.action.value}"
                )
            else:
                self.log_test(
                    "Rate Limit Enforcement",
                    result.triggered and result.action == GuardrailAction.BLOCK,
                    f"Request {i+1}: {result.action.value}"
                )
                break
        
        # Test 2: Concurrent analysis limits
        analysis_ids = []
        for i in range(guardrail_config.MAX_CONCURRENT_ANALYSES + 1):
            analysis_id = f"test_analysis_{i}"
            result = guardrails_system.check_behavioral_constraints(
                user_id=user_id,
                analysis_id=analysis_id
            )
            
            if i < guardrail_config.MAX_CONCURRENT_ANALYSES:
                self.log_test(
                    f"Concurrent Analysis {i+1}",
                    not result.triggered or result.action == GuardrailAction.ALLOW,
                    f"Analysis {i+1}: {result.action.value}"
                )
                analysis_ids.append(analysis_id)
            else:
                self.log_test(
                    "Concurrent Analysis Limit",
                    result.triggered and result.action == GuardrailAction.BLOCK,
                    f"Analysis {i+1}: {result.action.value}"
                )
                break
        
        # Clean up
        for analysis_id in analysis_ids:
            guardrails_system.behavioral_guardrails.complete_analysis(analysis_id)
    
    def test_configuration(self):
        """Test configuration settings"""
        print("\n=== Testing Configuration ===")
        
        # Test 1: Blocked patterns
        patterns = guardrail_config.get_blocked_patterns()
        self.log_test(
            "Blocked Patterns Available",
            len(patterns) > 0,
            f"Found {len(patterns)} blocked patterns"
        )
        
        # Test 2: Sensitive patterns
        patterns = guardrail_config.get_sensitive_patterns()
        self.log_test(
            "Sensitive Patterns Available",
            len(patterns) > 0,
            f"Found {len(patterns)} sensitive patterns"
        )
        
        # Test 3: Required disclaimers
        disclaimers = guardrail_config.get_required_disclaimers()
        self.log_test(
            "Required Disclaimers Available",
            len(disclaimers) > 0,
            f"Found {len(disclaimers)} required disclaimers"
        )
        
        # Test 4: Security headers
        headers = guardrail_config.get_security_headers()
        self.log_test(
            "Security Headers Available",
            len(headers) > 0,
            f"Found {len(headers)} security headers"
        )
        
        # Test 5: Rate limits
        upload_limit = guardrail_config.get_rate_limit("upload")
        self.log_test(
            "Upload Rate Limit",
            upload_limit == 10,
            f"Upload limit: {upload_limit} requests/minute"
        )
    
    def test_compliance(self):
        """Test compliance standards"""
        print("\n=== Testing Compliance Standards ===")
        
        # Test 1: GDPR compliance
        gdpr_requirements = compliance_standards.check_compliance("gdpr")
        self.log_test(
            "GDPR Requirements",
            len(gdpr_requirements) > 0,
            f"Found {len(gdpr_requirements)} GDPR requirements"
        )
        
        # Test 2: HIPAA compliance
        hipaa_requirements = compliance_standards.check_compliance("hipaa")
        self.log_test(
            "HIPAA Requirements",
            len(hipaa_requirements) > 0,
            f"Found {len(hipaa_requirements)} HIPAA requirements"
        )
        
        # Test 3: SOX compliance
        sox_requirements = compliance_standards.check_compliance("sox")
        self.log_test(
            "SOX Requirements",
            len(sox_requirements) > 0,
            f"Found {len(sox_requirements)} SOX requirements"
        )
    
    def test_ethical_guidelines(self):
        """Test ethical guidelines"""
        print("\n=== Testing Ethical Guidelines ===")
        
        # Test 1: Transparency guidelines
        transparency = ethical_guidelines.get_guideline("transparency")
        self.log_test(
            "Transparency Guidelines",
            len(transparency) > 0,
            f"Found {len(transparency)} transparency guidelines"
        )
        
        # Test 2: Fairness guidelines
        fairness = ethical_guidelines.get_guideline("fairness")
        self.log_test(
            "Fairness Guidelines",
            len(fairness) > 0,
            f"Found {len(fairness)} fairness guidelines"
        )
        
        # Test 3: Response validation
        response = "I am an AI assistant providing informational guidance. This analysis has limitations."
        validation = ethical_guidelines.validate_response(response, "transparency")
        self.log_test(
            "Ethical Response Validation",
            any(validation.values()),
            f"Validation results: {validation}"
        )
    
    def test_end_to_end(self):
        """Test end-to-end guardrails processing"""
        print("\n=== Testing End-to-End Processing ===")
        
        def mock_processing(input_data, **kwargs):
            """Mock processing function"""
            return f"Processed: {input_data[:50]}... This analysis is for informational purposes only and does not constitute legal advice."
        
        # Test 1: Normal processing
        result = guardrails_system.process_with_guardrails(
            "What are the payment terms in this contract?",
            mock_processing,
            input_type="text",
            context="chat_question"
        )
        
        self.log_test(
            "Normal Processing",
            result["success"],
            f"Success: {result['success']}, Guardrails: {result.get('guardrail_triggered', False)}"
        )
        
        # Test 2: Blocked input processing
        result = guardrails_system.process_with_guardrails(
            "exec('rm -rf /')",
            mock_processing,
            input_type="text",
            context="chat_question"
        )
        
        self.log_test(
            "Blocked Input Processing",
            not result["success"],
            f"Success: {result['success']}, Error: {result.get('error', 'None')}"
        )
        
        # Test 3: Sanitized processing
        result = guardrails_system.process_with_guardrails(
            "Contact john.doe@email.com for details",
            mock_processing,
            input_type="text",
            context="chat_question"
        )
        
        self.log_test(
            "Sanitized Processing",
            result["success"],
            f"Success: {result['success']}, Warnings: {len(result.get('warnings', []))}"
        )
    
    def run_all_tests(self):
        """Run all guardrails tests"""
        print("🔒 Guardrails System Test Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_input_validation()
        self.test_file_validation()
        self.test_output_validation()
        self.test_behavioral_constraints()
        self.test_configuration()
        self.test_compliance()
        self.test_ethical_guidelines()
        self.test_end_to_end()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        print(f"Duration: {end_time - start_time:.2f} seconds")
        
        if self.failed_tests == 0:
            print("\n🎉 All tests passed! Guardrails system is working correctly.")
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. Please review the guardrails configuration.")
        
        return self.failed_tests == 0

def main():
    """Main function to run guardrails tests"""
    tester = GuardrailsTester()
    success = tester.run_all_tests()
    
    # Export detailed results
    with open("guardrails_test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": tester.passed_tests + tester.failed_tests,
                "passed": tester.passed_tests,
                "failed": tester.failed_tests,
                "success_rate": (tester.passed_tests / (tester.passed_tests + tester.failed_tests) * 100) if (tester.passed_tests + tester.failed_tests) > 0 else 0
            },
            "results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: guardrails_test_results.json")
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
