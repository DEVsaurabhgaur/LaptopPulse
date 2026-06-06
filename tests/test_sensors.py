"""
tests/test_sensors.py
----------------------
Unit tests for sensor reading modules.
Mocks subprocess calls so tests run on any OS (Linux CI, Mac dev, Windows prod).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestNvidiaGpu:
    def test_available_with_valid_output(self):
        from core.sensors.gpu_nvidia import read_gpu_metrics
        mock_output = "72, 45, 38, 2048, 65.3"
        with patch("core.sensors.gpu_nvidia._run_nvidia_smi", return_value=mock_output):
            m = read_gpu_metrics()
        assert m.available is True
        assert m.temperature == 72
        assert m.utilization == 45
        assert m.fan_speed   == 38
        assert m.memory_used_mb == 2048

    def test_not_available_when_nvidia_smi_missing(self):
        from core.sensors.gpu_nvidia import read_gpu_metrics
        with patch("core.sensors.gpu_nvidia._run_nvidia_smi", return_value=None):
            m = read_gpu_metrics()
        assert m.available is False
        assert m.temperature is None

    def test_handles_na_values(self):
        from core.sensors.gpu_nvidia import read_gpu_metrics
        mock_output = "72, [N/A], 38, [N/A], [N/A]"
        with patch("core.sensors.gpu_nvidia._run_nvidia_smi", return_value=mock_output):
            m = read_gpu_metrics()
        assert m.available is True
        assert m.temperature == 72
        assert m.utilization is None

    def test_handles_malformed_output(self):
        from core.sensors.gpu_nvidia import read_gpu_metrics
        with patch("core.sensors.gpu_nvidia._run_nvidia_smi", return_value="bad"):
            m = read_gpu_metrics()
        assert m.temperature is None


class TestBattery:
    def test_battery_health_calculation(self):
        from core.sensors.battery import read_battery_metrics
        with patch("psutil.sensors_battery") as mock_bat, \
             patch("core.sensors.battery._read_wmi_battery_health",
                   return_value=(50000, 40000, 120)):
            mock_bat.return_value = MagicMock(percent=78.5, power_plugged=True)
            m = read_battery_metrics()
        assert m.available is True
        assert m.percent == 78.5
        assert m.is_plugged is True
        assert m.health_percent == 80.0   # 40000/50000 * 100
        assert m.cycle_count == 120

    def test_battery_unavailable_graceful(self):
        from core.sensors.battery import read_battery_metrics
        with patch("psutil.sensors_battery", return_value=None), \
             patch("core.sensors.battery._read_wmi_battery_health", return_value=(None, None, None)):
            m = read_battery_metrics()
        assert m.available is False
        assert m.percent is None


class TestStorage:
    def test_write_and_read_log(self, tmp_path):
        from unittest.mock import patch as p
        import json

        with p("core.storage.logger.get_log_dir", return_value=tmp_path):
            from core.storage.logger import write_reading, read_days
            metrics = {
                "ts": "2026-06-01T12:00:00",
                "cpu_temp": 65.0, "gpu_temp": 58.0,
                "fan_rpm": 2800, "cpu_load": 35.0,
                "is_throttling": False,
            }
            write_reading(metrics)
            # Reading should appear in read_days
            with p("core.storage.logger.get_log_dir", return_value=tmp_path):
                readings = read_days(1)
            assert len(readings) >= 1
            assert readings[0]["cpu_temp"] == 65.0

    def test_sanitise_removes_unknown_keys(self, tmp_path):
        from core.storage.logger import _sanitise
        dirty = {
            "cpu_temp": 65.0,
            "username": "saurabh",     # should be stripped
            "serial":   "XYZ123",      # should be stripped
            "fan_rpm":  2800,
        }
        clean = _sanitise(dirty)
        assert "cpu_temp" in clean
        assert "fan_rpm"  in clean
        assert "username" not in clean
        assert "serial"   not in clean
