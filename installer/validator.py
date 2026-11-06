from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .models import InstallerConfig


def is_valid_url(value: str) -> bool:
    if not value or not value.strip():
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def check_endpoint(url: str) -> bool:
    if not is_valid_url(url):
        return False

    try:
        request = Request(url, method="HEAD", headers={"User-Agent": "homepage-installer"})
        with urlopen(request, timeout=5) as response:
            return response.status < 500
    except (HTTPError, URLError, ValueError):
        try:
            request = Request(url, method="GET", headers={"User-Agent": "homepage-installer"})
            with urlopen(request, timeout=5) as response:
                return response.status < 500
        except (HTTPError, URLError, ValueError):
            return False


def validation_warnings(config: InstallerConfig):
    warnings = []

    if config.use_portainer:
        if not check_endpoint(config.portainer_url):
            warnings.append("Portainer: a URL não respondeu. Verifique a instância e a variável HOMEPAGE_VAR_PORTAINER_API_KEY.")
        else:
            warnings.append("Portainer: confirme que o token da API está em HOMEPAGE_VAR_PORTAINER_API_KEY antes de abrir o dashboard.")

    if config.use_glances:
        if not check_endpoint(config.glances_url):
            warnings.append("Glances: a URL não respondeu. Confirme que o serviço está instalado e acessível.")
        else:
            warnings.append("Glances: confirme que os sensores esperados existem para CPU, memória, rede, disco e uptime.")

    if not config.services:
        warnings.append("Nenhum serviço foi adicionado. O dashboard pode ficar vazio se você não incluir links ou widgets.")

    duplicate_names = {name for name in [s.name for s in config.services] if [s.name for s in config.services].count(name) > 1}
    if duplicate_names:
        warnings.append(f"Serviços duplicados detectados: {', '.join(sorted(duplicate_names))}.")

    return warnings


def validate_config(config: InstallerConfig):
    errors = []

    if not config.dashboard_name or not config.dashboard_name.strip():
        errors.append("O nome do dashboard não pode ficar vazio.")

    if not config.title or not config.title.strip():
        errors.append("O título do dashboard não pode ficar vazio.")

    if config.theme not in {"dark", "light"}:
        errors.append("O tema deve ser 'dark' ou 'light'.")

    if config.use_glances and not is_valid_url(config.glances_url):
        errors.append("A URL do Glances é inválida.")

    if config.use_portainer and not is_valid_url(config.portainer_url):
        errors.append("A URL do Portainer é inválida.")

    seen_names = set()
    for service in config.services:
        if not service.name or not service.name.strip():
            errors.append("Existe um serviço sem nome.")
            continue
        if service.name in seen_names:
            errors.append(f"O serviço '{service.name}' foi adicionado mais de uma vez.")
        seen_names.add(service.name)

        if not service.category or not service.category.strip():
            errors.append(f"O serviço '{service.name}' não possui categoria válida.")
        if not service.icon or not service.icon.strip():
            errors.append(f"O serviço '{service.name}' não possui ícone válido.")
        if not is_valid_url(service.url):
            errors.append(f"A URL do serviço '{service.name}' é inválida.")

    return errors
