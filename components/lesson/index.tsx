import type { ReactNode } from "react";

/* ============================================================
   Darslar uchun umumiy komponentlar.
   Qoida: hech biri qat'iy rang ishlatmaydi — faqat skin tokenlari.
   Shu sabab bitta komponent 17 ta turli UI ichida ham tabiiy ko'rinadi.
   ============================================================ */

export function Stat({ value, label, hint }: { value: string; label: string; hint?: string }) {
  return (
    <div className="rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface-2)] p-4">
      <div className="font-[family-name:var(--skin-mono)] text-2xl font-semibold text-[var(--skin-accent)]">
        {value}
      </div>
      <div className="mt-1 text-sm font-medium">{label}</div>
      {hint ? <div className="mt-1 text-xs text-[var(--skin-muted)]">{hint}</div> : null}
    </div>
  );
}

export function StatGrid({ children }: { children: ReactNode }) {
  return <div className="my-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{children}</div>;
}

export function Callout({
  type = "info",
  title,
  children,
}: {
  type?: "info" | "ogoh" | "maslahat" | "xato";
  title?: string;
  children: ReactNode;
}) {
  const mark = { info: "i", ogoh: "!", maslahat: "★", xato: "×" }[type];
  return (
    <aside className="my-6 flex gap-3 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
      <span
        aria-hidden
        className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--skin-accent)] text-sm font-bold text-[var(--skin-accent-text)]"
      >
        {mark}
      </span>
      <div className="min-w-0 text-sm leading-relaxed">
        {title ? <div className="mb-1 font-semibold">{title}</div> : null}
        <div className="text-[var(--skin-muted)] [&_a]:text-[var(--skin-accent)] [&_a]:underline [&_code]:font-[family-name:var(--skin-mono)]">
          {children}
        </div>
      </div>
    </aside>
  );
}

/** Evolyutsiya qadami: nima qo'shildi, nima yutdik, nimani yo'qotdik. */
export function Step({
  n,
  title,
  gain,
  cost,
  children,
}: {
  n: number | string;
  title: string;
  gain?: string;
  cost?: string;
  children: ReactNode;
}) {
  return (
    <section className="relative my-7 border-l-2 border-[var(--skin-border)] pl-6">
      <span className="absolute -left-[15px] top-0 flex h-7 w-7 items-center justify-center rounded-full bg-[var(--skin-accent)] font-[family-name:var(--skin-mono)] text-xs font-bold text-[var(--skin-accent-text)]">
        {n}
      </span>
      <h3 className="mt-0 mb-2 text-lg font-semibold">{title}</h3>
      <div className="text-sm leading-relaxed text-[var(--skin-muted)]">{children}</div>
      {(gain || cost) && (
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {gain ? (
            <p className="rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2 text-xs">
              <strong className="text-[var(--skin-accent)]">Yutuq:</strong> {gain}
            </p>
          ) : null}
          {cost ? (
            <p className="rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2 text-xs">
              <strong className="opacity-70">Narxi:</strong> {cost}
            </p>
          ) : null}
        </div>
      )}
    </section>
  );
}

/** Oddiy zanjirli oqim: Client → LB → API → DB */
export function Flow({ nodes, caption }: { nodes: string[]; caption?: string }) {
  return (
    <figure className="my-6 overflow-x-auto rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
      <div className="flex min-w-max items-center gap-2">
        {nodes.map((node, i) => (
          <div key={node} className="flex items-center gap-2">
            <span className="rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2 text-xs font-medium whitespace-nowrap">
              {node}
            </span>
            {i < nodes.length - 1 ? (
              <span aria-hidden className="text-[var(--skin-accent)]">
                →
              </span>
            ) : null}
          </div>
        ))}
      </div>
      {caption ? (
        <figcaption className="mt-3 text-xs text-[var(--skin-muted)]">{caption}</figcaption>
      ) : null}
    </figure>
  );
}

/** Qatlamli arxitektura diagrammasi. */
export function Arch({
  title,
  layers,
}: {
  title?: string;
  layers: { name: string; boxes: string[]; note?: string }[];
}) {
  return (
    <figure className="my-7 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] p-4">
      {title ? (
        <div className="mb-4 text-xs font-semibold tracking-wide text-[var(--skin-muted)] uppercase">
          {title}
        </div>
      ) : null}
      <div className="space-y-3">
        {layers.map((layer, i) => (
          <div key={layer.name}>
            <div className="mb-1.5 font-[family-name:var(--skin-mono)] text-[11px] text-[var(--skin-muted)]">
              {layer.name}
            </div>
            <div className="flex flex-wrap gap-2">
              {layer.boxes.map((b) => (
                <span
                  key={b}
                  className="flex-1 rounded-md border border-[var(--skin-border)] bg-[var(--skin-surface-2)] px-3 py-2.5 text-center text-xs font-medium whitespace-nowrap"
                  style={{ minWidth: "9rem" }}
                >
                  {b}
                </span>
              ))}
            </div>
            {layer.note ? (
              <p className="mt-1.5 text-[11px] text-[var(--skin-muted)]">{layer.note}</p>
            ) : null}
            {i < layers.length - 1 ? (
              <div aria-hidden className="py-1 text-center text-[var(--skin-accent)]">
                ↓
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </figure>
  );
}

/** Trade-off jadvali: yechim / foydasi / narxi. */
export function TradeOffs({ rows }: { rows: { choice: string; pro: string; con: string }[] }) {
  return (
    <div className="my-6 overflow-x-auto rounded-[var(--skin-radius)] border border-[var(--skin-border)]">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-[var(--skin-surface-2)] text-left">
            <th className="p-3 font-semibold">Qaror</th>
            <th className="p-3 font-semibold">Nima yutamiz</th>
            <th className="p-3 font-semibold">Nimani yo'qotamiz</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.choice} className="border-t border-[var(--skin-border)] align-top">
              <td className="p-3 font-medium">{r.choice}</td>
              <td className="p-3 text-[var(--skin-muted)]">{r.pro}</td>
              <td className="p-3 text-[var(--skin-muted)]">{r.con}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Intervyu savoli — javob yopiq holatda, o'quvchi avval o'zi o'ylaydi. */
export function QA({ q, children }: { q: string; children: ReactNode }) {
  return (
    <details className="group my-2.5 rounded-[var(--skin-radius)] border border-[var(--skin-border)] bg-[var(--skin-surface)] px-4 py-3">
      <summary className="cursor-pointer list-none font-medium marker:content-none">
        <span className="mr-2 text-[var(--skin-accent)] group-open:rotate-90 inline-block transition-transform">
          ▸
        </span>
        {q}
      </summary>
      <div className="mt-3 border-t border-[var(--skin-border)] pt-3 text-sm leading-relaxed text-[var(--skin-muted)]">
        {children}
      </div>
    </details>
  );
}

export function Task({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="my-6 rounded-[var(--skin-radius)] border border-dashed border-[var(--skin-accent)] bg-[var(--skin-surface)] p-5">
      <div className="mb-2 text-xs font-semibold tracking-wide text-[var(--skin-accent)] uppercase">
        Amaliyot
      </div>
      <h3 className="mt-0 mb-2 text-base font-semibold">{title}</h3>
      <div className="text-sm leading-relaxed text-[var(--skin-muted)]">{children}</div>
    </section>
  );
}
