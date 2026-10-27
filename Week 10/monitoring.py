import logging
import os

logger = logging.getLogger("week10_agent.monitoring")


def configure_monitoring() -> bool:
    """Enable Azure Monitor when a connection string is configured."""
    connection_string = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING"
    )

    if not connection_string:
        logger.info(
            "Azure Monitor disabled: no connection string configured."
        )
        return False

    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="week10_agent",
        )
        logger.info("Azure Monitor configured.")
        return True
    except Exception:
        # Avoid logging the connection string or exception details.
        logger.error("Azure Monitor configuration failed.")
        return False
