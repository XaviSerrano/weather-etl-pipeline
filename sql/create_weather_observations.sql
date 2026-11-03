CREATE TABLE IF NOT EXISTS public.weather_observations (
    extracted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    temperature_c DOUBLE PRECISION NOT NULL,
    feels_like_c DOUBLE PRECISION NOT NULL,
    humidity_pct INTEGER NOT NULL CHECK (humidity_pct BETWEEN 0 AND 100),
    pressure_hpa INTEGER NOT NULL,
    weather_description TEXT NOT NULL,
    wind_speed_m_s DOUBLE PRECISION NOT NULL,
    cloudiness_pct INTEGER NOT NULL CHECK (cloudiness_pct BETWEEN 0 AND 100),
    observed_at_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT weather_observations_unique
        UNIQUE (extracted_at, city, country)
);
