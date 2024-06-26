CREATE TABLE IF NOT EXISTS epic_images (
    id SERIAL PRIMARY KEY,
    image_key text,
    image_metadata jsonb,
    image_day text,
    fetched_at TIMESTAMP NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS space_pop (
    id SERIAL PRIMARY KEY,
    pop INTEGER NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS world_pop (
    id SERIAL PRIMARY KEY,
    pop BIGINT NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS video_pop (
    id SERIAL PRIMARY KEY,
    video_key text,
    video_day text,
    space_pop_id INTEGER REFERENCES space_pop,
    world_pop_id INTEGER REFERENCES world_pop
);
