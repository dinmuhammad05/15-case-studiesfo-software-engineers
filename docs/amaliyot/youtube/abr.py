"""ABR algoritmlari. TODO qismlarini to'ldiring.

Har bir algoritm: choose(st) -> pog'ona indeksi (0 = eng past).

st (sim.State) maydonlari — faqat o'qing:
  st.ladder              [0.3, 0.7, 1.2, 2.5, 5.0]  Mbit/s
  st.segment_s           4.0
  st.buffer_s            buferdagi soniyalar (so'rov paytida)
  st.throughput_history  har yuklangan bo'lak uchun o'lchangan tezlik, Mbit/s
  st.last_index          oldingi bo'lak pog'onasi yoki None
  st.segment_no          joriy bo'lak raqami (0 dan)
"""


# ---- TAYYOR: taqqoslash uchun asos ----------------------------------------
def fixed_lowest(st):
    return 0


def fixed_highest(st):
    return len(st.ladder) - 1


# ---- TODO -------------------------------------------------------------------
def throughput_based(st, safety=0.8, window=5):
    """O'tkazuvchanlikka asoslangan (darsning 6.2-bo'limi).

    TODO:
      1. Tarix bo'sh bo'lsa (birinchi bo'lak) — 0 qaytaring (6.4: past sifatdan boshlash)
      2. Oxirgi `window` ta o'lchovning GARMONIK o'rtachasi
      3. byudjet = baho x safety
      4. byudjetdan oshmaydigan eng yuqori pog'ona; hech biri sig'masa — 0
    """
    raise NotImplementedError("TODO: throughput_based")


def buffer_based(st, reservoir=5.0, cushion=20.0):
    """Buferga asoslangan (darsning 6.3-bo'limi, BBA uslubi).

    TODO:
      bufer < reservoir                  -> 0
      bufer >= reservoir + cushion       -> eng yuqori
      oraliqda                           -> chiziqli: (bufer - reservoir) / cushion
                                            ulushini pog'onalar soniga ko'paytirib,
                                            pastga yaxlitlang
    """
    raise NotImplementedError("TODO: buffer_based")


def hybrid(st):
    """Gibrid (darsning 6.3-bo'limi oxiri + 6.4 Callout).

    TODO — o'zingiz loyihalang. Maslahatlar:
      - boshlanishda (bufer kichik, tarix qisqa) throughput_based ga tayaning
      - bufer to'lgach buffer_based ga o'ting
      - ikkalasining MINIMUMi — xavfsiz, lekin ehtiyotkor variant
      - gisterezis: yuqoriga faqat bitta pog'ona va faqat bufer yetarli
        bo'lsa ko'tariling; pastga esa darhol tushing (6.4 Callout)

    Maqsad: sim.py hisobotida hybrid QoE eng ko'p izda eng yaxshi bo'lsin.
    """
    raise NotImplementedError("TODO: hybrid")


# sim.py shu lug'atni o'qiydi — nomlarini o'zgartirmang
ALGORITHMS = {
    "eng_past": fixed_lowest,
    "eng_yuqori": fixed_highest,
    "throughput": throughput_based,
    "buffer": buffer_based,
    "hybrid": hybrid,
}
