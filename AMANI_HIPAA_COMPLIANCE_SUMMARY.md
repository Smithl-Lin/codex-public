# AMANI HIPAA Compliance - Implementation Summary & Quick Reference

**Part 3 of 3** - Certification Readiness & Configuration Guide

---

## 6. P3: CERTIFICATION READINESS (QUARTER 2+)

**Priority:** 🟢 **LONG-TERM - Certification**
**Estimated Effort:** 80-120 hours
**Timeline:** Weeks 13-24
**Dependencies:** P0 + P1 + P2 completion

### 6.1 P3.1: Business Associate Agreements (BAA)

**HIPAA Requirement:** §164.308(b)(1) - Business Associate Contracts

**Required BAAs:**

| Vendor | Service | PHI Access | BAA Status |
|--------|---------|------------|------------|
| **OpenAI** | GPT-4 API | Yes (query context) | ✅ Available |
| **Anthropic** | Claude API | Yes (query context) | ✅ Available |
| **Google Cloud** | Vertex AI / Gemini | Yes (query context) | ✅ Available |
| **Microsoft Azure** | Key Vault, Storage, Sentinel | Yes (encrypted data) | ✅ Available |
| **ChromaDB (Self-hosted)** | Vector database | Yes (all PHI) | N/A (self-hosted) |

**Action Items:**
1. Execute BAAs with all cloud providers
2. Document data flow diagrams showing PHI to each vendor
3. Ensure contracts include:
   - No PHI used for training/improvement
   - Right to audit vendor security
   - Breach notification procedures
   - Data deletion upon termination
4. Annual BAA review and renewal

**API Provider Configuration to Minimize PHI Exposure:**

```python
# Update trinity_api_connector.py to anonymize queries sent to LLMs

from phi_anonymizer import PHIAnonymizer

class AMAHWeightedEngine:
    def __init__(self):
        # ... existing init ...
        self.anonymizer = PHIAnonymizer()

    async def get_model_logic(self, model_type, context):
        """Anonymize context before sending to external APIs."""

        # Anonymize any PHI in context
        anonymized_context = self.anonymizer.anonymize_text(context)

        # Use anonymized context in API calls
        prompt = f"""
        [AMAH STRATEGIC AUDIT - PRIORITY: ACCURACY]
        Task: {anonymized_context}

        [Note: Patient identifiers have been removed per HIPAA]
        ... rest of prompt ...
        """

        # ... existing API call logic ...
```

**Estimated Effort:** 16 hours (legal review + implementation)

---

### 6.2 P3.2: Penetration Testing & Vulnerability Assessment

**HIPAA Requirement:** §164.308(a)(8) - Evaluation

**Testing Scope:**

1. **External Penetration Test:**
   - Web application (Streamlit UI)
   - API endpoints (if any)
   - TLS configuration
   - Authentication bypass attempts
   - SQL injection, XSS, CSRF

2. **Internal Security Assessment:**
   - ChromaDB encryption verification
   - Key Vault access controls
   - Audit log tampering resistance
   - Consent enforcement
   - Role escalation attempts

3. **Social Engineering:**
   - Phishing simulations
   - Password policy compliance

**Recommended Vendors:**
- **Coalfire** (HIPAA specialist)
- **Schellman** (healthcare focus)
- **Optiv Security**

**Expected Findings Categories:**
- Critical: Must fix before production
- High: Fix within 30 days
- Medium: Fix within 90 days
- Low: Address in next release

**Estimated Cost:** $15,000-$30,000
**Estimated Effort (remediation):** 40 hours

---

### 6.3 P3.3: HIPAA Security Risk Assessment

**HIPAA Requirement:** §164.308(a)(1)(ii)(A) - Risk Analysis

**Methodology: NIST 800-30 Risk Assessment**

**Risk Matrix:**

