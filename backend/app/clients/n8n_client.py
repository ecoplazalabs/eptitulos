import httpx
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class N8nWebhookError(Exception):
    """Raised when the n8n webhook call fails."""


async def trigger_sunarp_analysis(
    analysis_id: str,
    oficina: str,
    partida: str,
    area_registral: str,
) -> bool:
    """
    Trigger the n8n workflow to analyze a SUNARP partida.

    Raises N8nWebhookError if the webhook call fails.
    """
    url = settings.n8n_webhook_url
    payload = {
        "analysis_id": analysis_id,
        "oficina": oficina,
        "partida": partida,
        "area_registral": area_registral,
    }

    log = logger.bind(analysis_id=analysis_id, oficina=oficina, partida=partida)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"X-API-Key": settings.n8n_api_key},
            )
            response.raise_for_status()
            log.info("n8n_webhook_triggered", status_code=response.status_code)
            return True
    except httpx.TimeoutException as exc:
        log.error("n8n_webhook_timeout", error=str(exc))
        raise N8nWebhookError("n8n webhook timed out") from exc
    except httpx.HTTPStatusError as exc:
        log.error(
            "n8n_webhook_http_error",
            status_code=exc.response.status_code,
            error=str(exc),
        )
        raise N8nWebhookError(
            f"n8n webhook returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        log.error("n8n_webhook_request_error", error=str(exc))
        raise N8nWebhookError(f"n8n webhook request failed: {exc}") from exc
