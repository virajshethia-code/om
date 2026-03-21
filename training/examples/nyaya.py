"""Nyaya training examples — 30 formal logic / syllogism examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "nyaya"


def generate_nyaya_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples


# ---------------------------------------------------------------------------
# 30 (query, response) pairs — 3 per domain
# Each response follows the full 5-step Nyaya method with hetvabhasa audit.
# ---------------------------------------------------------------------------

_DATA: List[tuple] = [

# ===== SOFTWARE ENGINEERING (3) =====

("Our CTO claims that rewriting our monolith in microservices will reduce deployment failures by 80%. Should we proceed?",
"""CLAIM: Rewriting our monolith in microservices will reduce deployment failures by 80%.

SYLLOGISM:
  Pratijna: Rewriting our monolith as microservices will reduce deployment failures by 80%.
  Hetu: Microservices allow independent deployment of smaller units, reducing blast radius and enabling isolated rollbacks. — Pramana basis: Anumana (inference from architectural principles) supplemented by Shabda (industry testimony from Netflix, Amazon).
  Udaharana: Amazon's migration from monolith to microservices (circa 2001-2006) resulted in measurably faster deployments and reduced cross-team conflicts. Deployment frequency increased from weekly to thousands per day, with each deployment affecting only its service boundary.
  Upanaya: In Amazon's case, independent deployment succeeded because each team owned a well-bounded service with clear API contracts. In our case, the same principle applies IF our domain boundaries are equally clear and our teams are organized to own individual services. The bridge depends on organizational structure mapping to service boundaries.
  Nigamana: Microservices CAN reduce deployment failures — but the 80% figure follows only PROBABLY, contingent on clean domain boundaries and team ownership. The specific 80% figure is unsupported. — Modality: Probable, not necessary.

HETVABHASA AUDIT:
  Asiddha: FAIL — The hetu assumes our failures are caused by blast-radius problems. Deployment failures have many causes: bad tests, environment drift, config errors, race conditions. If our failures stem from flaky integration tests, microservices would INCREASE failures by multiplying integration surfaces. The failure MODE is undiagnosed.
  Viruddha: PASS — Independent deployment does reduce blast radius; it does not increase it. The direction is correct.
  Anaikantika: FAIL — "Independent deployment of smaller units" equally supports modular monolith, serverless functions, feature flags, or better CI/CD pipelines. The hetu does not uniquely justify microservices. A counter-thesis ("modular monolith with feature flags") is equally supported.
  Satpratipaksha: FAIL — Counter-reason: "Microservices introduce distributed system complexity (network failures, eventual consistency, service discovery, distributed tracing) that CREATE new failure categories." This "microservices tax" is well-documented and supported by empirical data from organizations that migrated.
  Badhita: FAIL — No published migration shows a clean 80% reduction attributable to architecture alone. Most show a temporary INCREASE during migration, with improvements confounded by simultaneous CI/CD improvements.

FAILURE POINT: The argument fails at Asiddha (Step 3a). The hetu assumes deployment failures are caused by monolithic blast radius without diagnosing actual failure modes. This is solution-first reasoning: the CTO chose microservices and is constructing justification backward. The 80% figure is rhetoric, not data.

INSIGHT: The question "should we rewrite as microservices?" is premature. The prior question — "what are our deployment failures actually caused by?" — is unanswered. The syllogism collapses not because microservices are bad but because the diagnostic step was skipped. This pattern recurs: architectural decisions framed as solutions smuggle in unverified diagnoses."""),

("Is test-driven development actually more productive than writing tests after implementation?",
"""CLAIM: Test-driven development (TDD) is more productive than test-after development.

SYLLOGISM:
  Pratijna: TDD produces higher productivity (working features per unit time) than writing tests after implementation.
  Hetu: Writing tests first forces developers to clarify requirements and interface design before coding, reducing rework from ambiguity. — Pramana basis: Anumana plus Shabda (Kent Beck, Martin Fowler, TDD practitioner testimony).
  Udaharana: The IBM/Microsoft study (Nagappan et al., 2008) compared TDD vs. test-after across four products. TDD teams showed 40-90% defect density reduction. However, development time was 15-35% longer. This real study notably does NOT straightforwardly support the productivity claim.
  Upanaya: The defect reduction came from test-first discipline forcing specification clarity. In general practice, the same mechanism applies IF the domain has clear, testable requirements. For exploratory coding (UI prototyping, research spikes), requirements are discovered through implementation, weakening the bridge.
  Nigamana: TDD improves CODE QUALITY (fewer defects) but does not necessarily improve raw productivity. Modality: Probable for quality; WEAK for productivity.

HETVABHASA AUDIT:
  Asiddha: PASS — The mechanism (test-first forces requirement clarity, reducing rework) is established by both causal reasoning and empirical studies.
  Viruddha: PASS — Clarifying requirements before coding does not plausibly decrease productivity, though the TIME cost of clarification could offset gains.
  Anaikantika: FAIL — "Clarifying requirements before coding reduces rework" supports ANY requirements-first practice: design docs, specification reviews, type-driven development, formal methods. The hetu does not uniquely support TDD over alternatives.
  Satpratipaksha: FAIL — Counter: "TDD's overhead of writing tests for every unit BEFORE understanding design correctness leads to premature specification lock-in and expensive test rewrites." This YAGNI argument is equally supported by practitioner testimony (DHH's "TDD is dead," Jim Coplien's critiques).
  Badhita: PARTIAL FAIL — A 2014 meta-analysis by Rafique and Misic found "small positive effect on quality but inconclusive effects on productivity."

FAILURE POINT: The argument fails at Anaikantika (3c). The core mechanism — requirement clarification before coding — is not unique to TDD. The debate "TDD vs. test-after" is a false dichotomy obscuring the real variable: degree of upfront specification clarity, achievable through multiple means.

INSIGHT: Both sides argue about WHEN to write tests, but the actual causal variable is HOW MUCH SPECIFICATION CLARITY exists before coding. TDD is one forcing function for clarity; it is not the only one. The productive question is not "TDD or not?" but "What is the cheapest way to achieve sufficient specification clarity for THIS type of work?" The real enemy is not "test-after" but "specify-never." """),

("Our team lead argues we should never use ORMs because they hide SQL complexity and cause N+1 query problems. Is this reasoning sound?",
"""CLAIM: ORMs should never be used because they hide SQL complexity and cause N+1 query problems.

SYLLOGISM:
  Pratijna: ORMs should never be used in software development.
  Hetu: ORMs hide SQL complexity from developers and cause N+1 query problems, leading to performance degradation. — Pramana basis: Pratyaksha (direct observation of ORM-generated queries) supplemented by Anumana.
  Udaharana: The Django ORM N+1 problem: loading blog posts and accessing each post's author generates 1+N queries instead of a JOIN. Instagram documented ORM performance issues replaced with raw SQL for critical paths.
  Upanaya: In these cases, the ORM's lazy loading defaulted to N+1 because the abstraction hid query boundaries. However, the bridge is weakened because modern ORMs provide eager loading (select_related, includes, joinedload) that explicitly solves N+1 when used correctly.
  Nigamana: ORMs CAN cause N+1 and DO hide SQL complexity, but "never use ORMs" does not follow. — Modality: Premises established; conclusion is an INVALID leap from "X has risks" to "never use X."

HETVABHASA AUDIT:
  Asiddha: PASS — ORMs do hide SQL complexity (their stated purpose) and N+1 problems are well-documented and reproducible.
  Viruddha: FAIL — "Hiding SQL complexity" is precisely WHY teams use ORMs — reducing cognitive load, preventing SQL injection, ensuring consistent patterns. The same property cited as defect is also the primary benefit. The hetu frames a feature as a bug.
  Anaikantika: FAIL — "Hides complexity and can cause performance problems" applies to virtually every abstraction: garbage collectors, high-level languages, frameworks. If this justifies "never use ORMs," it equally justifies "never use any abstraction" — reducible to absurdity.
  Satpratipaksha: FAIL — Counter: "ORMs prevent SQL injection, ensure type-safe queries, enable database-agnostic code, reduce boilerplate by 60-80%, and provide migration management." Supported by widespread adoption at scale (Shopify, GitHub, Basecamp).
  Badhita: FAIL — The most successful web applications (Shopify, GitHub, Basecamp) use ORMs extensively, addressing critical paths with targeted raw SQL while keeping ORMs for 90%+ of queries.

FAILURE POINT: Fails at Anaikantika (3c) and Viruddha (3b) simultaneously. The "X hides complexity, therefore never use X" pattern proves too much. The team lead has taken the ORM's PRIMARY DESIGN PURPOSE and reframed it as a defect.

INSIGHT: The argument is not about ORMs but about anxiety regarding abstraction layers. The N+1 problem is not an ORM problem; it is a DEVELOPER KNOWLEDGE problem. A team that understands SQL uses eager loading correctly. The prescription should be "ensure the team understands SQL" — not "remove the abstraction." The word "never" is the logical red flag: absolute prohibitions in engineering almost always indicate arguments that have not survived stress-testing."""),

# ===== BUSINESS STRATEGY (3) =====

("Our board argues we must achieve profitability before pursuing international expansion. Is this logically sound?",
"""CLAIM: A company must achieve domestic profitability before pursuing international expansion.

SYLLOGISM:
  Pratijna: Our company must achieve profitability before expanding internationally.
  Hetu: International expansion requires significant capital (localization, compliance, hiring), and pursuing it while unprofitable accelerates cash burn, increasing insolvency risk. — Pramana basis: Anumana plus Shabda (standard venture/PE advisory).
  Udaharana: WeWork's international expansion while deeply unprofitable contributed to its near-collapse in 2019 — expanded to 29 countries while losing billions. Each new market added fixed costs without proven unit economics.
  Upanaya: The bridge holds IF our unit economics are similarly unproven. If domestic unit economics ARE proven and only aggregate profitability is missing (due to upfront platform costs that amortize over volume), the bridge weakens significantly.
  Nigamana: International expansion while unprofitable is high-risk. — Modality: Probable but dependent on a critical ambiguity in the term "profitability."

