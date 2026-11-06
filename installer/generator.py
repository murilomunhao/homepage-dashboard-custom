from __future__ import annotations

from pathlib import Path

from .models import InstallerConfig

DEFAULT_CATEGORY_ORDER = [
    "Ferramentas",
    "Infraestrutura",
    "Projetos",
    "Monitoramento",
]


def _quote_value(value: str) -> str:
    if value is None:
        return '""'
    value = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{value}"'


def category_sequence(config: InstallerConfig):
    service_categories = [service.category for service in config.services]
    categories = []
    seen = set()

    for name in DEFAULT_CATEGORY_ORDER:
        has_service = name in service_categories
        is_required = (
            (name == "Infraestrutura" and config.use_portainer)
            or (name == "Monitoramento" and config.use_glances)
            or (not config.services and name in DEFAULT_CATEGORY_ORDER)
        )
        if has_service or is_required:
            if name not in seen:
                categories.append(name)
                seen.add(name)

    for service in config.services:
        if service.category not in seen:
            categories.append(service.category)
            seen.add(service.category)

    return categories or ["Ferramentas"]


def render_settings(config: InstallerConfig) -> str:
    categories = category_sequence(config)
    lines = [
        f"title: {_quote_value(config.title)}",
        "background:",
        "  blur: \"sm\"",
        f"theme: {_quote_value(config.theme)}",
        "",
        "layout:",
    ]

    for category in categories:
        columns = 4 if category in {"Ferramentas", "Monitoramento"} else 3
        lines.append(f"  {category}:")
        lines.append("    style: row")
        lines.append(f"    columns: {columns}")

    return "\n".join(lines) + "\n"


def render_services(config: InstallerConfig) -> str:
    categories = category_sequence(config)
    lines = []

    for category in categories:
        if category == "Infraestrutura" and config.use_portainer:
            lines.append("- Infraestrutura:")
            lines.append("    - Portainer:")
            lines.append("        icon: portainer")
            lines.append(f"        href: {_quote_value(config.portainer_url)}")
            lines.append("        description: \"Docker Web GUI\"")
            lines.append("        container: infra_portainer")
            lines.append("        widget:")
            lines.append("            type: portainer")
            lines.append(f"            url: {_quote_value(config.portainer_url)}")
            lines.append("            env: 6")
            lines.append("            key: \"{{HOMEPAGE_VAR_PORTAINER_API_KEY}}\"")
            continue

        if category == "Monitoramento" and config.use_glances:
            lines.append("- Monitoramento:")
            lines.append("    - CPU:")
            lines.append("        icon: mdi-cpu-64")
            lines.append("        widget:")
            lines.append("          type: glances")
            lines.append(f"          url: {_quote_value(config.glances_url)}")
            lines.append("          version: 4")
            lines.append("          metric: cpu")
            lines.append("          chart: false")
            continue

        lines.append(f"- {category}:")
        service_items = [service for service in config.services if service.category == category]
        if not service_items:
            continue

        for service in service_items:
            lines.append(f"    - {service.name}:")
            lines.append(f"        icon: {service.icon}")
            lines.append(f"        href: {_quote_value(service.url)}")
            lines.append(f"        description: {_quote_value(service.description)}")
            if service.container:
                lines.append(f"        container: {service.container}")
            if service.widget_type:
                lines.append("        widget:")
                lines.append(f"            type: {service.widget_type}")
                if service.widget_url:
                    lines.append(f"            url: {_quote_value(service.widget_url)}")
                if service.widget_metric:
                    lines.append(f"            metric: {_quote_value(service.widget_metric)}")

    return "\n".join(lines).rstrip() + "\n"


