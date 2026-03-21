# Lakaras — The Verb System

## What is a Lakara?

**लकार** (lakāra) = the system of **10 verb forms** in Sanskrit grammar.

The name comes from Panini's metalanguage: each form is designated by a marker starting with **ल** (la), so they're collectively called lakaras. Panini didn't name them "tenses" or "moods" — he gave them algebraic labels. The verb forms do the rest.

Here's the thing: English splits verbs into "tenses" (past, present, future) and "moods" (imperative, subjunctive, optative) as separate systems. Sanskrit **unifies them**. A lakara encodes time, mood, possibility, command, and wish — all in one conjugation framework. The verb carries everything.

```
भवति (bhavati) — he/she/it is (present, indicative, third person, singular)
```

That single word encodes: **who** (third person), **how many** (singular), **when** (present), and **what kind of statement** (indicative fact). No helping verbs. No auxiliary constructions. One word, fully tagged.

---

## Why 10 Forms?

Because reality isn't just past-present-future. Sanskrit verbs must express:

- What **is** happening (fact)
- What **was** happening (recalled past)
- What **will** happen (prediction)
- What **should** happen (command)
- What **might** happen (possibility)
- What you **wish** would happen (benediction)
- What happened **long ago** (remote narrative past)
- What happened as **witnessed** (recent past)
- What was **about to** happen (conditional)
- What is **general truth** (timeless/Vedic present)

Ten slots. Ten lakaras.

---

## The 10 Lakaras

| # | Lakara | Sanskrit | Meaning / Usage | Approx. English Equivalent |
|---|---|---|---|---|
| 1 | **Laṭ** | **लट्** | Present tense — what is happening now | Present indicative |
| 2 | **Liṭ** | **लिट्** | Past — remote, unwitnessed, narrative | Past perfect / "had done" |
| 3 | **Luṭ** | **लुट्** | Future — periphrastic (analytical) | "will do" (distant/formal future) |
| 4 | **Lṛṭ** | **लृट्** | Future — simple, direct | "will do" (straightforward future) |
| 5 | **Leṭ** | **लेट्** | Vedic subjunctive — possibility, exhortation | Subjunctive (archaic, mostly Vedic) |
| 6 | **Loṭ** | **लोट्** | Command / request | Imperative — "do this!" |
| 7 | **Laṅ** | **लङ्** | Past — imperfect, recent, witnessed | Past imperfect / "was doing" |
| 8 | **Liṅ** | **लिङ्** | Wish / potential / should | Optative — "may it be", "one should" |
| 9 | **Luṅ** | **लुङ्** | Past — aorist, simple completed past | Simple past / "did" |
| 10 | **Lṛṅ** | **लृङ्** | Conditional — would have, if-then | Conditional — "would have done" |

> Notice the pattern in Panini's labels: every marker starts with **ल** and ends with a nasal or stop. The vowel in the middle distinguishes them. This isn't naming — it's indexing. Panini built a lookup table 2,500 years ago.

### Grouping by Function

**Time-based (indicative):**
- लट् (Laṭ) — present
- लङ् (Laṅ) — recent past
- लुङ् (Luṅ) — completed past (aorist)
- लिट् (Liṭ) — remote past (perfect)
- लृट् (Lṛṭ) — simple future
- लुट् (Luṭ) — distant future (periphrastic)

**Mood-based (non-indicative):**
- लोट् (Loṭ) — imperative (command)
- लिङ् (Liṅ) — optative (wish/potential)
- लेट् (Leṭ) — subjunctive (Vedic only)
- लृङ् (Lṛṅ) — conditional (hypothetical)

---

## The Three Core Lakaras

For everyday Sanskrit — reading texts, constructing sentences, understanding shlokas — three lakaras handle the vast majority of what you'll encounter.

### 1. लट् लकार (Laṭ Lakāra) — Present Tense

**What is happening, what is generally true.**

This is the workhorse. When you see a verb in most Sanskrit prose, it's probably Laṭ.

Formation: **dhatu + vikarana (class marker) + tiṅ pratyaya (personal ending)**

The verb gets built in layers:
```
भू → भव (dhatu strengthened) → भव + अ (vikarana for class 1) → भवति (+ ti ending for 3rd person singular)
```

### 2. लङ् लकार (Laṅ Lakāra) — Past Imperfect

