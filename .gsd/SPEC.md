# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
A daily, automated "heartbeat" service that provides the USD/COP exchange rate (TRM) to WhatsApp groups every morning at 7:00 AM. This keeps users informed about currency fluctuations using a robust, cloud-native approach (GitHub Actions) and official APIs.

## Goals
1. **Automated Scraping**: Retrieve the latest USD/COP rate from `dolar-colombia.com` daily.
2. **Reliable Broadcasting**: Use the official Meta WhatsApp Business Cloud API to send notifications.
3. **Low-Maintenance Deployment**: Host the service for free using GitHub Actions.
4. **Configurability**: Allow easy modification of the run time and target group IDs.

## Non-Goals (Out of Scope)
- **Historical Database**: We won't build a complex database for tracking trends (v1).
- **Web UI**: No front-end for users; management happens through config files and GitHub.
- **Bi-directional Bot**: The bot is push-only (notifications) for now, not a chatbot that answers questions.

## Users
- **nposadaa (Admin)**: Manages the script and configuration.
- **WhatsApp Group Members**: Receive the daily briefing.

## Constraints
- **Meta Business Verification**: Official WhatsApp Group Messaging requires a verified Meta Business Account. If your account is unverified, we may need to pivot to a 1-on-1 direct message notification model or investigate alternatives.
- **Message Templates**: Proactive (first) notifications require an approved Message Template from Meta.
- **Execution Schedule**: GitHub Actions runs on a cron schedule with a free-tier limit of 2,000 minutes per month (more than enough for this project).
- **Official API only**: We avoid "grey market" libraries to prevent phone number bans.

## Success Criteria
- [ ] Script successfully retrieves the TRM value from the target website.
- [ ] A test message is sent to a WhatsApp group via the API.
- [ ] GitHub Actions triggers the script automatically at the scheduled time.
- [ ] The notification message arrives in the WhatsApp group daily without manual intervention.
