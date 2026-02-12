# AMANI Platform: HIPAA Compliance Roadmap - Part 2

**Continuation of AMANI_HIPAA_COMPLIANCE_ROADMAP.md**

---

## 4. P1: CORE HIPAA IMPLEMENTATION (MONTH 1)

**Priority:** 🟡 **HIGH - Required for Production**
**Estimated Effort:** 120-160 hours
**Dependencies:** P0 completion (encryption, key management)

### 4.1 P1.1: User Authentication & RBAC Implementation

**HIPAA Requirements:**
- §164.312(a)(1) - Unique User Identification
- §164.312(a)(2)(ii)(B) - Automatic Logoff
- §164.312(d) - Person or Entity Authentication

**Implementation Summary:**

1. **Install Authentication Libraries**
```bash
pip install streamlit-authenticator==0.2.3 bcrypt==4.1.2 pyjwt==2.8.0
```

2. **Create `auth_manager.py`** - Full RBAC system with 4 roles:
   - **Admin**: Full access including user management, configuration
   - **Clinician**: PHI access for treatment purposes
   - **Researcher**: De-identified data only
   - **Support**: Audit log viewing only

3. **Update `app_v4.py`** - Add authentication gate:
   - Login required before any access
   - 15-minute session timeout (automatic logoff)
   - User/role displayed in sidebar
   - All actions logged with user_id

4. **Create Default Users**:
   ```bash
   python create_users.py
   # Creates: admin, demo_clinician, researcher, support
   ```

**Key Features:**
- Bcrypt password hashing
- JWT tokens for API access
- Account lockout after 5 failed attempts
- Session timeout enforcement
- Permission matrix enforcement

**Estimated Effort:** 24 hours

---

### 4.2 P1.2: Comprehensive Audit Logging

**HIPAA Requirement:** §164.312(b) - Audit Controls

**Enhancements to Existing `audit_logger.py`:**

1. **Structured JSON Logging**: Every log entry includes:
   - `user_id`: Who performed the action
   - `action`: CREATE, READ, UPDATE, DELETE, SEARCH, LOGIN
   - `resource`: What was accessed (collection, AGID, etc.)
   - `success`: Boolean
   - `phi_accessed`: Boolean flag
   - `integrity_hash`: SHA-256 for tamper detection
   - `timestamp_utc`: ISO 8601 timestamp
   - `metadata`: Context-specific data

2. **Integration Points**:
   - **TrinityBridge**: Log all queries with D-values and AGIDs returned
   - **ChromaDB access**: Log database connections and queries
   - **Authentication**: Log login/logout/failed attempts
   - **Consent operations**: Log consent grants/revocations
   - **Configuration changes**: Log admin modifications

3. **Audit Log Viewer** (`audit_viewer.py`):
   - Streamlit page for administrators
   - Date range filtering
   - Event type filtering
   - User filtering
   - Export to JSON/CSV
   - Real-time decryption of encrypted logs

**Log Retention:** 90 days minimum (configurable up to 6 years for research data)

**Estimated Effort:** 16 hours

---

### 4.3 P1.3: Patient Consent Management

**HIPAA Requirement:** §164.508 - Authorization for Uses and Disclosures

**Consent Types Supported:**
1. **PHI_ACCESS**: General treatment/matching purposes
2. **RESEARCH**: Clinical trial matching data
3. **THIRD_PARTY**: Disclosure to external parties
4. **MARKETING**: Communications (not currently used)

**Implementation: `consent_manager.py`**

**Database Schema:**
```sql
CREATE TABLE consent_records (
    consent_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    consent_type TEXT NOT NULL,  -- PHI_ACCESS, RESEARCH, etc.
    status TEXT NOT NULL,  -- ACTIVE, REVOKED, EXPIRED, PENDING
    granted_date TEXT NOT NULL,
    expiry_date TEXT,
    revoked_date TEXT,
    purpose TEXT NOT NULL,  -- Specific purpose of consent
    scope TEXT,  -- Data elements covered
    authorized_users TEXT,  -- Comma-separated user IDs
    signature_hash TEXT NOT NULL,  -- SHA-256 of signature
    ip_address TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE consent_audit_trail (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    consent_id TEXT NOT NULL,
    action TEXT NOT NULL,  -- GRANTED, REVOKED, EXPIRED, ACCESSED
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata TEXT,  -- JSON
    FOREIGN KEY (consent_id) REFERENCES consent_records(consent_id)
);
```