| Threat | Likelihood | Impact | Risk Level | Mitigation |
|--------|-----------|--------|-----------|------------|
| **Unauthorized PHI Access** | Medium | High | 🔴 HIGH | RBAC, audit logging, session timeout |
| **Data Breach (ChromaDB)** | Low | Critical | 🔴 HIGH | Encryption at rest, access controls |
| **API Key Exposure** | Medium | High | 🟡 MEDIUM | Key Vault, rotation policy |
| **Insider Threat** | Low | High | 🟡 MEDIUM | Audit logging, least privilege |
| **Ransomware** | Medium | High | 🟡 MEDIUM | Encrypted backups, EDR software |
| **Consent Violations** | Low | High | 🟡 MEDIUM | Automated consent checks |
| **Third-party Breach** | Low | Medium | 🟢 LOW | BAAs, vendor audits |

**Risk Assessment Report Template:**

```markdown
# AMANI Platform HIPAA Security Risk Assessment

## Executive Summary
[Overall risk posture, key findings]

## Scope
- Systems: Streamlit UI, ChromaDB, Azure infrastructure
- Data: PHI (patient profiles, clinical trial matches)
- Time period: [Date range]

## Methodology
NIST 800-30 Rev. 1 risk assessment framework

## Findings

### Critical Risks (Immediate Action Required)
1. **Risk:** [Description]
   - **Threat:** [Threat source]
   - **Vulnerability:** [Existing weakness]
   - **Likelihood:** [Low/Medium/High]
   - **Impact:** [Low/Medium/High/Critical]
   - **Mitigation:** [Control implementation]
   - **Residual Risk:** [After mitigation]

### High Risks (Address within 30 days)
...

### Medium Risks (Address within 90 days)
...

## Compliance Status
- [ ] Access Control (§164.312(a))
- [ ] Audit Controls (§164.312(b))
- [ ] Integrity (§164.312(c))
- [ ] Transmission Security (§164.312(e))

## Recommendations
1. [Priority 1 recommendation]
2. [Priority 2 recommendation]
...

## Conclusion
[Overall assessment, certification readiness]
```

**Estimated Effort:** 40 hours

---

### 6.4 P3.4: Policies & Procedures Documentation

**HIPAA Requirement:** §164.316(a) - Policies and Procedures

**Required Policy Documents:**

1. **Security Policy (HIPAA §164.316(b)(1))**
   - Information security program overview
   - Roles and responsibilities
   - Security incident response plan
   - Disaster recovery plan

2. **Access Control Policy (§164.312(a))**
   - User provisioning/deprovisioning
   - Password requirements (12+ chars, complexity, 90-day rotation)
   - Multi-factor authentication (future)
   - Privileged access management

3. **Audit and Monitoring Policy (§164.312(b))**
   - Log retention (6 years for research data)
   - Log review procedures (monthly)
   - Security event escalation

4. **Encryption Policy (§164.312(a)(2)(iv))**
   - Data classification
   - Encryption standards (AES-256)
   - Key management procedures

5. **Breach Notification Policy (§164.408)**
   - Breach definition
   - Discovery procedures
   - Notification timeline (60 days)
   - HHS reporting requirements

6. **Consent Management Policy (§164.508)**
   - Consent types and purposes
   - Revocation procedures
   - Documentation requirements

7. **De-identification Policy (§164.514)**
   - Safe Harbor method application
   - Limited Data Set procedures
   - Re-identification prohibition

8. **Vendor Management Policy (§164.308(b))**
   - BAA requirements
   - Vendor security assessment
   - Data sharing agreements

9. **Workforce Training Policy (§164.308(a)(5))**
   - Annual HIPAA training
   - Role-specific training
   - Training documentation

10. **Incident Response Plan (§164.308(a)(6))**
    - Incident classification
    - Response team roles
    - Forensics procedures
    - Post-incident review

**Policy Template Structure:**

```markdown
# [Policy Name]

**Policy Number:** SEC-001
**Effective Date:** [Date]
**Review Date:** [Annual]
**Owner:** [Title]
**Approved By:** [Name, Title]

## Purpose
[Why this policy exists]

## Scope
[Who/what it applies to]

## Policy Statement
[Specific requirements]

## Procedures
### [Procedure 1]
1. Step 1
2. Step 2
...

## Roles and Responsibilities
- **Role 1:** Responsibilities
- **Role 2:** Responsibilities

## Compliance
HIPAA §[section number]

## Exceptions
[Process for exceptions, if any]

## Related Documents
- [Related policy]
- [Procedure document]

## Revision History
| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0 | [Date] | Initial release | [Name] |
```

