"""1-daraja: Diffie-Hellman qo'lda va X25519 bilan. TAYYOR — ishga tushiring.

    python dh_demo.py            # standart: p=23, g=5, a=6, b=15
    python dh_demo.py 23 5 4 9   # o'z sonlaringiz bilan
"""
import sys
import time


def small_dh(p: int, g: int, a: int, b: int) -> int:
    print(f"OCHIQ:   p = {p}, g = {g}")
    A = pow(g, a, p)
    B = pow(g, b, p)
    print(f"Anvar:   a = {a} (yashirin)  ->  A = {g}^{a} mod {p} = {A}  (ochiq)")
    print(f"Bekzod:  b = {b} (yashirin)  ->  B = {g}^{b} mod {p} = {B}  (ochiq)")
    s_a = pow(B, a, p)
    s_b = pow(A, b, p)
    print(f"Anvar hisoblaydi:   B^a mod p = {B}^{a} mod {p} = {s_a}")
    print(f"Bekzod hisoblaydi:  A^b mod p = {A}^{b} mod {p} = {s_b}")
    assert s_a == s_b, "Sirlar mos kelmadi — parametrlarni tekshiring"
    print(f"UMUMIY SIR: {s_a}   (server faqat p, g, A={A}, B={B} ni ko'rdi)\n")

    # Hujumchi: A dan a ni sinab chiqish bilan topish (faqat kichik p da mumkin)
    t0 = time.perf_counter()
    for x in range(1, p):
        if pow(g, x, p) == A:
            found = x
            break
    dt = (time.perf_counter() - t0) * 1e6
    print(f"Hujumchi A={A} dan x ni sinab topdi: x = {found}  ({dt:.1f} mikrosoniya)")
    print("  (x boshqa bo'lishi mumkin — u ham xuddi shu sirni beradi,")
    print("   chunki g^x mod p = A bo'lgan har qanday x ishlaydi)\n")
    return s_a


def x25519_demo(n: int = 10_000) -> None:
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    except KeyboardInterrupt:
        raise
    except BaseException as e:  # buzuq o'rnatish pyo3 PanicException beradi (BaseException)
        print("X25519 qismi uchun ishlaydigan 'cryptography' kerak:")
        print("  python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt")
        print(f"  (xato turi: {type(e).__name__})")
        return

    a = X25519PrivateKey.generate()
    b = X25519PrivateKey.generate()
    s_a = a.exchange(b.public_key())
    s_b = b.exchange(a.public_key())
    assert s_a == s_b
    print("X25519: haqiqiy o'lchamda")
    print(f"  ochiq kalit hajmi:  {len(a.public_key().public_bytes_raw())} bayt")
    print(f"  umumiy sir (hex):   {s_a.hex()[:32]}...  ({len(s_a)} bayt)")
    print(f"  ikkala tomonda bir xil: {s_a == s_b}")

    t0 = time.perf_counter()
    for _ in range(n):
        k = X25519PrivateKey.generate()
        k.exchange(b.public_key())
    dt = time.perf_counter() - t0
    print(f"\n  {n} ta (kalit yaratish + DH): {dt:.3f} s")
    print(f"  bitta almashinuv: {dt / n * 1000:.4f} ms")
    print("  Darsdagi taxmin (2.2, Deep): ~0.05 ms DH + ~0.05 ms kalit yaratish")
    print("  Farq bo'lsa: Python qo'shimchasi, protsessor, kutubxona versiyasi.")


if __name__ == "__main__":
    args = [int(x) for x in sys.argv[1:5]] if len(sys.argv) >= 5 else [23, 5, 6, 15]
    small_dh(*args)
    x25519_demo()
