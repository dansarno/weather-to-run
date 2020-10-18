--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4 (Ubuntu 12.4-1.pgdg16.04+1)
-- Dumped by pg_dump version 12.4 (Ubuntu 12.4-1.pgdg16.04+1)

-- Started on 2020-10-18 18:11:57 BST

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
-- TOC entry 3889 (class 0 OID 0)
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
-- TOC entry 3890 (class 0 OID 0)
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
-- TOC entry 3891 (class 0 OID 0)
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
-- TOC entry 3892 (class 0 OID 0)
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
-- TOC entry 3880 (class 0 OID 16139369)
-- Dependencies: 206
-- Data for Name: forecasts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forecasts (used, tone, sentence, uses, forecasts_id, n_selections, deleted) FROM stdin;
f	amber	If I had to pick (I know, I know, that's my job) I'd run in the NOUN.	0	29	1	f
f	amber	I got NOUN, NOUN and NOUN. In that order.	0	44	3	f
f	amber	Your best option is in the NOUN.	0	30	1	f
f	amber	By my lights either A(N) NOUN or NOUN run will do.	0	39	2	f
f	amber	Tough to judge this one but a run in the NOUN or NOUN will be alright I reckon.	0	40	2	f
f	amber	Less than ideal but I'd say A(N) NOUN run is best tomorrow.	0	27	1	f
f	green	Looks like it's best to run in the NOUN.	0	4	1	f
f	green	Question: When should you run tomorrow? Answer: NOUN and NOUN are both great.	0	18	2	f
f	green	It's the NOUN or NOUN, take ya pick.	0	15	2	f
f	amber	Better running weather is in the NOUN.	0	28	1	f
f	amber	If you're going to run, the NOUN and NOUN are your only two options.	0	38	2	f
f	amber	You got two okay-ish options: NOUN or NOUN.	0	41	2	f
f	amber	Not the best out there, equally iffy in the NOUN, NOUN and NOUN.	0	42	3	f
f	amber	Well it has been better and honestly it up to you when you run. Less than best weather all day.	0	43	3	f
f	amber	Not perfect out there I'm afraid, equally meh throughout the day.	0	45	3	f
f	red	If you insist, A(N) NOUN run is the "best" time to run.	0	46	1	f
f	red	Bad across the board but the NOUN is the better time to run.	0	47	1	f
f	red	The NOUN is the best of a real bad bunch.	0	48	1	f
f	red	My hands are tied, I have to pick a best time to run, it's my job... NOUN is the "best".	0	49	1	f
f	red	... errmmm... I'm going to go with A(N) NOUN run. But don't hold me to it!	0	50	1	f
f	red	Drum roll... NOUN is the best time to run. That was a tough one!	0	51	1	f
f	red	Run in the NOUN if you really have to.	0	52	1	f
f	red	When can I run did I hear you say? It's complicated tbh, but in the NOUN is your best option.	0	53	1	f
f	red	If you insist, A(N) NOUN or A(N) NOUN run are the "best" times to run.	0	54	2	f
f	amber	The NOUN is best for a run, that's my best guess.	0	33	1	f
f	amber	Q: When is the best time to run? A: The NOUN, I think 🤷‍♂️	0	32	1	f
f	amber	I'm going to take a guess at... A(N) NOUN run.	0	34	1	f
f	amber	If you're going to run, the NOUN is looking like the only option. Well, unless you love bad weather!	0	35	1	f
f	amber	Not the nicest but the NOUN should have the better running conditions.	0	31	1	f
f	amber	I've done a few calculations and I reckon A(N) NOUN or NOUN run are looking alright.	0	37	2	f
f	green	The NOUN is looking best. Not happy with that? The NOUN is also alright I reckon.	0	19	2	f
f	green	According to my sources, the weather is looking good for A(N) NOUN or NOUN run.	0	16	2	f
f	green	Good all round, but the running order is 1st NOUN, 2nd NOUN and 3rd NOUN.	0	20	3	f
f	green	Looking great in the NOUN, I'd run then if I were you!	0	9	1	f
f	green	Glorious out there! The great weather gods are telling me it's looking good all day!	0	22	3	f
f	green	Wanna run tomorrow? The NOUN is looking like the best time to go out.	0	6	1	f
f	green	My pick: A(N) NOUN run.	0	12	1	f
f	green	The NOUN is the best time to run I reckon.	0	5	1	f
f	amber	Well, quite the day! But A(N) NOUN or NOUN run are looking like your best options.	0	36	2	f
f	green	You don't need a bot, run whenever you like, good weather all round.	0	24	3	f
f	green	1st: NOUN, 2nd: NOUN, 3rd: NOUN - but honestly run when ya like.	0	26	3	f
f	green	I got NOUN, NOUN and NOUN. In that order.	0	25	3	f
f	green	All good options but in first place is NOUN, followed by NOUN and then NOUN (but honestly its up to you).	0	21	3	f
f	green	You're in luck, good weather all round!	0	23	3	f
f	red	Bad across the board but the NOUN or the NOUN are the better times to run.	0	55	2	f
f	red	The NOUN or the NOUN are the best of a real bad bunch.	0	56	2	f
f	red	My hands are tied, I have to pick a best time to run, it's my job... NOUN or NOUN are the "best".	0	57	2	f
f	red	... errmmm... I'm going to go with A(N) NOUN run. But it's all bad out there!	0	58	2	f
f	red	Drum roll... the NOUN is the best time to run... or the NOUN. That was a tough one!	0	59	2	f
f	red	Run in the NOUN or NOUN if you really really have to.	0	60	2	f
f	red	When can I run did I hear you say? It's complicated tbh, but in the NOUN or the NOUN are your "best" options.	0	61	2	f
f	red	Equally crap all day, I'm sorry!	0	62	3	f
f	red	I'm sure you don't need me to say but it's less than favourable running conditions out there all day.	0	63	3	f
f	red	You're not going to like this, but I'm informed it'll poor weather all day.	0	64	3	f
f	red	By my calculations, it won't be good running weather condition all day!	0	65	3	f
f	red	Bad all day, but if I had to pick the "best" time to run I'd say it will be the NOUN	0	66	3	f
f	green	I've crunched the numbers... NOUN is the answer you're looking for.	0	13	1	f
f	green	The NOUN looks lovely for a run.	0	8	1	f
f	green	Either in the NOUN or NOUN works, go for it!	0	14	2	f
f	green	You got options, two in fact. In the NOUN or NOUN are both looking like good times to run.	0	17	2	f
f	green	Q: When is the best time to run? A: NOUN	0	10	1	f
f	green	The answer iiiiss [drum roll].... NOUN!	0	7	1	f
f	green	All green for a run in the NOUN 👌	0	11	1	f
\.


--
-- TOC entry 3877 (class 0 OID 15607891)
-- Dependencies: 203
-- Data for Name: intros; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.intros (used, tone, sentence, intros_id, uses, deleted) FROM stdin;
f	green	Whaddup.	11	0	f
f	amber	Here's the deal...	51	0	f
f	amber	Could be worse.	52	0	f
f	amber	Neither here nor there this one.	55	0	f
f	amber	Mixed bag coming up.	53	0	f
f	amber	Hmmm, tricky...	50	0	f
f	amber	[Incoming Alert]	43	0	f
f	amber	Now then.	40	0	f
f	amber	So, you know the drill...	41	0	f
f	amber	Looking... tricky.	46	0	f
f	amber	I've crunched the numbers...	44	0	f
f	amber	Here's what we got:	42	0	f
f	amber	This is what I've got....	56	0	f
f	green	Here's what I got:	26	0	f
f	green	Hello, world!	16	0	f
f	green	S'up.	14	0	f
f	green	Whoop.	35	0	f
f	green	Pssst...	15	0	f
f	green	Wooo!	34	0	f
f	green	👋	18	0	f
f	green	🙌	29	0	f
f	green	Hello, you.	21	0	f
f	green	Yo.	13	0	f
f	green	Deep Thought:	33	0	f
f	green	What a great day to be alive!	32	0	f
f	green	Looking good...	28	0	f
f	amber	Soooo, about this weather thing...	38	0	f
f	amber	Okay, so...	39	0	f
f	amber	Yeah, sooo..	45	0	f
f	amber	Well...	47	0	f
f	amber	Tricky one this.	48	0	f
f	amber	Soooo.	49	0	f
f	amber	Comme ci comme ça!	54	0	f
f	amber	Not ideal.	57	0	f
f	amber	I got this...	58	0	f
f	red	PSA:	59	0	f
f	red	Alert:	60	0	f
f	red	Ahhhhhh!	61	0	f
f	red	AGGHHH.	62	0	f
f	red	Eeeeek...	63	0	f
f	red	Listen up.	64	0	f
f	red	Panic... panic!	65	0	f
f	red	Oh jeez!	66	0	f
f	red	[Incoming Warning]:	67	0	f
f	red	How much do you like running?	68	0	f
f	green	Hallo,	36	0	t
f	green	Hey there.	12	0	f
f	green	Ciao!	25	0	f
f	green	🙋‍♂️	19	0	f
f	green	Go, get out there!	30	0	f
f	green	Hey!	20	0	f
f	green	Great news...	23	0	f
f	green	[Incoming Message]:	17	0	f
f	green	Hiya!	22	0	f
f	red	Do you want the bad news or the bad news?	69	0	f
f	red	Warning:	70	0	f
f	red	Urghhhh.	71	0	f
f	red	🙈	72	0	f
f	red	Ahhh, feck!	73	0	f
f	red	Oh dear!	74	0	f
f	red	Not today, Satan!	75	0	f
f	red	You may want to sit down for this...	76	0	f
f	red	Have you ever thought about not running?!	77	0	f
f	red	Maybe today isn't your day.	78	0	f
f	red	Try again tomorrow.	79	0	f
f	red	Houston, we have a problem!	80	0	f
f	red	Hope you like bad running conditions.	81	0	f
f	red	Have you heard of a treadmill?...	82	0	f
f	red	Deep breaths...	83	0	f
f	green	Oh yeahh.	37	0	f
f	green	Me again.	31	0	f
f	green	Hey babes,	27	0	f
f	green	You're in luck.	24	0	f
\.


--
-- TOC entry 3878 (class 0 OID 15656125)
-- Dependencies: 204
-- Data for Name: outros; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.outros (used, tone, sentence, uses, outros_id, deleted) FROM stdin;
f	green	Like and subscribe	0	22	f
f	green	This has been a message from your neighbourhood friendly bot	0	4	f
f	green	... go!	0	20	f
f	green	Byeeee x	0	29	f
f	green	Go get 'em	0	12	f
f	green	Go have fun	0	10	f
f	green	Thanks for listening	0	15	f
f	green	Happy running	0	9	f
f	green	Easy decision	0	18	f
f	green	Enjoy!	0	8	f
f	green	Now go	0	21	f
f	green	Hope you have a nice day x	0	32	f
f	green	You've been you, I've been me, goodbye	0	27	f
f	green	You heard me, go!	0	24	f
f	amber	Take it easy	0	33	f
f	amber	... I say go for it	0	34	f
f	amber	... now, over to you	0	36	f
f	amber	You can't have everything	0	41	f
f	amber	I believe in you	0	43	f
f	amber	Just do it	0	48	f
f	amber	There, I said it	0	50	f
f	amber	Beggars can't be choosers	0	39	f
f	amber	What doesn't kill you, makes you stronger	0	42	f
f	amber	Take the risk	0	45	f
f	amber	My opinion - go run	0	40	f
f	amber	See ya	0	49	f
f	amber	You're up!	0	37	f
f	amber	Piss off	0	47	f
f	amber	... go for it	0	44	f
f	amber	Off ya pop	0	38	f
f	amber	What do you have to lose, huh	0	35	f
f	green	No brainer	0	17	f
f	amber	Right, bye	0	46	f
f	red	Stay safe x	0	52	f
f	red	Good luck	0	53	f
f	red	... I warned ya!	0	54	f
f	red	Do watcha gotta do	0	55	f
f	red	Don't shoot the messenger	0	56	f
f	red	I'm sorry, okay	0	57	f
f	red	Over and out!	0	58	f
f	red	The dreadmill is always an option	0	59	f
f	red	The treadmill is looking pretty good right now isn't it	0	60	f
f	red	How about that treadmill	0	61	f
f	red	I'm not crying, you're crying	0	62	f
f	red	It'll be all okay	0	63	f
f	red	Sarryyyyy	0	64	f
f	red	Soz	0	65	f
f	amber	But what do I know	0	51	f
f	green	Kind regards, @weather_to_run x	0	11	f
f	green	No excuses	0	16	f
f	green	Have fun	0	13	f
f	green	Much love x	0	7	f
f	red	It is what is it	0	66	f
f	red	😬	0	67	f
f	red	🙃	0	68	f
f	red	RIP	0	69	f
f	red	Fingers crossed n all that	0	70	f
f	red	Not my problem	0	71	f
f	red	You were warned	0	72	f
f	red	You've been warned	0	73	f
f	red	Suck it up	0	74	f
f	red	So sorry	0	75	f
f	red	I'll say a prayer	0	76	f
f	red	All the best	0	77	f
f	green	End of transmission	0	25	f
f	green	K bye	0	5	f
f	green	End of message	0	26	f
f	green	Have a nice day	0	31	f
f	green	What are you waiting for?!	0	19	f
f	green	Easy one that	0	30	f
f	green	Love ya, bye	0	6	f
f	green	Peace and love	0	23	f
f	green	Goodbye	0	28	f
f	green	Go go go!	0	14	f
\.


--
-- TOC entry 3883 (class 0 OID 17115984)
-- Dependencies: 209
-- Data for Name: tweets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tweets (tweets_id, date_posted, intros_id, forecasts_id, outros_id, sentence) FROM stdin;
\.


--
-- TOC entry 3893 (class 0 OID 0)
-- Dependencies: 207
-- Name: forecasts_forecasts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forecasts_forecasts_id_seq', 71, true);


--
-- TOC entry 3894 (class 0 OID 0)
-- Dependencies: 202
-- Name: intros_intros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.intros_intros_id_seq', 83, true);


--
-- TOC entry 3895 (class 0 OID 0)
-- Dependencies: 205
-- Name: outros_outros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.outros_outros_id_seq', 77, true);


--
-- TOC entry 3896 (class 0 OID 0)
-- Dependencies: 208
-- Name: tweets_tweets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tweets_tweets_id_seq', 432, true);


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


-- Completed on 2020-10-18 18:12:01 BST

--
-- PostgreSQL database dump complete
--

