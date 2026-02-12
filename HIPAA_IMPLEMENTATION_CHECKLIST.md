# AMANI Platform: HIPAA Compliance Implementation Checklist

**Quick Reference Guide for Development Team - Print and Track Progress Weekly**

---

## WEEK 1: P0 - CRITICAL SECURITY (BLOCKING)

### Day 1-2: Azure Key Vault Integration ☐

- [ ] Create Azure Key Vault resource
- [ ] Install: `pip install azure-identity azure-keyvault-secrets`
- [ ] Create `config_secure.py` with vault integration
- [ ] Update `config.py` to use vault
- [ ] Store all API keys in Key Vault
- [ ] Remove keys from `.env` file
- [ ] Update `.gitignore`
- [ ] Verify vault integration working
- [ ] **CHECKPOINT:** No plaintext keys in repository

### Day 2-3: ChromaDB Encryption ☐

- [ ] Install: `pip install sqlcipher3-binary`
- [ ] Create `chromadb_encrypted.py`
- [ ] Generate encryption key in Key Vault
- [ ] Backup existing databases
- [ ] Run database migration
- [ ] Update `amani_trinity_bridge.py`
- [ ] Test encrypted DB access
- [ ] **CHECKPOINT:** All data encrypted at rest

### Day 4: Audit Log Encryption ☐

- [ ] Install: `pip install cryptography`
- [ ] Create `audit_logger.py`
- [ ] Generate audit encryption key
- [ ] Create `logs/` directory (chmod 700)
- [ ] Update Trinity bridge to use audit logger
- [ ] Test log encryption
- [ ] Create `audit_log_reader.py`
- [ ] **CHECKPOINT:** Audit logs encrypted

### Day 5: Key Rotation ☐

- [ ] Document rotation procedure
- [ ] Test with dummy key
- [ ] Create emergency runbook
- [ ] Set up expiry alerts
- [ ] **CHECKPOINT:** Rotation tested

**Week 1 Sign-off:** _____________________ Date: _______

---

## WEEKS 2-4: P1 - CORE HIPAA COMPLIANCE

### Authentication & RBAC ☐

- [ ] Install: `pip install streamlit-authenticator bcrypt pyjwt`
- [ ] Create `auth_manager.py`
- [ ] Update `app_v4.py` with login
- [ ] Add 15-minute timeout
- [ ] Create default users
- [ ] Test login/logout
- [ ] Test role permissions
- [ ] **CHECKPOINT:** Auth working

### Enhanced Audit Logging ☐

- [ ] Add user_id to all logs
- [ ] Create `query_auditor.py` decorator
- [ ] Update all PHI access points
- [ ] Create `audit_viewer.py` UI
- [ ] Test log completeness
- [ ] **CHECKPOINT:** Full audit trail

### Consent Management ☐

- [ ] Create `consent_manager.py`
- [ ] Initialize consent database
- [ ] Implement consent CRUD
- [ ] Update `app_v4.py` consent check
- [ ] Test consent workflow
- [ ] **CHECKPOINT:** Consent enforced

### TLS/HTTPS Setup ☐

- [ ] Install Nginx + Certbot
- [ ] Create Nginx config
- [ ] Obtain SSL certificate
- [ ] Test HTTPS access
- [ ] Verify TLS 1.2+
- [ ] **CHECKPOINT:** HTTPS enforced

**Month 1 Sign-off:** _____________________ Date: _______

---

## WEEKS 5-12: P2 - ENHANCED SECURITY

### PHI De-identification ☐

- [ ] Create `phi_anonymizer.py`
- [ ] Implement 18 identifiers
- [ ] Generate synthetic IDs
- [ ] Update app for researchers
- [ ] Test de-identification
- [ ] **CHECKPOINT:** Safe Harbor working

### Data Integrity ☐

- [ ] Create `integrity_manager.py`
- [ ] Add HMAC checksums
- [ ] Schedule nightly checks
- [ ] Test verification
- [ ] **CHECKPOINT:** Integrity monitoring

### SIEM Integration ☐

- [ ] Create `siem_logger.py`
- [ ] Set up Azure Sentinel
- [ ] Configure alert rules
- [ ] Test event forwarding
- [ ] **CHECKPOINT:** SIEM working

### Backup & DR ☐

- [ ] Create `backup_manager.py`
- [ ] Configure Azure Storage
- [ ] Schedule daily backups
- [ ] Test restore
- [ ] **CHECKPOINT:** Backups working

**Quarter 1 Sign-off:** _____________________ Date: _______

---

## FINAL PRE-PRODUCTION CHECKLIST

### Security Verification ☐
- [ ] All automated tests passing
- [ ] No secrets in git
- [ ] ChromaDB encrypted
- [ ] Audit logs encrypted
- [ ] HTTPS enforced
- [ ] TLS 1.2+ only

### HIPAA Compliance ☐
- [ ] Access Control (§164.312(a))
- [ ] Audit Controls (§164.312(b))
- [ ] Integrity (§164.312(c))
- [ ] Authentication (§164.312(d))
- [ ] Transmission Security (§164.312(e))
- [ ] De-identification (§164.514)
- [ ] Authorization (§164.508)

### Documentation ☐
- [ ] Architecture diagrams
- [ ] Data flow diagrams
- [ ] All policies approved
- [ ] DR plan documented
- [ ] Incident response plan
- [ ] Training materials

### External Verification ☐
- [ ] BAAs executed
- [ ] Pen test completed
- [ ] Risk assessment done
- [ ] Legal approved
- [ ] Executive approved

### Production Deployment ☐
- [ ] Deploy to production
- [ ] Verify HTTPS
- [ ] Test authentication
- [ ] Test consent
- [ ] Verify audit logs
- [ ] Check SIEM
- [ ] Confirm backup
- [ ] Monitor 24h

**Production Go-Live Approval:**

- [ ] Technical Lead: _____________________
- [ ] Security Officer: _____________________
- [ ] Legal Counsel: _____________________
- [ ] Executive Sponsor: _____________________

---

**Version:** 1.0 | **Date:** 2026-02-08
**Owner:** AMANI Development Team
**For details, see main roadmap documents**
