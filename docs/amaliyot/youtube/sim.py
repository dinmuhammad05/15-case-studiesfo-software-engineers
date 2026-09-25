"""ABR simulyatori. TAYYOR — o'zgartirish shart emas.

    python sim.py                  # abr.py dagi barcha algoritmlar, barcha izlar
    python sim.py --trace metro    # bitta iz
    python sim.py --verbose        # har bo'lak bo'yicha jurnal (birinchi algoritm)

Model (darsning 6-bo'limi):
  - video 600 s, bo'laklar 4 s (150 ta), zinapoya LADDER (Mbit/s)
  - bo'lak yuklanadi: hajm = R x 4 Mbit, har soniya iz bo'yicha o'tkazuvchanlik
  - har so'rovga RTT qo'shiladi
  - birinchi bo'lak kelgach o'ynash boshlanadi (boshlanish vaqti)
  - bufer MAX_BUFFER dan oshsa, pleyer keyingi so'rovni kutadi
  - bufer 0 ga yetsa — buferlash (to'xtash)

QoE (MPC maqolasi uslubida, Yin va boshq., 2015), bo'lak boshiga:
  QoE = o'rtacha(R) - 1.0 x o'rtacha|R_k - R_(k-1)|
        - 4.3 x (buferlash_s + boshlanish_s) / bo'laklar_soni
"""
import argparse
import statistics

import abr
from traces import TRACES

LADDER = [0.3, 0.7, 1.2, 2.5, 5.0]   # Mbit/s: 240p, 360p, 480p, 720p, 1080p
SEGMENT_S = 4.0
VIDEO_S = 600.0
RTT_S = 0.05
MAX_BUFFER = 30.0
STEP = 0.01                          # simulyatsiya qadami, soniya

SWITCH_PENALTY = 1.0
REBUF_PENALTY = 4.3


class State:
    """Algoritmga beriladigan holat. Faqat o'qing."""

    def __init__(self):
        self.ladder = LADDER
        self.segment_s = SEGMENT_S
        self.buffer_s = 0.0
        self.throughput_history = []   # har yuklangan bo'lak uchun o'lchangan Mbit/s
        self.last_index = None         # oldingi bo'lak pog'onasi (None — birinchi bo'lak)
        self.segment_no = 0
        self.segments_total = int(VIDEO_S / SEGMENT_S)


def throughput_at(trace, t):
    return trace[min(int(t), len(trace) - 1)]


def run(choose, trace, verbose=False):
    st = State()
    t = 0.0
    playing = False
    startup = None
    rebuffer = 0.0
    chosen = []

    def advance(dt):
        nonlocal t, rebuffer
        t += dt
        if playing:
            if st.buffer_s >= dt:
                st.buffer_s -= dt
            else:
                rebuffer += dt - st.buffer_s
                st.buffer_s = 0.0

    for k in range(st.segments_total):
        # to'la bufer: kutamiz
        while playing and st.buffer_s > MAX_BUFFER - SEGMENT_S:
            advance(STEP)

        st.segment_no = k
        idx = choose(st)
        if not isinstance(idx, int) or not 0 <= idx < len(LADDER):
            raise ValueError(f"choose() noto'g'ri indeks qaytardi: {idx!r}")
        rate = LADDER[idx]
        size = rate * SEGMENT_S                      # Mbit

        t0 = t
        advance(RTT_S)
        left = size
        while left > 1e-9:
            c = throughput_at(trace, t)
            got = c * STEP
            if got >= left:
                advance(left / c)
                left = 0
            else:
                left -= got
                advance(STEP)
        dl = t - t0
        st.throughput_history.append(size / dl)
        st.buffer_s += SEGMENT_S
        st.last_index = idx
        chosen.append(rate)

        if not playing:
            playing = True
            startup = t
        if verbose:
            print(f"  #{k:3d}  {rate:4.1f} Mbit/s  yuklash {dl:5.2f} s  bufer {st.buffer_s:5.1f} s  "
                  f"buferlash jami {rebuffer:5.1f} s")

    n = len(chosen)
    avg = statistics.fmean(chosen)
    switches = sum(1 for a, b in zip(chosen, chosen[1:]) if a != b)
    smooth = statistics.fmean(abs(a - b) for a, b in zip(chosen, chosen[1:])) if n > 1 else 0.0
    qoe = avg - SWITCH_PENALTY * smooth - REBUF_PENALTY * (rebuffer + startup) / n
    return {
        "startup_s": startup,
        "rebuffer_s": rebuffer,
        # sessiya vaqtining qancha qismi to'xtashda o'tdi (100% dan oshmaydi)
        "rebuffer_pct": 100 * rebuffer / (rebuffer + VIDEO_S),
        "avg_mbps": avg,
        "switches": switches,
        "qoe": qoe,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", choices=list(TRACES))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    algos = abr.ALGORITHMS
    traces = [args.trace] if args.trace else list(TRACES)
    results = {}
    for tn in traces:
        trace = TRACES[tn]()
        print(f"\n=== iz: {tn}  (o'rtacha {statistics.fmean(trace):.2f} Mbit/s) ===")
        print(f"  {'algoritm':22} {'boshlanish':>10} {'buferlash':>10} {'bitreyt':>8} "
              f"{'almashish':>9} {'QoE':>7}")
        for name, fn in algos.items():
            try:
                r = run(fn, trace, verbose=args.verbose and name == next(iter(algos)))
            except NotImplementedError:
                print(f"  {name:22} (TODO)")
                continue
            results[(tn, name)] = r
            print(f"  {name:22} {r['startup_s']:9.2f}s {r['rebuffer_pct']:9.2f}% "
                  f"{r['avg_mbps']:7.2f}  {r['switches']:9d} {r['qoe']:7.2f}")

    print("\n--- tekshiruv ---")
    ok = True

    def check(label, cond):
        nonlocal ok
        print(f"  {'OK ' if cond else 'XATO'}  {label}")
        ok &= cond

    need = ["throughput", "buffer", "hybrid"]
    if not all((tn, a) in results for tn in traces for a in need):
        print("  throughput / buffer / hybrid hali to'liq emas — abr.py dagi TODO larni to'ldiring.")
        return False

    for tn in traces:
        hi = results[(tn, "eng_yuqori")]
        lo = results[(tn, "eng_past")]
        for a in need:
            r = results[(tn, a)]
            check(f"{tn}: {a} buferlashi 'eng_yuqori' dan kam yoki teng",
                  r["rebuffer_s"] <= hi["rebuffer_s"] + 1e-9)
            check(f"{tn}: {a} bitreyti 'eng_past' dan yuqori", r["avg_mbps"] > lo["avg_mbps"])
    for tn in ("3g_tebranuvchi", "metro"):
        if tn in traces:
            h_, b_ = results[(tn, "hybrid")], results[(tn, "buffer")]
            check(f"{tn}: hybrid almashishlari buffer'dan kam ({h_['switches']} < {b_['switches']}) — gisterezis ishlayapti",
                  h_["switches"] < b_["switches"])
    wins = sum(
        1 for tn in traces
        if results[(tn, "hybrid")]["qoe"]
        >= max(results[(tn, "throughput")]["qoe"], results[(tn, "buffer")]["qoe"]) - 0.05
    )
    check(f"hybrid QoE kamida {len(traces) - 1} ta izda eng yaxshi (0.05 tolerans bilan): {wins}/{len(traces)}",
          wins >= len(traces) - 1)

    print("\n" + ("Hammasi o'tdi." if ok else "Tuzatish kerak."))
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
