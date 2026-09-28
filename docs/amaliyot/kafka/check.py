"""replication.py ni tekshiradi (tayyor, o'zgartirmang).

  python check.py

Uch qism: (1) kichik birlik testlari; (2) darsdagi aniq stsenariylar —
KIP-101 ning ikki holati (tasdiqlangan xabar yo'qolishi va nusxalar
ajralishi), KIP-279 holati, ISR ning kichrayishi va min.insync.replicas;
(3) xaos: yuzlab tasodifiy qulash, qaytish va tarmoq uzilishlaridan keyin
hech bir tasdiqlangan xabar yo'qolmaydi, takrorlanmaydi, nusxalar bir xil
va o'quvchi hech qachon "arvoh" yozuvni ko'rmaydi.
"""
import sys
import time

import replication as rep
from model import LeaderState, NotEnoughReplicas, Record, Replica
from sim import Sim

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'OK' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def attempt(fn, *a, **kw):
    try:
        return fn(*a, **kw), None
    except NotImplementedError:
        raise
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def vals(r):
    return [x.value for x in r.log]


def mk(leader_id, epoch, isr, min_isr=2, max_lag=3, now=0):
    """Yetakchi holati; ISR a'zolari "hozirgina yetib olgan" deb boshlanadi (simulyatordagi kabi)."""
    st = LeaderState(leader_id=leader_id, epoch=epoch, isr=set(isr), min_isr=min_isr, max_lag=max_lag)
    for b in isr:
        st.last_caught_up[b] = now
    return st


def fetch(leader, st, f, now):
    recs, hw = rep.on_fetch(leader, st, f.broker_id, f.leo, now)
    rep.on_response(f, recs, hw)


def follow(leader, f):
    """Simulyatordagi kabi: izdosh yangi yetakchiga ulanishdan oldin kesadi."""
    e, end = rep.end_offset_for_epoch(leader.log, f.last_epoch())
    _, own = rep.end_offset_for_epoch(f.log, e)
    rep.truncate(f, min(end, own))


# ---------------------------------------------------------------- 1. birlik

def part_units():
    print("1. Birlik testlari")
    A, B, C = Replica(0), Replica(1), Replica(2)
    st = mk(0, 0, {0, 1, 2}, min_isr=2, max_lag=3)
    o1, e1 = attempt(rep.append, A, st, "a", 7, 0)
    o2, e2 = attempt(rep.append, A, st, "a", 7, 0)
    o3, e3 = attempt(rep.append, A, st, "b", 7, 1)
    check("append: offset'lar 0,1; bir xil (pid, seq) takrori — yangi yozuv emas, o'sha offset",
          (o1, o2, o3) == (0, 0, 1) and vals(A) == ["a", "b"] and A.log[0].epoch == 0, e1 or e2 or e3 or "")
    check("HW izdoshlar olmaguncha siljimaydi (ISR = 3 ta)", A.hw == 0, f"hw={A.hw}")

    recs, hw = rep.on_fetch(A, st, 1, 0, 1)
    rep.on_response(B, recs, hw)
    recs, hw = rep.on_fetch(A, st, 1, 2, 2)  # B endi 2 ta yozuvga ega
    check("on_fetch: izdosh LEO si ma'lum bo'ldi, lekin C hali 0 — HW = 0", A.hw == 0 and st.follower_leo.get(1) == 2,
          f"hw={A.hw}")
    fetch(A, st, C, 3)
    fetch(A, st, C, 4)
    check("hamma ISR ikkala yozuvni olgach — HW = 2", A.hw == 2, f"hw={A.hw}")

    bad = False
    try:
        rep.on_response(Replica(9, log=[Record(0, 0, "x")]), [Record(5, 0, "y")], 0)
    except AssertionError:
        bad = True
    except Exception:  # noqa: BLE001
        bad = False
    check("on_response: uzilgan offset'li yozuvlar -> AssertionError", bad)

    L = [Record(0, 0, "a"), Record(1, 0, "b"), Record(2, 2, "c"), Record(3, 2, "d"), Record(4, 5, "e")]
    cases = [(0, (0, 2)), (1, (0, 2)), (2, (2, 4)), (4, (2, 4)), (5, (5, 5)), (9, (5, 5)), (-1, (-1, 0))]
    got = [(e, attempt(rep.end_offset_for_epoch, L, e)[0]) for e, _ in cases]
    check("end_offset_for_epoch: eng katta mos davr va uning tugash joyi (7 holat)",
          all(g == w for (_, g), (_, w) in zip(got, cases)) and rep.end_offset_for_epoch([], 3) == (-1, 0),
          f"olindi {got}")

    R = Replica(3, log=list(L), hw=4)
    rep.truncate(R, 2)
    ok = vals(R) == ["a", "b"] and R.hw == 2
    rep.truncate(R, 10)
    check("truncate: kesadi, hw ni pasaytiradi; katta offset — o'zgarishsiz", ok and vals(R) == ["a", "b"])

    F = Replica(5)
    rep.on_response(F, [Record(0, 0, "a"), Record(1, 0, "b")], 5)
    solo = Replica(0)
    st1 = mk(0, 0, {0}, min_isr=1)
    rep.append(solo, st1, "s", 1, 0)
    M = Replica(0, log=[Record(0, 0, "a"), Record(1, 0, "b"), Record(2, 0, "c")], hw=2)
    stm = mk(0, 1, {0, 1}, min_isr=1)
    rep.update_hw(M, stm)          # izdosh LEO si hali noma'lum (0)
    check("HW qoidalari: izdosh HW si o'z LEO sidan oshmaydi; yolg'iz ISR da append HW ni darhol siljitadi; "
          "yetakchi HW si kamaymaydi", F.hw == 2 and solo.hw == 1 and M.hw == 2,
          f"izdosh hw={F.hw}, yolg'iz hw={solo.hw}, yetakchi hw={M.hw}")

    Q = Replica(4, log=list(L), hw=3)
    check("consumer_read: faqat HW gacha", [r.value for r in rep.consumer_read(Q, 1)] == ["b", "c"]
          and rep.consumer_read(Q, 3) == [])

    st2 = mk(0, 0, {0}, min_isr=2, max_lag=100)
    blocked = False
    try:
        rep.append(Replica(0), st2, "z", 1, 0, "all")
    except NotEnoughReplicas:
        blocked = True
    r1, err = attempt(rep.append, Replica(0), st2, "z", 1, 0, "1")
    check("min.insync.replicas: ISR=1 da acks=all rad etiladi, acks=1 — qabul", blocked and r1 == 0, err or "")


