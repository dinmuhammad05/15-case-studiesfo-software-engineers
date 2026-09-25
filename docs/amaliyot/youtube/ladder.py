"""1-daraja: bitreyt zinapoyasi va I-kadrlar tekisligi. TAYYOR — ishga tushiring.

    python ladder.py                 # sintetik 20 s test video bilan
    python ladder.py mening.mp4      # o'z videongiz bilan (birinchi 20 s)

Kerak: ffmpeg (PATH da yoki FFMPEG muhit o'zgaruvchisida).
  O'rnatish: https://ffmpeg.org/download.html
  yoki: pip install imageio-ffmpeg  (skript uni avtomatik topadi)

Nima qiladi:
  1. Videoni 4 ta pog'onaga siqadi (darsning 2.3-bo'limi), I-kadrlar har 4 s da MAJBURIY
  2. Har pog'onaning haqiqiy bitreyti va hajmini o'lchaydi
  3. I-kadr vaqtlarini o'qib, barcha pog'onalarda bir xil ekanini tekshiradi (2.4)
  4. HLS manifest va bo'laklarni yaratadi: out/master.m3u8
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LADDER = [  # nom, balandlik, bitreyt (kbit/s) — darsning 2.3-jadvali (H.264)
    ("240p", 240, 300),
    ("360p", 360, 700),
    ("480p", 480, 1200),
    ("720p", 720, 2500),
]
SEGMENT_S = 4
DURATION_S = 20
OUT = Path("out")


def find_ffmpeg() -> str:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg topilmadi. O'rnating yoki: pip install imageio-ffmpeg")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def source_args(src):
    if src:
        return ["-t", str(DURATION_S), "-i", src]
    # Sintetik: harakatlanuvchi naqsh + ovoz. Harakat bor — siqish real ishlaydi.
    return [
        "-f", "lavfi", "-i", f"testsrc2=size=1280x720:rate=30:duration={DURATION_S}",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={DURATION_S}",
    ]


def encode(ff, src, name, height, kbps):
    out = OUT / f"{name}.mp4"
    cmd = [ff, "-y", "-loglevel", "error", *source_args(src),
           "-vf", f"scale=-2:{height}",
           "-c:v", "libx264", "-preset", "veryfast",
           "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.5)}k", "-bufsize", f"{kbps * 2}k",
           # I-kadr har SEGMENT_S soniyada, sahna almashishida qo'shimcha I-kadr YO'Q:
           "-force_key_frames", f"expr:gte(t,n_forced*{SEGMENT_S})",
           "-sc_threshold", "0",
           "-c:a", "aac", "-b:a", "64k",
           str(out)]
    run(cmd)
    return out


def keyframe_times(ff, path):
    r = subprocess.run([ff, "-i", str(path), "-vf", "select='eq(pict_type,I)',showinfo",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def package_hls(ff, mp4, name):
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    run([ff, "-y", "-loglevel", "error", "-i", str(mp4), "-c", "copy",
         "-f", "hls", "-hls_time", str(SEGMENT_S), "-hls_playlist_type", "vod",
         "-hls_segment_filename", str(d / "seg_%03d.ts"), str(d / "playlist.m3u8")])


def main():
    ff = find_ffmpeg()
    src = sys.argv[1] if len(sys.argv) > 1 else None
    OUT.mkdir(exist_ok=True)
    print(f"Manba: {src or 'sintetik testsrc2 1280x720@30'}, {DURATION_S} s, bo'lak {SEGMENT_S} s\n")
    print(f"  {'pog`ona':8} {'maqsad':>9} {'haqiqiy':>9} {'hajm':>9}   I-kadrlar (s)")

    rows, kf_sets = [], {}
    for name, h, kbps in LADDER:
        mp4 = encode(ff, src, name, h, kbps)
        size = mp4.stat().st_size
        real = size * 8 / DURATION_S / 1000
        kfs = keyframe_times(ff, mp4)
        kf_sets[name] = kfs
        package_hls(ff, mp4, name)
        rows.append((name, h, kbps))
        print(f"  {name:8} {kbps:7d}k {real:8.0f}k {size / 1e6:7.2f} MB   {kfs}")

    master = ["#EXTM3U"]
    for name, h, kbps in rows:
        w = round(h * 16 / 9 / 2) * 2
        master += [f"#EXT-X-STREAM-INF:BANDWIDTH={kbps * 1000},RESOLUTION={w}x{h}",
                   f"{name}/playlist.m3u8"]
    (OUT / "master.m3u8").write_text("\n".join(master) + "\n")

    first = next(iter(kf_sets.values()))
    aligned = all(v == first for v in kf_sets.values())
    expected = [float(t) for t in range(0, DURATION_S, SEGMENT_S)]
    on_grid = first == expected
    print(f"\n  I-kadrlar barcha pog'onalarda bir xil: {'HA' if aligned else 'YOQ'}")
    print(f"  I-kadrlar har {SEGMENT_S} s da (kutilgan {expected}): {'HA' if on_grid else 'YOQ'}")
    print(f"\n  HLS: {OUT / 'master.m3u8'}  (brauzerda hls.js yoki Safari bilan o'ynatish mumkin)")
    return aligned and on_grid


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
