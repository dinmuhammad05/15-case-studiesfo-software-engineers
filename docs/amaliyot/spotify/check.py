"""pipeline.py ni sintetik oqimda tekshiradi (tayyor, o'zgartirmang).

  python gen.py      # bir marta: data/ ni yaratadi
  python check.py

Har tekshiruv OK yoki FAIL chiqaradi; oxirida jami.
"""
import json
import os
import sys
import time

import pipeline as P

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
HEAVY_HUMANS = {f"u{i:04d}" for i in range(10)}
SHARE = 0.70

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load():
    if not os.path.exists(os.path.join(DATA, "events.jsonl")):
        sys.exit("data/ topilmadi — avval: python gen.py")
    with open(os.path.join(DATA, "tracks.json")) as f:
        tracks = json.load(f)
    with open(os.path.join(DATA, "users.json")) as f:
        users = json.load(f)
    with open(os.path.join(DATA, "truth.json")) as f:
        truth = json.load(f)
    with open(os.path.join(DATA, "events.jsonl")) as f:
        events = [json.loads(line) for line in f]
    return tracks, users, truth, events


def fraud_sum(payout):
    return payout.get("a_fraud", 0.0)


def main():
    tracks, users, truth, raw = load()
    print(f"Xom hodisalar: {len(raw):,}\n")
    t0 = time.time()

    print("1. Dedublikatsiya")
    uniq = P.dedup([dict(e) for e in raw])
    check("noyob hodisalar soni", len(uniq) == truth["unique_events"],
          f"{len(uniq):,} (kutilgan {truth['unique_events']:,})")
    first_at = {}
    for e in raw:
        first_at[e["id"]] = min(first_at.get(e["id"], e["at"]), e["at"])
    kept_earliest = all(e["at"] == first_at[e["id"]] for e in uniq)
    check("har id uchun eng erta kelgan nusxa qolgan", kept_earliest)

    print("\n2. Karantin (soati oldinda qurilmalar)")
    good, quar = P.quarantine(uniq)
    check("karantindagilar soni", len(quar) == truth["quarantined"],
          f"{len(quar):,} (kutilgan {truth['quarantined']:,})")
    check("hech narsa yo'qolmadi", len(good) + len(quar) == len(uniq))

    print("\n3. Oy va yopilish")
    on_time, corr = P.split_month(good, truth["month_start"], truth["month_end"],
                                  truth["close_at"])
    q_on, q_corr = P.qualify(on_time), P.qualify(corr)
    bots_true = set(truth["bots"])
    c_on = P.count_streams(q_on, bots_true)
    c_corr = P.count_streams(q_corr, bots_true)
    exp_on, exp_corr = truth["on_time"], truth["corrections"]
    check("o'z vaqtidagi tinglashlar (trek bo'yicha, aniq)", c_on == exp_on,
          f"{sum(c_on.values()):,} (kutilgan {sum(exp_on.values()):,})")
    check("tuzatishlar (oy yopilgandan keyin kelgan)", c_corr == exp_corr,
          f"{sum(c_corr.values()):,} (kutilgan {sum(exp_corr.values()):,})")

    print("\n4. Botlarni aniqlash")
    bots = set(P.detect_bots(good, tracks))
    tp = len(bots & bots_true)
    prec = tp / len(bots) if bots else 0.0
    rec = tp / len(bots_true)
    check("aniqlik (precision) >= 0.9", prec >= 0.9, f"{prec:.2f} ({len(bots)} belgilandi)")
    check("to'liqlik (recall) >= 0.9", rec >= 0.9, f"{rec:.2f} ({tp}/{len(bots_true)})")
    heavy_flagged = sorted(bots & HEAVY_HUMANS)
    check("ko'p tinglaydigan odamlar bot deb belgilanmagan", not heavy_flagged,
          ", ".join(heavy_flagged))

    print("\n5. Yo'qolgan hodisalar (ketma-ketlik raqamlari)")
    est = P.loss_rate(uniq)
    real = truth["lost_rate"]
    err = abs(est - real) / real
    check("baho haqiqiydan 25% dan ko'p farq qilmaydi", err <= 0.25,
          f"baho {est:.4%}, haqiqiy {real:.4%}")

    print("\n6. Royalti taqsimoti")
    pool = SHARE * sum(u["price"] for u in users.values())
    pr_raw = P.payout_pro_rata(q_on, set(), tracks, pool)
    uc_raw = P.payout_user_centric(q_on, set(), tracks, users, SHARE)
    pr_f = P.payout_pro_rata(q_on, bots, tracks, pool)
    uc_f = P.payout_user_centric(q_on, bots, tracks, users, SHARE)
    check("pro-rata yig'indisi = fond", abs(sum(pr_raw.values()) - pool) < 1e-6,
          f"{sum(pr_raw.values()):.2f} / {pool:.2f}")
    check("foydalanuvchi-markazli yig'indisi <= fond",
          sum(uc_raw.values()) <= pool + 1e-6, f"{sum(uc_raw.values()):.2f}")
    bot_cap = SHARE * sum(users[b]["price"] for b in bots_true)
    check("foydalanuvchi-markazlida botlar o'z obunasidan ko'p ololmaydi",
          fraud_sum(uc_raw) <= bot_cap + 1e-6,
          f"{fraud_sum(uc_raw):.2f} <= {bot_cap:.2f}")
    check("filtrsiz pro-rata botlarga ko'proq beradi",
          fraud_sum(pr_raw) > 2 * fraud_sum(uc_raw))
    check("filtr bilan firibgar ulushi fondning 0.5% idan kam",
          fraud_sum(pr_f) < 0.005 * pool and fraud_sum(uc_f) < 0.005 * pool)

    print(f"\n   Firibgar ijrochi ulushi (fond {pool:,.0f} dollar):")
    print(f"   {'':24}{'pro-rata':>12}{'foyd.-markazli':>16}")
    print(f"   {'filtrsiz':24}{fraud_sum(pr_raw):>12,.2f}{fraud_sum(uc_raw):>16,.2f}")
    print(f"   {'bot filtri bilan':24}{fraud_sum(pr_f):>12,.2f}{fraud_sum(uc_f):>16,.2f}")

    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} OK   ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError:
        sys.exit("pipeline.py da TODO qolgan — funksiyalarni yozing.")