**Key Methods:**
- `create_consent()`: Record new consent with digital signature
- `check_consent()`: Validate active consent before PHI access
- `revoke_consent()`: Patient right to revoke (§164.508(b)(5))
- `expire_consent()`: Automatic expiry based on date

**UI Integration:**
- Consent check before every query in `app_v4.py`
- Admin emergency consent creation
- Patient self-service consent portal (future)

**Estimated Effort:** 24 hours

---

### 4.4 P1.4: TLS/HTTPS Encryption for Web Traffic

**HIPAA Requirement:** §164.312(e) - Transmission Security

**Implementation Options:**

#### Option A: Nginx Reverse Proxy (Recommended)

**Configuration:**
- TLS 1.2/1.3 only (no TLS 1.0/1.1)
- Strong cipher suites (ECDHE, AES-256-GCM)
- HSTS header (force HTTPS)
- Security headers (X-Frame-Options, CSP, etc.)
- Let's Encrypt certificates (free, auto-renewal)

**Setup Steps:**
1. Install Nginx and Certbot
2. Configure reverse proxy to Streamlit (port 8501)
3. Obtain SSL certificate for domain
4. Enable auto-renewal via cron

**Nginx Config:** See main document Section 4.4

#### Option B: Azure App Service

For cloud deployments, Azure App Service provides:
- Automatic HTTPS with managed certificates
- Built-in TLS termination
- Custom domain support
- No manual certificate management

**Deployment:**
```bash
az webapp create --resource-group amani-rg --plan amani-plan \
  --name amani-app --runtime "PYTHON|3.10"
az webapp config ssl bind --certificate-thumbprint <thumbprint> \
  --ssl-type SNI --name amani-app --resource-group amani-rg
```

**Estimated Effort:** 8 hours

---

## P1 Summary: Month 1 Completion Checklist

| Component | Requirement | Files Created/Modified | Validation |
|-----------|-------------|----------------------|------------|
| **Authentication** | §164.312(a)(1) | `auth_manager.py`, `app_v4.py` | Login required, 4 roles enforced |
| **Automatic Logoff** | §164.312(a)(2)(ii)(B) | `app_v4.py` | 15-min timeout implemented |
| **Audit Controls** | §164.312(b) | `audit_logger.py`, all modules | All PHI access logged |
| **Consent Management** | §164.508 | `consent_manager.py`, `app_v4.py` | Consent checked before queries |
| **Transmission Security** | §164.312(e) | Nginx config, `.streamlit/config.toml` | HTTPS enforced with TLS 1.2+ |

**Total Effort:** 72 hours (1.8 weeks at 40h/week)

**Validation Tests:**
```bash
# Test authentication
python test_auth.py

# Test audit logging
python test_audit_logging.py

# Test consent workflow
python test_consent.py

# Test HTTPS
curl -I https://amani.mayo.edu
# Should return: HTTP/2 200, Strict-Transport-Security header
```

---

## 5. P2: ENHANCED SECURITY (QUARTER 1)

**Priority:** 🟡 **MEDIUM - Enhanced Compliance**
**Estimated Effort:** 160-200 hours
**Timeline:** Weeks 5-12
**Dependencies:** P0 + P1 completion

### 5.1 P2.1: PHI De-identification & Anonymization (Weeks 5-6)

**HIPAA Requirement:** §164.514(a) - De-identification of Protected Health Information

**Safe Harbor Method Implementation:**

Per §164.514(b)(2), remove/generalize the following 18 identifiers:

1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year) - all dates directly related to an individual
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers/serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photographs
18. Any other unique identifying number/characteristic/code

**Implementation: `phi_anonymizer.py`**

