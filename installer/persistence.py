from __future__ import annotations

import json
from pathlib import Path

from .models import InstallerConfig, ServiceItem


def config_to_dict(config: InstallerConfig) -> dict:
    return {
        "dashboard_name": config.dashboard_name,
        "title": config.title,
        "theme": config.theme,
        "use_glances": config.use_glances,
        "use_portainer": config.use_portainer,
        "glances_url": config.glances_url,
        "portainer_url": config.portainer_url,
        "services": [
            {
                "name": service.name,
                "url": service.url,
                "description": service.description,
                "icon": service.icon,
                "category": service.category,
                "container": service.container,
                "widget_type": service.widget_type,
                "widget_url": service.widget_url,
                "widget_metric": service.widget_metric,
            }
            for service in config.services
        ],
    }


def config_from_dict(data: dict) -> InstallerConfig:
    return InstallerConfig(
        dashboard_name=data.get("dashboard_name", "homepage"),
        title=data.get("title", "Homepage"),
        theme=data.get("theme", "dark"),
        use_glances=bool(data.get("use_glances", False)),
        use_portainer=bool(data.get("use_portainer", False)),
        glances_url=data.get("glances_url", "http://localhost:61208"),
        portainer_url=data.get("portainer_url", "http://localhost:9000"),
        services=[
            ServiceItem(
                name=item.get("name", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                icon=item.get("icon", "mdi-link"),
                category=item.get("category", "Ferramentas"),
                container=item.get("container"),
                widget_type=item.get("widget_type"),
                widget_url=item.get("widget_url"),
                widget_metric=item.get("widget_metric"),
            )
            for item in data.get("services", [])
        ],
    )


def save_config(config: InstallerConfig, state_path: str = ".homepage-installer-state.json") -> Path:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config_to_dict(config), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_config(state_path: str = ".homepage-installer-state.json") -> InstallerConfig | None:
    path = Path(state_path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return config_from_dict(data)
