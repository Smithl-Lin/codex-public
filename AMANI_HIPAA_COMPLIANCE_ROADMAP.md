# AMANI Platform: HIPAA Compliance Implementation & Security Roadmap

**Project:** A.M.A.N.I. (Mayo AI Asset Hub) V4.0
**Document Version:** 1.0
**Date:** 2026-02-08
**Classification:** CONFIDENTIAL - SECURITY ARCHITECTURE
**Prepared By:** Claude Sonnet 4.5 Security Analysis
**Stakeholder:** Dr. Smith Lin, Mayo Jacksonville

---

## EXECUTIVE SUMMARY

This document provides a prioritized roadmap to achieve HIPAA compliance for the AMANI platform's production deployment. The platform currently operates in a **pre-compliance state** with critical security gaps that must be addressed before handling Protected Health Information (PHI).

### Critical Findings

**Current Security Posture:** 🔴 **HIGH RISK - NOT HIPAA COMPLIANT**

| Risk Category | Current State | HIPAA Requirement | Gap Severity |
|--------------|---------------|-------------------|--------------|
| **Encryption at Rest** | ❌ None (ChromaDB unencrypted) | §164.312(a)(2)(iv) REQUIRED | 🔴 CRITICAL |
| **Access Controls** | ❌ No authentication/RBAC | §164.312(a)(1) REQUIRED | 🔴 CRITICAL |
| **Audit Logging** | ⚠️ Partial (sovereignty_audit.log) | §164.312(b) REQUIRED | 🔴 CRITICAL |
| **Transmission Security** | ❌ No TLS/encryption | §164.312(e)(1) REQUIRED | 🔴 CRITICAL |
| **API Key Management** | 🔴 Hardcoded in .env files | §164.312(a)(2)(i) REQUIRED | 🔴 CRITICAL |
| **PHI Anonymization** | ❌ No de-identification | §164.514(a) REQUIRED | 🟡 HIGH |
| **Consent Management** | ❌ Not implemented | §164.508 REQUIRED | 🟡 HIGH |
| **Data Integrity** | ⚠️ Partial (no checksums) | §164.312(c)(1) REQUIRED | 🟡 HIGH |

### Compliance Timeline

- **P0 (Week 1):** Critical security incidents - Encryption, API key rotation
- **P1 (Month 1):** Core HIPAA requirements - Access controls, audit logging, consent
- **P2 (Quarter 1):** Enhanced security - Anonymization, SIEM, monitoring
- **P3 (Quarter 2+):** Certification readiness - BAA preparation, penetration testing

### Estimated Investment

- **Development Effort:** 320-400 hours (8-10 weeks with 1 FTE)
- **Infrastructure Costs:** $500-2000/month (Azure Key Vault, encryption, monitoring)
- **External Audit/Certification:** $15,000-50,000 (HIPAA assessment)

---

## TABLE OF CONTENTS

