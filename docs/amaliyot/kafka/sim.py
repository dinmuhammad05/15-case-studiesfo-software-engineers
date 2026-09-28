"""Partition replikatsiyasi simulyatori (tayyor, o'zgartirmang).

Bitta partition, 3 broker. Har "tik"da:
  1. (xaos rejimida) tasodifiy hodisalar: broker qulaydi yoki qaytadi,
     izdosh tarmoqdan uziladi yoki ulanadi;
  2. yetakchi o'lgan bo'lsa — kontroller ISR dan yangi yetakchi saylaydi
     (toza saylov), davr (epoch) +1;
  3. yangi yetakchiga ulangan yoki qaytgan izdoshlar dumini kesadi
     (end_offset_for_epoch + truncate);
  4. ishlab chiqaruvchilar yozadi (append), javob yo'qolsa — qayta yuboradi;
  5. o'quvchi HW gacha o'qiydi (consumer_read);
  6. izdoshlar fetch qiladi (on_fetch + on_response) — har biri har tikda
     emas, o'z tezligida (fetch_p), shuning uchun ular yetakchidan orqada qoladi;
  7. tasdiqlar (HW yozuvdan o'tdi) ishlab chiqaruvchilarga yetkaziladi.

lose_unflushed=True: qulagan broker diskka yozilmagan (sahifa keshidagi)
dumini yo'qotadi — 6.3 Deep dagi "elektr o'chishi".
"""
import random

from model import LeaderState, NotEnoughReplicas, Replica


