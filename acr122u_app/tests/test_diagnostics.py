import pytest
import os
import sys
from unittest.mock import patch, Mock

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
