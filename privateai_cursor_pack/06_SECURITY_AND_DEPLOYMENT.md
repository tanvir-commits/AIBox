# PrivateAI Box — Security and Deployment

## 1. Security Position

PrivateAI Box is designed for local/private deployment.

Do NOT claim:

- HIPAA compliant
- SOC2 compliant
- legal compliance
- medical device compliance

unless reviewed and certified.

Use wording:

```text
Designed for local/private deployment.
```

Not:

```text
Guaranteed HIPAA compliant.
```

---

## 2. Default Network Posture

Default:

- LAN-only access
- no public internet exposure
- no open cloud tunnel
- no telemetry by default
- no customer documents in support bundles

Expose:

```text
http://privateai.local
```

Later support local HTTPS.

---

## 3. Auth

Phase 1:

- local username/password
- password hashing
- JWT/session token
- role-based permissions

Roles:

```text
owner
admin
user
read_only
```

---

## 4. Audit Logs

Log:

- login
- logout
- failed login
- document upload
- document delete
- source added
- source removed
- model changed
- backup created
- restore started
- user created
- user role changed

Do not log full chat contents in audit logs by default.

---

## 5. Backup Security

Backups include sensitive company information.

Backup location options:

- local disk
- external USB
- NAS path

Require admin/owner role.

Future:

- encrypted backup archives
- backup password
- offline recovery key

---

## 6. Support Bundles

Support bundle may include:

- app version
- service status
- logs
- hardware info
- redacted config
- failed indexing metadata

Must NOT include:

- customer documents
- extracted document text
- embeddings
- chat history
- passwords
- private keys

---

## 7. Deployment Modes

### Development

```bash
docker compose up --build
```

### Ubuntu Installer

```bash
sudo ./scripts/install_ubuntu.sh
```

### Appliance Image

```text
Flash privateai-box.img to SSD and boot.
```

---

## 8. Update Strategy

Early MVP:

```bash
git pull
docker compose pull
docker compose up -d
```

Appliance:

- update channel
- signed release manifest later
- rollback support later

Do not build complex OTA first.

---

## 9. Firewall Defaults

Allow:

- HTTP 80 on LAN
- HTTPS 443 later
- SSH optional/admin only

Block:

- public internet inbound
- database ports from LAN
- Qdrant direct LAN access
- Ollama direct LAN access unless explicitly enabled

Only nginx should be exposed to LAN.

---

## 10. Production Logging

Use structured logs.

Keep:

- backend logs
- ingestion logs
- admin actions
- service health

Add log rotation.

Avoid logging document contents.

---

## 11. Data Storage

Use:

```text
/opt/privateai/
 ├── config/
 ├── data/
 │   ├── uploads/
 │   ├── postgres/
 │   ├── qdrant/
 │   └── backups/
 ├── logs/
 └── docker-compose.yml
```

---

## 12. Factory Reset

Script:

```bash
sudo ./scripts/reset_factory.sh
```

Must ask for explicit confirmation:

```text
Type RESET PRIVATEAI to continue:
```

Factory reset deletes:

- users
- documents
- vectors
- metadata
- settings

Keeps:

- installed software
- appliance image base