```python
"""
HIPAA Safe Harbor de-identification per §164.514(b)(2).
"""
import re
from datetime import datetime
from typing import Dict, Any, List
import hashlib

class PHIAnonymizer:
    """De-identify PHI per HIPAA Safe Harbor method."""

    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s]+',
            'mrn': r'\b(?:MRN|Medical Record|Patient ID)[:\s]+[\w-]+\b',
        }

    def anonymize_text(self, text: str, preserve_year: bool = True) -> str:
        """
        Remove identifiers from free text per Safe Harbor.

        Args:
            text: Input text potentially containing PHI
            preserve_year: Keep year in dates (allowed by Safe Harbor)

        Returns:
            Anonymized text with identifiers removed/generalized
        """
        # Replace emails
        text = re.sub(self.patterns['email'], '[EMAIL_REDACTED]', text)

        # Replace phones
        text = re.sub(self.patterns['phone'], '[PHONE_REDACTED]', text)

        # Replace SSNs
        text = re.sub(self.patterns['ssn'], '[SSN_REDACTED]', text)

        # Replace IP addresses
        text = re.sub(self.patterns['ip_address'], '[IP_REDACTED]', text)

        # Replace URLs
        text = re.sub(self.patterns['url'], '[URL_REDACTED]', text)

        # Replace MRNs
        text = re.sub(self.patterns['mrn'], '[MRN_REDACTED]', text, flags=re.IGNORECASE)

        # Anonymize dates (keep year only if preserve_year=True)
        if preserve_year:
            # Replace MM/DD/YYYY with [DATE]/YYYY
            text = re.sub(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', r'[DATE]/\3', text)
        else:
            text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', '[DATE_REDACTED]', text)

        # Remove likely names (capitalized sequences)
        # This is heuristic - production needs NER model
        text = re.sub(r'\b([A-Z][a-z]+ ){1,3}[A-Z][a-z]+\b', '[NAME_REDACTED]', text)

        return text

    def anonymize_query_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize ChromaDB query results before displaying to researchers.

        Args:
            results: ChromaDB query results dict

        Returns:
            Anonymized results with PHI removed
        """
        if 'documents' in results:
            results['documents'] = [
                [self.anonymize_text(doc) for doc in doc_list]
                for doc_list in results['documents']
            ]

        if 'metadatas' in results:
            results['metadatas'] = [
                [self._anonymize_metadata(meta) for meta in meta_list]
                for meta_list in results['metadatas']
            ]

        return results

    def _anonymize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize metadata fields."""
        anonymized = {}
        for key, value in metadata.items():
            if key in ['patient_id', 'mrn', 'name', 'email', 'phone']:
                anonymized[key] = '[REDACTED]'
            elif key in ['zip', 'postal_code']:
                # Generalize to 3 digits per Safe Harbor
                if isinstance(value, str) and len(value) >= 5:
                    anonymized[key] = value[:3] + '00'
                else:
                    anonymized[key] = '[REDACTED]'
            elif key == 'age':
                # Ages >89 must be aggregated
                if isinstance(value, (int, float)) and value > 89:
                    anonymized[key] = '>89'
                else:
                    anonymized[key] = value
            elif isinstance(value, str):
                anonymized[key] = self.anonymize_text(value)
            else:
                anonymized[key] = value

        return anonymized

    def create_limited_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Limited Data Set per §164.514(e).
        Removes 16 of 18 identifiers, allows dates and geographic info.
        """
        # Implementation similar to anonymize_query_results
        # but preserves dates and ZIP codes (first 3 digits)
        pass

    def generate_synthetic_patient_id(self, original_id: str) -> str:
        """
        Generate consistent synthetic ID for research purposes.
        Uses HMAC to ensure same original ID always maps to same synthetic ID.
        """
        from config_secure import get_secret
        secret_key = get_secret("PHI-ANONYMIZATION-KEY")
        if not secret_key:
            raise ValueError("PHI-ANONYMIZATION-KEY not in Key Vault")

        hash_obj = hashlib.sha256(f"{secret_key}:{original_id}".encode())
        synthetic_id = "SYNTH-" + hash_obj.hexdigest()[:12].upper()
        return synthetic_id
```

**Integration with Query Flow:**

```python
# In app_v4.py, add anonymization for researcher role

from phi_anonymizer import PHIAnonymizer

anonymizer = PHIAnonymizer()

# After TrinityBridge query
result = bridge.run_safe(patient_input, top_k_agids=5, user_id=username)

# Check user role
if st.session_state['user_role'] == 'researcher':
    # Anonymize results for researchers
    if 'l3_nexus' in result and 'agids' in result['l3_nexus']:
        # Fetch AGID details and anonymize
        result = anonymizer.anonymize_query_results(result)

    st.warning("⚠️ Results have been de-identified per HIPAA §164.514 for research use.")

# Display results
st.json(result)
```

