# PrivateAI Box — Product Specification

## 1. Product Vision

PrivateAI Box is a **local AI appliance** for SMBs that lets staff privately search, summarize, and ask questions over company documents.

Target users:

- Law firms
- Doctors offices
- Accounting firms
- Engineering firms
- Small manufacturers
- Local professional offices

Core promise:

```text
Private ChatGPT for your company documents, running locally.
```

The product should not require sensitive files to leave the customer’s office.

---

## 2. Product Shape

PrivateAI Box runs on a dedicated Ubuntu AI box.

Office users connect from normal PCs using a browser.

```text
Office PCs / Browsers
        |
        v
http://privateai.local
        |
        v
Ubuntu AI Appliance
 ├── PrivateAI Web UI
 ├── PrivateAI Backend API
 ├── Document Ingestion Worker
 ├── Ollama / later vLLM
 ├── Qdrant Vector DB
 ├── PostgreSQL Metadata DB
 ├── Local File Storage
 ├── nginx Reverse Proxy
 ├── Setup Wizard
 ├── Backup / Restore
 └── Admin Dashboard
```

---

## 3. Product Modes

### Mode A — Docker Development Mode

Used by developers.

```bash
docker compose up --build
```

Runs on:

- Windows + Docker Desktop
- WSL2
- Ubuntu desktop/server
- CPU-only if needed

---

### Mode B — Ubuntu Installer Mode

Used by early customers or internal testing.

Customer installs Ubuntu Server, then runs:

```bash
sudo ./scripts/install_ubuntu.sh
```

The script installs:

- Docker
- Docker Compose
- NVIDIA Container Toolkit if GPU exists
- PrivateAI services
- nginx
- systemd wrapper
- first-run setup wizard

---

### Mode C — Bootable Appliance Image

Long-term commercial form.

User flashes:

```text
PrivateAI_Box.img
```

to SSD or USB SSD, boots a PC, and gets the setup wizard.

This should feel like:

- Synology NAS
- TrueNAS
- pfSense
- Ubiquiti appliance
- Home Assistant OS

---

## 4. MVP Features

The MVP is complete when:

- Admin can log in
- Admin can upload PDFs/DOCX/TXT/MD
- Documents are parsed
- Documents are chunked
- Embeddings are generated
- Chunks are stored in Qdrant
- Metadata is stored in PostgreSQL
- User can ask questions
- Answers include citations
- System says when answer is not found
- Admin can add watched folders
- Staff can access UI on LAN
- Admin dashboard shows system health
- Backup script works
- Docker mode works
- Ubuntu installer works
- Appliance image boots in QEMU

---

## 5. Non-Goals for MVP

Do not build these first:

- SaaS cloud dashboard
- Mobile app
- Browser extension
- Voice assistant
- Fine-tuning pipeline
- Custom model training
- Kubernetes
- Multi-node clustering
- HIPAA compliance claims
- Legal advice workflows
- Medical diagnosis workflows
- Direct SharePoint OAuth
- Direct Google Drive OAuth

---

## 6. Hardware Targets

### Minimum Useful Box

```text
GPU: RTX 3060 12GB
RAM: 64GB
CPU: Ryzen 7 / Intel i7
Storage: 2TB NVMe
OS: Ubuntu Server LTS
```

### Recommended SMB Box

```text
GPU: RTX 3090 24GB
RAM: 128GB
CPU: Ryzen 9 / Intel i9
Storage: 4TB NVMe
OS: Ubuntu Server LTS
```

### High-End Office Box

```text
GPU: Dual RTX 3090 or RTX 4090
RAM: 128GB-256GB
CPU: Threadripper / Ryzen 9 / Intel i9
Storage: 4TB+ NVMe
OS: Ubuntu Server LTS
```

---

## 7. User Experience

### First Boot

User sees:

```text
Welcome to PrivateAI Box

1. Create admin account
2. Set company name
3. Choose model
4. Configure storage
5. Add documents or watched folder
6. Configure backup
7. Start using PrivateAI
```

---

### Daily Usage

Users go to:

```text
http://privateai.local
```

They can:

- Ask questions
- Search documents
- Get citations
- Upload files if permitted
- Filter by document source
- View chat history

---

## 8. Core Product Rule

The AI must be grounded in retrieved documents.

If the answer is not in the retrieved context, it must say:

```text
I could not find that in the indexed company documents.
```

No hallucinated policies, medical claims, legal conclusions, or fabricated citations.