**What was happening, what happened (recently, witnessed).**

This is the most common past tense in classical Sanskrit. It describes completed action in the past — think of it as narrative past.

Formation: **augment अ (a-) + dhatu + vikarana + modified endings**

The distinguishing feature is the **augment** — a prefix **अ** (a-) added before the verb stem:

```
भवति (bhavati, "is") → अभवत् (abhavat, "was")
```

That prefixed अ is the marker of past tense. You'll learn to spot it instantly.

### 3. लृट् लकार (Lṛṭ Lakāra) — Simple Future

**What will happen.**

Formation: **dhatu + स्य (sya) or इष्य (iṣya) + personal endings**

The future is marked by the infix **स्य** inserted between the stem and the ending:

```
भवति (bhavati, "is") → भविष्यति (bhaviṣyati, "will be")
```

The **ष्य** (ṣya) in the middle is the future flag.

---

## Parasmaipada and Atmanepada

Before we conjugate, one essential distinction.

Every Sanskrit dhatu can take one of two sets of endings:

| | **Parasmaipada** (परस्मैपद) | **Atmanepada** (आत्मनेपद) |
|---|---|---|
| Root meaning | **परस्मै** (parasmai) = for another + **पद** (pada) = word/form | **आत्मने** (ātmane) = for oneself + **पद** (pada) = word/form |
| Sense | Action whose fruit goes to **others** | Action whose fruit comes to **oneself** |
| Example | पचति (pacati) — he cooks (for others) | पचते (pacate) — he cooks (for himself) |

This is not just grammar — it encodes **directionality of benefit**. The verb form itself tells you who the action serves.

Some dhatus take only parasmaipada, some only atmanepada, and some take both (**उभयपदी**, ubhayapadī). भू (bhū) is parasmaipada. Verbs like लभ् (labh, to obtain) are atmanepada — because the fruit of obtaining naturally comes to the obtainer.

> This is a genuine parallel to distributed systems: is this function call fire-and-forget (parasmaipada — action radiates outward) or does it return a value to the caller (atmanepada — result comes back to self)?

---

## Conjugation: The Tiṅ Pratyayas (Personal Endings)

Every conjugated verb encodes **person** and **number**:

| | Sanskrit Term | Who |
|---|---|---|
| **Third person** | प्रथम पुरुष (prathama puruṣa) | He/she/it/they |
| **Second person** | मध्यम पुरुष (madhyama puruṣa) | You |
| **First person** | उत्तम पुरुष (uttama puruṣa) | I/we |

> Note: Sanskrit counts persons in **reverse** order compared to English. Third person is "first" (prathama) because in traditional grammar, the subject being discussed comes first — the speaker comes last. Grammar isn't about you. You are the last reference frame.

Each person has three numbers: **singular** (एकवचन), **dual** (द्विवचन), **plural** (बहुवचन).

That gives us a **3 × 3 grid = 9 forms** per lakara per pada.

### Parasmaipada endings (Laṭ Lakāra)

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | -ति (-ti) | -तः (-taḥ) | -न्ति (-nti) |
| Madhyama (2nd) | -सि (-si) | -थः (-thaḥ) | -थ (-tha) |
| Uttama (1st) | -मि (-mi) | -वः (-vaḥ) | -मः (-maḥ) |

### Atmanepada endings (Laṭ Lakāra)

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | -ते (-te) | -ते (-ete) | -न्ते (-nte) |
| Madhyama (2nd) | -से (-se) | -एथे (-ethe) | -ध्वे (-dhve) |
| Uttama (1st) | -ए (-e) | -वहे (-vahe) | -महे (-mahe) |

---

## Conjugation Tables: Laṭ Lakāra (Present)

### भू (bhū) — to be, to become [Class 1, Parasmaipada]

Dhatu: भू → Strengthened stem: **भव** (bhava)

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **भवति** (bhavati) — he/she is | **भवतः** (bhavataḥ) — those two are | **भवन्ति** (bhavanti) — they are |
| Madhyama (2nd) | **भवसि** (bhavasi) — you are | **भवथः** (bhavathaḥ) — you two are | **भवथ** (bhavatha) — you all are |
| Uttama (1st) | **भवामि** (bhavāmi) — I am | **भवावः** (bhavāvaḥ) — we two are | **भवामः** (bhavāmaḥ) — we are |

