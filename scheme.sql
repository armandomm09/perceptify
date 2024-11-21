--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: belt_reading; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.belt_reading (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    gyro_x double precision,
    gyro_y double precision,
    gyro_z double precision,
    accel_x double precision,
    accel_y double precision,
    accel_z double precision,
    fall boolean
);


ALTER TABLE public.belt_reading OWNER TO postgres;

--
-- Name: belt_reading_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.belt_reading_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.belt_reading_id_seq OWNER TO postgres;

--
-- Name: belt_reading_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.belt_reading_id_seq OWNED BY public.belt_reading.id;


--
-- Name: emotion_detection; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emotion_detection (
    id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    img_id integer,
    dominant_emotion character varying(20) NOT NULL,
    angry_probability double precision NOT NULL,
    disgust_probability double precision NOT NULL,
    fear_probability double precision NOT NULL,
    happy_probability double precision NOT NULL,
    neutral_probability double precision NOT NULL,
    sad_probability double precision NOT NULL,
    surprise_probability double precision NOT NULL,
    video_id integer
);


ALTER TABLE public.emotion_detection OWNER TO postgres;

--
-- Name: emotion_detection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.emotion_detection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.emotion_detection_id_seq OWNER TO postgres;

--
-- Name: emotion_detection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.emotion_detection_id_seq OWNED BY public.emotion_detection.id;


--
-- Name: emotion_videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emotion_videos (
    id integer NOT NULL,
    path character varying(255) NOT NULL,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    duration_seconds integer NOT NULL
);


ALTER TABLE public.emotion_videos OWNER TO postgres;

--
-- Name: emotion_videos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.emotion_videos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.emotion_videos_id_seq OWNER TO postgres;

--
-- Name: emotion_videos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.emotion_videos_id_seq OWNED BY public.emotion_videos.id;


--
-- Name: fall_detection; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fall_detection (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    fall_detected boolean,
    confidence double precision,
    num_people_detected integer,
    img_id integer
);


ALTER TABLE public.fall_detection OWNER TO postgres;

--
-- Name: fall_detection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fall_detection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fall_detection_id_seq OWNER TO postgres;

--
-- Name: fall_detection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fall_detection_id_seq OWNED BY public.fall_detection.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    path character varying(255) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_img_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_img_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.images_img_id_seq OWNER TO postgres;

--
-- Name: images_img_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_img_id_seq OWNED BY public.images.id;


--
-- Name: belt_reading id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_reading ALTER COLUMN id SET DEFAULT nextval('public.belt_reading_id_seq'::regclass);


--
-- Name: emotion_detection id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_detection ALTER COLUMN id SET DEFAULT nextval('public.emotion_detection_id_seq'::regclass);


--
-- Name: emotion_videos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_videos ALTER COLUMN id SET DEFAULT nextval('public.emotion_videos_id_seq'::regclass);


--
-- Name: fall_detection id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fall_detection ALTER COLUMN id SET DEFAULT nextval('public.fall_detection_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_img_id_seq'::regclass);


--
-- Name: belt_reading belt_reading_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_reading
    ADD CONSTRAINT belt_reading_pkey PRIMARY KEY (id);


--
-- Name: emotion_detection emotion_detection_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_detection
    ADD CONSTRAINT emotion_detection_pkey PRIMARY KEY (id);


--
-- Name: emotion_videos emotion_videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_videos
    ADD CONSTRAINT emotion_videos_pkey PRIMARY KEY (id);


--
-- Name: fall_detection fall_detection_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fall_detection
    ADD CONSTRAINT fall_detection_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: emotion_detection emotion_detection_img_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_detection
    ADD CONSTRAINT emotion_detection_img_id_fkey FOREIGN KEY (img_id) REFERENCES public.images(id) ON DELETE SET NULL;


--
-- Name: fall_detection fall_detection_img_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fall_detection
    ADD CONSTRAINT fall_detection_img_id_fkey FOREIGN KEY (img_id) REFERENCES public.images(id);


--
-- Name: emotion_detection fk_video_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emotion_detection
    ADD CONSTRAINT fk_video_id FOREIGN KEY (video_id) REFERENCES public.emotion_videos(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