HETVABHASA AUDIT:
  Asiddha: PARTIAL FAIL — The hetu assumes international expansion always requires SIGNIFICANT capital. True historically but decreasingly true for digital products. A SaaS company can enter new markets by adding language support and payment methods — marginal costs.
  Viruddha: FAIL — The hetu supports the opposite: "Because we are unprofitable domestically, we MUST expand internationally to access larger markets providing the volume needed for profitability." Spotify expanded internationally while unprofitable because music licensing costs required global subscriber scale. The path to profitability REQUIRED international scale.
  Anaikantika: FAIL — "Capital burn increases risk" could justify any constraint on spending: "don't hire," "don't build features," "don't market." It is general capital conservation, not specific to international expansion.
  Satpratipaksha: FAIL — Counter: "Delaying international expansion while competitors enter those markets creates LARGER risk — permanent market loss. First-mover advantage in new geographies, once captured, is extremely expensive to reverse." Amazon expanded internationally while deeply unprofitable, locking in positions now enormously valuable.
  Badhita: FAIL — Many of the most successful companies expanded internationally before profitability: Amazon, Uber, Netflix, Spotify. The rule would have prevented these.

FAILURE POINT: Fails at Viruddha (3b). The hetu is reversible: for some business models, international expansion IS the path to profitability because unit economics only work at global scale. The board's blanket rule cannot distinguish the two types of unprofitability.

INSIGHT: The word "profitability" contains a critical ambiguity. Being unprofitable because each customer costs more than they pay (broken unit economics — fix first) is fundamentally different from being unprofitable because platform costs haven't been amortized over enough customers (scale problem — expansion may be the solution). The board's argument is valid for the first case and invalid for the second. The decision cannot be made without first determining which type applies."""),

("A startup founder claims: 'We don't need a business model yet — focus on user growth first, monetization will follow.' Is this valid?",
"""CLAIM: A startup should prioritize user growth over monetization, and revenue will follow from a large user base.

SYLLOGISM:
  Pratijna: Our startup should focus exclusively on user growth; a viable business model will emerge once we have sufficient users.
  Hetu: A large user base creates monetization options (advertising, data, premium tiers, network effects) unavailable at small scale. Companies that prioritized growth achieved dominant positions. — Pramana basis: Shabda (Silicon Valley orthodoxy) plus selective Pratyaksha.
  Udaharana: Facebook grew to 500M users before significant revenue. Deliberate monetization deferral, focus on engagement and network density. By the time advertising was introduced, data richness and lock-in made it extraordinarily monetizable. Revenue: $272M (2008) to $86B (2020).
  Upanaya: Facebook's growth-first worked because: viral loops (social graph), near-zero marginal cost per user, uniquely monetizable data asset. Bridge holds IF our product similarly has viral mechanics, low marginal cost, and latent monetization value. If our product has high marginal cost, the bridge collapses.
  Nigamana: Growth-first CAN lead to monetization — but only under specific conditions. — Modality: Weak. Multiple unverified conditions required.

HETVABHASA AUDIT:
  Asiddha: FAIL — A large user base does NOT automatically create monetization options. Twitter/X's monetization struggles despite 300M+ users, Snapchat's negative unit economics despite massive usage — user base size is necessary but not sufficient. The missing factor: whether usage patterns generate monetizable value.
  Viruddha: FAIL — "Because we have no business model, growing users faster means burning capital faster on users who may never generate revenue, bringing forward insolvency." Every user acquired without a revenue model is a cost, not an asset.
  Anaikantika: FAIL — "Growth creates options" equally supports adding more features, entering adjacent markets, building integrations. Does not specifically justify USER growth over revenue growth, margin growth, or retention growth.
  Satpratipaksha: FAIL — Counter: "Early monetization tests provide essential signal about whether the product delivers enough value that users will pay. Deferring this test allows building on an untested assumption." Supported by lean startup methodology.
  Badhita: FAIL — Contradicted by BASE RATES. For every Facebook, hundreds of growth-first startups failed to monetize: Vine (50M users, shut down), Quibi ($1.75B raised, shut down), Homejoy, MoviePass. Survivorship bias makes the strategy appear validated.

FAILURE POINT: The deepest failure is Badhita (3e) combined with Asiddha (3a). The base rate of "growth-first, monetize-later" producing viable businesses is extremely low. The founder reasons from memorable successes while ignoring the graveyard.

INSIGHT: The founder uses "monetization will follow" as a PROMISE to avoid a TEST. The statement functions not as prediction but as deferral — "don't make me prove the business model works yet." The valid growth-first strategy requires an explicit theory of HOW users convert to revenue (Facebook had: user data + advertiser marketplace). Without this theory, "focus on growth" is indistinguishable from "avoid confronting whether anyone will pay." """),

("Our competitor raised $50M. Our VP of Sales argues we need to match their customer acquisition spending or lose the market. Valid?",
"""CLAIM: We must match our competitor's customer acquisition spending or lose our market position.

SYLLOGISM:
  Pratijna: We must increase acquisition spending to match our well-funded competitor or face market loss.
  Hetu: The company that acquires customers fastest captures market share that is difficult to reclaim; our competitor's $50M enables outspending us, creating an existential threat. — Pramana basis: Anumana (competitive dynamics) plus Shabda (standard competitive strategy).
  Udaharana: Uber's massive raises enabled subsidized rides below cost, acquiring market share Lyft struggled to reclaim. Uber raised $8.1B before IPO and dominated through spending, establishing network effects that persist.
  Upanaya: The bridge holds IF our market has similar network effects and switching costs. If our product is B2B SaaS where decisions are based on product fit, the dynamic is entirely different — customers choose on capability, not acquisition spend.
  Nigamana: Matching competitor spending is necessary ONLY IF the market exhibits strong network effects. — Modality: Conditional.

HETVABHASA AUDIT:
  Asiddha: FAIL — Assumes acquisition spending translates to market share capture. In many B2B markets, spending has diminishing returns: you can buy awareness but not trust.
  Viruddha: FAIL — Attempting to match a 5-10x better-funded competitor depletes OUR resources faster, bringing forward insolvency while barely affecting their position. Matching spend against superior capital is the strategy most likely to kill us.
  Anaikantika: PASS — The hetu is reasonably specific to acquisition as a competitive mechanism.
  Satpratipaksha: FAIL — Counter: "Invest in differentiation, retention, and unit economics — competing on dimensions where capital advantage matters least. Superior retention needs far less acquisition to maintain the same base." Supported by Basecamp's strategy against well-funded competitors.
  Badhita: FAIL — Contradicted by Basecamp (profitable despite outspent 100:1), Mailchimp (bootstrapped to $12B acquisition), Atlassian (minimal sales, grew to $60B+).

FAILURE POINT: Fails at Viruddha (3b). The VP's strategy is self-defeating: matching the spending of a company with 5x our capital accelerates our own destruction. The VP correctly identified a threat but proposed the worst possible response: symmetric competition on the competitor's strongest dimension.

INSIGHT: The VP has committed a category error: treating a FUNDING event (competitor raised $50M) as equivalent to a MARKET event (competitor captured our customers). A competitor raising capital is potential energy, not kinetic energy. The correct response is making their spending ineffective: increase switching costs, improve retention, build product moats. The question is not "how do we match their spend?" but "how do we make their $50M as useless as possible?" """),

# ===== SCIENTIFIC ANALYSIS (3) =====

("A study with n=45 found a new drug reduces migraine frequency by 30%. The pharma company claims this proves effectiveness. Evaluate.",
"""CLAIM: A new drug is effective at reducing migraine frequency, as demonstrated by a 30% reduction in a study of 45 participants.

SYLLOGISM:
  Pratijna: The new drug is effective at reducing migraine frequency.
  Hetu: A clinical study showed a 30% reduction among participants. — Pramana basis: Pratyaksha (direct observation in study), but design details unspecified.
  Udaharana: Sumatriptan's efficacy was only considered established after multiple randomized controlled trials with hundreds of participants, followed by FDA review. The standard for "proven effective" is replication at scale.
  Upanaya: Small initial studies were hypothesis-generating, not hypothesis-confirming. A 45-person result generates a hypothesis worth testing at scale.
  Nigamana: The study provides preliminary evidence that the drug MAY be effective. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — Was the study randomized? Double-blinded? Placebo-controlled? P-value not reported. With n=45, confidence intervals would be wide. A 30% reduction could be consistent with true effects ranging from 5% to 55%, or zero effect if variance is high.
  Viruddha: PASS — A 30% reduction does not support the conclusion of ineffectiveness.
  Anaikantika: FAIL — A 30% reduction could be caused by: pharmacological action, placebo effect (migraine studies show 20-40% placebo responses), regression to the mean, seasonal variation, or lifestyle changes during the study. Without a placebo control, the hetu supports ALL explanations equally.
  Satpratipaksha: FAIL — Counter: "Placebo-controlled migraine studies show 20-40% placebo response rates. A 30% reduction in an uncontrolled study is entirely consistent with placebo alone." Supported by meta-analyses of migraine trials.
  Badhita: FAIL — "Proves effective" contradicted by pharmacology standards. The FDA requires Phase III trials (n=300-3000, RCT, double-blind). A single n=45 study is insufficient. "Proves" is factually incorrect.

FAILURE POINT: Fails at Anaikantika (3c) — the result is consistent with multiple explanations not requiring drug efficacy. But the deeper failure is linguistic: "proves" performs enormous rhetorical work the data cannot support. Even a perfect Phase III trial does not "prove" — it "establishes with high probability."

