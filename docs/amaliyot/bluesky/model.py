"""Tayyor qismlar (o'zgartirmang): xesh, imzo, MST tuguni va firehose hodisalari.

Imzo — o'quv uchun Schnorr imzosi kichik (128 bitli) guruhda. Matematikasi
haqiqiy: imzoni faqat maxfiy kalit egasi yasaydi, ochiq kalit bilan esa
istalgan kishi tekshiradi. Lekin guruh kichik — XAVFSIZ EMAS. Haqiqiy AT
Protocol secp256k1 yoki P-256 egri chiziqlaridagi imzolardan foydalanadi.
"""
import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------- xesh
def sha(data) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def key_level(key: str) -> int:
    """MST darajasi: sha256(kalit) boshidagi nol bitlar soni // 2.

    O'rtacha har 4 kalitdan biri 1-darajada, 16 tadan biri 2-darajada va
    hokazo — daraxt shoxlanishi ~4. Daraja faqat kalitning o'ziga bog'liq,
    shuning uchun bir xil kalitlar to'plami har doim bir xil daraxt beradi."""
    h = int.from_bytes(hashlib.sha256(key.encode()).digest(), "big")
    zeros = 256 - h.bit_length()
    return zeros // 2


# ---------------------------------------------------------------- imzo (o'quv)
P = 0xAA57E9E8D316CCF49AC71B8A3AC4D5D7   # xavfsiz tub: P = 2Q + 1
Q = 0x552BF4F4698B667A4D638DC51D626AEB
G = 4                                                                      # Q tartibli kichik guruh


def keypair(seed: str):
    """(maxfiy, ochiq) — seed dan deterministik."""
    x = int(sha("sk:" + seed), 16) % (Q - 1) + 1
    return x, pow(G, x, P)


def _e(r: int, msg: bytes) -> int:
    return int(sha(r.to_bytes(32, "big") + msg), 16) % Q


def sign(secret: int, msg: bytes) -> tuple:
    k = int(sha(secret.to_bytes(32, "big") + msg), 16) % (Q - 1) + 1   # deterministik nonce
    r = pow(G, k, P)
    return (r, (k + secret * _e(r, msg)) % Q)


def verify(public: int, msg: bytes, sig) -> bool:
    try:
        r, s = sig
        return pow(G, s, P) == (r * pow(public, _e(r, msg), P)) % P
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------- MST tuguni
@dataclass
class Entry:
    key: str                       # masalan "app.bsky.feed.post/3k2a"
    value: str                     # yozuv xeshi (CID o'rnida)
    right: Optional["Node"] = None # shu kalit va keyingi kalit orasidagi kalitlar


@dataclass
class Node:
    left: Optional["Node"] = None              # birinchi kalitdan kichik kalitlar
    entries: list = field(default_factory=list)
    h: Optional[str] = field(default=None, compare=False, repr=False)   # xesh keshi


def encode_node(left_hash, entries) -> bytes:
    """Tugunning kanonik baytlari. entries: [(key, value, right_hash), ...].
    Bolalar xeshlari (yoki None) — shuning uchun tugun xeshi butun pastki
    daraxtni ifodalaydi (Merkle)."""
    return json.dumps({"l": left_hash, "e": [list(e) for e in entries]},
                      separators=(",", ":")).encode()


def decode_node(data: bytes):
    """encode_node ning teskarisi: (left_hash, [(key, value, right_hash), ...])."""
    obj = json.loads(data)
    return obj["l"], [tuple(e) for e in obj["e"]]


def node_bytes(node: Node) -> bytes:
    return encode_node(tree_hash(node.left),
                       [(e.key, e.value, tree_hash(e.right)) for e in node.entries])


def tree_hash(node: Optional[Node]) -> Optional[str]:
    """Pastki daraxt xeshi (None -> None). Natija tugunda keshlanadi."""
    if node is None:
        return None
    if node.h is None:
        node.h = sha(node_bytes(node))
    return node.h


EMPTY_ROOT = sha(encode_node(None, []))


# ---------------------------------------------------------------- firehose
def commit_bytes(did: str, rev: int, prev: Optional[int], ops) -> bytes:
    """Imzolanadigan baytlar: kim, qaysi versiya, oldingisi va o'zgarishlar."""
    return json.dumps([did, rev, prev, ops], separators=(",", ":"), sort_keys=True).encode()


@dataclass(frozen=True)
class Commit:
    """Repo o'zgarishi. ops: ((action, path, record), ...);
    action — "create" | "update" | "delete" (delete da record = None).
    path — "kolleksiya/rkey", masalan "app.bsky.feed.like/3k2a".
    rev — repo versiyasi (o'sib boradi), prev — oldingi versiya (birinchisida None)."""
    seq: int
    did: str
    rev: int
    prev: Optional[int]
    ops: tuple
    sig: tuple


@dataclass(frozen=True)
class Identity:
    """Hisobning DID hujjati o'zgardi (masalan, kalit almashtirildi) — qayta o'qish kerak."""
    seq: int
    did: str


@dataclass(frozen=True)
class Account:
    """Hisob holati: active=False — o'chirilgan yoki to'xtatilgan, uning yozuvlari ko'rinmasin."""
    seq: int
    did: str
    active: bool


@dataclass(frozen=True)
class RepoSnapshot:
    """Butun repo (resinxronizatsiya uchun): rev va hamma yozuvlar {path: record}."""
    did: str
    rev: int
    records: dict


POST, LIKE, FOLLOW = "app.bsky.feed.post", "app.bsky.feed.like", "app.bsky.graph.follow"


def at_uri(did: str, path: str) -> str:
    return f"at://{did}/{path}"