**Validation:**
- Create test cases with known PHI
- Verify all 18 identifiers removed
- Test with HIPAA expert panel
- Document de-identification method in data use agreements

**Estimated Effort:** 40 hours

---

### 5.2 P2.2: Data Integrity Controls (Week 7)

**HIPAA Requirement:** §164.312(c)(1) - Integrity

**Implementation: Checksums & Digital Signatures**

```python
# Create integrity_manager.py

"""
Data integrity verification per HIPAA §164.312(c)(1).
"""
import hashlib
import hmac
from typing import Dict, Any
import json
from datetime import datetime

class IntegrityManager:
    """Manage data integrity checksums and verification."""

    def __init__(self):
        from config_secure import get_secret
        self.integrity_key = get_secret("DATA-INTEGRITY-KEY")
        if not self.integrity_key:
            raise ValueError("DATA-INTEGRITY-KEY not in Key Vault")

    def compute_record_hash(self, record: Dict[str, Any]) -> str:
        """
        Compute HMAC-SHA256 hash of record for integrity verification.

        Args:
            record: Data record (dict)

        Returns:
            Hex-encoded HMAC hash
        """
        # Normalize record to canonical JSON
        record_str = json.dumps(record, sort_keys=True, separators=(',', ':'))

        # Compute HMAC
        h = hmac.new(
            self.integrity_key.encode(),
            record_str.encode(),
            hashlib.sha256
        )
        return h.hexdigest()

    def verify_record_integrity(self, record: Dict[str, Any], expected_hash: str) -> bool:
        """
        Verify record has not been tampered with.

        Args:
            record: Data record to verify
            expected_hash: Previously computed hash

        Returns:
            True if integrity verified, False if tampered
        """
        computed_hash = self.compute_record_hash(record)
        return hmac.compare_digest(computed_hash, expected_hash)

    def add_integrity_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add integrity hash and timestamp to record.

        Returns:
            Record with _integrity_hash and _integrity_timestamp fields
        """
        # Don't hash the hash itself
        record_copy = {k: v for k, v in record.items()
                      if not k.startswith('_integrity_')}

        record['_integrity_hash'] = self.compute_record_hash(record_copy)
        record['_integrity_timestamp'] = datetime.utcnow().isoformat()

        return record

    def verify_database_integrity(self, collection_name: str) -> Dict[str, Any]:
        """
        Verify integrity of all records in a ChromaDB collection.

        Returns:
            Report with total, verified, failed counts
        """
        from chromadb_encrypted import create_encrypted_client
        import os

        base_path = os.path.dirname(__file__)
        client = create_encrypted_client(os.path.join(base_path, "medical_db"))
        collection = client.get_collection(collection_name)

        # Get all records
        all_data = collection.get(include=["metadatas"])

        total = len(all_data['ids'])
        verified = 0
        failed = []

        for i, (record_id, metadata) in enumerate(zip(all_data['ids'], all_data['metadatas'])):
            if '_integrity_hash' not in metadata:
                failed.append({
                    'id': record_id,
                    'reason': 'No integrity hash present'
                })
                continue

            expected_hash = metadata.pop('_integrity_hash')
            metadata.pop('_integrity_timestamp', None)

            if self.verify_record_integrity(metadata, expected_hash):
                verified += 1
            else:
                failed.append({
                    'id': record_id,
                    'reason': 'Hash mismatch - possible tampering'
                })

        return {
            'collection': collection_name,
            'total_records': total,
            'verified': verified,
            'failed': len(failed),
            'failed_records': failed,
            'timestamp': datetime.utcnow().isoformat()
        }
```

**Scheduled Integrity Verification:**

