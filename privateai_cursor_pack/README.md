# PrivateAI Cursor Pack

This folder contains the Cursor-ready specification pack for building **PrivateAI Box**.

## Files

- `00_CURSOR_START_HERE.md` — read this first
- `01_PRODUCT_SPEC.md` — product definition
- `02_ARCHITECTURE.md` — system architecture
- `03_PHASED_BUILD_PLAN.md` — build phases
- `04_TEST_STRATEGY.md` — unit/integration/E2E/GPU/QEMU testing
- `05_APPLIANCE_IMAGE_AND_QEMU.md` — bootable image plan
- `06_SECURITY_AND_DEPLOYMENT.md` — deployment/security rules
- `07_CURSOR_IMPLEMENTATION_PROMPT.md` — first prompt to give Cursor

## How to use

Create a new repo/folder named:

```text
privateai-box
```

Put these `.md` files in the root.

Tell Cursor:

```text
Read 00_CURSOR_START_HERE.md and 07_CURSOR_IMPLEMENTATION_PROMPT.md first.
Then implement Phase 0 only.
```
