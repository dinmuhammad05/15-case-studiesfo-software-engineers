"use client";

import { useCallback, useEffect, useState } from "react";
import { lessons } from "@/lib/lessons";
import { site } from "@/lib/site";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

type InstallPrompt = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

/**
 * Offline rejim va ilova sifatida o'rnatish boshqaruvi.
 * - service worker'ni ro'yxatdan o'tkazadi
 * - yangi versiya chiqqanda yangilashni taklif qiladi
 * - "Barcha darslarni yuklab olish" — progress bilan
 * - tarmoq yo'qolganda holatni ko'rsatadi
 */
export function PwaManager() {
  const [reg, setReg] = useState<ServiceWorkerRegistration | null>(null);
  const [updateReady, setUpdateReady] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<InstallPrompt | null>(null);
  const [offline, setOffline] = useState(false);
  const [open, setOpen] = useState(false);
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;

    navigator.serviceWorker
      .register(`${BASE}/sw.js`, { scope: `${BASE}/` })
      .then((r) => {
        setReg(r);
        if (r.waiting) setUpdateReady(true);
        r.addEventListener("updatefound", () => {
          const sw = r.installing;
          if (!sw) return;
          sw.addEventListener("statechange", () => {
            // Yangi versiya tayyor, lekin eskisi hali ishlayapti
            if (sw.state === "installed" && navigator.serviceWorker.controller) {
              setUpdateReady(true);
            }
          });
        });
      })
      .catch(() => {
        /* SW ishlamasa sayt oddiy holda ishlayveradi */
      });

    const onMessage = (e: MessageEvent) => {
      const d = e.data || {};
      if (d.type === "PRECACHE_PROGRESS") setProgress({ done: d.done, total: d.total });
      if (d.type === "PRECACHE_DONE") {
        setProgress(null);
        setSaved(true);
        try {
          localStorage.setItem("darslik:offline", "1");
        } catch {}
      }
    };
    navigator.serviceWorker.addEventListener("message", onMessage);
    return () => navigator.serviceWorker.removeEventListener("message", onMessage);
  }, []);

  useEffect(() => {
    try {
      setSaved(localStorage.getItem("darslik:offline") === "1");
    } catch {}

    const onInstall = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as InstallPrompt);
    };
    const sync = () => setOffline(!navigator.onLine);
    sync();
    window.addEventListener("beforeinstallprompt", onInstall);
    window.addEventListener("appinstalled", () => setInstallPrompt(null));
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    return () => {
      window.removeEventListener("beforeinstallprompt", onInstall);
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
    };
  }, []);

  const downloadAll = useCallback(() => {
    const sw = navigator.serviceWorker?.controller;
    if (!sw) return;
    const urls = lessons
      .filter((l) => l.status === "tayyor")
      .flatMap((l) => [`${BASE}/darslar/${l.slug}/`, `${BASE}/darslar/${l.slug}/index.txt`]);
    setProgress({ done: 0, total: urls.length });
    sw.postMessage({ type: "PRECACHE_URLS", urls });
  }, []);

  const applyUpdate = useCallback(() => {
    reg?.waiting?.postMessage({ type: "SKIP_WAITING" });
    setTimeout(() => window.location.reload(), 300);
  }, [reg]);

  // Ko'rsatadigan narsa bo'lmasa — hech narsa chizmaymiz
  const hasNews = updateReady || offline || !!installPrompt || !!progress;
  if (!reg && !installPrompt && !offline) return null;

  return (
    <div className="fixed right-3 bottom-3 z-50 flex flex-col items-end gap-2 print:hidden">
      {open ? (
        <div className="w-[280px] rounded-xl border border-[var(--skin-border)] bg-[var(--skin-surface)] p-3 text-sm shadow-2xl">
          <div className="mb-2 flex items-center justify-between">
            <span className="font-semibold">Offline rejim</span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Yopish"
              className="rounded px-1.5 text-[var(--skin-muted)] hover:bg-[var(--skin-surface-2)]"
            >
              ×
            </button>
          </div>

          <p className="mb-3 text-xs text-[var(--skin-muted)]">
            {offline
              ? "Tarmoq yo‘q. Yuklab olingan darslar ishlayapti."
              : site.protection.offlineDownload
                ? saved
                  ? "Darslar qurilmangizga saqlangan — internetsiz o‘qish mumkin."
                  : "Darslarni saqlab qo‘ysangiz, internetsiz ham o‘qiy olasiz."
                : "Ochilgan sahifalar vaqtincha saqlanadi, lekin darslarni qurilmaga yuklab olish o‘chirilgan."}
          </p>

          {!site.protection.offlineDownload ? null : progress ? (
            <div className="mb-2">
              <div className="h-1.5 overflow-hidden rounded-full bg-[var(--skin-surface-2)]">
                <div
                  className="h-full bg-[var(--skin-accent)] transition-[width]"
                  style={{ width: `${(progress.done / progress.total) * 100}%` }}
                />
              </div>
              <div className="mt-1 text-xs text-[var(--skin-muted)]">
                Yuklanmoqda… {progress.done}/{progress.total}
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={downloadAll}
              className="mb-2 w-full rounded-lg bg-[var(--skin-accent)] px-3 py-2 text-sm font-semibold text-[var(--skin-accent-text)]"
            >
              {saved ? "Qayta yuklab olish" : "Barcha darslarni yuklab olish"}
            </button>
          )}

          {installPrompt ? (
            <button
              type="button"
              onClick={async () => {
                await installPrompt.prompt();
                await installPrompt.userChoice;
                setInstallPrompt(null);
              }}
              className="w-full rounded-lg border border-[var(--skin-border)] px-3 py-2 text-sm font-medium hover:bg-[var(--skin-surface-2)]"
            >
              Ilova sifatida o‘rnatish
            </button>
          ) : null}

          {updateReady ? (
            <button
              type="button"
              onClick={applyUpdate}
              className="mt-2 w-full rounded-lg border border-[var(--skin-accent)] px-3 py-2 text-sm font-medium text-[var(--skin-accent)]"
            >
              Yangi versiya tayyor — yangilash
            </button>
          ) : null}
        </div>
      ) : null}

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Offline rejim sozlamalari"
        className={`flex items-center gap-2 rounded-full border px-3.5 py-2 text-xs font-medium shadow-lg backdrop-blur ${
          offline
            ? "border-[var(--skin-accent)] bg-[var(--skin-accent)] text-[var(--skin-accent-text)]"
            : "border-[var(--skin-border)] bg-[var(--skin-surface)] text-[var(--skin-text)]"
        }`}
      >
        <span
          aria-hidden
          className={`h-2 w-2 rounded-full ${
            offline ? "bg-[var(--skin-accent-text)]" : saved ? "bg-[var(--skin-accent)]" : "bg-[var(--skin-muted)]"
          }`}
        />
        {offline ? "Oflayn" : updateReady ? "Yangilanish bor" : saved ? "Offline tayyor" : "Offline"}
        {hasNews && !open && !offline && !updateReady ? null : null}
      </button>
    </div>
  );
}
