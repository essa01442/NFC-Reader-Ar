import pytest
import os
import sys
from unittest.mock import patch, Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from diagnostics import SystemDiagnostics

def test_linux_pcscd_active():
    with patch('platform.system', return_value='Linux'):
        # Mock subprocess.run to return active
        mock_result = Mock()
        mock_result.stdout = 'active\n'
        with patch('subprocess.run', return_value=mock_result):
            is_running, msg = SystemDiagnostics.check_pcscd_status()
            assert is_running is True
            assert "تعمل بشكل سليم" in msg

def test_linux_pcscd_inactive():
    with patch('platform.system', return_value='Linux'):
        # Mock subprocess.run to return inactive
        mock_result = Mock()
        mock_result.stdout = 'inactive\n'
        with patch('subprocess.run', return_value=mock_result):
            is_running, msg = SystemDiagnostics.check_pcscd_status()
            assert is_running is False
            assert "sudo systemctl start pcscd" in msg

def test_windows_scardsvr_active():
    with patch('platform.system', return_value='Windows'):
        # Mock subprocess.run
        mock_result = Mock()
        mock_result.stdout = 'STATE              : 4  RUNNING'
        with patch('subprocess.run', return_value=mock_result):
            is_running, msg = SystemDiagnostics.check_pcscd_status()
            assert is_running is True
            assert "تعمل بشكل سليم" in msg

def test_windows_scardsvr_inactive():
    with patch('platform.system', return_value='Windows'):
        # Mock subprocess.run
        mock_result = Mock()
        mock_result.stdout = 'STATE              : 1  STOPPED'
        with patch('subprocess.run', return_value=mock_result):
            is_running, msg = SystemDiagnostics.check_pcscd_status()
            assert is_running is False
            assert "services.msc" in msg

def test_mac_always_true():
    with patch('platform.system', return_value='Darwin'):
        is_running, msg = SystemDiagnostics.check_pcscd_status()
        assert is_running is True
        assert "macOS" in msg

# ── check_user_permissions ────────────────────────────────────────────────────

def test_user_permissions_linux_in_plugdev():
    """User is in plugdev group – should return ok=True."""
    import grp as grp_mod
    fake_grp = MagicMock()
    fake_grp.gr_gid = 999
    fake_grp.gr_mem = []

    with patch('platform.system', return_value='Linux'), \
         patch('os.getgroups', return_value=[999]), \
         patch('os.getgid', return_value=1000):
        def mock_getgrnam(name):
            if name == "plugdev":
                return fake_grp
            raise KeyError(name)
        with patch('grp.getgrnam', side_effect=mock_getgrnam):
            ok, groups, msg = SystemDiagnostics.check_user_permissions()
            assert ok is True
            assert "plugdev" in groups

def test_user_permissions_linux_not_in_groups():
    """User is not in plugdev or pcscd – should return ok=False."""
    fake_grp = MagicMock()
    fake_grp.gr_gid = 888  # different from user's GIDs
    fake_grp.gr_mem = []

    with patch('platform.system', return_value='Linux'), \
         patch('os.getgroups', return_value=[1000, 1001]), \
         patch('os.getgid', return_value=1000), \
         patch('os.environ', {"USER": "testuser"}):
        def mock_getgrnam(name):
            return fake_grp
        with patch('grp.getgrnam', side_effect=mock_getgrnam):
            ok, groups, msg = SystemDiagnostics.check_user_permissions()
            assert ok is False
            assert groups == []

def test_user_permissions_non_linux():
    """On non-Linux platforms, should always return ok=True."""
    with patch('platform.system', return_value='Windows'):
        ok, groups, msg = SystemDiagnostics.check_user_permissions()
        assert ok is True

# ── check_usb_devices ─────────────────────────────────────────────────────────

def test_usb_devices_acr122u_found():
    """lsusb output containing ACR122U should be detected."""
    lsusb_output = (
        "Bus 001 Device 003: ID 072f:2200 Advanced Card Systems, Ltd ACR122U\n"
        "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
    )
    mock_result = Mock()
    mock_result.stdout = lsusb_output

    with patch('platform.system', return_value='Linux'), \
         patch('subprocess.run', return_value=mock_result):
        devices, msg = SystemDiagnostics.check_usb_devices()
        assert len(devices) == 1
        assert devices[0]["vendor_id"] == "072f"
        assert devices[0]["product_id"] == "2200"
        assert "اكتشاف" in msg

def test_usb_devices_none_found():
    """When no NFC reader is in lsusb output, devices list should be empty."""
    lsusb_output = "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub\n"
    mock_result = Mock()
    mock_result.stdout = lsusb_output

    with patch('platform.system', return_value='Linux'), \
         patch('subprocess.run', return_value=mock_result):
        devices, msg = SystemDiagnostics.check_usb_devices()
        assert devices == []

# ── get_fix_commands ──────────────────────────────────────────────────────────

def test_get_fix_commands_linux():
    """On Linux, fix commands should include usermod and systemctl."""
    with patch('platform.system', return_value='Linux'):
        commands = SystemDiagnostics.get_fix_commands()
        assert len(commands) > 0
        all_cmds = " ".join(cmd for _, cmd in commands)
        assert "systemctl" in all_cmds
        assert "usermod" in all_cmds
        assert "plugdev" in all_cmds

def test_get_fix_commands_non_linux():
    """On non-Linux platforms, fix commands list should be empty."""
    with patch('platform.system', return_value='Windows'):
        commands = SystemDiagnostics.get_fix_commands()
        assert commands == []

# ── run_full_diagnostics ──────────────────────────────────────────────────────

def test_run_full_diagnostics_structure():
    """run_full_diagnostics should return a dict with expected keys."""
    with patch.object(SystemDiagnostics, 'check_pcscd_status', return_value=(True, "ok")), \
         patch.object(SystemDiagnostics, 'check_user_permissions', return_value=(True, ["plugdev"], "ok")), \
         patch.object(SystemDiagnostics, 'check_usb_devices', return_value=([], "none")):
        report = SystemDiagnostics.run_full_diagnostics()
        assert "pcscd" in report
        assert "permissions" in report
        assert "usb_devices" in report
        assert "os" in report
        assert "overall_ok" in report
        assert report["overall_ok"] is True

def test_run_full_diagnostics_overall_false_when_pcscd_down():
    """overall_ok should be False when pcscd is not running."""
    with patch.object(SystemDiagnostics, 'check_pcscd_status', return_value=(False, "not running")), \
         patch.object(SystemDiagnostics, 'check_user_permissions', return_value=(True, ["plugdev"], "ok")), \
         patch.object(SystemDiagnostics, 'check_usb_devices', return_value=([], "none")):
        report = SystemDiagnostics.run_full_diagnostics()
        assert report["overall_ok"] is False