INSIGHT: Two failures operate simultaneously. Evidential: the study is too small and its methodology unspecified to distinguish drug effect from placebo. Linguistic: "proves" is a category error conflating preliminary evidence with established fact. The question that matters: what was the placebo arm's response rate? If no placebo arm existed, the entire result is uninterpretable."""),

("A climate scientist argues: 'Because CO2 and temperature have risen together for 150 years, CO2 causes warming.' Evaluate the logical structure.",
"""CLAIM: Rising CO2 causes global warming, evidenced by 150-year correlation.

SYLLOGISM:
  Pratijna: Anthropogenic CO2 emissions cause global temperature increase.
  Hetu: CO2 concentration and temperature have risen in tandem over 150 years. — Pramana basis: Pratyaksha (direct measurement from ice cores and instruments) for correlation. The CAUSAL claim adds Anumana.
  Udaharana: Smoking and lung cancer. Strong epidemiological correlation, then causal mechanism established through biochemistry. Correlation was real AND causal — but proof required mechanism identification, not just correlation.
  Upanaya: The same structure applies to CO2: correlation exists, AND the causal mechanism is independently established (Arrhenius 1896 — CO2 absorbs infrared radiation, spectroscopically verified). The bridge is strong BECAUSE both correlation and mechanism exist.
  Nigamana: CO2 causes warming — highly probable, supported by both correlation AND independently verified mechanism. — Modality: Near-necessary.

HETVABHASA AUDIT:
  Asiddha: PASS — CO2 measurements (Mauna Loa since 1958, ice cores 800K years) and temperature records (NASA GISS, HadCRUT, Berkeley Earth) are among the most reliable measurements in Earth science.
  Viruddha: PASS — Rising CO2 paired with rising temperature cannot plausibly support "CO2 does not cause warming."
  Anaikantika: PARTIAL FAIL — This is the genuine weakness AS STATED. Correlation alone IS inconclusive. The FULL scientific case includes independently verified radiative forcing mechanism, which eliminates the problem. The argument as stated is too broad; the argument as supported by full evidence is not.
  Satpratipaksha: PASS — Solar forcing: flat/declining since 1980 while temperatures continued rising. Volcanic activity: doesn't match. Natural cycles: no known cycle matches. Urban heat island: satellite records confirm ground record.
  Badhita: PASS — Consistent with overwhelming evidence: radiative physics, paleoclimate, attribution studies, model predictions confirmed, stratospheric cooling fingerprint.

FAILURE POINT: The argument AS STATED has genuine weakness at Anaikantika (3c). "Because they rose together, CO2 causes warming" is technically correlation-causation fallacy. The argument is CORRECT in conclusion but FLAWED in stated reasoning. The full case rests on: (1) independently verified mechanism, (2) correlation consistent with mechanism, (3) elimination of alternatives, (4) successful prediction, (5) unique fingerprints.

INSIGHT: Correct conclusions can be undermined by weak argumentation. The CO2-warming link is one of the best-supported causal claims in Earth science — but presenting it as simple correlation invites the "correlation is not causation" objection. The scientist committed the "lazy hetu" error: using an easily stated but logically vulnerable reason when much stronger reasons exist. The strongest version: "CO2 causes warming because we measured its infrared absorption spectrum, calculated the energy imbalance, predicted the temperature response, and observed that prediction confirmed over decades." """),

("A neuroscience paper claims free will is an illusion because brain scans show neural activity preceding conscious decisions by 300ms. Valid?",
"""CLAIM: Free will is an illusion because neural activity precedes conscious awareness of decisions.

SYLLOGISM:
  Pratijna: Free will is an illusion — decisions are determined by unconscious neural processes before awareness.
  Hetu: Brain imaging studies (Libet 1983, Soon et al. 2008) show measurable neural activity 300ms-seconds before subjects report decision awareness. — Pramana basis: Pratyaksha (neuroimaging) for temporal gap. Interpretation is Anumana.
  Udaharana: Libet's 1983 experiment: subjects flexed wrists at chosen times while watching a clock. "Readiness potential" began ~550ms before action; conscious awareness ~200ms before — a 350ms gap. Real, replicated.
  Upanaya: This held for simple motor decisions. The paper extends to ALL decisions including complex moral and strategic choices. The bridge requires that simple motor and complex deliberative decisions share temporal structure — a massive extrapolation.
  Nigamana: Unconscious activity precedes awareness for simple motor decisions. The broader "free will is an illusion" does NOT follow. — Modality: Narrow finding established; broad conclusion weak.

HETVABHASA AUDIT:
  Asiddha: PARTIAL FAIL — Established for simple motor tasks but not complex deliberative decisions. You cannot extrapolate from "when to flex your wrist" to "whether to change careers."
  Viruddha: FAIL — The 300ms gap could indicate consciousness functions as VETO mechanism — Libet himself proposed this. If consciousness can veto unconsciously initiated impulses, that IS free will ("free won't"). Same data supports both interpretations.
  Anaikantika: FAIL — The reasoning pattern proves too much. If "unconscious activity precedes awareness" disproves free will, it equally disproves conscious perception, emotion, and thought itself. This undermines the very consciousness making the scientific argument — a reductio ad absurdum.
  Satpratipaksha: FAIL — Counter: Compatibilist free will (Frankfurt, Dennett) locates freedom in the capacity to respond to reasons, not in temporal priority of consciousness. ~59% of professional philosophers accept compatibilism (PhilPapers survey).
  Badhita: FAIL — Schurger et al. (2012) showed the "readiness potential" may reflect stochastic neural fluctuations, not deterministic pre-decision. When subjects chose WHAT to do (not just WHEN), the temporal gap was reduced or absent.

FAILURE POINT: Fails at Anaikantika (3c) with catastrophic generality. The pattern "unconscious process precedes awareness, therefore consciousness is irrelevant" would eliminate consciousness from ALL cognition — including the neuroscientist's own conscious reasoning about the experiment. The argument is self-undermining.

INSIGHT: The paper commits definitional smuggling. It uses "free will" to mean "consciousness temporally initiates motor impulses" — a definition virtually no philosopher holds. Then disproves this narrow definition and claims to have disproved free will generally. The neuroscience finding is real and interesting. The philosophical conclusion is a non sequitur."""),

# ===== PERSONAL DECISIONS (3) =====

("My friend argues I should leave my stable job to start a business because 'you only live once and regret is worse than failure.' Valid?",
"""CLAIM: One should leave a stable job to start a business because regret is worse than failure.

SYLLOGISM:
  Pratijna: I should leave my stable job to start a business.
  Hetu: Regret from not trying is worse than failure from trying, and since life is finite, one should take risks that avoid future regret. — Pramana basis: Shabda (YOLO philosophy) plus Anumana (inference from finitude to action imperative).
  Udaharana: Bronnie Ware's interviews with terminal patients found the #1 regret: "I wish I'd had the courage to live a life true to myself." This documented pattern supports inaction-regret's psychological power.
  Upanaya: Ware's patients regretted BROAD LIFE DIRECTION — living authentically vs. conforming. The question here is much narrower: one particular job for one particular business idea. Whether this specific job constitutes "living inauthentically" is unexamined.
  Nigamana: Life's finitude creates reason to consider opportunity costs, but the specific conclusion "leave this job for this business" does not follow. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — "Regret is worse than failure" is unproved. Affective forecasting research (Gilbert, Wilson) shows humans overestimate future emotion intensity. People who fail at businesses often experience lasting financial stress, depression, and damaged relationships they did NOT anticipate.
  Viruddha: FAIL — "You only live once" equally argues for caution: with only one life, catastrophic failure consumes an irreplaceable portion. YOLO is equally an argument for risk and for prudence.
  Anaikantika: FAIL — Could justify ANY risky action: quitting without a plan, gambling savings, ending relationships. Provides no mechanism for distinguishing wise risks from reckless ones.
  Satpratipaksha: FAIL — Counter: "Starting a business while keeping the stable job (nights, weekends, gradual transition) avoids BOTH regret AND catastrophic failure." This eliminates the forced choice.
  Badhita: FAIL — ~90% of startups fail. Founders who quit without validation report higher financial distress. Most successful founders validated before quitting (Sara Blakely developed Spanx while working at Dillard's).

FAILURE POINT: Fails at Viruddha (3b) — the hetu is perfectly reversible. "You only live once" provides zero directional guidance.

INSIGHT: The friend's argument is not an argument — it is an emotional appeal disguised as logic. "YOLO" and "regret is worse than failure" are FEELINGS about risk, not REASONS for a specific decision. What is needed is specific analysis: What business? What financial runway? Can I test without quitting? The friend's advice uses a motivational slogan to make caution feel like cowardice — emotional manipulation, not logical reasoning."""),

