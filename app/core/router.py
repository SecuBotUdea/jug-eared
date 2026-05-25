import logging
import httpx
from app.config import settings
from app.db.repository import MongoTeamRepository
from app.models.alert import IncomingAlert
from app.models.notification import DiscordNotification
from app.models.rescan import RescanRequest

logger = logging.getLogger("jug-eared.router")


def extract_repository(alert_id: str) -> str:
    """
    alert_id format: {source}-{owner}-{repo}-{number}
    ej: "dependabot-pangoaguirre-learndependabot-12"
    Retorna "{owner}-{repo}", ej: "pangoaguirre-learndependabot"
    """
    parts = alert_id.split("-")
    return "-".join(parts[1:-1])


async def route_alert(alert: IncomingAlert, repo: MongoTeamRepository, user_id: str | None = None) -> None:
    repository = extract_repository(alert.alert_id)
    team = await repo.get_by_repository(repository)

    if not team:
        logger.warning("No team found for repository=%s alert_id=%s", repository, alert.alert_id)
        return

    secubot_payload = {
        **alert.model_dump(mode="json"),
        "team_id": team.team_id,
        "team_name": team.name,
    }

    effective_user_id = user_id or await repo.consume_rescan_user(alert.alert_id)
    secubot_payload["user_id"] = effective_user_id
    logger.info(
        "Secubot user_id resolution | alert_id=%s incoming_user_id=%r resolved_user_id=%r source=%s",
        alert.alert_id,
        user_id,
        effective_user_id,
        "arg" if user_id is not None else "rescan_cache" if effective_user_id is not None else "missing",
    )
    if effective_user_id is None:
        logger.warning("Alert routed without user_id | alert_id=%s team=%s", alert.alert_id, team.team_id)

    discord_payload = DiscordNotification(
        alert_id=alert.alert_id,
        title=alert.title,
        severity=alert.severity,
        status=alert.status,
        component=alert.component,
        location=alert.location,
        source_type=alert.source_type,
        team_id=team.team_id,
        team_name=team.name,
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(settings.secubot_url, json=secubot_payload)
        logger.info("Alert routed to secubot | alert_id=%s team=%s", alert.alert_id, team.team_id)

        await client.post(settings.discord_url, json=discord_payload.model_dump(mode="json"))
        logger.info("Notification sent to discord | alert_id=%s team=%s", alert.alert_id, team.team_id)


async def route_rescan(payload: RescanRequest, repo: MongoTeamRepository) -> None:
    repository = extract_repository(payload.alert_id)
    team = await repo.get_by_repository(repository)

    if not team:
        logger.warning("No team found for repository=%s alert_id=%s", repository, payload.alert_id)
        return

    logger.info(
        "Rescan request received | alert_id=%s user_id=%r guild_id=%s action=%s",
        payload.alert_id,
        payload.user_id,
        payload.guild_id,
        payload.action,
    )

    await repo.save_rescan_user(payload.alert_id, payload.user_id, payload.guild_id)
    logger.info(
        "Rescan user cached | alert_id=%s user_id=%r guild_id=%s",
        payload.alert_id,
        payload.user_id,
        payload.guild_id,
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            f"{settings.parser_url}/{payload.alert_id}",
            headers={"X-Github-Token": team.github_token},
        )
        logger.info("Rescan routed to parser | alert_id=%s team=%s", payload.alert_id, team.team_id)