> **भवामि** — "I am." Two syllables. No subject pronoun needed. Compare with English "I am" — two separate words, one for the subject, one for the verb. Sanskrit packs both into one unit.

### गम् (gam) — to go [Class 1, Parasmaipada]

Dhatu: गम् → Strengthened stem: **गच्छ** (gaccha)

(The transformation गम् → गच्छ involves a process called **samprasarana** and reduplication patterns specific to this dhatu. You'll encounter such stem changes — they're irregular but frequent enough to memorize.)

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **गच्छति** (gacchati) — he/she goes | **गच्छतः** (gacchataḥ) — those two go | **गच्छन्ति** (gacchanti) — they go |
| Madhyama (2nd) | **गच्छसि** (gacchasi) — you go | **गच्छथः** (gacchathaḥ) — you two go | **गच्छथ** (gacchatha) — you all go |
| Uttama (1st) | **गच्छामि** (gacchāmi) — I go | **गच्छावः** (gacchāvaḥ) — we two go | **गच्छामः** (gacchāmaḥ) — we go |

### Bonus: लभ् (labh) — to obtain [Class 1, Atmanepada]

Dhatu: लभ् → Stem: **लभ** (labha)

This one takes atmanepada endings — because obtaining is inherently self-directed.

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **लभते** (labhate) — he obtains | **लभेते** (labhete) — those two obtain | **लभन्ते** (labhante) — they obtain |
| Madhyama (2nd) | **लभसे** (labhase) — you obtain | **लभेथे** (labhethe) — you two obtain | **लभध्वे** (labhadhve) — you all obtain |
| Uttama (1st) | **लभे** (labhe) — I obtain | **लभावहे** (labhāvahe) — we two obtain | **लभामहे** (labhāmahe) — we obtain |

> Compare the endings: भव**ति** vs लभ**ते**, भव**न्ति** vs लभ**न्ते**, भवा**मि** vs लभ**े**. The parasmaipada endings are harder, more outward-sounding (ti, nti, mi). The atmanepada endings are softer, more reflexive (te, nte, e). The sound itself mirrors the direction.

---

## Conjugation Tables: लङ् लकार (Past Imperfect)

### भू (bhū) — was/became

Formation: **अ** (augment) + **भव** (stem) + past endings

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **अभवत्** (abhavat) — he/she was | **अभवताम्** (abhavatām) — those two were | **अभवन्** (abhavan) — they were |
| Madhyama (2nd) | **अभवः** (abhavaḥ) — you were | **अभवतम्** (abhavatam) — you two were | **अभवत** (abhavata) — you all were |
| Uttama (1st) | **अभवम्** (abhavam) — I was | **अभवाव** (abhavāva) — we two were | **अभवाम** (abhavāma) — we were |

### गम् (gam) — went

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **अगच्छत्** (agacchat) — he/she went | **अगच्छताम्** (agacchatām) — those two went | **अगच्छन्** (agacchan) — they went |
| Madhyama (2nd) | **अगच्छः** (agacchaḥ) — you went | **अगच्छतम्** (agacchatam) — you two went | **अगच्छत** (agacchata) — you all went |
| Uttama (1st) | **अगच्छम्** (agaccham) — I went | **अगच्छाव** (agacchāva) — we two went | **अगच्छाम** (agacchāma) — we went |

> Spot the pattern: every Laṅ form starts with **अ** (a-). This augment is the single most reliable marker of past tense. When you're reading a text and see a verb starting with अ that doesn't normally start with अ — it's past tense.

---

## Conjugation Tables: लृट् लकार (Simple Future)

### भू (bhū) — will be

Formation: **भव** (stem) + **इष्य** (iṣya) + endings

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **भविष्यति** (bhaviṣyati) — will be | **भविष्यतः** (bhaviṣyataḥ) — those two will be | **भविष्यन्ति** (bhaviṣyanti) — they will be |
| Madhyama (2nd) | **भविष्यसि** (bhaviṣyasi) — you will be | **भविष्यथः** (bhaviṣyathaḥ) — you two will be | **भविष्यथ** (bhaviṣyatha) — you all will be |
| Uttama (1st) | **भविष्यामि** (bhaviṣyāmi) — I will be | **भविष्यावः** (bhaviṣyāvaḥ) — we two will be | **भविष्यामः** (bhaviṣyāmaḥ) — we will be |

