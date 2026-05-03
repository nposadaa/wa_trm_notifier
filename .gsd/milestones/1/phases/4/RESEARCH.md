# Phase 4 Research: Cloud Deployment (Final)

## Pivot: GCP e2-micro (Always Free)
Despite the 1GB RAM limitation, GCP us-central1 was chosen due to instant availability. Memory was stabilized using a 4GB swap file and optimized browser resource blocking.

## Headless Block Bypass
- **DEC-011**: confirmed `headless: True` is flagged by WhatsApp.
- **Solution**: `xvfb-run` + `headless: False` with Advanced Stealth (navigator spoofs).

## Session Activation Strategy
- **Option A (Success)**: Local-to-Cloud Session Transfer. 
Linking explicitly on a local machine and transferring the `whatsapp_session` folder via ZIP bypasses the cloud-IP handshake block.

## RAM/CPU Stability (Verified)
- **4GB Swap**: Prevents OOM crashes on e2-micro.
- **1024x768 Viewport**: Ensures Desktop layout for search box detection.
- **Resource Blocking**: Aborting "image", "font", and "media" requests saves ~200MB RAM.

## Localization
- Spanish (es-419) detected on VM browser.
- Selectors updated to be language-aware ("Unread" / "No leídos").
