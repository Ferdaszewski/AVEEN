CREATE TABLE IF NOT EXISTS epic_images (
    id SERIAL PRIMARY KEY,
    image_path text,
    image_metadata jsonb,
    fetched_at TIMESTAMP NOT NULL DEFAULT current_timestamp
)

CREATE TABLE IF NOT EXISTS space_pop (
  id SERIAL PRIMARY KEY,
  pop INTEGER NOT NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT current_timestamp
)