("Should I buy a house now or wait? Interest rates are high but my landlord just raised rent 20%.",
"""CLAIM: I should buy a house now despite high interest rates because rent has become excessively expensive.

SYLLOGISM:
  Pratijna: Buying now is better despite high rates because rent is increasingly costly.
  Hetu: A 20% rent increase makes renting costly; mortgage payments build equity while rent does not; therefore even high-rate ownership beats inflated rent. — Pramana basis: Anumana plus Shabda ("rent is throwing money away").
  Udaharana: 1980-82 buyers at 14-18% rates who held long-term built significant equity through appreciation and eventual refinancing at lower rates.
  Upanaya: The bridge holds IF home prices continue appreciating, rates eventually decline for refinancing, and the buyer holds 10+ years. All plausible but uncertain. The 20% rent increase's relevance depends on whether it is structural or a temporary landlord decision.
  Nigamana: Buying MAY be rational for long-term holders expecting rate relief, but the rent increase alone does not determine the answer. — Modality: Conditional.

HETVABHASA AUDIT:
  Asiddha: FAIL — "Rent builds no equity, therefore wasted" is false. Rent buys: housing without maintenance liability, flexibility, no exposure to property decline, and the ability to invest the down payment elsewhere. The "rent is waste" premise is not established — it depends on specific numbers.
  Viruddha: FAIL — At 7.5% on a $400K home, monthly interest alone is $2,500 — before taxes, insurance, maintenance. If post-increase rent is $2,000, buying is MORE expensive. The hetu can prove "buying is even more expensive right now."
  Anaikantika: FAIL — "My rent increased, therefore buy" could justify buying at ANY price point. The rent increase provides motivation but no guidance on WHAT to buy or at what price.
  Satpratipaksha: FAIL — Counter: "Waiting 12-24 months for rates to normalize may allow purchasing at lower rate and potentially lower price as market adjusts. The 20% increase can be addressed by moving to cheaper rental, negotiating, or finding a roommate."
  Badhita: PARTIAL — Depends entirely on local market conditions and personal financials, none specified.

FAILURE POINT: Fails at Asiddha (3a) — the foundational "rent is wasted money" premise is unproved and often false. The 20% increase triggered an emotional reaction being rationalized as financial logic.

INSIGHT: This decision is driven by a psychological trigger (the rent increase), not financial analysis. The relevant question is not "is rent too high?" but "is buying cheaper than renting given my specific numbers?" The real decision requires a spreadsheet, not a syllogism — and asking it philosophically suggests emotional framing has displaced analytical framing."""),

("My partner says we should send our child to private school because public school test scores are declining. Valid?",
"""CLAIM: We should send our child to private school because public school test scores are declining.

SYLLOGISM:
  Pratijna: Our child should attend private school rather than public.
  Hetu: Public school test scores are declining, indicating declining quality; private schools provide superior education. — Pramana basis: Shabda (media reports) plus Anumana (test scores as proxy for quality).
  Udaharana: The 2022 NAEP showed the largest math score declines in assessment history — 5-8 points for 4th/8th graders. Real, measured data.
  Upanaya: National averages include enormous variation. The relevant question is whether OUR LOCAL school's scores declined, not national averages. If our local school maintained scores, the national trend is irrelevant.
  Nigamana: The conclusion follows ONLY IF our local school participates in the trend AND private schools produce better outcomes for comparable students. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — Multiple unproved claims: (1) "declining scores" unverified for our school, (2) score declines may reflect pandemic disruption (temporary), not quality decline, (3) "private schools are superior" — when controlled for family income and parental education (Lubienski & Lubienski 2013), private schools perform NO BETTER. The apparent advantage is selection effect, not school effect.
  Viruddha: FAIL — "Because scores are declining, the school needs engaged parents to improve. Withdrawing our child accelerates the decline." The hetu supports civic engagement against private school flight.
  Anaikantika: FAIL — "Declining scores" justifies many responses: tutoring, charter schools, enrichment programs, moving districts, supplementing at home. Does not uniquely support private school.
  Satpratipaksha: FAIL — Counter: "Private school tuition ($10K-$40K/year) invested in tutoring, enrichment, travel, and college savings would provide greater benefit. Research shows family educational investment explains more outcome variance than school choice."
  Badhita: FAIL — The most rigorous studies (lottery-based admission) show school sector explains a small fraction of outcomes compared to family factors.

FAILURE POINT: Fails at Asiddha (3a) on the critical unstated assumption that private schools produce better outcomes for comparable students. The perceived superiority is largely SELECTION EFFECT: families choosing private school tend to be wealthier and more educationally involved. The argument attributes to the school what belongs to the family.

INSIGHT: The partner has observed a correlation (private school students perform better) and attributed it to the school, when research shows it is primarily attributable to the family. The argument uses test scores as proxy for a concern that is actually about social environment and class positioning — naming this honestly would lead to better decision-making."""),

# ===== DEBUGGING (3) =====

("Our production API returns 502 errors intermittently for 3 days. Backend team says network issue. Infra team says app is crashing. Who is right?",
"""CLAIM: The intermittent 502 errors are caused by application crashes (infra team) rather than network instability (backend team).

SYLLOGISM:
  Pratijna: The 502 errors are caused by application crashes.
  Hetu: A 502 Bad Gateway error means the reverse proxy received an invalid response from the upstream application. This is definitionally application-side. — Pramana basis: Pratyaksha (HTTP spec RFC 7231 defines 502 as gateway receiving invalid upstream response).
  Udaharana: Common 502 pattern: Nginx forwards to Gunicorn worker, worker is OOM-killed or deadlocked, Nginx gets no valid response, returns 502. Documented extensively in Nginx troubleshooting.
  Upanaya: If the load balancer returns 502, it received the request (network client-to-LB works) and attempted forwarding (network LB-to-app initiated) but got invalid response. Intermittent nature suggests app is sometimes healthy, sometimes unhealthy.
  Nigamana: The 502 code, by HTTP spec, indicates infra team's diagnosis is more likely correct. — Modality: Probable.

HETVABHASA AUDIT:
  Asiddha: PASS — The hetu (502 = upstream invalid response) is established by RFC standard.
  Viruddha: PASS — If the problem were pure network failure, the client would see connection timeouts or 503, not 502. 502 specifically requires the proxy received something invalid.
  Anaikantika: PARTIAL FAIL — Network instability BETWEEN LB and app servers (packet loss, TCP RST from firewalls) could cause the proxy to receive incomplete responses, triggering 502. "Network issue" is not fully eliminated — but the relevant segment is LB-to-app, not client-to-LB.
  Satpratipaksha: PARTIAL FAIL — Counter from backend: "App logs show no crashes during 502 events." However, if the process was OOM-killed, there would be no log entry — the process died before logging. Absence of logs does not prove absence of crashes.
  Badhita: PASS — Available evidence is consistent with the application-crash hypothesis.

FAILURE POINT: The genuine ambiguity at Anaikantika (3c) is real but narrow. The STRONGER failure is that neither team has checked DIAGNOSTIC EVIDENCE: (1) LB logs for upstream error type, (2) app server dmesg for OOM kills, (3) network metrics between LB and app tier.

INSIGHT: The dispute is not a LOGIC problem but a DIAGNOSTIC problem argued as if it were logic. Both teams reason from positional bias rather than evidence. The 502 constrains the hypothesis space but does not uniquely determine root cause. The real failure: the teams are arguing instead of looking. The intermittent nature suggests resource exhaustion under peak load — the infra team is more correct (app failing) but for reasons the backend team should own (resource management)."""),

("Our CI pipeline takes 45 minutes. A developer says we should switch from Jest to Vitest because Vitest is faster. Will this solve it?",
"""CLAIM: Switching from Jest to Vitest will solve our 45-minute CI pipeline problem.

SYLLOGISM:
  Pratijna: Replacing Jest with Vitest will significantly reduce CI duration.
  Hetu: Vitest is faster than Jest due to native ES modules and Vite's transformation pipeline, avoiding Jest's CJS transformation overhead. — Pramana basis: Pratyaksha (published benchmarks) plus Shabda (Vitest documentation).
  Udaharana: Vitest benchmarks show 2-5x speed improvements over Jest for ESM/TypeScript projects. Faker.js and Storybook reported meaningful improvements after switching.
  Upanaya: Speed gains came from eliminating CJS transformation. But a 45-minute pipeline is almost certainly NOT 45 minutes of tests. CI includes: checkout, dependency install, lint, type-check, build, test, deploy prep. If tests take 10 minutes of 45, even 5x improvement saves 8 minutes — a 17% reduction, not a solution.
  Nigamana: Vitest may be faster for test execution, but whether it "solves" the pipeline depends on what proportion is test time. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — The IMPLICIT claim ("test execution is the primary bottleneck") is completely unproved. No profiling done. Typical CI bottlenecks: dependency install (2-8 min), Docker builds (5-15 min), integration tests (10-20 min), deployment (5-10 min). Unit tests often a small fraction.
  Viruddha: PASS — Faster tests don't make the pipeline slower.
  Anaikantika: FAIL — "Tool X is faster than tool Y" equally justifies switching npm to pnpm, webpack to Vite, Docker to Nix. Without profiling, any substitution sounds equally valid.
  Satpratipaksha: FAIL — Counter: "Profiling and parallelizing the actual bottleneck would produce greater savings at lower cost. Pipeline optimization through parallelization and caching routinely yields 50-80% improvements without changing tools."
  Badhita: FAIL — Standard DevOps practice: profile, cache dependencies, parallelize, use incremental testing. These routinely reduce 45-minute pipelines to 10-15 minutes.

FAILURE POINT: Fails at Asiddha (3a) — the assumption that test execution is the bottleneck has not been established. The developer committed "premature optimization of the wrong component" — replacing the engine in a car with a flat tire.

INSIGHT: This reveals TOOL-SHAPED thinking. When excited about a new tool (Vitest), problems start looking solvable by adopting it. The valid first step is profiling ("where do the 45 minutes go?"), not tool switching. The answer is almost certainly: dependency caching, build layer caching, test parallelization. The tool migration might be right AFTER profiling — but proposing it BEFORE profiling is solution-first reasoning."""),