```python
# Create integrity_checker_cron.py

"""
Nightly integrity verification job.
"""
from integrity_manager import IntegrityManager
from audit_logger import get_audit_logger
import schedule
import time

def run_integrity_check():
    """Run integrity check on all collections."""
    manager = IntegrityManager()
    audit = get_audit_logger()

    collections = ['mayo_clinic_trials', 'expert_map_global']

    for coll in collections:
        report = manager.verify_database_integrity(coll)

        if report['failed'] > 0:
            # Log security incident
            audit.log_security_event(
                event_type="INTEGRITY_VIOLATION",
                severity="CRITICAL",
                description=f"Data integrity check failed for {coll}",
                metadata=report
            )

            # Send alert (implement email/Slack notification)
            send_alert(f"CRITICAL: Data integrity violation detected in {coll}")
        else:
            audit.log_access(
                user_id="SYSTEM",
                action="INTEGRITY_CHECK",
                resource=coll,
                success=True,
                phi_accessed=False,
                metadata=report
            )

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(run_integrity_check)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
```

**Estimated Effort:** 24 hours

---

### 5.3 P2.3: Security Monitoring & SIEM Integration (Weeks 8-9)

**HIPAA Requirement:** §164.308(a)(1)(ii)(D) - Information System Activity Review

**Implementation: Azure Sentinel / Splunk Integration**

```python
# Create siem_logger.py

"""
Security Information and Event Management (SIEM) integration.
Forwards security events to Azure Sentinel or Splunk.
"""
import logging
from logging.handlers import SysLogHandler
import json
from typing import Dict, Any

class SIEMLogger:
    """Forward security events to SIEM platform."""

    def __init__(self, siem_type: str = "azure_sentinel"):
        self.siem_type = siem_type
        self.logger = self._init_siem_logger()

    def _init_siem_logger(self) -> logging.Logger:
        """Initialize SIEM connection."""
        logger = logging.getLogger("amani.siem")
        logger.setLevel(logging.INFO)

        if self.siem_type == "azure_sentinel":
            # Azure Log Analytics workspace
            from azure.monitor.ingestion import LogsIngestionClient
            from azure.identity import DefaultAzureCredential

            endpoint = os.getenv("AZURE_LOGS_ENDPOINT")
            credential = DefaultAzureCredential()
            self.logs_client = LogsIngestionClient(endpoint, credential)

        elif self.siem_type == "splunk":
            # Splunk HTTP Event Collector
            handler = logging.handlers.HTTPHandler(
                os.getenv("SPLUNK_HEC_HOST"),
                os.getenv("SPLUNK_HEC_ENDPOINT"),
                method="POST"
            )
            logger.addHandler(handler)

        elif self.siem_type == "syslog":
            # Generic syslog (for ELK stack, etc.)
            handler = SysLogHandler(
                address=(os.getenv("SYSLOG_HOST", "localhost"), 514)
            )
            logger.addHandler(handler)

        return logger

    def log_security_event(self, event: Dict[str, Any]):
        """
        Forward security event to SIEM.

        Event types:
        - LOGIN_SUCCESS, LOGIN_FAILURE, LOGIN_LOCKOUT
        - PHI_ACCESS, PHI_EXPORT
        - CONSENT_GRANTED, CONSENT_REVOKED
        - INTEGRITY_VIOLATION
        - UNAUTHORIZED_ACCESS
        - CONFIG_CHANGE
        """
        # Add common fields
        event['source'] = 'amani_platform'
        event['version'] = 'v4.0'
        event['environment'] = os.getenv('ENVIRONMENT', 'production')

        # Map to SIEM severity
        severity_map = {
            'LOW': 'informational',
            'MEDIUM': 'warning',
            'HIGH': 'error',
            'CRITICAL': 'critical'
        }
        event['siem_severity'] = severity_map.get(event.get('severity', 'MEDIUM'))

        # Send to SIEM
        if self.siem_type == "azure_sentinel":
            self._send_to_azure_sentinel(event)
        else:
            self.logger.info(json.dumps(event))

    def _send_to_azure_sentinel(self, event: Dict[str, Any]):
        """Send event to Azure Sentinel."""
        rule_id = os.getenv("AZURE_DCR_RULE_ID")
        stream_name = os.getenv("AZURE_DCR_STREAM_NAME", "Custom-AMANISecurityLogs")

        try:
            self.logs_client.upload(
                rule_id=rule_id,
                stream_name=stream_name,
                logs=[event]
            )
        except Exception as e:
            logging.error(f"Failed to send to Azure Sentinel: {e}")

# Global instance
_siem_logger = None

def get_siem_logger() -> SIEMLogger:
    """Get singleton SIEM logger."""
    global _siem_logger
    if _siem_logger is None:
        siem_type = os.getenv("SIEM_TYPE", "azure_sentinel")
        _siem_logger = SIEMLogger(siem_type)
    return _siem_logger
```

