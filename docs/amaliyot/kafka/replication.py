"""Partition replikatsiyasi — 2-daraja topshirig'i. Oltita funksiya TODO.

Darsdan: 5-bo'lim 5-7 va 10-qadamlar, 6-bo'lim. Hammasi bitta partition
uchun; simulyator (sim.py) brokerlarni ishga tushiradi, o'ldiradi, tarmoqni
uzadi, yetakchi saylaydi va sizning funksiyalaringizni chaqiradi.

Asosiy qoidalar:
  * Tasdiqlangan = offset < high watermark (HW). HW = ISR dagi hamma nusxa
    LEO larining minimumi. HW hech qachon kamaymaydi (yetakchida).
  * O'quvchilar faqat HW gacha o'qiydi.
  * Izdosh yangi yetakchiga ulanishdan oldin o'z dumini LEADER EPOCH
    bo'yicha kesadi — o'z HW si bo'yicha EMAS (7-qadam Deep).

Tekshiruv: python check.py
"""
from model import NotEnoughReplicas, Record  # noqa: F401


def append(leader, state, value, pid, seq, acks="all"):
    """Yetakchiga yozuv qo'shadi va uning offset'ini qaytaradi.

    * acks == "all" va len(state.isr) < state.min_isr -> NotEnoughReplicas.
    * Idempotentlik: jurnalda (pid, seq) allaqachon bo'lsa — yangi yozuv
      qo'shmasdan, o'sha yozuvning offset'ini qaytaring (10-qadam).
    * Aks holda Record(offset=leader.leo, epoch=state.epoch, ...) qo'shing.
    * Oxirida HW ni qayta hisoblang (ISR faqat yetakchidan iborat bo'lishi ham
      mumkin) — update_hw dan foydalaning."""
    raise NotImplementedError("TODO: append")


def update_hw(leader, state):
    """leader.hw = max(eski hw, min(ISR a'zolarining LEO si)).
    Yetakchining LEO si — leader.leo; izdoshniki — state.follower_leo
    (noma'lum bo'lsa 0)."""
    raise NotImplementedError("TODO: update_hw")


def on_fetch(leader, state, follower_id, fetch_offset, now, max_records=50):
    """Izdosh "fetch_offset dan boshlab ber" deb so'radi. Yetakchi:

      1. state.follower_leo[follower_id] = fetch_offset  (u 0..fetch_offset-1 ni oldi)
      2. fetch_offset >= leader.leo bo'lsa — state.last_caught_up[follower_id] = now
         va izdoshni ISR ga qo'shing (yetib oldi);
      3. ISR dagi har izdosh (yetakchidan boshqa) uchun: now - last_caught_up > max_lag
         bo'lsa — ISR dan chiqaring (yetakchi saylanganda simulyator ISR a'zolari
         uchun last_caught_up ni to'ldiradi);
      4. update_hw;
      5. (leader.log[fetch_offset : fetch_offset + max_records], leader.hw) qaytaring."""
    raise NotImplementedError("TODO: on_fetch")


def on_response(follower, records, leader_hw):
    """Izdosh javobni qo'llaydi: yozuvlarni jurnal oxiriga qo'shadi
    (records[0].offset == follower.leo bo'lishi shart — aks holda AssertionError),
    keyin follower.hw = max(follower.hw, min(leader_hw, follower.leo))."""
    raise NotImplementedError("TODO: on_response")


def end_offset_for_epoch(log, epoch):
    """Jurnalda `epoch` davri qayerda TUGAYDI (7-qadam, 6.3 Deep).

    (e, end) qaytaradi:
      e   — jurnaldagi `epoch` dan KATTA BO'LMAGAN eng katta davr
            (bunday davr bo'lmasa: -1);
      end — e davridan keyingi birinchi yozuvning offset'i, ya'ni e dan katta
            davrli birinchi yozuv; e jurnaldagi oxirgi davr bo'lsa — len(log);
            e == -1 bo'lsa — 0.

    Simulyator izdoshni shunday kesadi (tayyor, sim.py da):
        e, end = end_offset_for_epoch(yetakchi.log, izdosh.last_epoch())
        _, own = end_offset_for_epoch(izdosh.log, e)
        truncate(izdosh, min(end, own))
    Ikkinchi qator muhim: yetakchida izdoshning oxirgi davri umuman bo'lmasa
    ham (izdosh o'sha davrda yolg'iz yetakchi bo'lgan), to'g'ri joyda kesiladi."""
    raise NotImplementedError("TODO: end_offset_for_epoch")


def truncate(replica, end_offset):
    """Nusxa jurnalini end_offset gacha kesadi (end_offset va undan keyingi
    yozuvlar o'chadi; end_offset > leo bo'lsa — hech narsa o'zgarmaydi) va
    replica.hw = min(replica.hw, replica.leo)."""
    raise NotImplementedError("TODO: truncate")


def consumer_read(leader, offset, max_records=20):
    """O'quvchi uchun: offset dan boshlab, faqat HW gacha (hw dan kichik
    offset'li) yozuvlar ro'yxati."""
    raise NotImplementedError("TODO: consumer_read")