### गम् (gam) — will go

Formation: **गम** (stem) + **इष्य** (iṣya) + endings

| Person | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (3rd) | **गमिष्यति** (gamiṣyati) — will go | **गमिष्यतः** (gamiṣyataḥ) — those two will go | **गमिष्यन्ति** (gamiṣyanti) — they will go |
| Madhyama (2nd) | **गमिष्यसि** (gamiṣyasi) — you will go | **गमिष्यथः** (gamiṣyathaḥ) — you two will go | **गमिष्यथ** (gamiṣyatha) — you all will go |
| Uttama (1st) | **गमिष्यामि** (gamiṣyāmi) — I will go | **गमिष्यावः** (gamiṣyāvaḥ) — we two will go | **गमिष्यामः** (gamiṣyāmaḥ) — we will go |

> The future infix **ष्य** (ṣya) is consistent across both. Once you hear it, you know the verb is talking about what hasn't happened yet. The stem may change (भव → भवि, गम → गमि) but the marker doesn't.

---

## Quick Reference: One Dhatu Across Three Times

**भू (bhū)** — third person singular:

| Lakara | Form | Meaning | Marker |
|---|---|---|---|
| लट् (present) | भवति (bhavati) | he is | base form |
| लङ् (past) | अभवत् (abhavat) | he was | अ- prefix |
| लृट् (future) | भविष्यति (bhaviṣyati) | he will be | -ष्य- infix |

**गम् (gam)** — third person singular:

| Lakara | Form | Meaning | Marker |
|---|---|---|---|
| लट् (present) | गच्छति (gacchati) | he goes | base form |
| लङ् (past) | अगच्छत् (agacchat) | he went | अ- prefix |
| लृट् (future) | गमिष्यति (gamiṣyati) | he will go | -ष्य- infix |

Two markers to internalize: **अ-** (prefix) = past. **-ष्य-** (infix) = future. Present is unmarked — it's the default.

---

## The Other 7 Lakaras — Brief Overview

### लोट् (Loṭ) — Imperative (Command)

**भव** (bhava) — "Be!"
**गच्छ** (gaccha) — "Go!"
**भवतु** (bhavatu) — "Let him/her be."

Used for orders, requests, blessings. The form changes based on who you're commanding.

### लिङ् (Liṅ) — Optative (Wish / Should)

**भवेत्** (bhavet) — "may it be" / "it should be"
**गच्छेत्** (gacchet) — "one should go" / "may one go"

This is the lakara of dharma-shastra — "one should do X." Legal, ethical, and philosophical texts are full of Liṅ forms.

### लिट् (Liṭ) — Perfect (Remote Past)

**बभूव** (babhūva) — "had been" / "was (long ago)"
**जगाम** (jagāma) — "had gone"

Recognizable by **reduplication** of the first syllable: भू → ब**भू**व, गम् → ज**गा**म. Used in epics and Puranas for narrative distance.

### लुङ् (Luṅ) — Aorist (Simple Completed Past)

**अभूत्** (abhūt) — "was" (simple, completed)

Has the अ- augment like Laṅ, but different endings. Relatively rare in classical prose.

### लुट् (Luṭ) — Periphrastic Future

**भविता** (bhavitā) — "will be" (emphatic/formal)

Uses a participial form + auxiliary. Think of it as the formal future — rarer in everyday use.

### लृङ् (Lṛṅ) — Conditional

**अभविष्यत्** (abhaviṣyat) — "would have been"

Combines the past augment अ- with the future marker ष्य — literally "past-of-the-future." Used in counterfactuals: "If X had happened, then Y **would have** happened."

> The conditional is architecturally beautiful: it grafts the past marker onto the future stem. "The past version of a future" = what would have been. The grammar is the logic.

### लेट् (Leṭ) — Vedic Subjunctive

Found only in Vedic texts. Essentially extinct in classical Sanskrit. Included for completeness.

---

## Practice: Translate These Sentences

Try these before looking at the answers.