def render_widgets(config: InstallerConfig) -> str:
    lines = [
        "- logo:",
        "    icon: \"mdi-cpu-64-bit\"",
        "",
        "- greeting:",
        f"    text: {_quote_value(config.title)}",
        "    text_size: 1.5rem",
        "",
        "- datetime:",
        "    text_size: 2.5rem",
        "    format:",
        "      dateStyle: short",
        "",
        "- datetime:",
        "    text_size: 2.5rem",
        "    format:",
        "      timeStyle: medium",
        "      hourCycle: h23",
    ]

    if config.use_glances:
        lines.extend([
            "",
            "- glances:",
            "    url: " + config.glances_url,
            "    version: 4",
            "    cputemp: true",
            "    cpu: true",
            "    mem: true",
            "    disk: /",
            "    uptime: true",
        ])

    return "\n".join(lines) + "\n"


def render_css() -> str:
    return """body {
  background: #0f172a;
}

.card {
  border-radius: 16px;
}
"""


def environment_checklist(config: InstallerConfig) -> str:
    lines = [
        "Regras do ambiente:",
        "- Glances precisa estar instalado e acessível pela URL configurada.",
        "- Portainer precisa estar instalado e a chave da API deve estar em HOMEPAGE_VAR_PORTAINER_API_KEY.",
        "- A URL de cada serviço deve apontar para o host e porta corretos da sua rede local ou nuvem.",
        "- Os nomes dos ícones devem seguir a convenção do Homepage ou usar um ícone compatível com o catálogo.",
    ]

    if not config.use_glances and not config.use_portainer:
        lines.append("- Nenhuma integração externa foi selecionada; o dashboard será basicamente um conjunto de links.")

    return "\n".join(lines) + "\n"


def preview_config(config: InstallerConfig) -> str:
    lines = [
        "=== Preview do dashboard ===",
        f"Nome: {config.dashboard_name}",
        f"Título: {config.title}",
        f"Tema: {config.theme}",
        "",
        "Integrações:",
        f"- Glances: {'sim' if config.use_glances else 'não'}",
        f"  URL: {config.glances_url if config.use_glances else 'n/a'}",
        f"- Portainer: {'sim' if config.use_portainer else 'não'}",
        f"  URL: {config.portainer_url if config.use_portainer else 'n/a'}",
        "",
        "Serviços:",
    ]

    if not config.services:
        lines.append("- Nenhum serviço adicionado.")
    else:
        for service in config.services:
            lines.append(f"- {service.name} ({service.category}) -> {service.url}")

    lines.extend([
        "",
        "Observações:",
        "- Se Portainer for usado, configure HOMEPAGE_VAR_PORTAINER_API_KEY antes de abrir o dashboard.",
        "- Se Glances for usado, confirme que a URL está acessível e os sensores existem.",
        "",
        environment_checklist(config),
    ])

    return "\n".join(lines) + "\n"


def export_config(config: InstallerConfig, output_dir: str = "generated") -> None:
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    config_dir = folder / "config"
    config_dir.mkdir(exist_ok=True)

    files = {
        "settings.yaml": render_settings(config),
        "services.yaml": render_services(config),
        "widgets.yaml": render_widgets(config),
        "custom.css": render_css(),
    }

    for filename, content in files.items():
        (folder / filename).write_text(content, encoding="utf-8")
        (config_dir / filename).write_text(content, encoding="utf-8")

    notes = [
        "Checklist do instalador:",
        "- Para o Portainer, configure a variável HOMEPAGE_VAR_PORTAINER_API_KEY.",
        "- Para o Glances, confirme que a URL do serviço está disponível e os sensores esperados estão ativos.",
        "- Ajuste os ícones e endpoints conforme o ambiente real do usuário.",
        "- Copie o conteúdo da pasta config para a pasta config do teu Homepage.",
        "",
        environment_checklist(config),
    ]
    (folder / "README.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    (config_dir / "README.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")

    return None


def write_output(config: InstallerConfig, output_dir: str = "generated") -> None:
    export_config(config, output_dir=output_dir)
    print(f"\nArquivos gerados em: {Path(output_dir).resolve()}")