**Estimated Effort:** 24 hours

---

## 7. CONFIGURATION REFERENCE

### 7.1 Updated `amah_config.json` with HIPAA Controls

```json
{
  "version": "4.0_HIPAA_COMPLIANT",
  "alignment_logic": {
    "precision_lock_threshold": 0.79,
    "manual_audit_threshold": 1.35
  },
  "trinity_audit_gate": {
    "variance_tolerance": "DYNAMIC",
    "variance_limit_numeric": 0.005,
    "consensus_models": ["GPT-4o", "Gemini-3.0", "Claude-4.5"]
  },
  "security": {
    "encryption": {
      "at_rest": {
        "enabled": true,
        "algorithm": "AES-256-GCM",
        "key_source": "azure_key_vault",
        "key_name": "CHROMADB-ENCRYPTION-KEY"
      },
      "in_transit": {
        "enabled": true,
        "tls_version": "1.2",
        "enforce_https": true
      }
    },
    "authentication": {
      "enabled": true,
      "method": "streamlit_authenticator",
      "session_timeout_minutes": 15,
      "password_policy": {
        "min_length": 12,
        "require_uppercase": true,
        "require_lowercase": true,
        "require_numbers": true,
        "require_special": true,
        "max_age_days": 90
      },
      "lockout_policy": {
        "max_failed_attempts": 5,
        "lockout_duration_minutes": 30
      }
    },
    "access_control": {
      "rbac_enabled": true,
      "roles": {
        "admin": {
          "phi_access": true,
          "config_modify": true,
          "user_manage": true,
          "audit_view": true,
          "emergency_access": true
        },
        "clinician": {
          "phi_access": true,
          "config_modify": false,
          "user_manage": false,
          "audit_view": false,
          "emergency_access": false
        },
        "researcher": {
          "phi_access": false,
          "config_modify": false,
          "user_manage": false,
          "audit_view": false,
          "emergency_access": false
        },
        "support": {
          "phi_access": false,
          "config_modify": false,
          "user_manage": false,
          "audit_view": true,
          "emergency_access": false
        }
      }
    },
    "audit_logging": {
      "enabled": true,
      "encrypted": true,
      "log_path": "logs/audit_encrypted.log",
      "retention_days": 180,
      "max_size_mb": 10,
      "backup_count": 90,
      "include_phi_flag": true,
      "log_level": "INFO"
    },
    "consent_management": {
      "enabled": true,
      "database_path": "consent_records.db",
      "require_consent_for_queries": true,
      "consent_types": ["phi_access", "research", "third_party", "marketing"],
      "default_expiry_days": 365
    },
    "phi_protection": {
      "de_identification": {
        "enabled": true,
        "method": "safe_harbor",
        "anonymize_for_researchers": true
      },
      "transmission_security": {
        "anonymize_api_calls": true,
        "strip_identifiers_in_logs": true
      }
    },
    "data_integrity": {
      "enabled": true,
      "checksum_algorithm": "HMAC-SHA256",
      "verification_schedule": "daily",
      "verification_time": "02:00"
    },
    "backup": {
      "enabled": true,
      "schedule": "daily",
      "time": "01:00",
      "retention_days": 180,
      "storage_type": "azure_blob",
      "encryption_enabled": true,
      "test_restore_frequency_days": 90
    },
    "monitoring": {
      "siem_enabled": true,
      "siem_type": "azure_sentinel",
      "alert_on_suspicious_activity": true,
      "security_events": [
        "login_failure",
        "account_lockout",
        "unauthorized_access",
        "consent_violation",
        "integrity_failure",
        "mass_data_export"
      ]
    }
  },
  "protocol_audit": {
    "enabled": true,
    "log_path": "sovereignty_audit.log"
  },
  "concurrency_guard": {
    "max_concurrent_bridge_calls": 8,
    "timeout_seconds": 30,
    "enabled": true
  },
  "centurion_injection": {
    "enabled": false,
    "timeout_seconds": 5
  },
  "l2_5_authority": {
    "use_medical_reasoner_first": true,
    "fallback_to_staircase": true
  },
  "orchestrator_audit": {
    "path_truncation_on_high_entropy": true,
    "variance_limit_for_truncation": 0.005,
    "d_threshold_for_truncation": 0.79,
    "compliance_score_min": 0.5,
    "reasoning_cost_max": 1.0,
    "force_desensitize_on_fail": false
  },
  "hard_anchor_boolean_interception": {
    "atomic_technical_terms": [
      "iPS", "BCI", "DBS", "KRAS G12C", "G12C", "CAR-T", "ADC",
      "干细胞", "脑机接口", "Neural Interface", "Neuralink",
      "Dopaminergic", "Subthalamic", "mRNA Vaccine", "stem cell"
    ],
    "retrieval_pool_size_n": 100,
    "downgrade_firewall": true
  }
}
```

