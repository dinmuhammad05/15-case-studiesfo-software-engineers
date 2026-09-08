"""ranking.py uchun testlar. TAYYOR — `python -m pytest test_ranking.py`"""
from datetime import timedelta

import pytest

from ranking import EPOCH, TIME_CONSTANT, controversy_score, hot_score, wilson_lower_bound


def at(hours):
    return EPOCH + timedelta(hours=hours)


def test_ovoz_ko_p_bo_lsa_ball_yuqori():
    assert hot_score(100, 0, at(10)) > hot_score(10, 0, at(10))


def test_logarifmik_o_sish():
    """10 barobar ovoz = +1 ball."""
    a = hot_score(10, 0, at(10))
    b = hot_score(100, 0, at(10))
    assert b - a == pytest.approx(1.0, abs=1e-6)


def test_o_n_ikki_yarim_soat_bir_ball():
    """45 000 s = 12.5 soat = +1 ball."""
    a = hot_score(10, 0, at(0))
    b = hot_score(10, 0, at(TIME_CONSTANT / 3600))
    assert b - a == pytest.approx(1.0, abs=1e-6)


def test_yangi_kam_ovozli_eski_ko_p_ovozliga_teng():
    """100 ovozli yangi post ≈ 1000 ovozli 12.5 soatlik post."""
    yangi = hot_score(100, 0, at(12.5))
    eski = hot_score(1000, 0, at(0))
    assert yangi == pytest.approx(eski, abs=1e-6)


def test_salbiy_post_vaqt_bilan_pastga_tushadi():
    a = hot_score(0, 10, at(0))
    b = hot_score(0, 10, at(24))
    assert b < a


def test_wilson_kam_ovozni_jazolaydi():
    assert wilson_lower_bound(1, 0) < wilson_lower_bound(100, 10)


def test_wilson_kutilgan_qiymatlar():
    """Darsdagi 3.5-bo'limdagi raqamlar (z = 1.96)."""
    assert wilson_lower_bound(1, 0) == pytest.approx(0.21, abs=0.01)
    assert wilson_lower_bound(10, 1) == pytest.approx(0.62, abs=0.01)
    assert wilson_lower_bound(100, 10) == pytest.approx(0.84, abs=0.01)
    assert wilson_lower_bound(0, 0) == 0.0


def test_wilson_bir_xil_nisbat_ko_p_ma_lumot_yuqori():
    """B va C nisbati bir xil (0.909), lekin B ishonchliroq."""
    assert wilson_lower_bound(100, 10) > wilson_lower_bound(10, 1)


def test_controversy_muvozanatni_mukofotlaydi():
    """Teng bo'lingan 100 ovoz, bir tomonlama 100 ovozdan yuqori."""
    assert controversy_score(50, 50) > controversy_score(99, 1)
    assert controversy_score(10, 0) == 0.0
