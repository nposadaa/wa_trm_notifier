---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: 1-on-1 WhatsApp API Handshake

## Objective
Establish a successful connection between our Python code and the Meta WhatsApp Cloud API. We will start by sending a test message to your personal test phone number to verify authentication and basic messaging functionality before investigating group options.

## Context
- .gsd/SPEC.md
- Meta Developer Dashboard (User provided)
- Python environment (Created in Phase 1)

## Tasks

<task type="checkpoint:human-verify">
  <name>Collect Meta API credentials</name>
  <files>.env.example</files>
  <action>
    Create a `.env.example` file with placeholders for:
    - `WHATSAPP_ACCESS_TOKEN`
    - `PHONE_NUMBER_ID`
    - `WABA_ID` (WhatsApp Business Account ID)
    - `RECIPIENT_PHONE_NUMBER` (Your own number for testing)
    
    Instruction: Ask the user to provide these from their Meta Developer Portal (WhatsApp > Getting Started).
  </action>
  <verify>Test-Path .env.example</verify>
  <done>User has the template for credentials.</done>
</task>

<task type="auto">
  <name>Implement WhatsApp Client</name>
  <files>whatsapp_client.py</files>
  <action>
    Create `whatsapp_client.py` using the `requests` library:
    1. Define a `WhatsAppClient` class.
    2. Implement a `send_test_message` method that calls the Meta Cloud API `messages` endpoint.
    3. Use the `hello_world` template provided by Meta by default for initial testing.
    4. Handle API errors and log the response.
  </action>
  <verify>.\venv\Scripts\python.exe whatsapp_client.py</verify>
  <done>API returns a 200/201 Success status code.</done>
</task>

## Success Criteria
- [ ] Environment variables are correctly mapped.
- [ ] `whatsapp_client.py` can successfully reach Meta's servers.
- [ ] A "Hello World" template message is received on the user's test phone.
