-- Tayyor. O'zgartirish shart emas.

CREATE TABLE IF NOT EXISTS channels (
    id         TEXT PRIMARY KEY,
    name       TEXT        NOT NULL,
    -- ts tayinlashda monotonlikni ta'minlash uchun (darsning 5.5-qadami)
    last_ts    NUMERIC(20, 6) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
    channel_id    TEXT           NOT NULL REFERENCES channels(id),
    -- ts: identifikator, tartib kaliti va kursor — bir vaqtda.
    -- NUMERIC, float emas: float64 16 raqamni aniq saqlay olmaydi.
    ts            NUMERIC(20, 6) NOT NULL,
    user_id       TEXT           NOT NULL,
    text          TEXT           NOT NULL,
    -- Dublikatni tanish uchun (darsning 5.6-qadami)
    client_msg_id UUID           NOT NULL,
    PRIMARY KEY (channel_id, ts)
);

-- Quvib yetish so'rovi shu indeksdan foydalanadi:
--   WHERE channel_id = ? AND ts > ? ORDER BY ts LIMIT 200
-- Birlamchi kalit allaqachon (channel_id, ts) — qo'shimcha indeks kerak emas.

-- Idempotentlik: bir xil client_msg_id ikkinchi marta yozilmaydi.
CREATE UNIQUE INDEX IF NOT EXISTS messages_client_msg
    ON messages (channel_id, client_msg_id);