class Sim:
    def __init__(self, rep, n=3, min_isr=2, max_lag=4, seed=0, producers=3, per_producer=40,
                 lose_unflushed=False, resp_loss=0.05, acks="all", fetch_p=0.5):
        self.rep = rep
        self.rng = random.Random(seed)
        self.n = n
        self.replicas = {i: Replica(i) for i in range(n)}
        self.alive = {i: True for i in range(n)}
        self.cut = set()
        self.flushed = {i: 0 for i in range(n)}
        self.now = 0
        self.state = LeaderState(leader_id=0, epoch=0, isr=set(range(n)), min_isr=min_isr, max_lag=max_lag)
        for i in range(n):
            self.state.last_caught_up[i] = 0
        self.offline = False
        self.needs_trunc = set()
        self.lose_unflushed = lose_unflushed
        self.resp_loss = resp_loss
        self.acks = acks
        self.fetch_p = fetch_p
        self.producers = [
            {"pid": 100 + p, "seq": 0, "left": per_producer, "pending": None} for p in range(producers)
        ]
        self.acked = []          # tasdiqlangan qiymatlar
        self.ack_offsets = {}    # qiymat -> tasdiqlangan offset
        self.consumed = []       # (offset, qiymat)
        self.cons_pos = 0
        self.events = []

    # ---------------------------------------------------------------- yordamchi
    @property
    def leader(self):
        return self.replicas[self.state.leader_id]

    def leader_ok(self):
        return not self.offline and self.alive[self.state.leader_id]

    def log(self, msg):
        self.events.append(f"t={self.now}: {msg}")

    # ---------------------------------------------------------------- hodisalar
    def crash(self, b):
        if not self.alive[b]:
            return
        self.alive[b] = False
        r = self.replicas[b]
        if self.lose_unflushed:
            del r.log[self.flushed[b]:]
            r.hw = min(r.hw, r.leo)
        self.log(f"broker {b} quladi (LEO={r.leo})")

    def restart(self, b):
        if self.alive[b]:
            return
        self.alive[b] = True
        self.needs_trunc.add(b)
        self.log(f"broker {b} qaytdi")

    def elect(self):
        """Toza saylov: faqat ISR dagi tirik nusxalardan."""
        old = self.state.leader_id
        cands = sorted(b for b in self.state.isr if self.alive[b] and (b != old or self.offline))
        if not cands:
            self.offline = True
            return
        new = self.rng.choice(cands)
        isr = {b for b in self.state.isr if self.alive[b]}
        st = LeaderState(leader_id=new, epoch=self.state.epoch + 1, isr=isr | {new},
                         min_isr=self.state.min_isr, max_lag=self.state.max_lag)
        for b in st.isr:
            st.last_caught_up[b] = self.now
        self.state = st
        self.offline = False
        self.needs_trunc = {b for b in range(self.n) if b != new and self.alive[b]}
        self.needs_trunc.discard(new)
        self.log(f"yangi yetakchi {new}, davr {st.epoch}, ISR {sorted(st.isr)}")

    def truncate_followers(self):
        if not self.leader_ok():
            return
        lead = self.leader
        for b in sorted(self.needs_trunc):
            if not self.alive[b] or b == self.state.leader_id:
                continue
            f = self.replicas[b]
            e, end = self.rep.end_offset_for_epoch(lead.log, f.last_epoch())
            _, own = self.rep.end_offset_for_epoch(f.log, e)
            self.rep.truncate(f, min(end, own))
        self.needs_trunc = {b for b in self.needs_trunc if not self.alive[b]}

    # ---------------------------------------------------------------- bir tik
    def chaos(self, p_crash=0.04, p_restart=0.25, p_cut=0.05, max_down=2):
        down = [b for b in range(self.n) if not self.alive[b]]
        if len(down) < max_down and self.rng.random() < p_crash:
            self.crash(self.rng.choice([b for b in range(self.n) if self.alive[b]]))
        for b in down:
            if self.rng.random() < p_restart:
                self.restart(b)
        if self.rng.random() < p_cut:
            b = self.rng.randrange(self.n)
            if b in self.cut:
                self.cut.discard(b)
            elif b != self.state.leader_id:
                self.cut.add(b)

    def step(self, chaos=False):
        self.now += 1
        if chaos:
            self.chaos()
        if self.offline or not self.alive[self.state.leader_id]:
            self.elect()
        self.truncate_followers()
        lead_ok = self.leader_ok()

        # ishlab chiqaruvchilar
        for pr in self.producers:
            pend = pr["pending"]
            if pend is None and pr["left"] > 0:
                pend = pr["pending"] = {"value": f"p{pr['pid']}-{pr['seq']}", "seq": pr["seq"], "offset": None,
                                        "epoch": None, "sent": None}
            if pend is None or not lead_ok:
                continue
            stale = pend["offset"] is None or pend["epoch"] != self.state.epoch or self.now - pend["sent"] > 8
            if stale:
                try:
                    off = self.rep.append(self.leader, self.state, pend["value"], pr["pid"], pend["seq"], self.acks)
                except NotEnoughReplicas:
                    continue
                pend.update(offset=off, epoch=self.state.epoch, sent=self.now)

        # o'quvchi (izdoshlar fetch qilishidan oldin — HW dan tashqariga o'qish xavfli bo'lgan payt)
        if lead_ok:
            for r in self.rep.consumer_read(self.leader, self.cons_pos):
                self.consumed.append((r.offset, r.value))
                self.cons_pos = r.offset + 1

        # izdoshlar fetch (har biri o'z tezligida: har tikda emas)
        if lead_ok:
            order = [b for b in range(self.n) if b != self.state.leader_id]
            self.rng.shuffle(order)
            for b in order:
                if not self.alive[b] or b in self.cut or b in self.needs_trunc:
                    continue
                if self.rng.random() > self.fetch_p:
                    continue
                f = self.replicas[b]
                recs, hw = self.rep.on_fetch(self.leader, self.state, b, f.leo, self.now)
                self.rep.on_response(f, recs, hw)

        # diskka yozish (fon flush)
        for b in range(self.n):
            if self.alive[b] and self.rng.random() < 0.3:
                self.flushed[b] = self.replicas[b].leo
            self.flushed[b] = min(self.flushed[b], self.replicas[b].leo)

        # tasdiqlar
        if lead_ok:
            lead = self.leader
            for pr in self.producers:
                pend = pr["pending"]
                if not pend or pend["offset"] is None or pend["epoch"] != self.state.epoch:
                    continue
                o = pend["offset"]
                if lead.hw > o and o < lead.leo and lead.log[o].value == pend["value"]:
                    if self.rng.random() < self.resp_loss:
                        pend["sent"] = -100  # javob yo'qoldi -> qayta yuboriladi
                        continue
                    self.acked.append(pend["value"])
                    self.ack_offsets[pend["value"]] = o
                    pr["seq"] += 1
                    pr["left"] -= 1
                    pr["pending"] = None


    # ---------------------------------------------------------------- yakun
    def heal(self, max_ticks=3000):
        for b in range(self.n):
            self.restart(b)
        self.cut.clear()
        self.fetch_p = 1.0
        for _ in range(max_ticks):
            self.step(chaos=False)
            lead = self.leader
            done = (
                self.leader_ok()
                and all(p["left"] == 0 for p in self.producers)
                and all(self.replicas[b].leo == lead.leo for b in range(self.n))
                and lead.hw == lead.leo
                and self.cons_pos >= lead.leo
            )
            if done:
                # izdoshlar HW ni ham olsin
                for _ in range(3):
                    self.step(chaos=False)
                return True
        return False

    def run(self, chaos_ticks=400):
        for _ in range(chaos_ticks):
            self.step(chaos=True)
        return self.heal()
