"""Ma'lumot tuzilmalari (tayyor, o'zgartirmang).

Record       — jurnal yozuvi: offset, epoch (yetakchilik davri), qiymat,
               ishlab chiqaruvchi ID (pid) va tartib raqami (seq)
Replica      — bitta brokerdagi partition nusxasi: jurnal va high watermark
LeaderState  — yetakchining xotiradagi holati: ISR, izdoshlar LEO lari
"""
from dataclasses import dataclass, field
from typing import Optional


class NotEnoughReplicas(Exception):
    """acks=all, lekin ISR min_isr dan kichik — yozish rad etiladi."""


@dataclass(frozen=True)
class Record:
    offset: int
    epoch: int
    value: str
    pid: Optional[int] = None
    seq: Optional[int] = None


@dataclass
class Replica:
    broker_id: int
    log: list = field(default_factory=list)  # log[i].offset == i
    hw: int = 0                               # high watermark: [0, hw) tasdiqlangan

    @property
    def leo(self):
        """Log end offset: keyingi yoziladigan offset."""
        return len(self.log)

    def last_epoch(self):
        return self.log[-1].epoch if self.log else -1


@dataclass
class LeaderState:
    leader_id: int
    epoch: int
    isr: set                                   # yetakchi ham ISR ichida
    min_isr: int = 2
    max_lag: int = 4                           # necha tik yetib olmasa — ISR dan chiqadi
    follower_leo: dict = field(default_factory=dict)     # broker_id -> ma'lum LEO
    last_caught_up: dict = field(default_factory=dict)   # broker_id -> oxirgi "yetib olgan" tik
