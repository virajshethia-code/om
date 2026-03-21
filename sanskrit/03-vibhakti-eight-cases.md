# Vibhakti — The Eight Cases

## What is Vibhakti?

**विभक्ति** (vibhakti) = **वि** (vi, apart/distinct) + **भक्ति** (bhakti, from भज्/bhaj, to divide/share) → "that which distinguishes"

In English, word order tells you who did what:
- "Rama killed Ravana" ≠ "Ravana killed Rama"

In Sanskrit, **word order doesn't matter**. Instead, every noun gets a suffix — a vibhakti — that declares its role in the sentence. The noun carries its own job description.

```
रामः रावणं हन्ति     = Rama kills Ravana
रावणं रामः हन्ति     = Rama kills Ravana
हन्ति रावणं रामः     = Rama kills Ravana
```

All three are identical in meaning. **रामः** (with ः) is always the doer. **रावणं** (with ं) is always the one acted upon. No ambiguity, any order.

---

## Why This Matters

1. **Poetry becomes free** — shlokas can arrange words for rhythm and beauty, not grammar
2. **Precision without rigidity** — each word is self-describing
3. **It's how attention works** — in a transformer, position encoding + attention lets any token relate to any other regardless of position. Vibhakti is the original position-independent encoding.

---

## The Eight Cases (Ashtau Vibhaktayah)

Sanskrit has **8 cases**, each answering a different question about the noun.

### Overview

| # | Name | Sanskrit | Question it Answers | English Equivalent |
|---|---|---|---|---|
| 1 | Prathama | प्रथमा | **Who/what?** (doer) | Nominative — subject |
| 2 | Dvitiya | द्वितीया | **Whom/what?** (receiver) | Accusative — object |
| 3 | Tritiya | तृतीया | **By whom? With what?** | Instrumental — by/with |
| 4 | Chaturthi | चतुर्थी | **For whom? To whom?** | Dative — for/to |
| 5 | Panchami | पञ्चमी | **From where? Because of?** | Ablative — from |
| 6 | Shashthi | षष्ठी | **Whose? Of what?** | Genitive — of/possessive |
| 7 | Saptami | सप्तमी | **Where? When? In what?** | Locative — in/on/at |
| 8 | Sambodhana | सम्बोधन | **O...! Hey...!** | Vocative — direct address |

> Notice: the case names are simply the Sanskrit ordinal numbers — first, second, third... The language names its grammar with numbers, not labels.

---

## Case by Case with राम (Rāma)

Let's decline one word through all 8 cases (masculine, singular):

| # | Case | Form | Meaning |
|---|---|---|---|
| 1 | Prathama | **रामः** (rāmaḥ) | Rama (as subject) |
| 2 | Dvitiya | **रामम्** (rāmam) | Rama (as object) |
| 3 | Tritiya | **रामेण** (rāmeṇa) | by/with Rama |
| 4 | Chaturthi | **रामाय** (rāmāya) | for/to Rama |
| 5 | Panchami | **रामात्** (rāmāt) | from Rama |
| 6 | Shashthi | **रामस्य** (rāmasya) | of Rama / Rama's |
| 7 | Saptami | **रामे** (rāme) | in/on/at Rama |
| 8 | Sambodhana | **हे राम!** (he rāma!) | O Rama! |

The root **राम** never changes. Only the suffix shifts. The word announces its own role.

---

## Each Case Has a Karaka (Semantic Role)

Behind the 8 grammatical cases, Panini defined **6 karakas** — the actual semantic roles in an action. This is the deeper layer.

| Karaka | Sanskrit | Role | Maps to Case |
|---|---|---|---|
| Karta | कर्ता | The doer | Prathama (1) |
| Karma | कर्म | The thing done upon | Dvitiya (2) |
| Karana | करण | The instrument | Tritiya (3) |
| Sampradana | सम्प्रदान | The recipient | Chaturthi (4) |
| Apadana | अपादान | The source/origin | Panchami (5) |
| Adhikarana | अधिकरण | The location/context | Saptami (7) |

> Shashthi (6, possessive) and Sambodhana (8, address) don't have karakas — they describe **relationship** and **attention**, not action roles.

