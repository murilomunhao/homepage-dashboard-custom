from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ServiceItem:
    name: str
    url: str
    description: str = ""
    icon: str = "mdi-link"
    category: str = "Ferramentas"
    container: Optional[str] = None
    widget_type: Optional[str] = None
    widget_url: Optional[str] = None
    widget_metric: Optional[str] = None


@dataclass
class InstallerConfig:
    dashboard_name: str
    title: str
    theme: str = "dark"
    use_glances: bool = False
    use_portainer: bool = False
    glances_url: str = "http://localhost:61208"
    portainer_url: str = "http://localhost:9000"
    services: List[ServiceItem] = field(default_factory=list)
