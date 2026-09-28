-- Bron dvigateli sxemasi (tayyor, o'zgartirmang).
-- Darsning 2-bo'limi (tun modeli) va 5-bo'lim 1-2-qadamlari.

CREATE TABLE IF NOT EXISTS listings (
  id            INTEGER PRIMARY KEY,
  nightly_minor INTEGER NOT NULL,          -- kechalik narx, sentlarda
  cleaning_minor INTEGER NOT NULL DEFAULT 0,
  min_nights    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS bookings (
  id              INTEGER PRIMARY KEY,
  listing_id      INTEGER NOT NULL REFERENCES listings(id),
  guest_id        INTEGER NOT NULL,
  check_in        TEXT NOT NULL,            -- 'YYYY-MM-DD', kiritiladi
  check_out       TEXT NOT NULL,            -- 'YYYY-MM-DD', kiritilmaydi
  state           TEXT NOT NULL CHECK (state IN ('HOLD','CONFIRMED','EXPIRED','CANCELLED')),
  hold_expires_at REAL,                     -- HOLD uchun: shu lahzadan keyin kuchsiz
  amount_minor    INTEGER NOT NULL,
  idem_key        TEXT NOT NULL UNIQUE,
  created_at      REAL NOT NULL
);

-- Asosiy kafolat: bitta e'lonning bitta tuni — bitta qator.
CREATE TABLE IF NOT EXISTS booked_nights (
  listing_id INTEGER NOT NULL,
  night      TEXT NOT NULL,                 -- 'YYYY-MM-DD'
  booking_id INTEGER NOT NULL REFERENCES bookings(id),
  PRIMARY KEY (listing_id, night)
);
CREATE INDEX IF NOT EXISTS booked_nights_booking ON booked_nights(booking_id);

-- Ikki tomonlama kitob (darsning 5-bo'lim 5-qadami, 8-bo'lim).
-- Har txn_id bo'yicha amount_minor yig'indisi nol bo'lishi shart.
CREATE TABLE IF NOT EXISTS ledger (
  id           INTEGER PRIMARY KEY,
  txn_id       TEXT NOT NULL,
  booking_id   INTEGER NOT NULL,
  account      TEXT NOT NULL,               -- 'guest_payments' | 'host_payable' | 'platform_fees'
  amount_minor INTEGER NOT NULL,
  created_at   REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ledger_booking ON ledger(booking_id);

-- Soxta to'lov provayderi holati (db.FakeProvider ishlatadi).
CREATE TABLE IF NOT EXISTS provider_ops (
  key          TEXT PRIMARY KEY,            -- idempotentlik kaliti
  kind         TEXT NOT NULL,               -- 'charge' | 'refund'
  amount_minor INTEGER NOT NULL,
  calls        INTEGER NOT NULL DEFAULT 1   -- necha marta chaqirildi (takrorlar ham)
);