("Users say our web app is slow. A team member says adding Redis caching will fix it. Evaluate.",
"""CLAIM: Adding Redis caching will fix our web application's slowness.

SYLLOGISM:
  Pratijna: Implementing Redis will resolve performance problems reported by users.
  Hetu: Caching reduces database query load by serving frequent data from memory instead of disk. — Pramana basis: Pratyaksha (caching is established optimization) plus Anumana.
  Udaharana: Stack Overflow achieved sub-millisecond response for cached pages that previously took 50-100ms from database. Cache hit rates above 90% on high-traffic pages.
  Upanaya: Stack Overflow's read-heavy workload had extreme data locality. Bridge holds IF our slowness is caused by repeated reads of cacheable data. If slowness comes from slow writes, complex joins, N+1 queries, frontend rendering, or third-party API calls, caching won't help.
  Nigamana: Redis CAN improve read-heavy performance, but fixes our problem ONLY IF repeated database reads are the bottleneck. — Modality: Conditional.

HETVABHASA AUDIT:
  Asiddha: FAIL — "The app is slow because of database query load" is assumed, not established. "Users say it's slow" could mean: slow initial page load (frontend bundle size), slow API responses (database, logic, or third-party), sluggish interactions (frontend rendering), or specific slow operations.
  Viruddha: PASS — Caching doesn't make performance worse (assuming correct implementation).
  Anaikantika: FAIL — "Reducing database load improves performance" equally justifies: adding indexes, optimizing queries, connection pooling, read replicas, denormalization. Caching is architecturally the most complex option.
  Satpratipaksha: FAIL — Counter: "Before adding Redis (deployment, monitoring, cache invalidation, failure handling), check: proper indexes (missing indexes are #1 slow-query cause), N+1 queries, frontend performance. Zero-infrastructure changes often solve 80% of problems."
  Badhita: FAIL — Frontend issues (render-blocking resources, large JS bundles) account for ~80% of perceived user-facing latency. Backend caching while ignoring frontend may produce no user-perceived improvement.

FAILURE POINT: Fails at Asiddha (3a) — diagnosis is entirely absent. "Users say it's slow" has been translated to "add caching" without analysis. The team member has pattern-matched "slow" to their favorite solution.

INSIGHT: This is PRESCRIPTION WITHOUT DIAGNOSIS. Redis is a SPECIFIC solution to a SPECIFIC problem (repeated reads of cacheable data). The valid sequence: (1) MEASURE where time is spent, (2) IDENTIFY bottleneck, (3) OPTIMIZE with simplest effective solution, (4) MEASURE again. Caching may appear at step 3 — but should NEVER appear at step 1."""),

# ===== ETHICS (3) =====

("A company's AI hiring tool disproportionately rejects women. The CEO says: 'The algorithm is objective — it just finds patterns in historical data. The data is biased, not the algorithm.' Valid?",
"""CLAIM: The AI hiring tool is not biased because it objectively reflects patterns in historical data.

SYLLOGISM:
  Pratijna: The AI algorithm is not biased because it is an objective pattern-finder.
  Hetu: The algorithm applies mathematical functions without human prejudice; any disparate impact originates from data, not tool. — Pramana basis: Anumana plus Shabda (AI as "objective" framing).
  Udaharana: Amazon's recruiting tool (2014) trained on 10 years of male-dominated hiring data learned to penalize resumes containing "women's" and downgrade all-women's college graduates. Amazon scrapped it in 2017.
  Upanaya: Amazon's algorithm faithfully learned biased patterns in biased data. The same dynamic applies: if historical data reflects past discrimination, the algorithm reproduces it.
  Nigamana: The algorithm IS biased precisely BECAUSE it accurately reflects biased data. The CEO's defense actually CONFIRMS rather than refutes the bias. — Modality: Necessary.

HETVABHASA AUDIT:
  Asiddha: FAIL — Mathematical precision is not ethical objectivity. The CHOICE of training data, features, optimization target, and evaluation metrics embeds human values at every step. "Objective" meaning "mathematical" differs from "objective" meaning "free from unjust discrimination."
  Viruddha: FAIL — The hetu is SELF-REFUTING. "The algorithm finds patterns in historical data" is simultaneously an explanation of WHY it is biased. If historical data contains discriminatory patterns (it does), the algorithm REPRODUCES them. The defense IS the indictment.
  Anaikantika: FAIL — The reasoning "mathematical pattern-finding is objective, therefore fair" could justify any discrimination laundered through data: redlining, racial profiling, credit discrimination. In each case, "objective data" reflects structural discrimination.
  Satpratipaksha: FAIL — Counter: "An algorithm reproducing historical discrimination is discriminatory BY DEFINITION. Legal frameworks (Title VII disparate impact) state discriminatory outcomes are actionable regardless of intent."
  Badhita: FAIL — EEOC, EU AI Act, and OFCCP all establish that automated tools producing disparate impact must demonstrate job-relatedness. "It's mathematical" is not a legal defense.

FAILURE POINT: Self-refuting at Viruddha (3b). The CEO's own explanation of how the algorithm works IS the mechanism of algorithmic bias. This is logically identical to "I'm not prejudiced — I'm just treating people based on stereotypes I learned growing up."

INSIGHT: The CEO treats "bias" as synonymous with "human prejudice" (conscious discrimination). But algorithmic bias is a STRUCTURAL property — systematically different outcomes for protected groups without job-relevant justification. Structural bias requires no intent. The real question is not "is the algorithm biased?" (it is, by the CEO's own description) but "what are we going to do about it?" """),

("'It is ethical to lie to a murderer who asks where your friend is hiding.' Evaluate using Nyaya method.",
"""CLAIM: It is ethical to lie to a murderer seeking their victim's location.

SYLLOGISM:
  Pratijna: Lying to a murderer seeking their victim is ethically permissible (possibly obligatory).
  Hetu: The moral prohibition against lying exists to protect trust and prevent harm; when truth-telling would directly cause an innocent person's death, the stronger duty to prevent harm overrides. — Pramana basis: Anumana (moral principle weighing) plus Shabda (extensive philosophical tradition from Benjamin Constant to modern ethics).
  Udaharana: During the Holocaust, Corrie ten Boom's family lied to Nazi soldiers about hiding Jewish refugees. This is universally regarded as morally praiseworthy.
  Upanaya: In the ten Boom case: (a) murderous intent, (b) truth would cause death, (c) no other protection available, (d) lie harmed no innocent party. Same conditions hold in the philosopher's scenario.
  Nigamana: Lying to a murderer seeking their victim is ethically permissible. — Modality: Highly probable across nearly all ethical frameworks except strict Kantian absolutism.

HETVABHASA AUDIT:
  Asiddha: PASS — The grounding (lying prohibitions exist to protect trust and prevent harm) is well-established even in Kant's own framework.
  Viruddha: FAIL (interesting case) — Kant argued the opposite: "Lying always corrupts rational nature and undermines universal truth-telling." Internally consistent within his framework. However, this conclusion is rejected by the vast majority of moral philosophers as reductio ad absurdum of absolutism.
  Anaikantika: PARTIAL FAIL — "Stronger duties override weaker ones" is a general principle that needs bounding. The limiting principle: (a) direct and immediate conflict, (b) no third option, (c) minimal violation, (d) categorically higher protected value (human life > this truth-telling).
  Satpratipaksha: PASS — Kantian absolutism has been widely examined and rejected. Near-universal consensus across ethical traditions supports this conclusion.
  Badhita: PASS — Moral intuition overwhelmingly supports the lie as right across cultures.

FAILURE POINT: The ONLY vulnerability is Anaikantika (3c) — the override principle needs bounding to prevent abuse. The opponent would argue: "If you accept duty-override here, where do you draw the line?"

INSIGHT: The scenario is not really about lying — it is about the STRUCTURE OF MORAL RULES. Kant's counterintuitive conclusion is a NECESSARY CONSEQUENCE of treating moral rules as absolute. Anyone who finds it repulsive has implicitly accepted that moral rules have exceptions. The real philosophical question: what is the PRINCIPLED STRUCTURE for when rules can be overridden? This is what Ross's prima facie duties attempt to answer."""),

("A tech company argues collecting and selling user location data is ethical because users agreed to the terms of service. Evaluate.",
"""CLAIM: Collecting and selling location data is ethical because users consented via terms of service.

SYLLOGISM:
  Pratijna: Collecting and selling location data is permissible because users accepted the ToS.
  Hetu: Consent legitimizes data practices — users who accept ToS have voluntarily agreed. — Pramana basis: Anumana (consent doctrine) plus Shabda (contractual consent tradition).
  Udaharana: A gym membership: members accept liability waivers, and the gym is protected when warned-about injuries occur. Consent transforms the gym's duty.
  Upanaya: The bridge FAILS because: (a) average ToS is 30+ pages of legal language users cannot understand, (b) scope of "selling location data" is not foreseeable, (c) users often have no viable alternatives, (d) consent is bundled — cannot accept service while declining data sale.
  Nigamana: Formal ToS acceptance does not establish ethically valid consent because conditions for meaningful consent are unmet. — Modality: The conclusion does NOT follow.

HETVABHASA AUDIT:
  Asiddha: FAIL — Clicking "I agree" is not meaningful consent. Research (Obar & Oeldorf-Hirsch, 2018): 74% skip reading ToS, average ToS requires college reading level and 20-30 minutes, comprehension below 50%. "Consent" without understanding is a legal fiction.
  Viruddha: FAIL — If the company relies on ToS "consent" KNOWING users don't understand, it deliberately exploits information asymmetry. Using a consent mechanism known to produce no actual consent is LESS ethical than having no mechanism — adding deception to privacy violation.
  Anaikantika: FAIL — ToS acceptance could justify ANY buried practice: biometric sale, in-home recording, election manipulation. If ToS legitimizes anything, there is no ethical limit — only a drafting challenge.
  Satpratipaksha: FAIL — Counter: "Ethical data practices require informed, specific, freely-given, revocable consent. Location data reveals home, workplace, medical visits, political activity. The ethical standard exceeds ToS acceptance." Supported by GDPR's explicit requirements.
  Badhita: FAIL — GDPR, CCPA, and FTC enforcement actions have rejected ToS consent as insufficient for data selling.

FAILURE POINT: Self-defeating at Viruddha (3b). The company knows users don't meaningfully consent (every metric confirms this), yet uses formal consent as ethical justification. This is PERFORMATIVE CONTRADICTION: citing consent while designing systems to minimize genuine consent.

INSIGHT: The real test: if the company offered a one-sentence opt-in — "We will sell your GPS coordinates to data brokers who will sell them to anyone" — how many users would agree? The answer reveals whether the current ToS represents consent or exploitation of friction."""),