# ---------------------------------------------------------- 2. stsenariylar

def part_scenarios():
    print("2. Darsdagi stsenariylar")
    # KIP-101 (1): izdosh eskirgan HW gacha kesib, tasdiqlangan xabarni yo'qotadi
    A, B = Replica(0), Replica(1)
    st = mk(0, 0, {0, 1}, min_isr=1, max_lag=100)
    rep.append(A, st, "m1", 1, 0)
    fetch(A, st, B, 1)                              # B: [m1], hw=0
    rep.on_fetch(A, st, 1, B.leo, 2)               # A: hw=1 (m1 tasdiqlandi), javob B ga yetmadi
    committed = A.hw == 1 and B.hw == 0
    follow(A, B)                                    # B qayta ishga tushdi
    st = mk(1, 1, {1}, min_isr=1, max_lag=100)   # A o'ldi, B yetakchi
    rep.update_hw(B, st)
    check("KIP-101 (1): qayta ishga tushgan izdosh tasdiqlangan m1 ni o'chirmaydi (7-qadam Deep)",
          committed and vals(B) == ["m1"] and [r.value for r in rep.consumer_read(B, 0)] == ["m1"], f"B: {vals(B)}")

    # KIP-101 (2): elektr o'chishi va nusxalar ajralishi
    A, B = Replica(0), Replica(1)
    st = mk(0, 0, {0, 1}, min_isr=1, max_lag=100)
    rep.append(A, st, "m1", 1, 0)
    rep.append(A, st, "m2", 1, 1)
    fetch(A, st, B, 1)
    rep.on_fetch(A, st, 1, B.leo, 2)                # A: hw = 2
    del B.log[1:]                                   # B diskka yozmagan m2 ni yo'qotdi
    B.hw = min(B.hw, B.leo)
    stB = mk(1, 1, {1}, min_isr=1, max_lag=100)
    rep.append(B, stB, "m3", 2, 0)                  # B yetakchi, offset 1 = m3
    follow(B, A)                                    # A qaytdi, izdosh
    fetch(B, stB, A, 3)
    check("KIP-101 (2): elektr o'chishidan keyin nusxalar ajralmaydi (6.3 Deep)",
          vals(A) == vals(B) == ["m1", "m3"], f"A: {vals(A)}, B: {vals(B)}")

    # KIP-279: izdoshning oxirgi davri yetakchida umuman yo'q
    A, B, C = Replica(0), Replica(1), Replica(2)
    st = mk(0, 1, {0, 1, 2}, min_isr=1, max_lag=100)
    for i in range(8):
        rep.append(A, st, f"r{i}", 1, i)
    fetch(A, st, B, 1)
    fetch(A, st, C, 1)
    rep.append(A, st, "r8", 1, 8)
    rep.append(A, st, "r9", 1, 9)
    fetch(A, st, C, 2)                              # r8, r9 faqat C da
    stB = mk(1, 2, {1, 2}, min_isr=1, max_lag=100)   # A o'ldi -> B
    for i in range(4):
        rep.append(B, stB, f"b{8 + i}", 2, i)       # B yolg'iz yozdi, keyin o'ldi
    stC = mk(2, 3, {2}, min_isr=1, max_lag=100)      # C yetakchi
    follow(C, A)
    rep.append(C, stC, "c10", 3, 0)
    follow(C, B)                                    # B qaytdi: oxirgi davri 2, C da 2-davr yo'q
    fetch(C, stC, B, 3)
    fetch(C, stC, A, 3)
    check("KIP-279: izdoshning oxirgi davri yetakchida yo'q — baribir to'g'ri joyda kesadi",
          vals(A) == vals(B) == vals(C) == [f"r{i}" for i in range(10)] + ["c10"],
          f"B: {vals(B)[-4:]}, C: {vals(C)[-4:]}")

    # ISR kichrayishi va kengayishi
    A, B, C = Replica(0), Replica(1), Replica(2)
    st = mk(0, 0, {0, 1, 2}, min_isr=2, max_lag=3)
    t = 0
    for i in range(3):
        rep.append(A, st, f"x{i}", 1, i)
        t += 1
        fetch(A, st, B, t)
        fetch(A, st, C, t)
        fetch(A, st, B, t)
        fetch(A, st, C, t)
    before = A.hw
    for i in range(3, 9):                           # C tarmoqdan uzildi
        rep.append(A, st, f"x{i}", 1, i)
        t += 1
        fetch(A, st, B, t)
        fetch(A, st, B, t)
    shrunk = 2 not in st.isr and A.hw == A.leo == 9
    t += 1
    fetch(A, st, C, t)                              # qaytdi, lekin hali orqada (LEO 3 dan so'radi)
    not_yet = 2 not in st.isr
    for _ in range(2):
        t += 1
        fetch(A, st, C, t)
    check("ISR: uzilgan izdosh max_lag dan keyin chiqariladi, HW qolganlar bilan siljiydi; qaytgach — faqat "
          "yetib olganda ISR ga qaytadi",
          before == 3 and shrunk and not_yet and 2 in st.isr and vals(C) == vals(A), f"ISR={sorted(st.isr)}, hw={A.hw}")


