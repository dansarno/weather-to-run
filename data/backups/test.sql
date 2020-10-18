--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4 (Ubuntu 12.4-1.pgdg16.04+1)
-- Dumped by pg_dump version 12.4 (Ubuntu 12.4-1.pgdg16.04+1)

-- Started on 2020-10-18 16:25:25 BST

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

ALTER TABLE IF EXISTS ONLY public.tweets DROP CONSTRAINT IF EXISTS tweets_outros_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tweets DROP CONSTRAINT IF EXISTS tweets_intros_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tweets DROP CONSTRAINT IF EXISTS tweets_forecasts_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tweets DROP CONSTRAINT IF EXISTS tweets_pkey;
ALTER TABLE IF EXISTS ONLY public.outros DROP CONSTRAINT IF EXISTS outros_pkey;
ALTER TABLE IF EXISTS ONLY public.intros DROP CONSTRAINT IF EXISTS intros_pkey;
ALTER TABLE IF EXISTS ONLY public.forecasts DROP CONSTRAINT IF EXISTS forecasts_pkey;
ALTER TABLE IF EXISTS public.tweets ALTER COLUMN tweets_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.outros ALTER COLUMN outros_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.intros ALTER COLUMN intros_id DROP DEFAULT;
ALTER TABLE IF EXISTS public.forecasts ALTER COLUMN forecasts_id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.tweets_tweets_id_seq;
DROP TABLE IF EXISTS public.tweets;
DROP SEQUENCE IF EXISTS public.outros_outros_id_seq;
DROP TABLE IF EXISTS public.outros;
DROP SEQUENCE IF EXISTS public.intros_intros_id_seq;
DROP TABLE IF EXISTS public.intros;
DROP SEQUENCE IF EXISTS public.forecasts_forecasts_id_seq;
DROP TABLE IF EXISTS public.forecasts;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 206 (class 1259 OID 16139369)
-- Name: forecasts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forecasts (
    used boolean DEFAULT false NOT NULL,
    tone character varying(20) NOT NULL,
    sentence text NOT NULL,
    uses integer DEFAULT 0 NOT NULL,
    forecasts_id integer NOT NULL,
    n_selections integer DEFAULT 1 NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- TOC entry 207 (class 1259 OID 16139395)
-- Name: forecasts_forecasts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forecasts_forecasts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3881 (class 0 OID 0)
-- Dependencies: 207
-- Name: forecasts_forecasts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forecasts_forecasts_id_seq OWNED BY public.forecasts.forecasts_id;


--
-- TOC entry 203 (class 1259 OID 15607891)
-- Name: intros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.intros (
    used boolean DEFAULT false NOT NULL,
    tone character varying(20) NOT NULL,
    sentence text NOT NULL,
    intros_id integer NOT NULL,
    uses integer DEFAULT 0 NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- TOC entry 202 (class 1259 OID 15607889)
-- Name: intros_intros_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.intros_intros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3882 (class 0 OID 0)
-- Dependencies: 202
-- Name: intros_intros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.intros_intros_id_seq OWNED BY public.intros.intros_id;


--
-- TOC entry 204 (class 1259 OID 15656125)
-- Name: outros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outros (
    used boolean DEFAULT false NOT NULL,
    tone character varying(20) NOT NULL,
    sentence text NOT NULL,
    uses integer DEFAULT 0 NOT NULL,
    outros_id integer NOT NULL,
    deleted boolean DEFAULT false NOT NULL
);


--
-- TOC entry 205 (class 1259 OID 15657966)
-- Name: outros_outros_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.outros_outros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3883 (class 0 OID 0)
-- Dependencies: 205
-- Name: outros_outros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.outros_outros_id_seq OWNED BY public.outros.outros_id;


--
-- TOC entry 209 (class 1259 OID 17115984)
-- Name: tweets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tweets (
    tweets_id integer NOT NULL,
    date_posted timestamp without time zone,
    intros_id integer,
    forecasts_id integer,
    outros_id integer,
    sentence text
);


--
-- TOC entry 208 (class 1259 OID 17115982)
-- Name: tweets_tweets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tweets_tweets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3884 (class 0 OID 0)
-- Dependencies: 208
-- Name: tweets_tweets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tweets_tweets_id_seq OWNED BY public.tweets.tweets_id;


--
-- TOC entry 3735 (class 2604 OID 16139397)
-- Name: forecasts forecasts_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forecasts ALTER COLUMN forecasts_id SET DEFAULT nextval('public.forecasts_forecasts_id_seq'::regclass);


--
-- TOC entry 3726 (class 2604 OID 15607895)
-- Name: intros intros_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intros ALTER COLUMN intros_id SET DEFAULT nextval('public.intros_intros_id_seq'::regclass);


--
-- TOC entry 3730 (class 2604 OID 15657968)
-- Name: outros outros_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outros ALTER COLUMN outros_id SET DEFAULT nextval('public.outros_outros_id_seq'::regclass);


--
-- TOC entry 3738 (class 2604 OID 17115987)
-- Name: tweets tweets_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tweets ALTER COLUMN tweets_id SET DEFAULT nextval('public.tweets_tweets_id_seq'::regclass);


--
-- TOC entry 3744 (class 2606 OID 16139405)
-- Name: forecasts forecasts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forecasts
    ADD CONSTRAINT forecasts_pkey PRIMARY KEY (forecasts_id);


--
-- TOC entry 3740 (class 2606 OID 15607900)
-- Name: intros intros_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intros
    ADD CONSTRAINT intros_pkey PRIMARY KEY (intros_id);


--
-- TOC entry 3742 (class 2606 OID 15657989)
-- Name: outros outros_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outros
    ADD CONSTRAINT outros_pkey PRIMARY KEY (outros_id);


--
-- TOC entry 3746 (class 2606 OID 17115992)
-- Name: tweets tweets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tweets
    ADD CONSTRAINT tweets_pkey PRIMARY KEY (tweets_id);


--
-- TOC entry 3748 (class 2606 OID 17115998)
-- Name: tweets tweets_forecasts_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tweets
    ADD CONSTRAINT tweets_forecasts_id_fkey FOREIGN KEY (forecasts_id) REFERENCES public.forecasts(forecasts_id);


--
-- TOC entry 3747 (class 2606 OID 17115993)
-- Name: tweets tweets_intros_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tweets
    ADD CONSTRAINT tweets_intros_id_fkey FOREIGN KEY (intros_id) REFERENCES public.intros(intros_id);


--
-- TOC entry 3749 (class 2606 OID 17116003)
-- Name: tweets tweets_outros_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tweets
    ADD CONSTRAINT tweets_outros_id_fkey FOREIGN KEY (outros_id) REFERENCES public.outros(outros_id);


-- Completed on 2020-10-18 16:25:29 BST

--
-- PostgreSQL database dump complete
--