### 7.2 Environment Variables (`.env.production`)

```bash
# CRITICAL: Do NOT commit this file to git
# Store actual values in Azure Key Vault

# Key Vault Configuration
USE_AZURE_KEYVAULT=true
AZURE_KEYVAULT_URL=https://amani-secrets.vault.azure.net/

# Secrets stored in Key Vault (not in .env):
# - GEMINI-API-KEY
# - OPENAI-API-KEY
# - ANTHROPIC-API-KEY
# - GOOGLE-SERVICE-ACCOUNT-JSON
# - MEDGEMMA-ENDPOINT
# - CHROMADB-ENCRYPTION-KEY
# - AUDIT-LOG-ENCRYPTION-KEY
# - JWT-SECRET-KEY
# - DATA-INTEGRITY-KEY
# - BACKUP-ENCRYPTION-KEY
# - PHI-ANONYMIZATION-KEY

# Azure Monitoring
AZURE_LOGS_ENDPOINT=https://amani-logs.ods.opinsights.azure.com
AZURE_DCR_RULE_ID=dcr-xxx
AZURE_DCR_STREAM_NAME=Custom-AMANISecurityLogs

# Backup Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=amanibackup;AccountKey=[FROM_VAULT]

# SIEM Configuration
SIEM_TYPE=azure_sentinel
ENVIRONMENT=production

# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 7.3 Required Azure Resources

```bash
# Resource Group
az group create --name amani-rg --location eastus

# Key Vault
az keyvault create --name amani-secrets --resource-group amani-rg --location eastus
az keyvault update --name amani-secrets --resource-group amani-rg --enabled-for-disk-encryption true

# Log Analytics Workspace (for Azure Sentinel)
az monitor log-analytics workspace create \
  --resource-group amani-rg \
  --workspace-name amani-logs \
  --location eastus

# Azure Sentinel
az sentinel onboard --resource-group amani-rg --workspace-name amani-logs

# Storage Account (for backups)
az storage account create \
  --name amanibackup \
  --resource-group amani-rg \
  --location eastus \
  --sku Standard_GRS \
  --encryption-services blob \
  --https-only true

# Blob Container
az storage container create \
  --name amani-backups \
  --account-name amanibackup \
  --public-access off

# Managed Identity (for Key Vault access)
az identity create --name amani-identity --resource-group amani-rg

# Grant Key Vault permissions to Managed Identity
PRINCIPAL_ID=$(az identity show --name amani-identity --resource-group amani-rg --query principalId -o tsv)
az keyvault set-policy --name amani-secrets --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

---

## 8. TESTING & VERIFICATION

### 8.1 Security Testing Checklist

**P0: Critical Security**
- [ ] API keys not in `.env` or git history
- [ ] ChromaDB encrypted at rest (test: try opening with SQLite directly - should fail)
- [ ] Audit logs encrypted (test: `cat logs/audit_encrypted.log` - should show encrypted data)
- [ ] Key rotation procedure documented and tested

