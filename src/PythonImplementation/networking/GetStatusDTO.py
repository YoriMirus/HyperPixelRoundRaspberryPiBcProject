from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TempData:
    temperature: float
    humidity: float


@dataclass(frozen=True)
class AccelData:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class GyroData:
    roll: float
    pitch: float


@dataclass(frozen=True)
class SHT3x_status:
    connected: bool
    values: Optional[TempData] = None


@dataclass(frozen=True)
class MMA5452Q_status:
    connected: bool
    values_accel: Optional[AccelData] = None
    values_gyro: Optional[GyroData] = None


@dataclass(frozen=True)
class GetStatusDTO:
    SHT3x: SHT3x_status
    MMA5452Q: MMA5452Q_status
    is_raspberry_pi: bool
