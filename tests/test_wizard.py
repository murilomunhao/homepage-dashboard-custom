import tempfile
import unittest
from pathlib import Path

from installer.generator import export_config, preview_config, render_services, render_settings, render_widgets
from installer.models import InstallerConfig, ServiceItem
from installer.validator import validate_config
from installer.wizard import render_prerequisite_notes, review_config, suggest_icon


class TestInstallerWizard(unittest.TestCase):
    def test_suggest_icon_for_common_services(self):
        self.assertEqual(suggest_icon("portainer"), "portainer")
        self.assertEqual(suggest_icon("glances"), "glances")
        self.assertEqual(suggest_icon("n8n"), "n8n")

    def test_render_prerequisite_notes_mentions_token_and_installation(self):
        notes = render_prerequisite_notes(use_glances=True, use_portainer=True)
        text = notes.lower()
        self.assertIn("glances", text)
        self.assertIn("instalado", text)
        self.assertIn("token", text)
        self.assertIn("portainer", text)

    def test_render_settings_uses_homepage_layout_style(self):
        config = InstallerConfig(dashboard_name="Lab", title="Lab", use_glances=True, use_portainer=True)
        rendered = render_settings(config)
        self.assertIn("theme:", rendered)
        self.assertIn("dark", rendered)
        self.assertIn("layout:", rendered)
        self.assertIn("Ferramentas:", rendered)

    def test_export_config_creates_homepage_files(self):
        config = InstallerConfig(
            dashboard_name="Lab",
            title="Lab Dashboard",
            use_glances=True,
            use_portainer=True,
            services=[ServiceItem(name="Home Assistant", url="http://localhost:8123", description="Casa", category="Ferramentas")],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            export_config(config, output_dir=tmpdir)
            files = {path.name for path in Path(tmpdir).iterdir()}
            self.assertIn("settings.yaml", files)
            self.assertIn("services.yaml", files)
            self.assertIn("widgets.yaml", files)
            self.assertIn("custom.css", files)

    def test_validate_config_accepts_valid_configuration(self):
        config = InstallerConfig(
            dashboard_name="Lab",
            title="Lab Dashboard",
            use_portainer=True,
            use_glances=True,
            services=[ServiceItem(name="Home Assistant", url="http://localhost:8123", category="Ferramentas")],
        )
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_preview_config_contains_summary(self):
        config = InstallerConfig(
            dashboard_name="Lab",
            title="Lab Dashboard",
            use_glances=True,
            use_portainer=True,
            services=[ServiceItem(name="Home Assistant", url="http://localhost:8123", category="Ferramentas")],
        )
        preview = preview_config(config)
        self.assertIn("Lab Dashboard", preview)
        self.assertIn("Glances", preview)
        self.assertIn("Portainer", preview)

    def test_review_config_contains_editable_summary(self):
        config = InstallerConfig(
            dashboard_name="Lab",
            title="Lab Dashboard",
            use_glances=True,
            use_portainer=False,
            services=[ServiceItem(name="Home Assistant", url="http://localhost:8123", category="Ferramentas")],
        )
        review = review_config(config)
        self.assertIn("Resumo final", review)
        self.assertIn("Ferramentas", review)
        self.assertIn("Home Assistant", review)

    def test_export_config_creates_copy_ready_folder(self):
        config = InstallerConfig(
            dashboard_name="Lab",
            title="Lab Dashboard",
            use_glances=False,
            use_portainer=False,
            services=[ServiceItem(name="Home Assistant", url="http://localhost:8123", category="Ferramentas")],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            export_config(config, output_dir=tmpdir)
            root_files = {path.name for path in Path(tmpdir).iterdir()}
            config_dir = Path(tmpdir) / "config"
            self.assertIn("settings.yaml", root_files)
            self.assertTrue(config_dir.exists())
            self.assertIn("services.yaml", {path.name for path in config_dir.iterdir()})


if __name__ == "__main__":
    unittest.main()
