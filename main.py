import os
import sys
import logging
import argparse
from datetime import datetime, timezone, timedelta
from scraper import scrape_trm, scrape_spot_market
from broadcaster import run_broadcaster

# --- State files (per-edition deduplication) ---
LAST_SUCCESS_FILE_MORNING = ".gsd/last_success_morning.date"
LAST_SUCCESS_FILE_CLOSING = ".gsd/last_success_closing.date"

# Backward-compatible alias kept so any external scripts referencing the old
# single-file name still find a file to check.
LAST_SUCCESS_FILE_LEGACY  = ".gsd/last_success.date"

LAST_FAIL_NOTIFICATION    = ".gsd/last_fail_notify.date"

COT_TZ = timezone(timedelta(hours=-5), name="America/Bogota")

def get_cot_now():
    return datetime.now(COT_TZ)

# --- Logging Setup ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"notifier_{get_cot_now().strftime('%Y-%m-%d')}.log")

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding="utf-8")
    ]
)
logger = logging.getLogger("trm_notifier")

# ---------------------------------------------------------------------------
# Edition helpers
# ---------------------------------------------------------------------------

def _success_file_for(edition: str) -> str:
    """Return the per-edition dedup state file path."""
    return LAST_SUCCESS_FILE_MORNING if edition == "morning" else LAST_SUCCESS_FILE_CLOSING


def _already_sent_today(edition: str, today_str: str) -> bool:
    """Return True if the given edition was already broadcast successfully today."""
    path = _success_file_for(edition)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip() == today_str
    return False


def _record_success(edition: str, today_str: str):
    """Write today's date to the edition-specific success file."""
    path = _success_file_for(edition)
    with open(path, "w") as f:
        f.write(today_str)
    # Keep legacy file in sync for backward compatibility (morning only)
    if edition == "morning":
        with open(LAST_SUCCESS_FILE_LEGACY, "w") as f:
            f.write(today_str)


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------

def build_morning_message(trm_data: dict, is_friday: bool) -> str:
    """Build the morning TRM broadcast message."""
    trm_value    = trm_data["trm"]
    previous_trm = trm_data.get("previous_trm", trm_value)
    trm_date     = trm_data["date"]

    # Staleness check
    today_str = get_cot_now().strftime("%Y-%m-%d")
    stale_disclaimer = ""
    if trm_date != today_str:
        logger.warning(f"TRM data is stale! Site date: {trm_date}, Today: {today_str}")
        stale_disclaimer = f"\n\n⚠️ _Datos del {trm_date} (sitio no actualizado al momento de consulta)_"

    # Trend
    if trm_value > previous_trm:
        trend_emoji, sign = "📈", "+"
    elif trm_value < previous_trm:
        trend_emoji, sign = "📉", "-"
    else:
        trend_emoji, sign = "➖", ""

    delta = abs(trm_value - previous_trm)
    delta_str = f" ({sign} ${delta:,.2f})" if delta > 0 else ""

    message_text = (
        f"{trend_emoji} *TRM Oficial - {trm_date}*\n\n"
        f"💵 Valor: ${trm_value:,.2f} COP{delta_str}. "
        f"Fuente: www.superfinanciera.gov.co{stale_disclaimer}"
    )

    # Friday Weekly Intelligence Summary (morning only)
    if is_friday:
        logger.info("Friday detected — fetching weekly TRM data...")
        weekly_data = scrape_trm(limit=7)
        if "weekly_max" in weekly_data:
            wk_max    = weekly_data["weekly_max"]
            wk_min    = weekly_data["weekly_min"]
            wk_change = weekly_data["weekly_change"]
            wk_pct    = weekly_data["weekly_change_pct"]

            if wk_change > 0:
                wk_trend, wk_sign = "📈", "+"
            elif wk_change < 0:
                wk_trend, wk_sign = "📉", "-"
            else:
                wk_trend, wk_sign = "➖", ""

            weekly_block = (
                f"\n\n📊 *Resumen Semanal TRM*\n"
                f"🔹 Máximo semana: ${wk_max:,.2f} COP\n"
                f"🔹 Mínimo semana: ${wk_min:,.2f} COP\n"
                f"{wk_trend} Variación semanal: {wk_sign}${abs(wk_change):,.2f} ({wk_pct:+.2f}%)"
            )
            message_text += weekly_block
        else:
            logger.warning("Weekly data unavailable — skipping Friday summary block.")

    return message_text


