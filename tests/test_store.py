import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from prepare_store import create_manifest, validate_identity, FOUNDATION, RESCAP


class StoreManifestTests(unittest.TestCase):
    def identity(self):
        return {"name": "12345.Test.PixelArtStudio", "publisher": "CN=00000000-0000-0000-0000-000000000000",
                "publisher_display_name": "Editor & autor", "display_name": "PixelArt Studio",
                "version": "1.0.0.0"}

    def test_example_cannot_be_packaged_as_real_identity(self):
        example = Path(__file__).resolve().parent.parent / "store/identity.example.json"
        with self.assertRaises(ValueError):
            validate_identity(json.loads(example.read_text(encoding="utf-8")))

    def test_identity_and_publisher_survive_xml_serialization(self):
        identity = self.identity()
        root = ET.fromstring(ET.tostring(create_manifest(identity).getroot()))
        tag = lambda name: f"{{{FOUNDATION}}}{name}"
        self.assertEqual(root.find(tag("Identity")).get("Name"), identity["name"])
        self.assertEqual(root.find(tag("Identity")).get("Publisher"), identity["publisher"])
        self.assertEqual(root.find(f"{tag('Properties')}/{tag('PublisherDisplayName')}").text,
                         identity["publisher_display_name"])
        application = root.find(f"{tag('Applications')}/{tag('Application')}")
        self.assertEqual(application.get("Executable"), "App\\PixelArtStudio.exe")
        self.assertEqual([item.get("Name") for item in root.findall(
            f"{tag('Capabilities')}/{{{RESCAP}}}Capability")], ["runFullTrust"])

    def test_reject_invalid_version_and_missing_values(self):
        for changes in ({"version": "1.0.0.1"}, {"version": "1.0"}, {"version": "65536.0.0.0"},
                        {"publisher": ""}, {"name": "with spaces"}, {"display_name": ""}):
            with self.assertRaises(ValueError):
                validate_identity(self.identity() | changes)
