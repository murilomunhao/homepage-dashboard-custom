from __future__ import annotations

from typing import List

from .models import InstallerConfig, ServiceItem

DEFAULT_ICONS = {
    "portainer": "portainer",
    "glances": "glances",
    "n8n": "n8n",
    "docker": "docker",
    "nginx": "nginx",
    "grafana": "grafana",
    "prometheus": "prometheus",
    "wordpress": "wordpress",
    "laravel": "laravel",
    "home-assistant": "mdi-home-assistant",
    "homeassistant": "mdi-home-assistant",
    "adguard": "adguard-home",
    "proxmox": "proxmox",
    "pihole": "pihole",
    "open-webui": "open-webui",
    "openwebui": "open-webui",
    "traefik": "traefik",
    "nextcloud": "nextcloud",
    "jellyfin": "jellyfin",
}

DEFAULT_CATEGORIES = [
    "Ferramentas",
    "Infraestrutura",
    "Projetos",
    "Monitoramento",
]


def safe_input(prompt: str, default: str = "") -> str:
    try:
        value = input(prompt)
    except EOFError:
        print()
        return default
    return value.strip()


def print_step_header(title: str) -> None:
    print(f"\n=== {title} ===")


def ask_yes_no(prompt: str) -> bool:
    answer = safe_input(f"{prompt} [s/N]: ", "").lower()
    return answer in {"s", "sim", "y", "yes"}


def suggest_icon(service_name: str) -> str:
    normalized = service_name.strip().lower().replace(" ", "-")
    return DEFAULT_ICONS.get(normalized, "mdi-link")


def render_prerequisite_notes(*, use_glances: bool, use_portainer: bool) -> str:
    lines: List[str] = []

    if use_glances:
        lines.append(
            "Glances: precisa estar instalado e acessível. Confirme que a URL do serviço está online "
            "e que os sensores esperados estão disponíveis para CPU, memória, rede, disco e uptime."
        )

    if use_portainer:
        lines.append(
            "Portainer: precisa estar instalado e ativo. Você também precisará do token da API e deve "
            "guardá-lo em uma variável de ambiente, como HOMEPAGE_VAR_PORTAINER_API_KEY, em vez de deixar "
            "o valor no arquivo de configuração."
        )

    if not lines:
        return "Sem integrações opcionais selecionadas."

    return "\n".join(f"- {line}" for line in lines)


def review_config(config: InstallerConfig) -> str:
    lines = [
        "Resumo final",
        f"- Dashboard: {config.dashboard_name}",
        f"- Título: {config.title}",
        f"- Tema: {config.theme}",
        f"- Glances: {'sim' if config.use_glances else 'não'}",
        f"- Portainer: {'sim' if config.use_portainer else 'não'}",
        "",
        "Categorias:",
    ]

    categories = []
    for service in config.services:
        if service.category not in categories:
            categories.append(service.category)
    if not categories:
        lines.append("- Nenhuma categoria definida")
    else:
        lines.extend(f"- {category}" for category in categories)

    lines.append("")
    lines.append("Serviços:")
    if not config.services:
        lines.append("- Nenhum serviço adicionado")
    else:
        for service in config.services:
            lines.append(f"- {service.name} ({service.category}) -> {service.url}")

    return "\n".join(lines) + "\n"


def remove_service(config: InstallerConfig) -> None:
    if not config.services:
        print("Nenhum serviço para remover.")
        return

    for index, service in enumerate(config.services, start=1):
        print(f"{index}. {service.name} ({service.category})")

    choice = safe_input("Selecione o serviço para remover: ", "")
    try:
        service_index = int(choice) - 1
        removed = config.services.pop(service_index)
        print(f"Serviço removido: {removed.name}")
    except (ValueError, IndexError):
        print("Seleção inválida.")


