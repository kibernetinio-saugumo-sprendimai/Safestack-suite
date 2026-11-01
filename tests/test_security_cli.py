"""Regression tests for secret input and untrusted filename output."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    spec = importlib.util.spec_from_file_location("security_cli", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class VaultCliTests(unittest.TestCase):
    def setUp(self):
        self.vault = load("safestack-vault/vault.py")

    def test_stdin_roundtrip_preserves_exact_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            key, vault = Path(tmp) / "key", Path(tmp) / "vault"
            self.vault.create_key(key)
            value = "  dummy secret\nsecond line\n"
            result = subprocess.run([sys.executable, str(ROOT / "safestack-vault/vault.py"), "put", str(vault), str(key), "name", "--stdin"], input=value, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(value, result.stdout + result.stderr)
            self.assertEqual(self.vault.get(vault, key, "name"), value)

    def test_empty_stdin_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            key, vault = Path(tmp) / "key", Path(tmp) / "vault"
            self.vault.create_key(key)
            with patch.object(sys, "stdin", io.StringIO("")):
                self.vault.main(["put", str(vault), str(key), "empty", "--stdin"])
            self.assertEqual(self.vault.get(vault, key, "empty"), "")

    def test_interactive_prompt(self):
        with patch.object(sys.stdin, "isatty", return_value=True), patch.object(self.vault.getpass, "getpass", return_value="dummy") as prompt, patch.object(self.vault, "put") as put:
            self.vault.main(["put", "vault", "key", "name"])
            prompt.assert_called_once()
            put.assert_called_once_with("vault", "key", "name", "dummy")

    def test_noninteractive_requires_explicit_stdin(self):
        with patch.object(sys.stdin, "isatty", return_value=False), patch.object(self.vault, "put") as put, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                self.vault.main(["put", "vault", "key", "name"])
            self.assertEqual(error.exception.code, 2)
            put.assert_not_called()

    def test_rejects_legacy_secret_without_echo(self):
        for value in ["dummy-argv-secret", "--value=dummy-argv-secret"]:
            with self.subTest(value=value):
                result = subprocess.run([sys.executable, str(ROOT / "safestack-vault/vault.py"), "put", "vault", "key", "name", value], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("dummy-argv-secret", result.stdout + result.stderr)

    def test_prompt_failure_does_not_fall_back_to_echo(self):
        with patch.object(sys.stdin, "isatty", return_value=True), patch.object(self.vault.getpass, "getpass", side_effect=self.vault.getpass.GetPassWarning("echo")), patch.object(self.vault, "put") as put, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.vault.main(["put", "vault", "key", "name"])
            put.assert_not_called()

class UsbCliTests(unittest.TestCase):
    def test_control_characters_cannot_create_output_records(self):
        usb = load("safestack-usb-sentinel/usb.py")
        with tempfile.TemporaryDirectory() as tmp:
            names = ["ordinary.bin", "evil\n" + "a" * 64 + "  trusted.bin", "control\r\x1b[2J\t\\.bin", "unicode-\u202e.bin"]
            for name in names:
                (Path(tmp) / name).write_bytes(b"dummy data")
            result = subprocess.run([sys.executable, str(ROOT / "safestack-usb-sentinel/usb.py"), tmp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), usb.scan(tmp))
            self.assertEqual(set(json.loads(result.stdout)), set(names))
            for character in ["\r", "\x1b", "\t", "\u202e"]:
                self.assertNotIn(character, result.stdout)
            self.assertNotIn("\n" + "a" * 64 + "  trusted.bin", result.stdout)

if __name__ == "__main__":
    unittest.main()