**Azure Sentinel Configuration:**

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group amani-rg \
  --workspace-name amani-logs

# Enable Azure Sentinel
az sentinel onboard \
  --resource-group amani-rg \
  --workspace-name amani-logs

# Create custom log table
az monitor log-analytics workspace table create \
  --resource-group amani-rg \
  --workspace-name amani-logs \
  --name AMANISecurityLogs_CL \
  --retention-time 180  # 6 months
```

**Alert Rules:**

Create alerts in Azure Sentinel for:
1. **Failed Login Threshold**: >5 failed logins in 5 minutes
2. **After-Hours Access**: PHI access outside 7 AM - 7 PM
3. **Mass Data Export**: >100 records accessed in single session
4. **Integrity Violations**: Any integrity check failure
5. **Consent Violations**: PHI access without consent
6. **Privilege Escalation**: Role changes or permission grants

**Estimated Effort:** 48 hours

---

### 5.4 P2.4: Backup & Disaster Recovery (Week 10)

**HIPAA Requirement:** §164.308(a)(7)(ii)(A) - Data Backup Plan

**Implementation:**

```python
# Create backup_manager.py

"""
Automated backup and disaster recovery for HIPAA compliance.
"""
import os
import shutil
from datetime import datetime, timedelta
import subprocess
from typing import List
import boto3  # For S3 backup
from azure.storage.blob import BlobServiceClient  # For Azure Blob