# ===== PROJECT PLANNING (3) =====

("Our PM says adding more developers to our late project will help meet the deadline. Evaluate.",
"""CLAIM: Adding more developers to our late project will accelerate delivery to meet the deadline.

SYLLOGISM:
  Pratijna: Adding developers to our behind-schedule project will speed delivery.
  Hetu: More developers = more parallel capacity; more people working = features completed faster. — Pramana basis: Anumana (linear scaling assumption) plus Shabda (intuitive management principle).
  Udaharana: Construction: adding bricklayers DOES reduce wall-building time because bricklaying is highly parallelizable with minimal coordination.
  Upanaya: The bridge FAILS for software because: (a) code modules are deeply interdependent, (b) each new developer requires onboarding, (c) communication overhead scales quadratically (n*(n-1)/2), (d) partitioning work requires architectural understanding taking weeks to acquire.
  Nigamana: Adding developers to a late project will likely make it LATER. — Modality: Highly probable. This is Brooks's Law, established since 1975.

HETVABHASA AUDIT:
  Asiddha: FAIL — "More developers = more parallel capacity" is unproved for software. Brooks demonstrated non-linear scaling: adding a developer to team of N creates N new communication channels and weeks of onboarding drain on existing developers.
  Viruddha: FAIL — Adding developers introduces: onboarding time (existing devs teach instead of produce), quadratic communication overhead, codebase partitioning costs, integration overhead (more merges, reviews). Net effect: NEGATIVE productivity for 4-8 weeks.
  Anaikantika: PASS — The hetu specifically addresses developer count and velocity.
  Satpratipaksha: PASS — No strong counter. Exceptions (highly modular codebases, purely parallelizable tasks) are narrow.
  Badhita: FAIL — QSM Associates' analysis of 4,000+ projects found inverse relationship between team size and individual productivity beyond optimal size (5-9 for software).

FAILURE POINT: Fails at Viruddha (3b). Adding developers to a late project typically makes it later. Brooks's Law is the most replicated finding in software engineering management.

INSIGHT: Managers keep making this mistake because the intuition works for physical tasks. The error is a category error: treating knowledge work like manual labor. Software development is a COMMUNICATION problem, not a labor problem. The bottleneck is shared understanding, which cannot be parallelized."""),

("A Scrum Master insists: 'If we follow Scrum correctly, the project will succeed.' Evaluate.",
"""CLAIM: Correct Scrum implementation guarantees project success.

SYLLOGISM:
  Pratijna: Following Scrum correctly will make our project succeed.
  Hetu: Scrum provides iterative delivery, feedback, transparency, and adaptation that eliminate causes of failure (unclear requirements, late feedback, scope creep). — Pramana basis: Shabda (Scrum Guide, Agile Manifesto) plus Anumana.
  Udaharana: Spotify's Scrum-derived engineering culture (squads, chapters, guilds) enabled scaling to 4,000+ engineers. But Spotify's success also includes exceptional product-market fit, $2.7B+ in VC, and first-mover advantage. And Spotify has publicly moved away from many elements.
  Upanaya: The bridge is weak: Spotify's success cannot be attributed to methodology alone. A project with bad product-market fit fails regardless of Scrum quality.
  Nigamana: Scrum's practices are valuable but cannot guarantee success because success depends on factors outside Scrum's scope. — Modality: Invalid as stated.

HETVABHASA AUDIT:
  Asiddha: FAIL — The hetu assumes unclear requirements, late feedback, and scope creep are THE causes of failure. Projects also fail from: wrong product (no market need — #1 killer per CB Insights), wrong timing, insufficient resources, technical infeasibility, competitive pressure. Scrum addresses none of these.
  Viruddha: FAIL — Scrum's ceremony overhead (20-30% of team time) can REDUCE velocity for small teams with clear vision or exploratory projects requiring deep focus.
  Anaikantika: FAIL — "Iterative delivery and feedback" equally supports Kanban, XP, Shape Up, or informal "build, show, adjust." The hetu proves iterative development is valuable, not that Scrum specifically is necessary.
  Satpratipaksha: FAIL — Counter: "CHAOS Report data shows project success rates haven't significantly improved since widespread Agile/Scrum adoption. If correct Scrum guaranteed success, industry success rates should have improved."
  Badhita: FAIL — Project success requires building the right thing (product-market fit), building it well (quality), fast enough (timing), cheaply enough (cost), in a viable market. Scrum addresses aspects of quality and timing but provides no mechanism for product-market fit.

FAILURE POINT: Fails at Asiddha (3a) — misidentifies failure causes as exclusively process-related. The Scrum Master sees all risks as methodology problems because that is their domain.

INSIGHT: The Scrum Master conflates two definitions of "success." Scrum meaning: "deliver working software on a predictable cadence." Broader meaning: "achieve business objectives." Scrum is an EXECUTION framework presented as a SUCCESS framework. Excellent execution of a bad strategy produces beautifully built products nobody uses."""),

("A stakeholder says: 'We need detailed requirements docs before development begins, or we'll build the wrong thing.' Evaluate.",
"""CLAIM: Detailed requirements documentation must precede development to prevent building the wrong product.

SYLLOGISM:
  Pratijna: Detailed requirements documentation is necessary before development begins.
  Hetu: Without comprehensive requirements, developers lack specification, wasting effort on misaligned features. Documentation provides shared, unambiguous reference. — Pramana basis: Anumana plus Shabda (waterfall methodology, PMBOK).
  Udaharana: Denver International Airport baggage system (1994): built from incomplete, evolving requirements, resulting in $560M overrun and 16-month delay. System eventually scrapped.
  Upanaya: DIA's requirements instability was extreme. Most software projects have lower complexity. Modern iterative approaches manage evolving requirements through feedback loops rather than upfront documentation.
  Nigamana: Some requirement clarity is necessary, but DETAILED documentation as prerequisite is neither necessary nor sufficient. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — Two unproved assumptions: (1) detailed documentation produces shared understanding (different readers interpret differently; docs create ILLUSION of alignment more dangerous than acknowledged ambiguity), (2) requirements can be known before development (for novel products, requirements are DISCOVERED through building).
  Viruddha: FAIL — Detailed documentation can CAUSE the problem it claims to prevent. Teams treat the document as authoritative, resisting course changes when feedback contradicts specification. Documentation locks teams into building the wrong thing MORE thoroughly.
  Anaikantika: FAIL — "Without clear specification, developers build wrong things" supports: user story mapping, rapid prototyping, design sprints, stakeholder interviews, competitive analysis, MVP testing. Documentation is one approach and arguably the least efficient.
  Satpratipaksha: FAIL — Counter: "Building a quick prototype and testing with users provides better clarity in one week than months of documentation, because it reveals requirements stakeholders cannot articulate until they see working software." Supported by lean startup methodology.
  Badhita: FAIL — Standish Group data consistently shows iterative approaches with minimal upfront documentation produce higher success rates than documentation-heavy waterfall.

FAILURE POINT: Fails at Viruddha (3b). Documentation creates organizational inertia — the document becomes a political artifact (stakeholders "signed off") rather than a learning tool.

INSIGHT: The stakeholder treats requirements as FIXED REALITY to be discovered and recorded, like surveying land. For most software, requirements are EMERGENT — discovered through building. The question is not "do we need requirements?" (yes) but "what is the most efficient way to discover accurate requirements?" For most software: "build and test" not "write and review." """),

# ===== LEGAL/CONTRACTUAL (3) =====

("A vendor's SLA guarantees 99.99% uptime. They had 4 hours downtime last month. Their legal team claims SLA is annual, not monthly. Who's right?",
"""CLAIM: The vendor's 4 hours of monthly downtime complies with 99.99% SLA because measurement is annual.

SYLLOGISM:
  Pratijna: The vendor is within SLA despite 4 hours of downtime because the SLA measures annually.
  Hetu: 99.99% annual uptime allows ~52.6 minutes per year; single months may have more. — Pramana basis: Anumana (math) — but depends on contract language (Shabda).
  Udaharana: AWS S3's February 2017 outage (~4 hours): SLA was explicitly monthly, resulting in service credits. AWS's SLA specifies monthly measurement.
  Upanaya: If our contract doesn't specify measurement window, the annual interpretation is arguable. However, industry standard is monthly, and ambiguous contracts are interpreted against the drafter (contra proferentem).
  Nigamana: Even under the vendor's annual interpretation, 4 hours (240 minutes) ALREADY exceeds the annual allowance of 52.6 minutes. The legal argument is mathematically self-defeating. — Modality: Necessary.

HETVABHASA AUDIT:
  Asiddha: FAIL — The hetu collapses on its own arithmetic. 99.99% annual = 52.6 min/year. The vendor had 240 minutes in ONE month. Even under annual measurement, 240 > 52.6. They may have confused 99.99% with 99.9% (8.76 hrs/year) or 99.5% (~43 hrs/year).
  Viruddha: FAIL — By invoking annual measurement, the vendor made their position WORSE: they've exhausted 4.56x their annual budget in one month and must maintain perfect uptime for 11 remaining months.
  Anaikantika: PASS — Measurement window IS relevant to SLA interpretation generally.
  Satpratipaksha: PASS — No counter-argument available. Mathematics is conclusive.
  Badhita: FAIL — 4 hours violates 99.99% under any measurement window shorter than ~4.56 years.

FAILURE POINT: Catastrophic Asiddha (3a) — the vendor's own numbers disprove their position. The legal team constructed an argument without checking whether the numbers support it.

INSIGHT: Two failures: (1) Mathematical: the legal team used legal pattern-matching ("argue longest window") without domain verification. (2) Contractual design: a 99.99% SLA without explicit measurement window is poorly drafted. Under contra proferentem, if the vendor drafted it, ambiguity resolves in the customer's favor."""),