1. [Architecture Analysis](#1-architecture-analysis)
2. [HIPAA Technical Safeguards Mapping](#2-hipaa-technical-safeguards-mapping)
3. [P0: Critical Security Fixes (Week 1)](#3-p0-critical-security-fixes-week-1)
4. [P1: Core HIPAA Implementation (Month 1)](#4-p1-core-hipaa-implementation-month-1)
5. [P2: Enhanced Security (Quarter 1)](#5-p2-enhanced-security-quarter-1)
6. [P3: Certification Readiness (Quarter 2+)](#6-p3-certification-readiness-quarter-2)
7. [Configuration Reference](#7-configuration-reference)
8. [Testing & Verification](#8-testing-verification)
9. [Compliance Checklist](#9-compliance-checklist)

---

## 1. ARCHITECTURE ANALYSIS

### 1.1 Current System Architecture

The AMANI platform implements a 5-layer architecture processing sensitive patient data:

```
User Input (PHI)
    ↓
[L1] ECNNSentinel (Entropy Gate) - D ≤ 0.79 threshold
    ↓
[L2] Centurion Injection (4 components: Patient Resources, Therapeutics, PI Registry, Lifecycle)
    ↓
[L2.5] Value Orchestrator (Shadow Quote, Billing Engine)
    ↓
[L3] Global Nexus (AGID → Physical Nodes, ChromaDB vector search)
    ↓
[L4] Interface Layer (Streamlit UI, Multi-modal outputs)
```

### 1.2 Data Flow & PHI Exposure Points

**PHI Data Identified:**
- Patient profiles (age, gender, diagnosis) in query inputs
- Medical history in `match_patient.py` queries
- Clinical trial matching results containing patient-specific recommendations
- Audit logs in `sovereignty_audit.log` (timestamps, D-values, L3 origins)

**Critical Exposure Points:**

| Component | File Path | PHI Risk | Current Protection |
|-----------|-----------|----------|-------------------|
| **ChromaDB Databases** | `20260128/medical_db/chroma.sqlite3` (339MB) | 🔴 HIGH | None - Unencrypted |
| **ChromaDB Databases** | `20260128/amah_vector_db/chroma.sqlite3` | 🔴 HIGH | None - Unencrypted |
| **Audit Logs** | `sovereignty_audit.log` (2.4MB) | 🔴 HIGH | Plain text |
| **API Keys** | `.env` file | 🔴 CRITICAL | Plain text |
| **Streamlit UI** | `app_v4.py` (port 8501) | 🟡 MEDIUM | No TLS, No auth |
| **Trinity API Calls** | `trinity_api_connector.py` | 🟡 MEDIUM | No encryption context |
| **Patient Query Cache** | In-memory (ChromaDB client) | 🟡 MEDIUM | Not persisted |

### 1.3 Configuration Structure Analysis

**Current Configuration:** `amah_config.json` (1.3KB)

```json
{
  "alignment_logic": {
    "precision_lock_threshold": 0.79,
    "manual_audit_threshold": 1.35
  },
  "trinity_audit_gate": {
    "variance_tolerance": "DYNAMIC",
    "variance_limit_numeric": 0.005,
    "consensus_models": ["GPT-4o", "Gemini-3.0", "Claude-4.5"]
  },
  "protocol_audit": {
    "enabled": true,
    "log_path": "sovereignty_audit.log"
  },
  "concurrency_guard": {
    "max_concurrent_bridge_calls": 8,
    "timeout_seconds": 30,
    "enabled": true
  }
}
```

**HIPAA-Required Extensions Needed:**
- `encryption` section (at-rest, in-transit)
- `access_control` section (RBAC, user roles)
- `audit_controls` section (structured logging, retention)
- `phi_handling` section (anonymization, consent)
- `key_management` section (vault integration)

---

## 2. HIPAA TECHNICAL SAFEGUARDS MAPPING

### 2.1 Access Control (§164.312(a)(1))

| HIPAA Requirement | Implementation Status | Gap Analysis |
|-------------------|----------------------|--------------|
| **(a)(1) Unique User Identification** | ❌ Not implemented | No user authentication system exists. Streamlit UI is open to anyone with URL access. |
| **(a)(2)(i) Automatic Logoff** | ❌ Not implemented | Streamlit sessions persist indefinitely. |
| **(a)(2)(ii) Encryption and Decryption** | ❌ Not implemented | ChromaDB stores data in plain SQLite without encryption. |
| **(a)(2)(iii) Emergency Access Procedure** | ❌ Not implemented | No break-glass mechanism for emergency PHI access. |

**Required Implementation:** See Section 4.1

### 2.2 Audit Controls (§164.312(b))

| HIPAA Requirement | Implementation Status | Gap Analysis |
|-------------------|----------------------|--------------|
| **(b) Audit Controls** | ⚠️ Partial | `sovereignty_audit.log` captures some events but lacks: <br>- User identity<br>- PHI access events<br>- Structured format<br>- Tamper protection |

**Current Logging Example:**
```
2026-02-04T19:10:23	intercepted=False	d_effective=0.75	variance=0.002	l3_origin=chromadb
```

**Missing Fields:**
- User ID / Session ID
- Action type (CREATE, READ, UPDATE, DELETE)
- PHI identifiers accessed
- Source IP address
- Success/failure status
- Retention policy enforcement

**Required Implementation:** See Section 4.2

### 2.3 Integrity Controls (§164.312(c)(1))

| HIPAA Requirement | Implementation Status | Gap Analysis |
|-------------------|----------------------|--------------|
| **(c)(1) Integrity** | ❌ Not implemented | No mechanisms to verify PHI has not been improperly altered/destroyed. |
| **(c)(2) Authentication** | ❌ Not implemented | No electronic authentication for PHI transmissions. |

**Required Implementation:** See Section 5.3

### 2.4 Transmission Security (§164.312(e))

| HIPAA Requirement | Implementation Status | Gap Analysis |
|-------------------|----------------------|--------------|
| **(e)(1) Transmission Security** | ❌ Not implemented | - Streamlit runs on HTTP (not HTTPS)<br>- API calls to OpenAI/Anthropic/Google use HTTPS but payload not encrypted<br>- No VPN or network encryption |
| **(e)(2)(ii) Encryption** | ⚠️ Partial | External API calls use TLS but internal data flows are unencrypted. |

**Required Implementation:** See Section 4.4

---

## 3. P0: CRITICAL SECURITY FIXES (WEEK 1)

**Priority:** 🔴 **IMMEDIATE - Block Production Deployment**
**Estimated Effort:** 40-60 hours
**Risk if Delayed:** Breach notification required under §164.404 if PHI exposed

### 3.1 P0.1: Secure API Key Management (Day 1-2)

**Current Risk:** API keys in `.env` file are committed to git history and stored in plain text.

**Implementation:**

#### Option A: Azure Key Vault (Recommended for Azure deployments)

**Step 1:** Install dependencies
```bash
pip install azure-identity azure-keyvault-secrets
```

**Step 2:** Create new file: `config_secure.py`
```python
# C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128\config_secure.py
"""
HIPAA-compliant credential management using Azure Key Vault.
Replaces config.py for production deployments.
"""
import os
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import logging

logger = logging.getLogger(__name__)

# Key Vault configuration
VAULT_URL = os.getenv("AZURE_KEYVAULT_URL")  # e.g., https://amani-secrets.vault.azure.net/
_kv_client: Optional[SecretClient] = None
_secret_cache = {}  # In-memory cache with TTL

def _get_kv_client() -> SecretClient:
    """Initialize Key Vault client with managed identity."""
    global _kv_client
    if _kv_client is None:
        if not VAULT_URL:
            raise ValueError("AZURE_KEYVAULT_URL not set in environment")
        credential = DefaultAzureCredential()
        _kv_client = SecretClient(vault_url=VAULT_URL, credential=credential)
    return _kv_client

def get_secret(secret_name: str, use_cache: bool = True) -> Optional[str]:
    """
    Retrieve secret from Azure Key Vault with caching.
    Logs access for HIPAA audit trail.
    """
    if use_cache and secret_name in _secret_cache:
        return _secret_cache[secret_name]

    try:
        client = _get_kv_client()
        secret = client.get_secret(secret_name)
        _secret_cache[secret_name] = secret.value
        logger.info(f"Secret retrieved: {secret_name}", extra={
            "action": "SECRET_ACCESS",
            "secret_name": secret_name,
            "timestamp": secret.properties.created_on
        })
        return secret.value
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        return None

def get_gemini_api_key() -> Optional[str]:
    return get_secret("GEMINI-API-KEY")

def get_openai_api_key() -> Optional[str]:
    return get_secret("OPENAI-API-KEY")

def get_anthropic_api_key() -> Optional[str]:
    return get_secret("ANTHROPIC-API-KEY")

def get_google_credentials_path() -> Optional[str]:
    """Returns path to service account JSON stored in Key Vault."""
    # Store JSON content as secret, write to temp file
    json_content = get_secret("GOOGLE-SERVICE-ACCOUNT-JSON")
    if json_content:
        import tempfile
        import json
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(json.loads(json_content), temp_file)
        temp_file.close()
        return temp_file.name
    return None

def get_medgemma_endpoint() -> Optional[str]:
    return get_secret("MEDGEMMA-ENDPOINT")

def rotate_secret_cache():
    """Clear cache to force re-fetch. Call on key rotation events."""
    global _secret_cache
    _secret_cache = {}
    logger.info("Secret cache rotated", extra={"action": "CACHE_ROTATION"})
```

**Step 3:** Update `config.py` to use secure backend
```python
# Insert at top of config.py after imports
USE_SECURE_VAULT = os.getenv("USE_AZURE_KEYVAULT", "false").lower() == "true"

if USE_SECURE_VAULT:
    from config_secure import (
        get_gemini_api_key as _secure_get_gemini,
        get_openai_api_key as _secure_get_openai,
        get_anthropic_api_key as _secure_get_anthropic,
        get_google_credentials_path as _secure_get_google,
        get_medgemma_endpoint as _secure_get_medgemma
    )
    get_gemini_api_key = _secure_get_gemini
    get_openai_api_key = _secure_get_openai
    get_anthropic_api_key = _secure_get_anthropic
    get_google_credentials_path = _secure_get_google
    get_medgemma_endpoint = _secure_get_medgemma
```

**Step 4:** Azure Setup
```bash
# Create Key Vault
az keyvault create --name amani-secrets --resource-group amani-rg --location eastus

# Store secrets
az keyvault secret set --vault-name amani-secrets --name GEMINI-API-KEY --value "YOUR_KEY"
az keyvault secret set --vault-name amani-secrets --name OPENAI-API-KEY --value "YOUR_KEY"
az keyvault secret set --vault-name amani-secrets --name ANTHROPIC-API-KEY --value "YOUR_KEY"

# Grant access to managed identity
az keyvault set-policy --name amani-secrets --object-id <MANAGED_IDENTITY_ID> --secret-permissions get list
```

**Step 5:** Update `.env` for vault mode
```bash
USE_AZURE_KEYVAULT=true
AZURE_KEYVAULT_URL=https://amani-secrets.vault.azure.net/
```

**Step 6:** Remove secrets from `.env` and update `.gitignore`
```bash
# Add to .gitignore
.env
.env.production
*.env.local
google_key.json
```

**Verification:**
```bash
python -c "
import os
os.environ['USE_AZURE_KEYVAULT'] = 'true'
os.environ['AZURE_KEYVAULT_URL'] = 'https://amani-secrets.vault.azure.net/'
from config import get_openai_api_key
key = get_openai_api_key()
print('✅ Key Vault integration working' if key else '❌ Failed')
"
```

**Alternative: AWS Secrets Manager**
```python
# For AWS deployments, use boto3
import boto3
sm_client = boto3.client('secretsmanager', region_name='us-east-1')
secret = sm_client.get_secret_value(SecretId='amani/openai-api-key')
```

**Alternative: HashiCorp Vault**
```python
# For on-premise or multi-cloud
import hvac
client = hvac.Client(url='https://vault.example.com:8200', token=os.getenv('VAULT_TOKEN'))
secret = client.secrets.kv.v2.read_secret_version(path='amani/api-keys')
```

**Estimated Effort:** 8 hours
**Dependencies:** Azure subscription or AWS account
**Compliance Mapping:** §164.312(a)(2)(i) - Encryption and Decryption

---

### 3.2 P0.2: ChromaDB Encryption at Rest (Day 2-3)

**Current Risk:** 339MB+ of medical data in `chroma.sqlite3` is unencrypted.

**Implementation Options:**

#### Option A: SQLite Encryption Extension (SQLCipher)

**Step 1:** Install SQLCipher-enabled ChromaDB fork
```bash
pip install sqlcipher3-binary
```

**Step 2:** Create encryption wrapper: `chromadb_encrypted.py`
```python
# C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128\chromadb_encrypted.py
"""
Encrypted ChromaDB wrapper using SQLCipher for HIPAA compliance.
"""
import chromadb
from chromadb.config import Settings
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_encryption_key() -> str:
    """
    Retrieve database encryption key from Key Vault.
    CRITICAL: Never log or print this key.
    """
    from config_secure import get_secret
    key = get_secret("CHROMADB-ENCRYPTION-KEY")
    if not key:
        raise ValueError("CHROMADB-ENCRYPTION-KEY not found in Key Vault")
    return key

def create_encrypted_client(path: str) -> chromadb.PersistentClient:
    """
    Create ChromaDB client with SQLCipher encryption.

    Args:
        path: Database directory path

    Returns:
        Encrypted PersistentClient instance
    """
    encryption_key = get_encryption_key()

    # SQLCipher pragma settings
    sqlite_pragmas = {
        f"PRAGMA key = '{encryption_key}'",
        "PRAGMA cipher_page_size = 4096",
        "PRAGMA kdf_iter = 64000",  # PBKDF2 iterations
        "PRAGMA cipher_hmac_algorithm = HMAC_SHA512",
        "PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512"
    }

    settings = Settings(
        anonymized_telemetry=False,
        allow_reset=False,  # Prevent accidental data deletion
        is_persistent=True
    )

    client = chromadb.PersistentClient(
        path=path,
        settings=settings
    )

    # Apply encryption pragmas to underlying SQLite connection
    # Note: This requires ChromaDB fork with SQLCipher support
    # See: https://github.com/chroma-core/chroma/issues/encryption

    logger.info(f"Encrypted ChromaDB client created: {path}", extra={
        "action": "DB_INIT_ENCRYPTED",
        "path": path
    })

    return client

def migrate_existing_db(source_path: str, dest_path: str):
    """
    Migrate unencrypted ChromaDB to encrypted version.

    WARNING: This is a one-way migration. Backup source_path first.
    """
    logger.warning(f"Starting database encryption migration: {source_path} → {dest_path}")

    # Open unencrypted source
    source_client = chromadb.PersistentClient(path=source_path)

    # Create encrypted destination
    dest_client = create_encrypted_client(dest_path)

    # Migrate each collection
    for collection in source_client.list_collections():
        logger.info(f"Migrating collection: {collection.name}")

        # Get all data from source
        source_coll = source_client.get_collection(collection.name)
        all_data = source_coll.get(include=["documents", "metadatas", "embeddings"])

        # Create in destination
        dest_coll = dest_client.get_or_create_collection(collection.name)

        # Batch insert (ChromaDB limit: 41666 per batch)
        batch_size = 5000
        ids = all_data["ids"]
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_docs = all_data["documents"][i:i+batch_size] if all_data["documents"] else None
            batch_metas = all_data["metadatas"][i:i+batch_size] if all_data["metadatas"] else None
            batch_embeds = all_data["embeddings"][i:i+batch_size] if all_data["embeddings"] else None

            dest_coll.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embeds
            )
            logger.info(f"Migrated batch {i//batch_size + 1}: {len(batch_ids)} records")

    logger.info("Migration complete. Verify dest_path before deleting source_path.")
```

**Step 3:** Update `amani_trinity_bridge.py` to use encrypted client
```python
# In amani_trinity_bridge.py, line 298-309, replace:
# self._chroma_client = chromadb.PersistentClient(path=chromadb_path)

# With:
from chromadb_encrypted import create_encrypted_client
self._chroma_client = create_encrypted_client(path=chromadb_path)
```

**Step 4:** Encrypt existing databases
```bash
# Backup first
cp -r medical_db/ medical_db_backup/
cp -r amah_vector_db/ amah_vector_db_backup/

# Run migration
python -c "
from chromadb_encrypted import migrate_existing_db
migrate_existing_db('medical_db', 'medical_db_encrypted')
migrate_existing_db('amah_vector_db', 'amah_vector_db_encrypted')
"

# Test encrypted DB
python -c "
from chromadb_encrypted import create_encrypted_client
client = create_encrypted_client('medical_db_encrypted')
colls = client.list_collections()
print(f'✅ Encrypted DB working: {len(colls)} collections')
"

# Once verified, replace directories
mv medical_db/ medical_db_unencrypted_OLD/
mv medical_db_encrypted/ medical_db/
mv amah_vector_db/ amah_vector_db_unencrypted_OLD/
mv amah_vector_db_encrypted/ amah_vector_db/
```

#### Option B: Filesystem-Level Encryption (Azure Disk Encryption / LUKS)

If SQLCipher integration is not feasible:

**Linux (LUKS):**
```bash
# Create encrypted volume
cryptsetup luksFormat /dev/sdb
cryptsetup luksOpen /dev/sdb amani_encrypted_volume
mkfs.ext4 /dev/mapper/amani_encrypted_volume
mount /dev/mapper/amani_encrypted_volume /mnt/amani_data

# Move databases
mv medical_db/ /mnt/amani_data/
mv amah_vector_db/ /mnt/amani_data/
ln -s /mnt/amani_data/medical_db medical_db
ln -s /mnt/amani_data/amah_vector_db amah_vector_db
```

**Azure:**
```bash
# Enable Azure Disk Encryption
az vm encryption enable --resource-group amani-rg --name amani-vm --disk-encryption-keyvault amani-secrets
```

**Windows (BitLocker):**
```powershell
Enable-BitLocker -MountPoint "C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128" -EncryptionMethod Aes256 -UsedSpaceOnly
```

**Estimated Effort:** 16 hours (including testing)
**Dependencies:** SQLCipher or encrypted filesystem
**Compliance Mapping:** §164.312(a)(2)(iv) - Encryption and Decryption

---

### 3.3 P0.3: Audit Log Encryption & Rotation (Day 4)

**Current Risk:** `sovereignty_audit.log` contains query metadata in plain text.

**Implementation:**

**Step 1:** Create secure logging module: `audit_logger.py`
```python
# C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\20260128\audit_logger.py
"""
HIPAA-compliant audit logging with encryption and rotation.
"""
import logging
import logging.handlers
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class EncryptedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Rotating file handler with per-record encryption for HIPAA compliance.
    """
    def __init__(self, filename, mode='a', maxBytes=10*1024*1024, backupCount=90,
                 encoding=None, delay=False, encryption_key: Optional[bytes] = None):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.cipher = self._init_cipher(encryption_key)

    def _init_cipher(self, key: Optional[bytes]) -> Fernet:
        """Initialize Fernet cipher with derived key."""
        if key is None:
            # Derive key from Key Vault secret
            from config_secure import get_secret
            password = get_secret("AUDIT-LOG-ENCRYPTION-KEY")
            if not password:
                raise ValueError("AUDIT-LOG-ENCRYPTION-KEY not in Key Vault")
            salt = b'amani_audit_salt_v1'  # Store in config
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
        return Fernet(key)

    def emit(self, record):
        """Encrypt log record before writing."""
        try:
            msg = self.format(record)
            encrypted = self.cipher.encrypt(msg.encode())
            # Write encrypted bytes in base64
            self.stream.write(encrypted.decode() + '\n')
            self.stream.flush()
        except Exception:
            self.handleError(record)

class HIPAAAuditLogger:
    """
    Structured audit logger for HIPAA §164.312(b) compliance.
    """
    def __init__(self, log_path: str = "audit_encrypted.log", encrypt: bool = True):
        self.logger = logging.getLogger("amani.audit")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't propagate to root logger

        # Remove existing handlers
        self.logger.handlers = []

        # Add encrypted rotating handler
        if encrypt:
            handler = EncryptedRotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=90  # 90-day retention minimum
            )
        else:
            handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10*1024*1024,
                backupCount=90
            )

        # Structured JSON formatter
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s","event":"%(message)s"}'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_access(self, user_id: str, action: str, resource: str,
                   success: bool, phi_accessed: bool = False,
                   metadata: Optional[Dict[str, Any]] = None):
        """
        Log PHI access event per HIPAA requirements.

        Args:
            user_id: Unique user identifier
            action: CREATE, READ, UPDATE, DELETE, SEARCH
            resource: Resource accessed (collection name, AGID, etc.)
            success: Whether action succeeded
            phi_accessed: Whether PHI was accessed
            metadata: Additional context (IP, session ID, etc.)
        """
        event = {
            "event_type": "PHI_ACCESS" if phi_accessed else "SYSTEM_ACCESS",
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "success": success,
            "phi_accessed": phi_accessed,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Add integrity hash
        event["integrity_hash"] = self._compute_hash(event)

        self.logger.info(json.dumps(event))

    def log_security_event(self, event_type: str, severity: str, description: str,
                          metadata: Optional[Dict[str, Any]] = None):
        """Log security incident per §164.308(a)(6)."""
        event = {
            "event_type": "SECURITY_INCIDENT",
            "severity": severity,  # LOW, MEDIUM, HIGH, CRITICAL
            "description": description,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        event["integrity_hash"] = self._compute_hash(event)
        self.logger.warning(json.dumps(event))

    def _compute_hash(self, event: Dict[str, Any]) -> str:
        """Compute SHA-256 hash for tamper detection."""
        event_copy = {k: v for k, v in event.items() if k != "integrity_hash"}
        event_str = json.dumps(event_copy, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()

# Global instance
_audit_logger: Optional[HIPAAAuditLogger] = None

def get_audit_logger() -> HIPAAAuditLogger:
    """Get singleton audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        log_path = os.path.join(
            os.path.dirname(__file__),
            "logs",
            "audit_encrypted.log"
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        _audit_logger = HIPAAAuditLogger(log_path, encrypt=True)
    return _audit_logger
```

**Step 2:** Update `amani_trinity_bridge.py` to use structured audit logging

```python
# In amani_trinity_bridge.py, replace _append_protocol_audit function (lines 254-272) with:

def _append_protocol_audit(base_dir: str, log_path: str, result: Dict[str, Any],
                          intercepted: bool, user_id: str = "SYSTEM") -> None:
    """Append audit event using HIPAA-compliant structured logging."""
    from audit_logger import get_audit_logger

    audit = get_audit_logger()
    l1 = result.get("l1_sentinel") or {}
    l3 = result.get("l3_nexus") or {}

    audit.log_access(
        user_id=user_id,
        action="SEARCH" if not intercepted else "BLOCKED",
        resource=f"L3_ChromaDB:{l3.get('l3_origin', 'unknown')}",
        success=not intercepted,
        phi_accessed=True,  # Assume all queries involve PHI
        metadata={
            "d_effective": l1.get("d_effective"),
            "shannon_entropy_variance": l1.get("shannon_entropy_variance"),
            "l3_origin": l3.get("l3_origin"),
            "intercepted": intercepted,
            "agids_returned": len(l3.get("agids", []))
        }
    )
```

**Step 3:** Create log directory and set permissions
```bash
mkdir -p logs/
chmod 700 logs/  # Owner-only access
```

**Step 4:** Add log decryption utility for compliance audits
```python
# audit_log_reader.py
"""Utility to decrypt and read audit logs for compliance review."""
from cryptography.fernet import Fernet
import sys

def decrypt_audit_log(encrypted_path: str, output_path: str):
    from audit_logger import EncryptedRotatingFileHandler
    handler = EncryptedRotatingFileHandler.__new__(EncryptedRotatingFileHandler)
    handler._init_cipher(None)  # Load key from vault

    with open(encrypted_path, 'r') as enc_file, open(output_path, 'w') as dec_file:
        for line in enc_file:
            decrypted = handler.cipher.decrypt(line.strip().encode())
            dec_file.write(decrypted.decode() + '\n')
    print(f"✅ Decrypted log written to {output_path}")

if __name__ == "__main__":
    decrypt_audit_log("logs/audit_encrypted.log", "audit_decrypted.json")
```

**Estimated Effort:** 8 hours
**Dependencies:** cryptography library
**Compliance Mapping:** §164.312(b) - Audit Controls

---

*Document continues in next section...*

### 3.4 P0.4: Emergency API Key Rotation Procedure (Day 5)

**Scenario:** API key exposed in git history or compromised

**Immediate Actions:**

**Step 1:** Revoke compromised keys
```bash
# Anthropic
curl -X POST https://api.anthropic.com/v1/keys/revoke \
  -H "x-api-key: ${OLD_KEY}" \
  -d '{"key_id": "key_xyz"}'

# OpenAI
curl -X DELETE https://api.openai.com/v1/organization/keys/key_xyz \
  -H "Authorization: Bearer ${OLD_KEY}"

# Google Cloud
gcloud auth revoke service-account@project.iam.gserviceaccount.com
```

**Step 2:** Generate new keys and update Key Vault
```bash
az keyvault secret set --vault-name amani-secrets --name OPENAI-API-KEY --value "NEW_KEY"
az keyvault secret set --vault-name amani-secrets --name ANTHROPIC-API-KEY --value "NEW_KEY"
```

**Step 3:** Force cache rotation
```python
from config_secure import rotate_secret_cache
rotate_secret_cache()
```

**Step 4:** Audit all sessions using old keys
```bash
python audit_log_reader.py
grep "API_KEY_ROTATION" audit_decrypted.json
```

**Estimated Effort:** 2 hours (emergency response)
**Compliance Mapping:** §164.308(a)(4)(ii)(A) - Access Authorization

---

## Summary of P0 (Week 1)

| Task | Effort | Status | Files Modified |
|------|--------|--------|----------------|
| P0.1: Azure Key Vault Integration | 8h | ⬜ Pending | `config.py`, new `config_secure.py` |
| P0.2: ChromaDB Encryption | 16h | ⬜ Pending | `amani_trinity_bridge.py`, new `chromadb_encrypted.py` |
| P0.3: Audit Log Encryption | 8h | ⬜ Pending | `amani_trinity_bridge.py`, new `audit_logger.py` |
| P0.4: Key Rotation Procedure | 2h | ⬜ Pending | Documentation only |
| **Total Week 1** | **34h** | - | - |

**Validation Checklist:**
- [ ] All API keys stored in Key Vault (not .env)
- [ ] ChromaDB databases encrypted with AES-256
- [ ] Audit logs encrypted and rotated (90-day retention)
- [ ] Emergency key rotation procedure documented
- [ ] No secrets in git history

---