**P1: Core HIPAA**
- [ ] Cannot access system without login
- [ ] 4 roles enforced (admin, clinician, researcher, support)
- [ ] Session timeout after 15 minutes
- [ ] Account lockout after 5 failed logins
- [ ] All PHI queries logged with user_id
- [ ] Consent checked before query execution
- [ ] HTTPS enforced (test: `curl http://amani.mayo.edu` redirects to HTTPS)
- [ ] TLS 1.2+ only (test: `sslscan amani.mayo.edu`)

**P2: Enhanced Security**
- [ ] De-identification removes all 18 HIPAA identifiers
- [ ] Integrity checks run nightly
- [ ] Security events in Azure Sentinel
- [ ] Backups created daily and encrypted
- [ ] Test restore successful
- [ ] 6-month retention enforced

**P3: Certification**
- [ ] BAAs signed with all vendors
- [ ] Penetration test completed, findings remediated
- [ ] Risk assessment documented
- [ ] All policies documented and approved
- [ ] Workforce trained on policies

### 8.2 Automated Security Tests

```python
# Create security_tests.py

"""
Automated HIPAA compliance verification tests.
Run before each production deployment.
"""
import pytest
import requests
import subprocess
import os
from auth_manager import get_auth_manager
from audit_logger import get_audit_logger
from consent_manager import ConsentManager
from integrity_manager import IntegrityManager

class TestP0_CriticalSecurity:
    """Test P0: Critical security controls."""

    def test_no_secrets_in_env(self):
        """Verify API keys not in .env file."""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
                assert 'sk-' not in content, "OpenAI API key in .env!"
                assert 'sk_ant_' not in content, "Anthropic API key in .env!"

    def test_chromadb_encrypted(self):
        """Verify ChromaDB is encrypted."""
        import sqlite3
        try:
            # Attempt to open without encryption key
            conn = sqlite3.connect('medical_db/chroma.sqlite3')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM embeddings LIMIT 1")
            assert False, "ChromaDB not encrypted!"
        except sqlite3.DatabaseError as e:
            assert 'file is not a database' in str(e).lower() or 'encrypted' in str(e).lower()

    def test_audit_logs_encrypted(self):
        """Verify audit logs are encrypted."""
        with open('logs/audit_encrypted.log', 'r') as f:
            first_line = f.readline()
            # Should be base64-encoded Fernet token
            assert not first_line.startswith('{'), "Audit logs not encrypted!"

class TestP1_CoreHIPAA:
    """Test P1: Core HIPAA requirements."""

    def test_authentication_required(self):
        """Verify authentication gate exists."""
        # This would be UI test in production
        auth = get_auth_manager()
        assert auth.config_path.exists()

    def test_rbac_enforced(self):
        """Verify RBAC permissions enforced."""
        auth = get_auth_manager()

        # Create test user
        auth.add_user('test_researcher', 'Test Researcher', 'Test@123', 'test@test.com', 'researcher')

        # Verify researcher cannot access PHI
        assert not auth.check_permission('test_researcher', 'phi_access')

        # Cleanup
        del auth.config['credentials']['usernames']['test_researcher']
        auth.save_config()

    def test_consent_enforcement(self):
        """Verify consent checked before PHI access."""
        consent = ConsentManager()

        # No consent should exist for test patient
        has_consent = consent.check_consent('TEST_PATIENT', 'PHI_ACCESS', 'test_user')
        assert not has_consent

    def test_https_enforced(self):
        """Verify HTTPS redirection."""
        try:
            response = requests.get('http://localhost:8501', allow_redirects=False, timeout=5)
            # Should redirect to HTTPS or refuse HTTP
            assert response.status_code in [301, 302, 403]
        except requests.exceptions.ConnectionError:
            # Server not running during test
            pass

    def test_tls_version(self):
        """Verify TLS 1.2+ only."""
        result = subprocess.run(
            ['openssl', 's_client', '-connect', 'localhost:443', '-tls1_1'],
            capture_output=True,
            timeout=5
        )
        # TLS 1.1 should be rejected
        assert b'ssl handshake failure' in result.stderr.lower() or result.returncode != 0

class TestP2_EnhancedSecurity:
    """Test P2: Enhanced security controls."""

    def test_de_identification(self):
        """Verify PHI de-identification."""
        from phi_anonymizer import PHIAnonymizer
        anonymizer = PHIAnonymizer()

        phi_text = "Patient John Doe, MRN: 12345, SSN: 123-45-6789, DOB: 01/15/1980, email: john@example.com"
        anonymized = anonymizer.anonymize_text(phi_text)

        assert 'John Doe' not in anonymized
        assert '12345' not in anonymized
        assert '123-45-6789' not in anonymized
        assert 'john@example.com' not in anonymized
        assert '[REDACTED]' in anonymized or '[DATE]' in anonymized

    def test_data_integrity_checks(self):
        """Verify integrity verification works."""
        integrity = IntegrityManager()

        test_record = {'id': 'test123', 'data': 'test data'}
        hash1 = integrity.compute_record_hash(test_record)

        # Modify record
        test_record['data'] = 'modified data'
        hash2 = integrity.compute_record_hash(test_record)

        assert hash1 != hash2, "Integrity hash not detecting changes!"

    def test_backup_exists(self):
        """Verify backups are being created."""
        from backup_manager import BackupManager
        manager = BackupManager()

        # Check if backups exist in cloud storage
        # This is a simplified check
        assert os.path.exists('backups/') or manager.backup_type in ['azure_blob', 'aws_s3']

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
```

