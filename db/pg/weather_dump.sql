--
-- PostgreSQL database dump
--

\restrict 1R5HXV0p0n25z1Jl6lp74OSeKp3gqd2QxuqXrjYi2HdQlKeT1Ijf7ehAKwDOxo1

-- Dumped from database version 16.10 (Debian 16.10-1.pgdg13+1)
-- Dumped by pg_dump version 16.10 (Debian 16.10-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: weather
--

CREATE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.ingested_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_modified_column() OWNER TO weather;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: weather_daily; Type: TABLE; Schema: public; Owner: weather
--

CREATE TABLE public.weather_daily (
    date date NOT NULL,
    temp_max_c numeric(5,2),
    temp_min_c numeric(5,2),
    temp_max_f numeric(5,2),
    temp_min_f numeric(5,2),
    app_temp_max_c numeric(5,2),
    app_temp_min_c numeric(5,2),
    precip_mm numeric(8,2),
    rain_mm numeric(8,2),
    showers_mm numeric(8,2),
    snowfall_mm numeric(8,2),
    precip_hours numeric(4,2),
    sunrise timestamp with time zone,
    sunset timestamp with time zone,
    daylight_sec integer,
    sunshine_sec integer,
    shortwave_radiation_mj_m2 numeric(10,3),
    wind_max_kmh numeric(6,2),
    wind_gust_max_kmh numeric(6,2),
    wind_dir_deg numeric(6,2),
    weather_code integer,
    et0_mm numeric(8,3),
    uv_index_max numeric(5,2),
    uv_index_clear_sky_max numeric(5,2),
    source text DEFAULT 'open-meteo'::text NOT NULL,
    ingested_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_app_temp_max_c CHECK (((app_temp_max_c IS NULL) OR ((app_temp_max_c > ('-120'::integer)::numeric) AND (app_temp_max_c < (80)::numeric)))),
    CONSTRAINT chk_app_temp_min_c CHECK (((app_temp_min_c IS NULL) OR ((app_temp_min_c > ('-120'::integer)::numeric) AND (app_temp_min_c < (80)::numeric)))),
    CONSTRAINT chk_daylight_sec CHECK (((daylight_sec IS NULL) OR ((daylight_sec >= 0) AND (daylight_sec <= 86400)))),
    CONSTRAINT chk_et0_mm CHECK (((et0_mm IS NULL) OR (et0_mm >= (0)::numeric))),
    CONSTRAINT chk_precip_hours CHECK (((precip_hours IS NULL) OR ((precip_hours >= (0)::numeric) AND (precip_hours <= (24)::numeric)))),
    CONSTRAINT chk_precip_mm CHECK (((precip_mm IS NULL) OR (precip_mm >= (0)::numeric))),
    CONSTRAINT chk_rain_mm CHECK (((rain_mm IS NULL) OR (rain_mm >= (0)::numeric))),
    CONSTRAINT chk_shortwave_radiation CHECK (((shortwave_radiation_mj_m2 IS NULL) OR (shortwave_radiation_mj_m2 >= (0)::numeric))),
    CONSTRAINT chk_showers_mm CHECK (((showers_mm IS NULL) OR (showers_mm >= (0)::numeric))),
    CONSTRAINT chk_snowfall_mm CHECK (((snowfall_mm IS NULL) OR (snowfall_mm >= (0)::numeric))),
    CONSTRAINT chk_sunshine_sec CHECK (((sunshine_sec IS NULL) OR ((sunshine_sec >= 0) AND (sunshine_sec <= 86400)))),
    CONSTRAINT chk_temp_max_c CHECK (((temp_max_c IS NULL) OR ((temp_max_c > ('-100'::integer)::numeric) AND (temp_max_c < (70)::numeric)))),
    CONSTRAINT chk_temp_min_c CHECK (((temp_min_c IS NULL) OR ((temp_min_c > ('-120'::integer)::numeric) AND (temp_min_c < (70)::numeric)))),
    CONSTRAINT chk_uv_index_clear_sky_max CHECK (((uv_index_clear_sky_max IS NULL) OR (uv_index_clear_sky_max >= (0)::numeric))),
    CONSTRAINT chk_uv_index_max CHECK (((uv_index_max IS NULL) OR (uv_index_max >= (0)::numeric))),
    CONSTRAINT chk_weather_code CHECK (((weather_code IS NULL) OR ((weather_code >= 0) AND (weather_code <= 99)))),
    CONSTRAINT chk_wind_dir_deg CHECK (((wind_dir_deg IS NULL) OR ((wind_dir_deg >= (0)::numeric) AND (wind_dir_deg <= (360)::numeric)))),
    CONSTRAINT chk_wind_gust_max_kmh CHECK (((wind_gust_max_kmh IS NULL) OR (wind_gust_max_kmh >= (0)::numeric))),
    CONSTRAINT chk_wind_max_kmh CHECK (((wind_max_kmh IS NULL) OR (wind_max_kmh >= (0)::numeric)))
);


ALTER TABLE public.weather_daily OWNER TO weather;

--
-- Name: TABLE weather_daily; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON TABLE public.weather_daily IS 'Daily weather data from Open-Meteo API';


--
-- Name: COLUMN weather_daily.date; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.date IS 'Date of the weather record (YYYY-MM-DD)';


--
-- Name: COLUMN weather_daily.temp_max_c; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.temp_max_c IS 'Maximum temperature in Celsius';


--
-- Name: COLUMN weather_daily.temp_min_c; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.temp_min_c IS 'Minimum temperature in Celsius';


--
-- Name: COLUMN weather_daily.temp_max_f; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.temp_max_f IS 'Maximum temperature in Fahrenheit';


--
-- Name: COLUMN weather_daily.temp_min_f; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.temp_min_f IS 'Minimum temperature in Fahrenheit';


--
-- Name: COLUMN weather_daily.app_temp_max_c; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.app_temp_max_c IS 'Apparent (feels-like) maximum temperature in Celsius';


--
-- Name: COLUMN weather_daily.app_temp_min_c; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.app_temp_min_c IS 'Apparent (feels-like) minimum temperature in Celsius';


--
-- Name: COLUMN weather_daily.precip_mm; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.precip_mm IS 'Total precipitation in millimeters';


--
-- Name: COLUMN weather_daily.rain_mm; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.rain_mm IS 'Rainfall in millimeters';


--
-- Name: COLUMN weather_daily.showers_mm; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.showers_mm IS 'Shower precipitation in millimeters';


--
-- Name: COLUMN weather_daily.snowfall_mm; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.snowfall_mm IS 'Snowfall in millimeters';


--
-- Name: COLUMN weather_daily.precip_hours; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.precip_hours IS 'Number of hours with precipitation';


--
-- Name: COLUMN weather_daily.sunrise; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.sunrise IS 'Sunrise time (timestamp with timezone)';


--
-- Name: COLUMN weather_daily.sunset; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.sunset IS 'Sunset time (timestamp with timezone)';


--
-- Name: COLUMN weather_daily.daylight_sec; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.daylight_sec IS 'Daylight duration in seconds';


--
-- Name: COLUMN weather_daily.sunshine_sec; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.sunshine_sec IS 'Sunshine duration in seconds';


--
-- Name: COLUMN weather_daily.shortwave_radiation_mj_m2; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.shortwave_radiation_mj_m2 IS 'Shortwave solar radiation in megajoules per square meter';


--
-- Name: COLUMN weather_daily.wind_max_kmh; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.wind_max_kmh IS 'Maximum wind speed in kilometers per hour';


--
-- Name: COLUMN weather_daily.wind_gust_max_kmh; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.wind_gust_max_kmh IS 'Maximum wind gust speed in kilometers per hour';


--
-- Name: COLUMN weather_daily.wind_dir_deg; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.wind_dir_deg IS 'Wind direction in degrees (0-360)';


--
-- Name: COLUMN weather_daily.weather_code; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.weather_code IS 'WMO weather code (0-99)';


--
-- Name: COLUMN weather_daily.et0_mm; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.et0_mm IS 'Reference evapotranspiration in millimeters';


--
-- Name: COLUMN weather_daily.uv_index_max; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.uv_index_max IS 'Maximum UV index';


--
-- Name: COLUMN weather_daily.uv_index_clear_sky_max; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.uv_index_clear_sky_max IS 'Maximum UV index under clear sky conditions';


--
-- Name: COLUMN weather_daily.source; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.source IS 'Data source identifier';


--
-- Name: COLUMN weather_daily.ingested_at; Type: COMMENT; Schema: public; Owner: weather
--

COMMENT ON COLUMN public.weather_daily.ingested_at IS 'Timestamp when the record was last updated';


--
-- Data for Name: weather_daily; Type: TABLE DATA; Schema: public; Owner: weather
--

COPY public.weather_daily (date, temp_max_c, temp_min_c, temp_max_f, temp_min_f, app_temp_max_c, app_temp_min_c, precip_mm, rain_mm, showers_mm, snowfall_mm, precip_hours, sunrise, sunset, daylight_sec, sunshine_sec, shortwave_radiation_mj_m2, wind_max_kmh, wind_gust_max_kmh, wind_dir_deg, weather_code, et0_mm, uv_index_max, uv_index_clear_sky_max, source, ingested_at) FROM stdin;
2025-08-01	24.10	13.00	75.38	55.40	23.90	11.30	0.20	0.20	0.00	0.00	2.00	2025-08-01 05:26:00+00	2025-08-01 20:42:00+00	54977	50330	24.350	13.10	31.30	288.00	51	4.670	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-02	26.20	14.90	79.16	58.82	27.70	14.60	0.00	0.00	0.00	0.00	0.00	2025-08-02 05:27:00+00	2025-08-02 20:40:00+00	54795	50252	24.060	7.80	14.80	239.00	1	4.520	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-03	26.80	17.60	80.24	63.68	27.00	18.20	0.00	0.00	0.00	0.00	0.00	2025-08-03 05:29:00+00	2025-08-03 20:39:00+00	54610	50172	22.840	10.10	28.40	55.00	3	4.730	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-04	28.00	18.30	82.40	64.94	27.40	19.30	0.00	0.00	0.00	0.00	0.00	2025-08-04 05:30:00+00	2025-08-04 20:37:00+00	54422	50092	23.150	10.70	30.60	343.00	2	5.150	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-05	28.80	17.60	83.84	63.68	28.90	18.10	0.10	0.10	0.00	0.00	1.00	2025-08-05 05:32:00+00	2025-08-05 20:35:00+00	54233	50011	23.380	11.30	32.40	288.00	51	4.990	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-06	28.20	19.00	82.76	66.20	29.70	20.00	2.90	2.90	0.00	0.00	3.00	2025-08-06 05:33:00+00	2025-08-06 20:34:00+00	54041	46285	19.890	20.40	49.00	247.00	61	3.940	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-07	22.80	14.30	73.04	57.74	21.60	13.50	0.00	0.00	0.00	0.00	0.00	2025-08-07 05:35:00+00	2025-08-07 20:32:00+00	53848	49706	24.430	13.90	32.80	331.00	3	4.520	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-08	23.30	13.60	73.94	56.48	23.90	14.10	0.00	0.00	0.00	0.00	0.00	2025-08-08 05:36:00+00	2025-08-08 20:30:00+00	53653	46166	23.290	8.50	21.60	167.00	3	4.290	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-09	24.80	15.30	76.64	59.54	23.90	14.50	4.00	4.00	0.00	0.00	4.00	2025-08-09 05:38:00+00	2025-08-09 20:28:00+00	53457	47845	22.520	13.00	33.80	296.00	63	4.500	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-10	26.60	14.00	79.88	57.20	26.10	13.80	0.10	0.10	0.00	0.00	1.00	2025-08-10 05:39:00+00	2025-08-10 20:27:00+00	53259	49161	23.700	10.90	24.80	262.00	51	4.570	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-11	22.20	16.00	71.96	60.80	19.60	14.80	4.50	4.50	0.00	0.00	2.00	2025-08-11 05:41:00+00	2025-08-11 20:25:00+00	53061	46258	20.520	20.10	49.70	306.00	63	4.190	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-12	23.80	13.10	74.84	55.58	21.80	11.60	0.00	0.00	0.00	0.00	0.00	2025-08-12 05:42:00+00	2025-08-12 20:23:00+00	52861	46265	19.590	14.60	37.10	301.00	3	4.250	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-13	25.70	13.90	78.26	57.02	24.50	12.80	0.00	0.00	0.00	0.00	0.00	2025-08-13 05:44:00+00	2025-08-13 20:21:00+00	52661	48604	21.470	8.90	27.00	310.00	2	4.250	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-14	26.40	14.50	79.52	58.10	24.70	14.20	0.00	0.00	0.00	0.00	0.00	2025-08-14 05:45:00+00	2025-08-14 20:19:00+00	52461	48416	21.660	12.80	34.20	349.00	2	4.680	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-15	24.10	15.00	75.38	59.00	22.80	14.20	0.00	0.00	0.00	0.00	0.00	2025-08-15 05:47:00+00	2025-08-15 20:17:00+00	52260	48227	23.550	11.50	32.80	6.00	0	4.670	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-16	27.00	14.70	80.60	58.46	26.10	14.70	0.00	0.00	0.00	0.00	0.00	2025-08-16 05:48:00+00	2025-08-16 20:16:00+00	52056	48036	23.310	10.50	27.70	217.00	0	4.840	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-17	26.50	17.30	79.70	63.14	26.30	16.30	0.20	0.20	0.00	0.00	2.00	2025-08-17 05:50:00+00	2025-08-17 20:14:00+00	51851	47690	20.410	14.80	38.90	286.00	51	4.810	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-18	21.50	14.10	70.70	57.38	19.00	12.50	0.20	0.20	0.00	0.00	2.00	2025-08-18 05:51:00+00	2025-08-18 20:12:00+00	51643	46042	18.910	15.00	39.60	327.00	51	4.000	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-19	23.40	11.20	74.12	52.16	20.80	9.40	0.00	0.00	0.00	0.00	0.00	2025-08-19 05:53:00+00	2025-08-19 20:10:00+00	51434	47002	20.600	12.00	32.00	291.00	3	3.990	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-20	24.30	13.80	75.74	56.84	21.90	12.10	0.00	0.00	0.00	0.00	0.00	2025-08-20 05:54:00+00	2025-08-20 20:08:00+00	51223	39456	18.180	12.70	33.80	232.00	3	3.970	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-21	26.50	15.90	79.70	60.62	25.30	14.70	1.00	1.00	0.00	0.00	2.00	2025-08-21 05:56:00+00	2025-08-21 20:06:00+00	51010	42982	20.350	12.50	37.40	253.00	53	4.500	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-22	23.80	16.20	74.84	61.16	25.10	16.10	5.10	5.10	0.00	0.00	10.00	2025-08-22 05:57:00+00	2025-08-22 20:04:00+00	50796	10800	8.520	13.20	29.20	20.00	61	1.770	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-23	20.90	14.30	69.62	57.74	19.10	13.60	0.30	0.30	0.00	0.00	3.00	2025-08-23 05:59:00+00	2025-08-23 20:02:00+00	50581	41075	17.330	13.40	34.60	325.00	51	3.300	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-24	17.50	11.50	63.50	52.70	15.30	9.10	2.50	2.50	0.00	0.00	6.00	2025-08-24 06:00:00+00	2025-08-24 20:00:00+00	50365	28663	15.590	16.70	38.20	270.00	53	2.720	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-25	19.10	10.10	66.38	50.18	15.80	7.20	0.00	0.00	0.00	0.00	0.00	2025-08-25 06:02:00+00	2025-08-25 19:57:00+00	50147	44987	20.290	19.20	45.70	259.00	3	3.940	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-26	17.50	10.70	63.50	51.26	14.50	8.60	7.70	7.70	0.00	0.00	9.00	2025-08-26 06:03:00+00	2025-08-26 19:55:00+00	49929	33695	15.050	18.80	46.80	257.00	63	2.710	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-27	22.50	10.70	72.50	51.26	20.00	8.40	0.00	0.00	0.00	0.00	0.00	2025-08-27 06:05:00+00	2025-08-27 19:53:00+00	49711	44450	20.050	11.70	32.40	265.00	3	3.820	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-28	25.10	11.30	77.18	52.34	24.00	10.00	0.00	0.00	0.00	0.00	0.00	2025-08-28 06:06:00+00	2025-08-28 19:51:00+00	49492	44207	21.200	12.00	24.10	140.00	3	4.010	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-29	29.00	15.50	84.20	59.90	25.90	13.80	0.00	0.00	0.00	0.00	0.00	2025-08-29 06:08:00+00	2025-08-29 19:49:00+00	49273	44070	21.320	17.50	44.60	168.00	1	5.380	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-30	30.30	16.60	86.54	61.88	27.80	14.40	0.00	0.00	0.00	0.00	0.00	2025-08-30 06:09:00+00	2025-08-30 19:47:00+00	49054	43873	21.270	14.90	40.00	150.00	0	5.710	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-08-31	31.40	17.60	88.52	63.68	30.60	16.50	0.00	0.00	0.00	0.00	0.00	2025-08-31 06:11:00+00	2025-08-31 19:45:00+00	48834	43528	20.320	10.50	27.70	79.00	0	4.820	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-01	30.30	19.00	86.54	66.20	28.70	19.30	0.10	0.10	0.00	0.00	1.00	2025-09-01 06:12:00+00	2025-09-01 19:43:00+00	48615	41610	17.260	16.70	42.10	24.00	51	4.780	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-02	24.70	17.30	76.46	63.14	23.60	16.70	0.00	0.00	0.00	0.00	0.00	2025-09-02 06:14:00+00	2025-09-02 19:40:00+00	48396	43313	20.410	14.90	33.50	15.00	0	4.250	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-03	24.80	13.90	76.64	57.02	24.20	13.70	0.00	0.00	0.00	0.00	0.00	2025-09-03 06:15:00+00	2025-09-03 19:38:00+00	48177	43312	20.510	9.00	19.40	55.00	1	3.740	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-04	25.80	14.40	78.44	57.92	25.10	15.20	0.00	0.00	0.00	0.00	0.00	2025-09-04 06:17:00+00	2025-09-04 19:36:00+00	47959	43200	19.970	9.30	21.20	64.00	1	3.810	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-05	23.90	13.90	75.02	57.02	22.50	13.20	0.00	0.00	0.00	0.00	0.00	2025-09-05 06:19:00+00	2025-09-05 19:34:00+00	47740	43247	19.660	8.80	24.10	98.00	0	3.790	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-06	23.70	14.30	74.66	57.74	22.40	14.30	0.00	0.00	0.00	0.00	0.00	2025-09-06 06:20:00+00	2025-09-06 19:32:00+00	47519	43200	18.920	10.80	28.80	72.00	3	3.750	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-07	22.60	13.30	72.68	55.94	20.50	12.10	0.00	0.00	0.00	0.00	0.00	2025-09-07 06:22:00+00	2025-09-07 19:30:00+00	47297	36854	16.130	13.10	35.30	41.00	3	3.520	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-08	23.90	13.70	75.02	56.66	23.60	13.10	0.90	0.90	0.00	0.00	1.00	2025-09-08 06:23:00+00	2025-09-08 19:27:00+00	47074	42553	15.820	16.20	43.90	51.00	53	3.040	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-09	24.20	13.80	75.56	56.84	23.70	13.00	0.00	0.00	0.00	0.00	0.00	2025-09-09 06:25:00+00	2025-09-09 19:25:00+00	46850	42816	18.220	10.70	28.80	71.00	0	3.420	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-10	25.10	15.70	77.18	60.26	25.40	16.40	0.10	0.10	0.00	0.00	1.00	2025-09-10 06:26:00+00	2025-09-10 19:23:00+00	46625	42684	17.450	13.10	33.80	89.00	51	3.530	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-11	22.70	13.90	72.86	57.02	19.40	11.90	0.00	0.00	0.00	0.00	0.00	2025-09-11 06:28:00+00	2025-09-11 19:21:00+00	46399	42552	18.730	15.00	38.20	117.00	3	4.130	\N	\N	open-meteo	2025-09-16 19:02:41+00
2025-09-12	23.00	13.10	73.40	55.58	19.80	10.80	0.00	0.00	0.00	0.00	0.00	2025-09-12 06:29:00+00	2025-09-12 19:19:00+00	46173	39012	15.610	14.30	37.80	124.00	3	3.880	\N	\N	open-meteo	2025-09-16 19:02:42+00
2025-09-13	22.90	15.00	73.22	59.00	20.60	13.30	0.00	0.00	0.00	0.00	0.00	2025-09-13 06:31:00+00	2025-09-13 19:16:00+00	45947	26860	10.540	14.00	34.60	122.00	3	3.070	\N	\N	open-meteo	2025-09-16 19:02:42+00
\.


--
-- Name: weather_daily weather_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: weather
--

ALTER TABLE ONLY public.weather_daily
    ADD CONSTRAINT weather_daily_pkey PRIMARY KEY (date);


--
-- Name: idx_weather_daily_code; Type: INDEX; Schema: public; Owner: weather
--

CREATE INDEX idx_weather_daily_code ON public.weather_daily USING btree (weather_code);


--
-- Name: weather_daily update_weather_daily_ingested_at; Type: TRIGGER; Schema: public; Owner: weather
--

CREATE TRIGGER update_weather_daily_ingested_at BEFORE UPDATE ON public.weather_daily FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- PostgreSQL database dump complete
--

\unrestrict 1R5HXV0p0n25z1Jl6lp74OSeKp3gqd2QxuqXrjYi2HdQlKeT1Ijf7ehAKwDOxo1