| # | Sanskrit | Hint |
|---|---|---|
| 1 | **अहं गच्छामि** (ahaṁ gacchāmi) | अहम् = I; Laṭ form |
| 2 | **त्वं भवसि** (tvaṁ bhavasi) | त्वम् = you; Laṭ form |
| 3 | **सः अगच्छत्** (saḥ agacchat) | सः = he; spot the अ- |
| 4 | **ते भविष्यन्ति** (te bhaviṣyanti) | ते = they; spot the ष्य |
| 5 | **बालः गृहं गच्छति** (bālaḥ gṛhaṁ gacchati) | बालः = boy; गृहम् = house |
| 6 | **नराः वनम् अगच्छन्** (narāḥ vanam agacchan) | नराः = men; वनम् = forest |
| 7 | **सा फलं लभते** (sā phalaṁ labhate) | सा = she; फलम् = fruit; note the ending |
| 8 | **गच्छ** (gaccha) | Just the verb — which lakara? |

### Answers

| # | Translation | Analysis |
|---|---|---|
| 1 | I go. | Laṭ, uttama puruṣa, ekavachana |
| 2 | You are. | Laṭ, madhyama puruṣa, ekavachana |
| 3 | He went. | Laṅ (past — see the अ- augment), prathama puruṣa, ekavachana |
| 4 | They will be. | Lṛṭ (future — see the ष्य infix), prathama puruṣa, bahuvachana |
| 5 | The boy goes to the house. | Laṭ; बालः = nominative (doer), गृहं = accusative (destination) |
| 6 | The men went to the forest. | Laṅ; नराः = nominative plural, वनम् = accusative |
| 7 | She obtains a fruit. | Laṭ, but **atmanepada** — notice लभ**ते** not लभ**ति**. The obtaining is for herself. |
| 8 | Go! | Loṭ (imperative), madhyama puruṣa, ekavachana. A command. |

---

## The 10 Dhatu Classes (Gaṇas)

One more structural piece: not all dhatus conjugate the same way. Panini organized them into **10 classes** (gaṇas), each with its own **vikarana** (class marker inserted between the stem and ending).

| Class | Name | Vikarana | Example |
|---|---|---|---|
| 1 | Bhvādi | -अ (-a) | भू → भव + अ → भवति |
| 2 | Adādi | (none) | अद् → अत्ति (atti, eats) |
| 3 | Juhotyādi | reduplication | हु → जुहोति (juhoti, offers) |
| 4 | Divādi | -य (-ya) | दिव् → दीव्यति (dīvyati, plays) |
| 5 | Svādi | -नु (-nu) | सु → सुनोति (sunoti, presses) |
| 6 | Tudādi | -अ (-a) | तुद् → तुदति (tudati, strikes) |
| 7 | Rudhādi | -न- (-na- infix) | रुध् → रुणद्धि (ruṇaddhi, obstructs) |
| 8 | Tanādi | -उ (-u) | तन् → तनोति (tanoti, stretches) |
| 9 | Kryādi | -ना (-nā) | क्री → क्रीणाति (krīṇāti, buys) |
| 10 | Churādi | -अय (-aya) | चुर् → चोरयति (corayati, steals) |

> Each class name follows Panini's convention: it's named after the **first dhatu** in that class's list. Bhvādi = "starting with भू." This is like naming an array by its first element — a convention, not a description.

For now, Classes 1 and 10 are the most regular. Classes 2, 3, and 7 are the ones that will trip you up — they involve stem changes and infixes that break the simple pattern.

---

## Key Takeaway

Sanskrit verbs are **self-contained instruction packets**. A single conjugated form tells you:

1. **Who** is acting (person — 3rd, 2nd, 1st)
2. **How many** are acting (number — one, two, many)
3. **When** the action occurs (time — present, past, future)
4. **What kind** of statement it is (mood — fact, command, wish, hypothetical)
5. **Who benefits** from the action (pada — others or self)

No subject pronoun required. No auxiliary verbs. No word order dependency.

The 10 lakaras are not 10 tenses. They're **10 modes of relating to action across time and intention**. English needs helper constructions ("would have been going") to express what Sanskrit encodes in a single morphological form.

> Think of it this way: a Sanskrit verb is a fully serialized function call. It encodes the caller, the arguments, the temporal context, and the execution mode — all in one token. Deserialization is deterministic. No ambiguity, no parsing required.

The 3 markers to burn into memory:
- **Base form** → present (Laṭ)
- **अ- prefix** → past (Laṅ)
- **-ष्य- infix** → future (Lṛṭ)

Everything else is built on these.

---

## Next

- **Kridanta and Taddhita** — how dhatus become nouns, adjectives, and compounds (the word-building machine)