def build_closing_message(spot_data: dict) -> str:
    """Build the 1:00 PM market close broadcast message."""
    cierre   = spot_data["cierre"]
    apertura = spot_data["apertura"]
    minimo   = spot_data["minimo"]
    maximo   = spot_data["maximo"]
    change   = spot_data["change"]
    pct      = spot_data["change_pct"]
    fecha    = spot_data.get("fecha", "")

    if change > 0:
        trend_emoji, sign = "📈", "+"
    elif change < 0:
        trend_emoji, sign = "📉", "-"
    else:
        trend_emoji, sign = "➖", ""

    # Date label: prefer API-provided fecha, fall back to COT today
    date_label = fecha if fecha else get_cot_now().strftime("%Y-%m-%d")

    message_text = (
        f"{trend_emoji} *Cierre Mercado USD/COP - {date_label}*\n\n"
        f"💵 Cierre: ${cierre:,.2f} COP ({sign}{pct:+.2f}% vs apertura)\n"
        f"🔼 Máximo: ${maximo:,.2f} COP\n"
        f"🔽 Mínimo: ${minimo:,.2f} COP\n"
        f"📊 Apertura: ${apertura:,.2f} COP\n\n"
        f"Fuente: SET-ICAP (proxy.icap.com.co)"
    )
    return message_text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="TRM Notifier — Daily USD/COP Broadcaster")
    parser.add_argument(
        "--edition",
        choices=["morning", "closing"],
        default="morning",
        help="Which broadcast to run: 'morning' (official TRM) or 'closing' (spot market close). Default: morning."
    )
    parser.add_argument("--headless",   action="store_true", help="Run browser in headless mode (production)")
    parser.add_argument("--discovery",  action="store_true", help="List available WhatsApp chats")
    parser.add_argument("--dry-run",    action="store_true", help="Print message and exit without sending")
    parser.add_argument("--force",      action="store_true", help="Force broadcast even if already sent today")
    parser.add_argument("--friday",     action="store_true", help="Force Friday weekly summary (morning edition, for testing)")
    args = parser.parse_args()

    edition   = args.edition
    today_str = get_cot_now().strftime("%Y-%m-%d")

    logger.info(f"--- Starting TRM Notifier [{edition.upper()} edition] ---")

    # --- Per-edition deduplication guard ---
    if _already_sent_today(edition, today_str) and not args.force:
        logger.info(
            f"[{edition}] Broadcast for {today_str} already completed successfully. "
            "Skipping to avoid double-post (use --force to override)."
        )
        return

    # -----------------------------------------------------------------------
    # MORNING EDITION
    # -----------------------------------------------------------------------
    if edition == "morning":
        logger.info("Scraping TRM data...")
        trm_data = scrape_trm()

        if "error" in trm_data:
            error_msg = trm_data["error"]
            logger.error(f"Error scraping TRM: {error_msg}")

            status_update = (
                f"⚠️ *Aviso de Sistema*\n\n"
                f"La API de la Superfinanciera no responde (Error: {error_msg})."
            )

            if not args.dry_run:
                already_notified = False
                if os.path.exists(LAST_FAIL_NOTIFICATION):
                    with open(LAST_FAIL_NOTIFICATION, "r") as f:
                        if f.read().strip() == today_str:
                            already_notified = True

                if not already_notified:
                    logger.info("Sending API Failure notification...")
                    success, _ = run_broadcaster(status_update, headless=args.headless)
                    if success:
                        with open(LAST_FAIL_NOTIFICATION, "w") as f:
                            f.write(today_str)
                    else:
                        logger.error("Failed to send API Failure notification. Will try again on next run.")
                else:
                    logger.info("API Failure notification already sent today. Skipping redundant notification.")
            else:
                logger.info(f"[Dry Run] Would send failure notification:\n{status_update}")
            return

        is_friday    = get_cot_now().weekday() == 4 or args.friday
        message_text = build_morning_message(trm_data, is_friday)

    # -----------------------------------------------------------------------
    # CLOSING EDITION
    # -----------------------------------------------------------------------
    else:  # closing
        logger.info("Scraping SET-ICAP spot market data...")
        spot_data = scrape_spot_market()

        if "error" in spot_data:
            error_msg = spot_data["error"]
            logger.error(f"Error scraping spot market: {error_msg}")

            status_update = (
                f"⚠️ *Aviso de Sistema*\n\n"
                f"El feed de cierre SET-ICAP no responde (Error: {error_msg})."
            )

            if not args.dry_run:
                logger.info("Sending spot market failure notification...")
                run_broadcaster(status_update, headless=args.headless)
            else:
                logger.info(f"[Dry Run] Would send spot failure notification:\n{status_update}")
            return

        message_text = build_closing_message(spot_data)

    # -----------------------------------------------------------------------
    # Common broadcast path
    # -----------------------------------------------------------------------
    logger.info(f"Prepared Message:\n{message_text}")

    if args.dry_run:
        logger.info("Dry run complete. Exiting without broadcasting.")
        return

    logger.info(f"Invoking Playwright Broadcaster (headless={args.headless})...")
    try:
        success, needs_maintenance = run_broadcaster(
            message_text, headless=args.headless, discovery_mode=args.discovery
        )
    except RuntimeError as e:
        logger.error(f"Broadcaster fatal error: {e}")
        sys.exit(1)

    if success:
        logger.info("Task completed successfully!")
        _record_success(edition, today_str)
        # Clear maintenance flag if it exists
        if os.path.exists(".gsd/needs_maintenance"):
            os.remove(".gsd/needs_maintenance")
    else:
        if needs_maintenance:
            logger.error("Broadcast failed with session issues — marking profile for deep clean and exiting.")
            with open(".gsd/needs_maintenance", "w") as f:
                f.write(get_cot_now().isoformat())
        else:
            logger.error("Broadcast failed due to temporary/interaction issues — exiting without marking for deep clean.")
        sys.exit(1)


if __name__ == "__main__":
    main()