("An NDA prohibits sharing 'confidential information.' An employee shares publicly available information learned through employment. Violation?",
"""CLAIM: Sharing publicly available information learned through employment violates the NDA.

SYLLOGISM:
  Pratijna: The employee violated the NDA by sharing information learned through employment, even though it is publicly available.
  Hetu: The NDA prohibits "confidential information" and the employee learned it in a confidential context. — Pramana basis: Anumana plus Shabda (NDA language).
  Udaharana: In Convolve v. Compaq (2013), the court ruled information independently available in public sources does not constitute trade secrets, even if also learned through employment. Public availability destroys confidentiality.
  Upanaya: If the shared information is genuinely publicly available (published papers, press releases, open-source code), the NDA's designation cannot override its public nature. Bridge holds if truly public.
  Nigamana: Sharing publicly available information does NOT violate the NDA. — Modality: Highly probable under established doctrine, with narrow exception for confirming/contextualizing public information with private knowledge.

HETVABHASA AUDIT:
  Asiddha: FAIL — The hetu assumes CONTEXT of learning determines confidentiality. Legally incorrect. Confidentiality is a PROPERTY OF THE INFORMATION, not the channel. Most well-drafted NDAs explicitly exclude publicly available information.
  Viruddha: PASS — There IS a gray area: combining public information with confidential knowledge.
  Anaikantika: FAIL — "Learned through employment, therefore confidential" would make ALL knowledge gained during employment confidential — including general skills and public conference content. This turns NDAs into non-compete agreements.
  Satpratipaksha: PARTIAL — Legitimate counter: the "mosaic theory." Individual public facts CAN become confidential when combined to reveal non-public strategy (public patent + public job posting + public supplier contract = unannounced product direction).
  Badhita: PASS — Standard NDA law: public domain information cannot be confidential.

FAILURE POINT: Fails at Asiddha (3a) — the premise that learning context determines confidentiality is legally wrong. But the mosaic problem at Satpratipaksha is a real nuance.

INSIGHT: The question turns on a subtle distinction between INFORMATION and CONTEXT. The information itself (public) is not confidential. But the CONTEXT — that this particular information is relevant to the employer's plans — can be confidential. Sharing a public paper is fine. Sharing a public paper and saying "this is what we're building our next product on" potentially violates the NDA — not the paper (public) but the relevance (confidential)."""),

("A consulting firm bills T&M hours the client suspects are inflated. The firm says: 'You agreed to T&M, so you accepted variable hours.' Valid?",
"""CLAIM: Under T&M, the firm bears no obligation to justify hours because the client accepted T&M pricing.

SYLLOGISM:
  Pratijna: The firm is within rights to bill claimed hours because the client accepted T&M.
  Hetu: T&M means the client pays actual time; accepting T&M means accepting that hours are determined by the provider. — Pramana basis: Anumana (T&M contract structure) plus Shabda (contract law).
  Udaharana: In US v. Bechtel, the court found T&M contractors DO have an implied good-faith obligation including not billing for unperformed work. T&M is not carte blanche.
  Upanaya: The firm's argument conflates (a) variability in hours required (legitimate) with (b) billing for hours not worked (fraud). The client accepted (a) but not (b).
  Nigamana: The client accepted variable hours but did NOT accept fraudulent billing. T&M shifts estimation risk, not integrity risk. — Modality: Necessary under basic contract law.

HETVABHASA AUDIT:
  Asiddha: FAIL — T&M does NOT transfer ALL billing risk. Implied covenant of good faith in all US jurisdictions. The client accepted "work might take longer" not "hours might be fabricated."
  Viruddha: FAIL — The firm's insistence that T&M eliminates accountability STRENGTHENS the client's case: a firm confident in its billing would welcome scrutiny.
  Anaikantika: FAIL — "You accepted the pricing model, therefore cannot question any bill" could justify any overcharge. Applied to a restaurant or mechanic, the absurdity is clear.
  Satpratipaksha: FAIL — Counter: "T&M universally includes or implies audit rights, contemporaneous time records, and honest billing obligation." Supported by standard templates.
  Badhita: FAIL — UCC implied covenant, standard contract terms, and case law all establish that T&M providers must maintain verifiable records.

FAILURE POINT: Anaikantika (3c) — the reasoning eliminates all accountability. If "accepting T&M means accepting any bill," then T&M is legalized fraud. No legal system supports this.

INSIGHT: The firm performed a sleight-of-hand with "risk acceptance." T&M transfers ESTIMATION RISK (work might take longer) but not INTEGRITY RISK (provider might bill for unworked hours). These are fundamentally different. The valid response: "Provide daily timesheets with task descriptions, and we will pay every legitimate hour." """),

# ===== CREATIVE DECISIONS (3) =====

("A game designer says: 'Our game should have permadeath because roguelikes are the most popular indie genre.' Sound?",
"""CLAIM: Our game should include permadeath because roguelikes are currently the most popular indie genre.

SYLLOGISM:
  Pratijna: We should implement permadeath because the roguelike genre is popular.
  Hetu: Roguelikes are popular; popular genres attract more players; therefore incorporating permadeath maximizes player base. — Pramana basis: Shabda (industry trends) plus Anumana.
  Udaharana: Hades incorporated roguelike permadeath into narrative action and achieved 1M+ units in first three days. But permadeath worked because the narrative was DESIGNED around dying (Zagreus escaping the underworld), each run had permanent progression, and core gameplay was excellent independently.
  Upanaya: The bridge holds ONLY IF our game similarly accommodates permadeath as integrated mechanic. If our game is a narrative adventure or city builder, permadeath would be hostile to core experience.
  Nigamana: "Roguelikes are popular" does not justify adding permadeath to any game. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — "Roguelikes are the most popular indie genre" is debatable. Depends on metric: total sales, number of titles, revenue per title, active players. Market saturation means MORE competition.
  Viruddha: FAIL — If roguelikes are popular, the market is SATURATED. Entering means competing against Hades, Slay the Spire, Dead Cells. Choosing a LESS popular genre with less competition might yield better results.
  Anaikantika: FAIL — "Most popular genre right now" could justify any trend-following: battle royale, crafting-survival, cozy sim, deckbuilder. Provides no mechanism for evaluating THIS game's fit.
  Satpratipaksha: FAIL — Counter: "The most successful indie games succeed by DEFINING a niche. Stardew Valley, Hollow Knight, Undertale, Celeste — all succeeded through distinctive vision, not trend-following."
  Badhita: FAIL — Genre choice is a weak predictor compared to quality, marketing, and distinctive identity.

FAILURE POINT: Fails at Viruddha (3b). Genre popularity creates saturation working AGAINST new entrants. "Many people buy roguelikes" differs from "many people will buy OUR roguelike."

INSIGHT: The designer confuses market analysis with design vision. Hades succeeded not because it was a roguelike but because Supergiant made an extraordinary game that used roguelike mechanics as narrative device. The question is not "what genre is popular?" but "what mechanics serve the experience we're creating?" """),

("A band's manager argues they should release music exclusively on TikTok because that's where music goes viral. Sound reasoning?",
"""CLAIM: A band should release exclusively on TikTok because that's where music goes viral.

SYLLOGISM:
  Pratijna: Exclusive TikTok release will maximize audience growth.
  Hetu: TikTok is the primary viral music discovery platform; concentrating there maximizes breakthrough probability. — Pramana basis: Pratyaksha (documented cases) plus Shabda (industry commentary).
  Udaharana: Lil Nas X's "Old Town Road" propelled partly through TikTok virality — 19 weeks at #1. Fleetwood Mac's "Dreams" resurged after a TikTok video. Real cases.
  Upanaya: In Lil Nas X's case, TikTok drove discovery but success required ALL platforms — Spotify, Apple Music, radio. TikTok created awareness; streaming platforms generated revenue. Exclusive TikTok captures discovery but FORFEITS monetization.
  Nigamana: TikTok is valuable for discovery but neither sufficient nor optimal as exclusive platform. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — Survivorship bias. Millions of songs on TikTok did NOT go viral. The viral hit rate is below 0.01%. "Viral" is an outcome, not a strategy.
  Viruddha: FAIL — TikTok favors 15-60 second clips. Music optimized for virality (catchy hooks, meme-able moments) may sacrifice depth, coherence, and artistic identity — qualities building lasting fanbases.
  Anaikantika: FAIL — "Release where discovery happens" equally justifies Spotify playlists, YouTube, Instagram Reels. "Exclusively" on any platform is concentration risk.
  Satpratipaksha: FAIL — Counter: "TikTok pays ~$0.002-0.004/view. Spotify pays $0.003-0.005/stream. Apple Music $0.006-0.01. Revenue requires streaming presence. Exclusive TikTok forfeits radio, playlists, sync licensing."
  Badhita: FAIL — Every TikTok music success (Lil Nas X, Doja Cat, PinkPantheress) involved multi-platform release with TikTok as ONE channel.

FAILURE POINT: The argument fails at the word "exclusively." TikTok's value is as a DISCOVERY CHANNEL — one input to multi-platform strategy.

INSIGHT: The manager confuses the DISCOVERY funnel with the REVENUE funnel. TikTok drives discovery → Spotify drives listening → touring drives revenue. Cutting the funnel at TikTok captures attention with no conversion mechanism. Exclusivity on any single platform is concentration risk, not strategy."""),