def edit_review_config(config: InstallerConfig):
    print(review_config(config))
    while True:
        action = safe_input("Escolha uma ação [A]provar / [E]ditar / [R]emover / [C]ancelar: ", "A").lower()
        if action in {"a", "aprovar", "s", "sim", "y"}:
            return True
        if action in {"c", "cancelar", "q", "quit"}:
            return False
        if action in {"r", "remover"}:
            remove_service(config)
            print(review_config(config))
            continue
        if action in {"e", "editar"}:
            field = safe_input(
                "Qual campo editar? [1] nome [2] titulo [3] tema [4] glances [5] portainer [6] serviços: ",
                "0",
            )
            if field == "1":
                config.dashboard_name = safe_input("Novo nome do dashboard: ", config.dashboard_name) or config.dashboard_name
            elif field == "2":
                config.title = safe_input("Novo título: ", config.title) or config.title
            elif field == "3":
                config.theme = safe_input("Novo tema [dark/light]: ", config.theme) or config.theme
            elif field == "4":
                config.use_glances = ask_yes_no("Ativar Glances?")
                if config.use_glances:
                    config.glances_url = safe_input("URL do Glances: ", config.glances_url) or config.glances_url
            elif field == "5":
                config.use_portainer = ask_yes_no("Ativar Portainer?")
                if config.use_portainer:
                    config.portainer_url = safe_input("URL do Portainer: ", config.portainer_url) or config.portainer_url
            elif field == "6":
                if not config.services:
                    print("Nenhum serviço para editar.")
                else:
                    for index, service in enumerate(config.services, start=1):
                        print(f"{index}. {service.name} ({service.category})")
                    choice = safe_input("Selecione o serviço para editar: ", "")
                    try:
                        service_index = int(choice) - 1
                        service = config.services[service_index]
                        service.name = safe_input(f"Novo nome para '{service.name}': ", service.name) or service.name
                        service.url = safe_input(f"Nova URL para '{service.name}': ", service.url) or service.url
                        service.category = safe_input(f"Nova categoria para '{service.name}': ", service.category) or service.category
                    except (ValueError, IndexError):
                        print("Seleção inválida.")
            else:
                print("Opção inválida.")
            print(review_config(config))
        else:
            print("Opção inválida. Tente novamente.")


def collect_categories() -> List[str]:
    print_step_header("Etapa 3: categorias")
    if ask_yes_no("Deseja usar as categorias padrão do dashboard?"):
        print("Categorias padrão selecionadas:", ", ".join(DEFAULT_CATEGORIES))
        return list(DEFAULT_CATEGORIES)

    print("Digite as categorias desejadas. Deixe em branco para terminar.")
    categories: List[str] = []
    while True:
        category = safe_input("Categoria: ", "")
        if not category:
            break
        categories.append(category)

    return categories or list(DEFAULT_CATEGORIES)


def collect_service_items(categories: List[str]) -> List[ServiceItem]:
    services: List[ServiceItem] = []

    print_step_header("Etapa 4: serviços")

    for category in categories:
        print(f"\n=== Categoria: {category} ===")
        if not ask_yes_no(f"Deseja adicionar serviços em '{category}'?"):
            continue

        while True:
            name = safe_input("Nome do serviço: ", "")
            if not name:
                break

            url = safe_input("URL do serviço: ", "")
            description = safe_input("Descrição: ", name) or name
            icon = safe_input(f"Ícone para '{name}' [padrão: {suggest_icon(name)}]: ", suggest_icon(name))
            if not icon:
                icon = suggest_icon(name)

            services.append(
                ServiceItem(
                    name=name,
                    url=url,
                    description=description,
                    icon=icon,
                    category=category,
                )
            )
            print(f"Serviço adicionado: {name} ({category})")

            if not ask_yes_no("Adicionar outro serviço nesta categoria?"):
                break

    return services


def collect_user_input() -> InstallerConfig:
    print("==== Assistente de configuração do Homepage ====")
    print_step_header("Etapa 1: dados do dashboard")
    dashboard_name = safe_input("Nome do dashboard: ", "homepage") or "homepage"
    title = safe_input("Título exibido no cabeçalho: ", dashboard_name.title()) or dashboard_name.title()
    theme = safe_input("Tema [dark/light]: ", "dark").lower() or "dark"

    print_step_header("Etapa 2: integrações")
    use_glances = ask_yes_no("Deseja usar Glances para monitoramento?")
    use_portainer = ask_yes_no("Deseja usar Portainer?")

    if use_glances or use_portainer:
        print("\nPré-requisitos:")
        print(render_prerequisite_notes(use_glances=use_glances, use_portainer=use_portainer))

    glances_url = "http://localhost:61208"
    if use_glances:
        glances_url = safe_input("URL do Glances [http://localhost:61208]: ", glances_url) or glances_url

    portainer_url = "http://localhost:9000"
    if use_portainer:
        portainer_url = safe_input("URL do Portainer [http://localhost:9000]: ", portainer_url) or portainer_url

    categories = collect_categories()
    services = collect_service_items(categories)

    return InstallerConfig(
        dashboard_name=dashboard_name,
        title=title,
        theme=theme,
        use_glances=use_glances,
        use_portainer=use_portainer,
        glances_url=glances_url,
        portainer_url=portainer_url,
        services=services,
    )