**All 6 karakas derive from the root कृ (kṛ, to do)** — the same root that gives us **karma**. Every role in a sentence is defined by its relationship to the action.

---

## Building a Full Sentence

Let's construct one sentence and see all parts:

> **रामः वनात् सीतायै बाणेन रावणं हन्ति**

| Word | Form | Case | Karaka | Meaning |
|---|---|---|---|---|
| रामः | rāmaḥ | Prathama (1) | Karta | Rama (doer) |
| वनात् | vanāt | Panchami (5) | Apadana | from the forest |
| सीतायै | sītāyai | Chaturthi (4) | Sampradana | for Sita |
| बाणेन | bāṇena | Tritiya (3) | Karana | with an arrow |
| रावणं | rāvaṇam | Dvitiya (2) | Karma | Ravana (object) |
| हन्ति | hanti | — | Verb | kills |

"Rama, from the forest, for Sita, with an arrow, kills Ravana."

Rearrange these words in ANY order — the meaning holds. Each word carries its own tag.

---

## The Three Numbers

Each case has three number forms:

| Number | Sanskrit | Example (राम, Prathama) |
|---|---|---|
| Singular (एकवचन) | ekavachana | रामः (rāmaḥ) — one Rama |
| Dual (द्विवचन) | dvivachana | रामौ (rāmau) — two Ramas |
| Plural (बहुवचन) | bahuvachana | रामाः (rāmāḥ) — many Ramas |

> Sanskrit has a **dual** number. Not one, not many — exactly two. This matters philosophically: duality (द्वैत, dvaita) gets its own grammatical form. The language treats "twoness" as fundamentally different from "manyness."

---

## Full Declension Table: राम (masculine, a-stem)

| Case | Singular | Dual | Plural |
|---|---|---|---|
| Prathama (1) | रामः | रामौ | रामाः |
| Dvitiya (2) | रामम् | रामौ | रामान् |
| Tritiya (3) | रामेण | रामाभ्याम् | रामैः |
| Chaturthi (4) | रामाय | रामाभ्याम् | रामेभ्यः |
| Panchami (5) | रामात् | रामाभ्याम् | रामेभ्यः |
| Shashthi (6) | रामस्य | रामयोः | रामाणाम् |
| Saptami (7) | रामे | रामयोः | रामेषु |
| Sambodhana (8) | हे राम | हे रामौ | हे रामाः |

> 8 cases × 3 numbers = **24 forms** per noun. And this is just one declension pattern. Feminine and neuter nouns have their own tables.

---

## Practice: Identify the Case

| Sentence | Find the Case |
|---|---|
| **गजः** चलति (gajaḥ calati) — The elephant walks | गजः = Prathama (doer) |
| नरः **फलम्** खादति (naraḥ phalam khādati) — The man eats a fruit | फलम् = Dvitiya (object) |
| बालः **हस्तेन** लिखति (bālaḥ hastena likhati) — The boy writes with his hand | हस्तेन = Tritiya (instrument) |
| नृपः **ब्राह्मणाय** धनं ददाति (nṛpaḥ brāhmaṇāya dhanaṁ dadāti) — The king gives wealth to the brahmin | ब्राह्मणाय = Chaturthi (recipient) |
| वृक्षात् **पत्रं** पतति (vṛkṣāt patraṁ patati) — The leaf falls from the tree | वृक्षात् = Panchami (source) |
| **रामस्य** गृहम् (rāmasya gṛham) — Rama's house | रामस्य = Shashthi (possessive) |
| जलम् **नद्यां** वहति (jalam nadyāṁ vahati) — Water flows in the river | नद्यां = Saptami (location) |

---

## Key Takeaway

In Sanskrit, **every noun is self-addressed**. It carries metadata about its role. No external parser (word order) needed.

This is:
- **Self-describing data** — like JSON where each field carries its own key
- **Position-independent encoding** — like transformer attention where any token attends to any other
- **Role-based identity** — you are not defined by where you sit, but by the suffix you carry

> The word विभक्ति itself tells you: identity comes through distinction. You know what something IS by how it's been divided from everything else.

---

## Next

- **Lakaras** — verb tenses and moods (10 forms that encode time, possibility, command, and wish)