class BackupManager:
    """Manage encrypted backups of PHI databases."""

    def __init__(self, backup_type: str = "azure_blob"):
        self.backup_type = backup_type
        self.local_backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        os.makedirs(self.local_backup_dir, exist_ok=True)

        if backup_type == "azure_blob":
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            self.blob_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_name = "amani-backups"

        elif backup_type == "aws_s3":
            self.s3_client = boto3.client('s3')
            self.bucket_name = os.getenv("AWS_S3_BACKUP_BUCKET", "amani-backups")

    def backup_databases(self) -> Dict[str, str]:
        """
        Create encrypted backup of ChromaDB databases.

        Returns:
            Dict of database paths and backup URLs
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backups = {}

        databases = [
            "medical_db",
            "amah_vector_db",
            "consent_records.db",
            "logs/audit_encrypted.log"
        ]

        for db_path in databases:
            if not os.path.exists(db_path):
                continue

            # Create compressed encrypted backup
            backup_name = f"{os.path.basename(db_path)}_{timestamp}.tar.gz.enc"
            backup_path = os.path.join(self.local_backup_dir, backup_name)

            # Tar + gzip + encrypt
            self._create_encrypted_archive(db_path, backup_path)

            # Upload to cloud storage
            cloud_url = self._upload_backup(backup_path, backup_name)
            backups[db_path] = cloud_url

            # Clean up local backup (keep cloud only for security)
            os.remove(backup_path)

        # Log backup completion
        from audit_logger import get_audit_logger
        audit = get_audit_logger()
        audit.log_access(
            user_id="SYSTEM",
            action="BACKUP_CREATE",
            resource="ALL_DATABASES",
            success=True,
            phi_accessed=False,
            metadata={
                "timestamp": timestamp,
                "databases": list(backups.keys()),
                "backup_type": self.backup_type
            }
        )

        return backups

    def _create_encrypted_archive(self, source_path: str, dest_path: str):
        """Create tar.gz.enc archive of database."""
        # Step 1: Tar + gzip
        temp_tar = dest_path.replace('.enc', '')
        subprocess.run([
            'tar', 'czf', temp_tar, source_path
        ], check=True)

        # Step 2: Encrypt with GPG
        from config_secure import get_secret
        gpg_key = get_secret("BACKUP-ENCRYPTION-KEY")

        with open(temp_tar, 'rb') as f:
            data = f.read()

        # Encrypt using Fernet (symmetric)
        from cryptography.fernet import Fernet
        cipher = Fernet(gpg_key.encode())
        encrypted_data = cipher.encrypt(data)

        with open(dest_path, 'wb') as f:
            f.write(encrypted_data)

        os.remove(temp_tar)

    def _upload_backup(self, local_path: str, backup_name: str) -> str:
        """Upload backup to cloud storage."""
        if self.backup_type == "azure_blob":
            blob_client = self.blob_client.get_blob_client(
                container=self.container_name,
                blob=backup_name
            )

            with open(local_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)

            return f"https://{self.blob_client.account_name}.blob.core.windows.net/{self.container_name}/{backup_name}"

        elif self.backup_type == "aws_s3":
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                backup_name,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            return f"s3://{self.bucket_name}/{backup_name}"

    def restore_backup(self, backup_url: str, restore_path: str):
        """Restore database from encrypted backup."""
        # Download from cloud
        backup_name = os.path.basename(backup_url)
        local_backup = os.path.join(self.local_backup_dir, backup_name)

        if self.backup_type == "azure_blob":
            blob_client = self.blob_client.get_blob_client(
                container=self.container_name,
                blob=backup_name
            )
            with open(local_backup, 'wb') as f:
                f.write(blob_client.download_blob().readall())

        # Decrypt
        from config_secure import get_secret
        from cryptography.fernet import Fernet

        gpg_key = get_secret("BACKUP-ENCRYPTION-KEY")
        cipher = Fernet(gpg_key.encode())

        with open(local_backup, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        temp_tar = local_backup.replace('.enc', '')
        with open(temp_tar, 'wb') as f:
            f.write(decrypted_data)

        # Extract
        subprocess.run([
            'tar', 'xzf', temp_tar, '-C', os.path.dirname(restore_path)
        ], check=True)

        # Clean up
        os.remove(local_backup)
        os.remove(temp_tar)

        # Log restore
        from audit_logger import get_audit_logger
        audit = get_audit_logger()
        audit.log_access(
            user_id="SYSTEM",
            action="BACKUP_RESTORE",
            resource=restore_path,
            success=True,
            phi_accessed=False,
            metadata={"backup_url": backup_url}
        )

    def rotate_backups(self, retention_days: int = 180):
        """Delete backups older than retention period (default 6 months)."""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        if self.backup_type == "azure_blob":
            container_client = self.blob_client.get_container_client(self.container_name)

            for blob in container_client.list_blobs():
                if blob.creation_time < cutoff_date:
                    container_client.delete_blob(blob.name)
                    logging.info(f"Deleted old backup: {blob.name}")

# Scheduled backup job
import schedule

def run_daily_backup():
    """Run daily backup at 1 AM."""
    manager = BackupManager()
    manager.backup_databases()
    manager.rotate_backups(retention_days=180)  # 6 month retention

schedule.every().day.at("01:00").do(run_daily_backup)
```

**Disaster Recovery Plan:**

1. **Recovery Time Objective (RTO):** 4 hours
2. **Recovery Point Objective (RPO):** 24 hours (daily backups)
3. **Backup Schedule:**
   - Daily full backups at 1 AM
   - Retain for 6 months (180 days)
   - Test restores quarterly

4. **Recovery Procedure:**
```bash
# Restore from backup
python -c "
from backup_manager import BackupManager
manager = BackupManager()
manager.restore_backup(
    backup_url='https://storage.blob.core.windows.net/amani-backups/medical_db_20260208_010000.tar.gz.enc',
    restore_path='medical_db'
)
"
```

**Estimated Effort:** 32 hours

---

## P2 Summary: Quarter 1 Completion Checklist

| Component | Requirement | Files Created | Effort |
|-----------|-------------|---------------|--------|
| **PHI De-identification** | §164.514(a) | `phi_anonymizer.py` | 40h |
| **Data Integrity** | §164.312(c)(1) | `integrity_manager.py` | 24h |
| **SIEM Integration** | §164.308(a)(1)(ii)(D) | `siem_logger.py` | 48h |
| **Backup & DR** | §164.308(a)(7)(ii)(A) | `backup_manager.py` | 32h |
| **Testing & Documentation** | - | Test scripts, runbooks | 16h |
| **Total Quarter 1** | - | - | **160h** |

**Validation Tests:**
- [ ] De-identification removes all 18 HIPAA identifiers
- [ ] Integrity checks run nightly, alert on violations
- [ ] Security events forwarded to SIEM in real-time
- [ ] Backups created daily, test restore successful
- [ ] 6-month backup retention enforced

---

*Document continues in summary section...*