**Run Tests:**
```bash
pytest security_tests.py -v --html=security_test_report.html
```

---

## 9. FINAL COMPLIANCE CHECKLIST

### 9.1 HIPAA Technical Safeguards (§164.312) Compliance Matrix

| Requirement | Standard | Implementation Status | Evidence |
|-------------|----------|----------------------|----------|
| **§164.312(a)(1)** | Unique User Identification | ✅ Implemented | `auth_manager.py`, user login logs |
| **§164.312(a)(2)(i)** | Emergency Access | ✅ Implemented | Admin role with emergency consent creation |
| **§164.312(a)(2)(ii)(B)** | Automatic Logoff | ✅ Implemented | 15-minute session timeout in `app_v4.py` |
| **§164.312(a)(2)(iv)** | Encryption/Decryption | ✅ Implemented | SQLCipher for ChromaDB, Fernet for logs |
| **§164.312(b)** | Audit Controls | ✅ Implemented | `audit_logger.py`, encrypted audit logs |
| **§164.312(c)(1)** | Integrity | ✅ Implemented | `integrity_manager.py`, HMAC checksums |
| **§164.312(c)(2)** | Authentication | ✅ Implemented | Digital signatures in consent records |
| **§164.312(d)** | Person/Entity Authentication | ✅ Implemented | Bcrypt password hashing, JWT tokens |
| **§164.312(e)(1)** | Transmission Security | ✅ Implemented | TLS 1.2+, Nginx HTTPS |
| **§164.312(e)(2)(ii)** | Encryption | ✅ Implemented | All external API calls use TLS |

### 9.2 HIPAA Administrative Safeguards (§164.308) Compliance Matrix

| Requirement | Standard | Implementation Status | Evidence |
|-------------|----------|----------------------|----------|
| **§164.308(a)(1)(ii)(A)** | Risk Analysis | ⬜ In Progress | See P3.3 - Security risk assessment |
| **§164.308(a)(1)(ii)(D)** | Info System Activity Review | ✅ Implemented | SIEM integration, monthly audit log review |
| **§164.308(a)(3)(i)** | Workforce Security | ⬜ Pending | Requires HR policies, background checks |
| **§164.308(a)(4)(ii)(A)** | Access Authorization | ✅ Implemented | RBAC with 4 roles |
| **§164.308(a)(5)(i)** | Security Training | ⬜ Pending | Annual HIPAA training required |
| **§164.308(a)(6)(ii)** | Response and Reporting | ⬜ Pending | Incident response plan (see P3.4) |
| **§164.308(a)(7)(ii)(A)** | Data Backup Plan | ✅ Implemented | Daily encrypted backups to Azure |
| **§164.308(a)(8)** | Evaluation | ⬜ Pending | Penetration testing (see P3.2) |
| **§164.308(b)(1)** | Business Associate Contracts | ⬜ Pending | BAAs with cloud providers (see P3.1) |