("A novelist's editor says: 'Make your protagonist more likeable or readers won't finish the book.' Valid?",
"""CLAIM: A novel's protagonist must be likeable for readers to finish the book.

SYLLOGISM:
  Pratijna: The protagonist must be more likeable or readers will disengage.
  Hetu: Readers continue because they identify with and care about the protagonist; unlikeability breaks identification. — Pramana basis: Anumana (reader psychology) plus Shabda (publishing conventional wisdom).
  Udaharana: Gone Girl features two deeply unlikeable protagonists. Sold 20M+ copies. Readers were compelled by psychological puzzle, not affection. Patricia Highsmith's Tom Ripley (sociopathic murderer protagonist) — in print for 70 years.
  Upanaya: Readers stayed engaged despite disliking characters because other mechanisms operated: mystery, surprise, complexity, narrative virtuosity. The bridge holds only when likeability is the PRIMARY engagement mechanism.
  Nigamana: Protagonist likeability is ONE engagement mechanism, not a necessary condition. — Modality: False as stated.

HETVABHASA AUDIT:
  Asiddha: FAIL — "Caring about" is conflated with "liking." Readers of Crime and Punishment care intensely about Raskolnikov without liking him. "Care" can be driven by fascination, horror, intellectual engagement, desire to see consequences.
  Viruddha: FAIL — Making a protagonist more likeable can REDUCE engagement. The most memorable characters (Hamlet, Emma Bovary, Gatsby, Humbert Humbert, Amy Dunne) are memorable precisely because of flaws and moral ambiguity. Softening edges produces blander characters.
  Anaikantika: FAIL — "Readers need to identify with the protagonist" could justify any modification: make them younger, more attractive, more relatable. No specific guidance beyond "more pleasant."
  Satpratipaksha: FAIL — Counter: "Reader engagement depends on being COMPELLING, not likeable. Compelling characters can be fascinating, terrifying, pitiable, or morally complex."
  Badhita: FAIL — Bestsellers and enduring literature are populated by unlikeable protagonists. No correlation between likeability and success.

FAILURE POINT: Fails at Asiddha (3a) — "liking" is conflated with "caring about." The real question: "Does the reader have a REASON to keep turning pages?" Likeability is one reason among many.

INSIGHT: The editor's advice comes from risk-averse commercial instinct. "Make them likeable" is SAFE — reduces alienation risk. But it also reduces memorability. The correct question: "Is there sufficient reason for readers to keep reading?" The answer might be more complexity, stakes, mystery, or prose — not a more pleasant protagonist."""),

# ===== EDUCATION (3) =====

("A school administrator claims: 'Students who use laptops in class perform worse, so we should ban laptops.' Evaluate.",
"""CLAIM: Laptops should be banned from classrooms because their use correlates with lower exam performance.

SYLLOGISM:
  Pratijna: Ban laptops because laptop use correlates with lower scores.
  Hetu: Studies show laptop users score lower; therefore laptops cause worse performance. — Pramana basis: Pratyaksha (published studies) plus Anumana (correlation to causation to policy).
  Udaharana: Mueller and Oppenheimer (2014): laptop note-takers performed worse on conceptual questions due to verbatim transcription rather than active processing.
  Upanaya: The lab study controlled for distraction while real classrooms cannot. Real laptop use includes non-note-taking activities (browsing). The study measured immediate recall, not semester-long learning with review. Bridge from lab to policy is substantial.
  Nigamana: Laptop use correlates with lower performance in some contexts, but universal ban is not supported. — Modality: Weak for the policy conclusion.

HETVABHASA AUDIT:
  Asiddha: FAIL — Correlation-causation conflation. Laptop users who perform worse may be: (a) less engaged regardless (selection), (b) distracted by browsing (distraction, not device), (c) in larger lectures where all perform worse. Ravizza et al. (2017): the correlation disappeared when controlling for non-academic internet use.
  Viruddha: FAIL — Banning laptops HARMS students with disabilities (dyslexia, motor impairments), ESL students needing translation, STEM students needing computational tools.
  Anaikantika: FAIL — "X correlates with worse performance, ban X" could justify banning: back-row seating, part-time jobs, commuting. No mechanism for distinguishing harmful tools from correlates.
  Satpratipaksha: FAIL — Counter: "Teaching productive laptop use prepares students for a professional world. Banning the tool rather than teaching its use fails to develop digital literacy."
  Badhita: FAIL — Morehead et al. (2019) direct replication found NO significant difference between laptop and longhand note-takers.

FAILURE POINT: Fails at Asiddha (3a) — the causal claim is confounded by engagement levels, browsing behavior, and selection effects. When controlled, the laptop effect diminishes or disappears.

INSIGHT: The administrator is solving the WRONG PROBLEM. The issue is student attention management, not laptops. In classes with active learning pedagogies (frequent questions, group exercises), the laptop-performance gap disappears because students are too busy participating to browse. The real intervention: redesigning instruction to demand engagement, not banning tools."""),

("A university dean claims: 'Our MBA is valuable because graduates earn 40% more than before enrollment.' Evaluate.",
"""CLAIM: The MBA program is valuable because graduates earn 40% more post-graduation.

SYLLOGISM:
  Pratijna: Our MBA is valuable, demonstrated by 40% salary increase.
  Hetu: A 40% increase demonstrates the program adds significant economic value. — Pramana basis: Pratyaksha (salary data) plus Anumana (salary increase = program value).
  Udaharana: Medical school: salary increase is accepted as evidence of value because (a) credential legally required, (b) skills directly cause productivity, (c) the counterfactual means not practicing medicine.
  Upanaya: For MBAs: (a) not required for any job, (b) same positions accessible without MBA, (c) the 40% increase may be from career switching, maturation, or credential signaling rather than education.
  Nigamana: MBA graduates earn more, but whether the MBA CAUSED the increase is not established. — Modality: Weak.

HETVABHASA AUDIT:
  Asiddha: FAIL — Post hoc ergo propter hoc. Confounds: (a) career maturation (most earn more at 30 than 28 regardless), (b) self-selection (ambitious people would grow without MBA), (c) career switching (nonprofit to consulting = sector jump, not education effect), (d) relocation to higher-COL cities.
  Viruddha: FAIL — Full costs: $150K-$250K tuition + $150K-$250K foregone salary = $300K-$500K investment. 40% increase on $80K = $32K/year additional. Break-even: 9-15 YEARS. May represent poor ROI.
  Anaikantika: FAIL — "Salary increase after program" could justify any credential. Any program attracting ambitious people and taking 1-2 years will show post-completion increases from time passage and self-selection alone.
  Satpratipaksha: FAIL — Dale and Krueger (2002, 2014): students ACCEPTED to elite schools but attending less selective ones showed virtually no earnings difference. Selection effect accounts for nearly all "prestige premium."
  Badhita: FAIL — PayScale data shows MBA ROI is negative for many programs outside top 20.

FAILURE POINT: Fails at Asiddha (3a). The before-after comparison is one of the weakest forms of evidence in program evaluation — cannot distinguish program effect from time, selection, career-switching, and relocation effects.

INSIGHT: The before-after metric was CHOSEN for its flattering number. The unreported metrics: salary vs. matched non-MBA control group, net return after costs, median (not mean) increase, what percentage saw stagnant returns. The dean's choice of most favorable metric reveals more about marketing than educational value."""),

("A parent argues: 'My child should skip a grade because they scored in the 99th percentile on standardized tests.' Sufficient reasoning?",
"""CLAIM: A child should skip a grade based on 99th percentile test performance.

SYLLOGISM:
  Pratijna: My child should skip a grade due to exceptional test scores.
  Hetu: 99th percentile indicates mastery of grade-level material; the child would benefit more from advanced content. — Pramana basis: Pratyaksha (the test score) plus Anumana (mastery implies readiness for advancement).
  Udaharana: The SMPY longitudinal study (5,000+ gifted individuals since 1970s) found accelerated students showed higher achievement and life satisfaction than equally gifted non-accelerated students.
  Upanaya: The bridge holds IF advancement is uniform across subjects (not just math) AND the child has sufficient social-emotional maturity for older peers. The 99th percentile indicates cognitive readiness but says nothing about social readiness or the child's preference.
  Nigamana: Strong evidence of ACADEMIC readiness, but the full decision requires assessment beyond test scores. — Modality: Probable for academic readiness; INSUFFICIENT for the full decision.

HETVABHASA AUDIT:
  Asiddha: PARTIAL FAIL — Standardized tests measure a SUBSET of academic skills (reading comprehension, math computation). They do not measure: writing quality, scientific reasoning, artistic development, executive function, work persistence. A 99th percentile scorer could lack organizational skills needed for the higher grade.
  Viruddha: FAIL — Placement with older students may cause: social isolation (youngest, smallest), loss of leadership (led in their grade, unexceptional in the higher one), premature academic pressure, developmental misalignment during puberty.
  Anaikantika: FAIL — 99th percentile could justify: curriculum compaction, enrichment within grade, pull-out gifted programs, subject-specific acceleration, dual enrollment, independent projects. Does not uniquely support GRADE-SKIPPING. Subject-specific acceleration is recommended by most gifted education experts as less disruptive.
  Satpratipaksha: PASS (weak) — Research generally supports acceleration (SMPY, Iowa Acceleration Scale). But these studies typically examined holistically assessed students, not test-score-only decisions.
  Badhita: PARTIAL — Not contradicted (acceleration IS beneficial) but reasoning is incomplete.

FAILURE POINT: Fails at Anaikantika (3c). The 99th percentile justifies SOME advanced accommodation but does not uniquely justify grade-skipping. The parent jumped from "needs more challenge" to the most dramatic intervention.

INSIGHT: The parent conflated a MEASUREMENT (test performance) with a DECISION (grade placement). A test score is an INPUT to a decision, not the decision itself. The valid process includes: cognitive readiness (established), social-emotional assessment (not done), child's preference (not consulted), school environment (not evaluated), and alternative accommodations (not considered). Recommended: Iowa Acceleration Scale or similar holistic assessment."""),

]
