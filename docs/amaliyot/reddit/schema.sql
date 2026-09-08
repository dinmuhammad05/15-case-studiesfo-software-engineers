-- Tayyor. O'zgartirish shart emas.

CREATE TABLE IF NOT EXISTS posts (
    id          BIGSERIAL PRIMARY KEY,
    subreddit   TEXT        NOT NULL,
    title       TEXT        NOT NULL,
    author_id   BIGINT      NOT NULL,
    ups         INTEGER     NOT NULL DEFAULT 0,
    downs       INTEGER     NOT NULL DEFAULT 0,
    deleted     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS posts_sub_created
    ON posts (subreddit, created_at DESC) WHERE NOT deleted;

-- Kompozit birlamchi kalit: ovoz o'z tabiatiga ko'ra idempotent.
-- Sun'iy id ishlatsangiz, navbatdan kelgan takroriy xabar
-- hisoblagichni ikki marta oshiradi.
CREATE TABLE IF NOT EXISTS votes (
    user_id    BIGINT      NOT NULL,
    thing_id   BIGINT      NOT NULL,
    direction  SMALLINT    NOT NULL CHECK (direction IN (-1, 0, 1)),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, thing_id)
);

CREATE INDEX IF NOT EXISTS votes_thing ON votes (thing_id);