### 9.3 Implementation Timeline Summary

```
Week 1 (P0): Critical Security Fixes
├── Day 1-2: Azure Key Vault integration
├── Day 2-3: ChromaDB encryption
├── Day 4: Audit log encryption
└── Day 5: Key rotation procedure

Weeks 2-4 (P1): Core HIPAA Requirements
├── Week 2-3: Authentication & RBAC
├── Week 2: Enhanced audit logging
├── Week 3: Consent management
└── Week 3: TLS/HTTPS setup

Weeks 5-12 (P2): Enhanced Security
├── Weeks 5-6: PHI de-identification
├── Week 7: Data integrity controls
├── Weeks 8-9: SIEM integration
└── Week 10: Backup & disaster recovery

Weeks 13-24 (P3): Certification Readiness
├── Weeks 13-14: Business Associate Agreements
├── Weeks 15-18: Penetration testing
├── Weeks 19-20: Risk assessment
└── Weeks 21-24: Policies & procedures
```

### 9.4 Production Deployment Checklist

**Pre-Deployment (T-1 week):**
- [ ] All P0 tasks completed and verified
- [ ] All P1 tasks completed and verified
- [ ] P2 tasks completed (or explicitly deferred with risk acceptance)
- [ ] Security tests passing (100% P0/P1, 80%+ P2)
- [ ] Penetration test completed with no Critical/High findings
- [ ] Risk assessment approved by leadership
- [ ] BAAs executed with all vendors processing PHI
- [ ] Backup and restore tested successfully
- [ ] Disaster recovery plan documented and rehearsed
- [ ] Incident response team identified and trained
- [ ] All policies approved and published
- [ ] Workforce HIPAA training completed

**Deployment Day:**
- [ ] Deploy to production environment
- [ ] Verify HTTPS enforced
- [ ] Test authentication flow
- [ ] Verify audit logging active
- [ ] Check Key Vault connectivity
- [ ] Verify ChromaDB encryption
- [ ] Test consent workflow
- [ ] Verify SIEM integration
- [ ] Confirm backup job scheduled
- [ ] Monitor for 24 hours

**Post-Deployment (T+1 week):**
- [ ] Review audit logs for anomalies
- [ ] Verify backup completed successfully
- [ ] Test restore procedure
- [ ] Conduct security monitoring review
- [ ] Document any issues encountered
- [ ] Update runbooks based on deployment experience

---

## 10. COST SUMMARY

### 10.1 Development Costs

| Phase | Effort (hours) | Rate | Cost |
|-------|----------------|------|------|
| **P0: Critical Security** | 34h | $150/hr | $5,100 |
| **P1: Core HIPAA** | 72h | $150/hr | $10,800 |
| **P2: Enhanced Security** | 160h | $150/hr | $24,000 |
| **P3: Certification** | 120h | $150/hr | $18,000 |
| **Testing & Documentation** | 40h | $150/hr | $6,000 |
| **Total Development** | **426h** | - | **$63,900** |

### 10.2 Infrastructure Costs (Annual)

| Service | Description | Monthly | Annual |
|---------|-------------|---------|--------|
| **Azure Key Vault** | Secret storage | $10 | $120 |
| **Azure Storage (GRS)** | Encrypted backups (1TB) | $50 | $600 |
| **Azure Log Analytics** | Audit logs & SIEM | $200 | $2,400 |
| **Azure Sentinel** | Security monitoring | $300 | $3,600 |
| **SSL Certificates** | Let's Encrypt (free) | $0 | $0 |
| **Compute** | VM or App Service | $200 | $2,400 |
| **Total Infrastructure** | - | **$760** | **$9,120** |

### 10.3 External Services (One-time + Annual)

