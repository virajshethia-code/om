"""Vritti classification examples — 50 text classification examples (10 per type)."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import vritti_msg


def generate_vritti_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(vritti_msg(q, a))
    return examples


def _vritti(vtype: str, confidence: float, explanation: str) -> str:
    return f"vritti: {vtype}\nconfidence: {confidence:.2f}\nexplanation: {explanation}"


_DATA: List[tuple] = [

    # ===== PRAMANA (valid cognition) — 10 examples =====

    ("The Python GIL (Global Interpreter Lock) prevents true parallel execution of Python threads on multi-core processors. CPU-bound tasks using threading will not see speedup from multiple cores. Use multiprocessing or async I/O instead.",
     _vritti("pramana", 0.95, "Factually correct, grounded in CPython's documented implementation. The GIL is a real mutex, its effect on threading is well-documented, and the recommended alternatives (multiprocessing, async) are standard practice. The claim is specific, verifiable, and actionable.")),

    ("Water boils at 100°C at standard atmospheric pressure (1 atm). At higher altitudes, atmospheric pressure decreases, so water boils at a lower temperature — approximately 95°C at 1,500 meters elevation.",
     _vritti("pramana", 0.97, "Grounded in established physics (Clausius-Clapeyron relation). The specific numbers are correct: 100°C at 1 atm is definitional, and the altitude-temperature relationship is well-documented. Both the rule and the exception are stated precisely.")),

    ("According to the 2023 Stack Overflow Developer Survey, JavaScript remains the most commonly used programming language, with 63.6% of respondents reporting using it. TypeScript usage grew to 38.9%.",
     _vritti("pramana", 0.90, "Grounded in Pratyaksha via cited survey data. The specific percentages are verifiable against the source. Confidence slightly below 1.0 because survey data has selection bias (only active Stack Overflow users respond), but this is the standard source and the claim acknowledges its basis.")),

    ("A randomized controlled trial published in The Lancet (n=30,000) found that the mRNA COVID-19 vaccine reduced symptomatic infection by 95% in the trial population. Effectiveness in real-world conditions was somewhat lower due to variants and waning immunity.",
     _vritti("pramana", 0.93, "Grounded in Pratyaksha (published RCT data) with appropriate caveats (real-world effectiveness differs from trial efficacy). The distinction between efficacy and effectiveness demonstrates epistemic sophistication. The specific trial result is verifiable.")),

    ("Git uses a directed acyclic graph (DAG) to represent commit history. Each commit points to its parent(s), forming a graph with no cycles. Merge commits have multiple parents. This structure enables efficient branching and merging.",
     _vritti("pramana", 0.98, "Highly precise technical claim about Git's internal data structure, fully verifiable from Git's source code and documentation. The DAG structure is fundamental and correctly described. Each claim is independently verifiable.")),

    ("The time complexity of binary search on a sorted array is O(log n), because each comparison eliminates half of the remaining elements. This requires the array to be sorted; on an unsorted array, binary search produces incorrect results.",
     _vritti("pramana", 0.99, "Mathematical fact derivable from first principles. The O(log n) complexity, the halving mechanism, and the sorted-array precondition are all correct and provable. Near-maximum confidence because this is a mathematical result, not an empirical claim.")),

    ("PostgreSQL's MVCC (Multi-Version Concurrency Control) allows readers and writers to operate concurrently without blocking each other. Each transaction sees a snapshot of the database as of its start time. This can lead to serialization anomalies under high concurrency with certain isolation levels.",
     _vritti("pramana", 0.94, "Accurate technical description of PostgreSQL's concurrency model, grounded in PostgreSQL documentation. The nuance about serialization anomalies demonstrates understanding of edge cases, not just the happy path.")),

    ("The average adult human body contains approximately 37.2 trillion cells, according to a 2013 estimate published in the Annals of Human Biology. This figure has significant uncertainty due to the difficulty of counting all cell types.",
     _vritti("pramana", 0.88, "Grounded in cited research with explicit acknowledgment of uncertainty. The specific estimate is verifiable, and the uncertainty caveat shows epistemic honesty. Confidence reflects the acknowledged imprecision of the estimate itself.")),

    ("TCP ensures reliable, ordered delivery of data by using sequence numbers, acknowledgments, and retransmission of lost packets. This adds latency compared to UDP but guarantees that all data arrives intact and in order.",
     _vritti("pramana", 0.97, "Correct technical description of TCP's reliability mechanisms versus UDP's lack thereof. The specific mechanisms (sequence numbers, ACKs, retransmission) are accurately stated. The tradeoff (reliability vs. latency) is well-established.")),

    ("Compound interest grows exponentially. An investment of $1,000 at 7% annual return doubles approximately every 10.3 years (per the Rule of 72: 72/7 ≈ 10.3). After 30 years, the original $1,000 becomes approximately $7,612.",
     _vritti("pramana", 0.96, "Mathematical claim that is precisely calculable. The Rule of 72 approximation is stated correctly, the doubling time is accurate, and the 30-year projection ($1000 × 1.07^30 = $7,612) is verifiable. The result is derived, not recalled.")),

    # ===== VIPARYAYA (misconception) — 10 examples =====

    ("Humans only use 10% of their brains. If we could unlock the other 90%, we would have superhuman abilities.",
     _vritti("viparyaya", 0.98, "Factual misconception contradicted by neuroscience. Brain imaging studies (fMRI, PET) show that virtually all brain regions are active over the course of a day, and damage to any significant brain area causes measurable deficits. The 10% myth likely originated from a misquotation of William James or from early misinterpretation of neuroimaging data.")),

    ("NoSQL databases are always faster than relational databases because they don't have the overhead of joins and ACID transactions.",
     _vritti("viparyaya", 0.92, "Contains a logical error (false generalization) and factual misconceptions. NoSQL databases are NOT universally faster — they make different tradeoffs. PostgreSQL with proper indexing outperforms MongoDB for many query patterns. The claim confuses 'different tradeoff space' with 'universally faster.' Additionally, some NoSQL databases DO support joins and ACID (e.g., CockroachDB, FaunaDB).")),

    ("Lightning never strikes the same place twice.",
     _vritti("viparyaya", 0.99, "Directly contradicted by empirical evidence. Tall structures like the Empire State Building are struck approximately 20-25 times per year. Lightning is attracted to the tallest conducting point, making repeated strikes at the same location not only possible but statistically expected.")),

    ("We don't need to worry about SQL injection because we're using a modern framework.",
     _vritti("viparyaya", 0.90, "Misconception about security. While modern frameworks provide parameterized queries that prevent most SQL injection, they do not prevent ALL injection vectors. Raw queries, dynamic table names, ORM bypasses, and stored procedures can still be vulnerable. The claim creates false security confidence.")),

    ("Goldfish have a 3-second memory.",
     _vritti("viparyaya", 0.97, "Factual misconception. Research published in the journal Animal Cognition demonstrates that goldfish can remember information for at least 5 months. They can be trained to respond to stimuli, navigate mazes, and recognize feeding schedules — all requiring memory far exceeding 3 seconds.")),

    ("Adding more RAM always makes your computer faster.",
     _vritti("viparyaya", 0.85, "Misleading oversimplification. Adding RAM improves performance ONLY if the system is memory-constrained (swapping to disk). If the system has sufficient RAM for its workload, adding more has zero performance benefit. The actual bottleneck may be CPU, disk I/O, or network — none of which are affected by additional RAM.")),

    ("The Great Wall of China is visible from space with the naked eye.",
     _vritti("viparyaya", 0.98, "Factual misconception contradicted by astronaut testimony and physics. The Wall is approximately 6 meters wide — far below the resolution limit of the naked eye at orbital distances. Multiple astronauts, including Yang Liwei (China's first astronaut), have confirmed it is not visible from orbit.")),

    ("Microservices are always better than monoliths for scalability.",
     _vritti("viparyaya", 0.88, "False generalization. Monoliths can scale horizontally (run multiple instances behind a load balancer) and vertically (larger hardware). Stack Overflow serves millions of requests per day from a monolithic architecture. Microservices add distributed system complexity that can REDUCE effective scalability for teams that cannot manage the operational overhead.")),

    ("Using var in JavaScript is the same as using let, just an older syntax.",
     _vritti("viparyaya", 0.94, "Factual misconception. var and let have fundamentally different scoping rules: var is function-scoped and hoisted, let is block-scoped and in the temporal dead zone before declaration. This difference causes real bugs (var in for-loops shares the variable across iterations; let creates a new binding per iteration). They are not interchangeable.")),

    ("Vitamin C prevents the common cold.",
     _vritti("viparyaya", 0.90, "Misconception not supported by evidence. Meta-analyses (Hemila & Chalker, Cochrane Review) show that regular vitamin C supplementation does NOT prevent colds in the general population. It may slightly reduce cold duration (8% in adults) but this effect is modest and inconsistent. The prevention claim originated from Linus Pauling's advocacy in the 1970s but has not been validated by rigorous trials.")),

    # ===== VIKALPA (verbal delusion) — 10 examples =====

    ("We need to leverage our synergies to drive holistic transformation across the enterprise.",
     _vritti("vikalpa", 0.95, "Classic vikalpa — every word sounds meaningful but the statement has no corresponding reality. 'Leverage synergies' is undefined (which synergies? how leveraged?). 'Holistic transformation' has no measurable outcome. 'Across the enterprise' provides no specificity. The sentence could be removed from any document without loss of information. It is language performing the appearance of strategy without containing any.")),

    ("Our AI solution uses advanced algorithms to unlock unprecedented insights from your data.",
     _vritti("vikalpa", 0.93, "Marketing vikalpa. 'Advanced algorithms' is meaningless without specifying which algorithms. 'Unlock' is a metaphor with no technical content. 'Unprecedented insights' is unverifiable and hyperbolic. The sentence contains zero technical information while sounding technical. If you asked 'what specifically does it do?', this sentence provides no answer.")),

    ("We're building a platform that empowers creators to tell their stories in authentic ways.",
     _vritti("vikalpa", 0.88, "Startup pitch vikalpa. 'Empowers' — how specifically? 'Tell their stories' — what stories, what medium, what format? 'Authentic ways' — as opposed to what? Every word feels positive and meaningful but the sentence describes nothing concrete. It could describe a blog platform, a video editor, a social network, or a greeting card maker equally well.")),

    ("The key to success is having the right mindset and believing in yourself.",
     _vritti("vikalpa", 0.91, "Self-help vikalpa. 'The right mindset' is circular — it is 'right' because it leads to success, and leads to success because it is 'right.' 'Believing in yourself' is unfalsifiable advice — it explains failures ('you didn't believe enough') and successes ('see, belief works') equally. The statement provides no actionable guidance because it contains no mechanism.")),

    ("Our proprietary methodology ensures best-in-class outcomes through a combination of cutting-edge technology and deep domain expertise.",
     _vritti("vikalpa", 0.94, "Consulting vikalpa. 'Proprietary methodology' — could mean anything. 'Best-in-class' — compared to what class, measured how? 'Cutting-edge technology' — which technology? 'Deep domain expertise' — in what domain? The sentence is constructed entirely from credibility-signaling phrases with no referential content. It describes no actual capability.")),

    ("We need to be more agile and responsive to market dynamics while maintaining our core competencies.",
     _vritti("vikalpa", 0.90, "Corporate strategy vikalpa. 'More agile' — than what baseline? By what measure? 'Responsive to market dynamics' — which dynamics? What response? 'Core competencies' — never defined. This sentence could appear in any company's strategy deck without modification. Its universality is proof of its emptiness.")),

    ("In a world of constant change, adaptability is the ultimate competitive advantage.",
     _vritti("vikalpa", 0.87, "Thought-leadership vikalpa. Sounds profound but is tautological: 'when things change, being able to change is good.' The sentence adds no information. It does not specify HOW to be adaptable, WHAT to adapt, or WHEN adaptation is more important than consistency. It is a bumper sticker masquerading as insight.")),

    ("We're disrupting the industry by reimagining the paradigm of customer engagement.",
     _vritti("vikalpa", 0.96, "Peak vikalpa. 'Disrupting' — every startup claims this. 'Reimagining the paradigm' — a paradigm is a mental model, and you cannot 'reimagine' it without saying what the old paradigm was and what the new one is. 'Customer engagement' — the vaguest possible description of a business activity. The sentence communicates nothing except the desire to sound innovative.")),

    ("Our values of integrity, innovation, and excellence guide everything we do.",
     _vritti("vikalpa", 0.89, "Corporate values vikalpa. These three words appear in approximately 80% of corporate value statements. They are so common as to be meaningless. 'Integrity' — defined how? Measured how? 'Innovation' — what kind? At what cost? 'Excellence' — by whose standard? A company that does not claim these values would be unusual, making their presence uninformative.")),

    ("At the intersection of technology and human potential lies the future of work.",
     _vritti("vikalpa", 0.92, "Conference keynote vikalpa. 'The intersection of technology and human potential' is a spatial metaphor with no referent. 'The future of work' is undefined. The sentence predicts nothing, describes nothing, and recommends nothing. Its function is to create a feeling of forward-looking importance while communicating zero content.")),

    # ===== NIDRA (absence of knowledge) — 10 examples =====

    ("I think the new framework is probably better for our use case, but I'm not really sure why. It just seems like the right choice.",
     _vritti("nidra", 0.88, "The speaker explicitly acknowledges they cannot articulate reasons ('not really sure why') and is relying on a feeling ('seems like'). This is absence of knowledge — the conclusion exists but the knowledge foundation does not. The 'I think' and 'probably' qualifiers signal low epistemic confidence. The correct response is to investigate, not to act on the feeling.")),

    ("The economy will probably recover by Q3, based on my general sense of things.",
     _vritti("nidra", 0.90, "Economic prediction with no cited data, model, or reasoning — only 'general sense.' Economic forecasting is notoriously difficult even with sophisticated models. A prediction based on 'sense' has no epistemic basis. This is the system generating a plausible-sounding prediction while having no actual knowledge of future economic conditions.")),

    ("I assume the database can handle 10x our current load, but I haven't tested it.",
     _vritti("nidra", 0.92, "Explicit nidra — the speaker openly states they are assuming without evidence ('haven't tested it'). The assumption may be correct or incorrect, but it is not knowledge. Load handling capacity is measurable; the fact that it hasn't been measured makes this a guess, not a claim.")),

    ("That technology is probably fine for production use. I've heard of it but never used it.",
     _vritti("nidra", 0.85, "The speaker's basis for the claim ('heard of it') is insufficient for the conclusion ('fine for production use'). Hearing about a technology provides essentially zero information about its production readiness. This is absence of knowledge dressed up as a casual assessment.")),

    ("I'm guessing the outage was caused by a memory leak, but I haven't looked at the logs yet.",
     _vritti("nidra", 0.90, "Explicit guessing acknowledged. Without log examination, any specific root cause attribution is speculation. The 'memory leak' guess may be influenced by recency bias (previous outages were memory leaks) rather than evidence from this incident.")),

    ("The project should take about 6 months. I'm estimating from gut feel — we haven't broken it down yet.",
     _vritti("nidra", 0.87, "Explicit nidra — the estimator acknowledges the estimate is not grounded in analysis ('gut feel,' 'haven't broken it down'). Software project estimation without decomposition is reliably inaccurate. This is absence of knowledge that could be corrected through analysis.")),

    ("I think our competitors are probably working on something similar, but I don't have any information.",
     _vritti("nidra", 0.93, "The speaker explicitly states they have no information. The 'I think' and 'probably' are pure speculation. This is the clearest form of nidra — acknowledging absence while still generating a claim.")),

    ("The users probably won't notice the performance difference. I haven't measured it though.",
     _vritti("nidra", 0.88, "Unmeasured claim about user perception. User perception of performance is complex and often counterintuitive (users notice 100ms latency increases even when they cannot articulate what changed). The absence of measurement makes this a guess.")),

    ("That API is probably rate-limited, but I'm not sure what the limits are or if they apply to us.",
     _vritti("nidra", 0.86, "Multiple explicit knowledge gaps: 'probably,' 'not sure,' 'if they apply.' The speaker has some awareness of the concept (rate limiting exists) but no specific knowledge about this case. API rate limits are documented and testable — this knowledge gap is easily fillable.")),

    ("I feel like our customer churn increased last quarter, but I haven't checked the dashboard.",
     _vritti("nidra", 0.91, "A measurable business metric is being assessed by feeling rather than measurement. Churn is precisely calculable from data the company already has. The 'feeling' may be influenced by anecdotal evidence (memorable churned customers) rather than representative data.")),

    # ===== SMRITI (memory recall) — 10 examples =====

    ("The best way to handle state in React is to use Redux. That's what we learned in our bootcamp.",
     _vritti("smriti", 0.88, "Pure recall from training without fresh reasoning. Redux was the dominant React state management approach in 2016-2019 but the ecosystem has evolved significantly. React Context, Zustand, Jotai, and React Query have changed the state management landscape. The claim recites learned wisdom without evaluating whether it still applies.")),

    ("The standard way to deploy is to SSH into the server and pull the latest code. That's how we've always done it.",
     _vritti("smriti", 0.92, "Reciting an established pattern ('how we've always done it') without fresh evaluation. This deployment method was standard in the 2000s but has been superseded by CI/CD pipelines, container orchestration, and immutable deployments. The speaker is recalling a learned practice without assessing its current validity.")),

    ("Object-oriented programming is the best paradigm because it models the real world.",
     _vritti("smriti", 0.85, "A recalled teaching from OOP education ('OOP models the real world') that was common in 1990s-2000s CS curricula. The 'models the real world' justification has been extensively criticized (real-world objects don't inherit from each other in neat hierarchies). This is learned doctrine being repeated without fresh critical evaluation.")),

    ("You should always normalize your database to third normal form.",
     _vritti("smriti", 0.87, "Database design rule recalled from education without context-specific reasoning. 3NF is taught as a default in database courses, but many production systems intentionally denormalize for performance (read-heavy workloads, analytics, caching). The rule is valid as a starting point but the speaker presents it as absolute truth rather than a contextual guideline.")),

    ("The Agile Manifesto says we should value working software over comprehensive documentation.",
     _vritti("smriti", 0.80, "Accurate recall of the Agile Manifesto's second principle. This is smriti (memory of a source) rather than pramana (fresh reasoning) because the speaker is citing an authority rather than reasoning about whether this principle applies to their specific context. The Manifesto is 20+ years old and its principles are often cited without evaluating whether they apply to the current situation.")),

    ("In my experience, Python is too slow for production systems. We tried it in 2015 and had performance issues.",
     _vritti("smriti", 0.83, "Memory of a specific past experience being generalized as current truth. Python's performance characteristics, hosting options (async frameworks, compiled extensions, PyPy), and the problems it is applied to have all changed significantly since 2015. The speaker is recalling a past experience without updating for current reality.")),

    ("The rule of thumb is to keep functions under 20 lines. That's what Clean Code recommends.",
     _vritti("smriti", 0.82, "Recalled guideline from a specific book (Robert Martin's Clean Code). The 20-line rule is a teaching heuristic, not a universal truth. Some functions are naturally longer (state machines, parsers, complex business rules) and artificially splitting them creates indirection without clarity. The speaker recalls the rule without reasoning about when it applies.")),

    ("We should use microservices because that's what Netflix does and they handle massive scale.",
     _vritti("smriti", 0.90, "Recall of a famous architecture case study being applied without fresh analysis. Netflix's architecture decisions were driven by Netflix's specific constraints (millions of concurrent streams, 100+ engineering teams, multi-region global deployment). Recalling Netflix's choice as justification for a different company's architecture is smriti — repeating a learned pattern without evaluating whether the pattern's preconditions apply.")),

    ("The waterfall methodology is outdated. Agile is always the right approach for software development.",
     _vritti("smriti", 0.86, "Recalled narrative from the Agile movement without fresh reasoning. The 'waterfall is dead' narrative was powerful in the 2000s-2010s but contemporary software engineering recognizes that different project types benefit from different approaches. Regulatory software, safety-critical systems, and well-understood infrastructure often benefit from waterfall-like planning. The speaker recites a movement's position as fact.")),

    ("The CAP theorem means you have to choose between consistency and availability. You can't have both.",
     _vritti("smriti", 0.78, "Partially accurate recall of a theoretical result, but oversimplified. The CAP theorem states that during a NETWORK PARTITION, you must choose between consistency and availability. When there is no partition (the vast majority of the time), you CAN have both. The speaker recalls the theorem's conclusion without its crucial premise (partition), producing a misleading simplification. This is smriti because the simplification comes from how the theorem is commonly taught and remembered, not from fresh analysis.")),
]