# ------------------------------------------------------------------ 3. xaos

def verify(sim):
    lead = sim.leader
    final = vals(lead)
    problems = []
    if any(vals(sim.replicas[b]) != final for b in range(sim.n)):
        problems.append("nusxalar farq qiladi")
    if len(set(final)) != len(final):
        problems.append("jurnalda takror")
    pos = {v: i for i, v in enumerate(final)}
    lost = [v for v in sim.acked if v not in pos or pos[v] >= lead.hw]
    if lost:
        problems.append(f"{len(lost)} ta tasdiqlangan xabar yo'q (masalan {lost[0]})")
    ghost = [(o, v) for o, v in sim.consumed if o >= len(final) or final[o] != v]
    if ghost:
        problems.append(f"o'quvchi {len(ghost)} ta 'arvoh' yozuv ko'rgan (masalan {ghost[0]})")
    if [v for _, v in sim.consumed] != final:
        problems.append("o'quvchi hamma yozuvni tartib bilan o'qimagan")
    return problems


def part_chaos():
    print("3. Xaos: tasodifiy qulashlar, qaytishlar va tarmoq uzilishlari")
    fails, stuck, elections = [], 0, 0
    t0 = time.time()
    for seed in range(40):
        s = Sim(rep, seed=seed)
        ok = s.run(chaos_ticks=400)
        elections += sum("yangi yetakchi" in e for e in s.events)
        if not ok:
            stuck += 1
            fails.append((seed, "yakunlanmadi (liveness)"))
            continue
        p = verify(s)
        if p:
            fails.append((seed, p[0]))
    check(f"40 ta xaos stsenariysi ({elections} ta yetakchi almashinuvi): tasdiqlangan xabar yo'qolmaydi, takror yo'q, "
          "nusxalar bir xil, 'arvoh' o'qish yo'q", not fails, f"{len(fails)} ta xato, birinchisi: {fails[0]}" if fails else
          f"{time.time() - t0:.1f} s")

    fails = []
    for seed in range(100, 125):
        s = Sim(rep, seed=seed, lose_unflushed=True)
        if not s.run(chaos_ticks=300):
            fails.append((seed, "yakunlanmadi"))
            continue
        # elektr o'chishida tasdiqlangan dumning yo'qolishi ongli qabul qilingan (6.3 Deep),
        # shuning uchun bu yerda faqat ajralish va takrorlar tekshiriladi
        p = [x for x in verify(s) if x.startswith("nusxalar") or x.startswith("jurnalda")]
        if p:
            fails.append((seed, p[0]))
    check("25 ta 'elektr o'chishi' stsenariysi (diskka yozilmagan dum yo'qoladi): nusxalar hech qachon ajralmaydi",
          not fails, f"birinchi xato: {fails[0]}" if fails else "")


def main():
    t0 = time.time()
    try:
        part_units()
        if all(results):
            part_scenarios()
            part_chaos()
        else:
            print("2-3. O'tkazib yuborildi: avval birlik testlari to'liq o'tsin")
            results.append(False)
    except NotImplementedError as e:
        print(f"\n  To'xtadi: {e}. Avval shu funksiyani yozing.")
        results.append(False)
    ok = sum(results)
    print(f"\nJami: {ok}/{len(results)} {'OK' if ok == len(results) else 'FAIL'}  ({time.time() - t0:.1f} s)")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