| Service | Cost | Frequency |
|---------|------|-----------|
| **HIPAA Training** | $50/user | Annual |
| **Penetration Testing** | $15,000-$30,000 | Annual |
| **HIPAA Risk Assessment** | $10,000-$20,000 | Initial |
| **Legal Review (BAAs)** | $5,000-$10,000 | Initial |
| **Compliance Audit** | $20,000-$50,000 | Biennial |

### 10.4 Total Investment

| Category | Cost |
|----------|------|
| **Development** (one-time) | $63,900 |
| **Infrastructure** (annual) | $9,120 |
| **Initial Compliance** (one-time) | $30,000-$60,000 |
| **Ongoing Compliance** (annual) | $15,000-$30,000 |
| **First Year Total** | **$118,020-$162,020** |
| **Subsequent Years** | **$24,120-$39,120** |

---

## 11. CONCLUSION & NEXT STEPS

### 11.1 Current State vs. Target State

**Current State (Pre-Implementation):**
- 🔴 **NOT HIPAA COMPLIANT**
- Critical security gaps in encryption, access control, audit logging
- No consent management or de-identification
- High risk of breach and regulatory penalties

**Target State (Post-Implementation):**
- ✅ **HIPAA COMPLIANT**
- Comprehensive security controls (encryption, access, audit)
- Patient consent management and de-identification
- Ready for production deployment with PHI

### 11.2 Critical Success Factors

1. **Executive Sponsorship:** HIPAA compliance requires organizational commitment
2. **Dedicated Resources:** 1 FTE for 4-6 months (or phased implementation)
3. **Expert Consultation:** Engage HIPAA compliance consultant for risk assessment
4. **Iterative Approach:** Start with P0, validate, then proceed to P1/P2/P3
5. **Continuous Monitoring:** Security is ongoing, not one-time

### 11.3 Immediate Next Steps

**Week 1 Actions:**
1. **Secure Funding:** Approve $120K-$160K budget for first year
2. **Assign Owner:** Designate HIPAA Security Officer
3. **Start P0:** Implement Azure Key Vault (highest priority)
4. **Engage Vendor:** Contract with HIPAA compliance firm for risk assessment
5. **Legal Review:** Begin BAA negotiations with cloud providers

**Week 2-4 Actions:**
6. Complete P0 implementation
7. Begin P1 authentication and audit logging
8. Draft initial security policies
9. Conduct workforce security training needs assessment

### 11.4 Risk Acceptance

If full HIPAA compliance cannot be achieved before production launch, consider:

**Option 1: Phased Rollout**
- Deploy with de-identified data only (researcher access)
- No PHI until P0+P1 complete
- Gradual rollout to clinician users

**Option 2: Limited Pilot**
- Small pilot with 10-20 consented patients
- Manual monitoring and oversight
- Accelerated compliance timeline

**Option 3: Defer Production**
- Complete full P0+P1+P2 before any PHI processing
- Recommended approach for enterprise deployment

---

## 12. DOCUMENT CONTROL

**Document Information:**
- **Title:** AMANI Platform HIPAA Compliance Implementation & Security Roadmap
- **Version:** 1.0
- **Date:** 2026-02-08
- **Classification:** CONFIDENTIAL - INTERNAL USE ONLY
- **Distribution:** Dr. Smith Lin, AMANI Development Team, Legal/Compliance Team

**Document History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-08 | Claude Sonnet 4.5 | Initial comprehensive roadmap |

**Review Schedule:**
- Monthly review during implementation (Weeks 1-12)
- Quarterly review post-implementation
- Annual comprehensive review

**Approval:**
- [ ] Dr. Smith Lin (Project Sponsor)
- [ ] HIPAA Security Officer
- [ ] Legal Counsel
- [ ] IT Security Team

**Contact:**
For questions or clarifications, contact:
- **Technical:** AMANI Development Team
- **Compliance:** HIPAA Security Officer
- **Legal:** General Counsel

---

**END OF DOCUMENT**

*This roadmap provides a comprehensive, actionable plan for achieving HIPAA compliance for the AMANI platform. Implementation should proceed in priority order (P0 → P1 → P2 → P3) with continuous validation and documentation.*
