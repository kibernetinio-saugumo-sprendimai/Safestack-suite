"""Automated test suite for SafeStack security tools."""
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(rel_path):
    spec = importlib.util.spec_from_file_location('module', ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommonFilesystemTests(unittest.TestCase):
    def setUp(self):
        self.common = load('safestack_common.py')

    def test_atomic_write_and_read_regular(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'test.txt'
            self.common.atomic_write(f, b"safe data", mode=0o600)
            self.assertTrue(f.exists())
            self.assertEqual(self.common.read_regular(f), b"safe data")
            file_stat = os.stat(f)
            self.assertEqual(stat.S_IMODE(file_stat.st_mode), 0o600)

    def test_atomic_write_rejects_symlink_parent(self):
        with tempfile.TemporaryDirectory() as d:
            real_dir = Path(d) / 'real'
            real_dir.mkdir()
            sym_dir = Path(d) / 'symlink_dir'
            sym_dir.symlink_to(real_dir)

            target = sym_dir / 'test.txt'
            with self.assertRaises(ValueError):
                self.common.atomic_write(target, b"data")

    def test_atomic_write_rejects_directory_target(self):
        with tempfile.TemporaryDirectory() as d:
            sub = Path(d) / 'existing_dir'
            sub.mkdir()
            with self.assertRaises(ValueError):
                self.common.atomic_write(sub, b"data")

    def test_read_regular_rejects_symlinks_and_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            real_file = Path(d) / 'real.txt'
            real_file.write_text("hello")
            sym_file = Path(d) / 'sym.txt'
            sym_file.symlink_to(real_file)

            with self.assertRaises(ValueError):
                self.common.read_regular(sym_file)

            dir_path = Path(d) / 'dir'
            dir_path.mkdir()
            with self.assertRaises(ValueError):
                self.common.read_regular(dir_path)

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'test.bin'
            f.write_bytes(b"hello safestack")
            digest = self.common.sha256_file(f)
            # sha256("hello safestack")
            self.assertEqual(digest, "7f562b29cd4e7d93c679dfb6c79e7d62bc0f10518f7131a587c7665178d80617")


            sym = Path(d) / 'sym.bin'
            sym.symlink_to(f)
            with self.assertRaises(ValueError):
                self.common.sha256_file(sym)


class BackupGuardianTests(unittest.TestCase):
    def setUp(self):
        self.guardian = load('safestack-backup-guardian/guardian.py')

    def test_backup_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / 'a.txt').write_text('content a')
            (p / 'b.txt').write_text('content b')
            manifest_file = p / 'manifest.json'
            self.guardian.write(p, manifest_file)
            result = self.guardian.verify(p, manifest_file)
            self.assertEqual(result, {'missing': [], 'changed': [], 'new': []})

    def test_backup_detects_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            f1 = p / 'a.txt'
            f2 = p / 'b.txt'
            f1.write_text('original a')
            f2.write_text('original b')
            manifest_file = p / 'manifest.json'
            self.guardian.write(p, manifest_file)

            # Modify f1, delete f2, add f3
            f1.write_text('modified a')
            f2.unlink()
            (p / 'c.txt').write_text('new c')

            diff = self.guardian.verify(p, manifest_file)
            self.assertEqual(diff['changed'], ['a.txt'])
            self.assertEqual(diff['missing'], ['b.txt'])
            self.assertEqual(diff['new'], ['c.txt'])


class DnsShieldTests(unittest.TestCase):
    def setUp(self):
        self.shield = load('safestack-dns-shield/shield.py')

    def test_dns_deduplicates_and_formats(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            src = p / 'domains.txt'
            out = p / 'hosts.block'
            src.write_text("Example.com\nexample.com\n# comment\ninvalid_domain!@#\nanother-good.org\n\n")
            count = self.shield.generate(src, out)
            self.assertEqual(count, 2)
            content = out.read_text()
            self.assertIn("0.0.0.0 another-good.org\n", content)
            self.assertIn("0.0.0.0 example.com\n", content)

    def test_dns_rejects_symlink_source(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            real = p / 'real.txt'
            real.write_text("evil.com\n")
            sym = p / 'sym.txt'
            sym.symlink_to(real)
            out = p / 'hosts.block'
            with self.assertRaises(ValueError):
                self.shield.generate(sym, out)


class HomeSocTests(unittest.TestCase):
    def setUp(self):
        self.soc = load('safestack-home-soc/soc.py')

    def test_inventory_structure(self):
        inv = self.soc.inventory()
        self.assertIn('hostname', inv)
        self.assertIn('ipv4', inv)
        self.assertIn('default_route', inv)
        self.assertIsInstance(inv['ipv4'], list)


class IncidentKitTests(unittest.TestCase):
    def setUp(self):
        self.kit = load('safestack-incident-kit/kit.py')

    def test_incident_collect(self):
        with tempfile.TemporaryDirectory() as d:
            out_dir = Path(d) / 'bundle'
            target = self.kit.collect(out_dir)
            self.assertTrue(target.exists())
            self.assertEqual(target.name, 'system.json')

    def test_incident_rejects_symlink_output(self):
        with tempfile.TemporaryDirectory() as d:
            real_dir = Path(d) / 'real'
            real_dir.mkdir()
            sym_dir = Path(d) / 'sym'
            sym_dir.symlink_to(real_dir)
            with self.assertRaises(ValueError):
                self.kit.collect(sym_dir)


class PrivacyLensTests(unittest.TestCase):
    def setUp(self):
        self.lens = load('safestack-privacy-lens/lens.py')

    def test_privacy_audit(self):
        res = self.lens.audit()
        self.assertIn('platform', res)
        self.assertIn('hostname_exposed', res)
        self.assertIn('home_permissions', res)


class UsbSentinelTests(unittest.TestCase):
    def setUp(self):
        self.usb = load('safestack-usb-sentinel/usb.py')

    def test_usb_scan(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            f1 = p / 'file1.bin'
            f1.write_bytes(b"usb test content")
            sym = p / 'symlink.bin'
            sym.symlink_to(f1)

            results = self.usb.scan(p)
            self.assertIn('file1.bin', results)
            self.assertNotIn('symlink.bin', results)
            self.assertEqual(
                results['file1.bin'],
                "2c3c5e9509388e2990d01b8e00f591c176540cd3cb357dc3015e45b89c29c9bc"
            )



class VaultTests(unittest.TestCase):
    def setUp(self):
        self.vault = load('safestack-vault/vault.py')

    def test_vault_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            key_file = p / 'secret.key'
            vault_file = p / 'secrets.vault'

            self.vault.create_key(key_file)
            self.assertTrue(key_file.exists())
            self.assertEqual(stat.S_IMODE(os.stat(key_file).st_mode), 0o600)

            self.vault.put(vault_file, key_file, 'api_token', 'super_secret_123')
            self.vault.put(vault_file, key_file, 'db_pass', 'pass456')

            self.assertEqual(self.vault.get(vault_file, key_file, 'api_token'), 'super_secret_123')
            self.assertEqual(self.vault.get(vault_file, key_file, 'db_pass'), 'pass456')

            with self.assertRaises(KeyError):
                self.vault.get(vault_file, key_file, 'non_existent_key')


if __name__ == '__main__':
    unittest.main()

