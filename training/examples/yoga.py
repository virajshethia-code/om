"""Yoga training examples — 30 attention filtering / signal-noise examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "yoga"

def generate_yoga_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples

def _yoga(inventory: str, scores: str, discarded: str, retained: str,
          dharana: str, second_order: str, vritti_audit: str) -> str:
    return f"""COMPLETE INPUT INVENTORY:
{inventory}

SIGNAL SCORES:
{scores}

DISCARDED (below 7):
{discarded}

RETAINED SIGNAL:
{retained}

DHARANA POINT: {dharana}

SECOND-ORDER FOCUS:
{second_order}

VRITTI AUDIT:
{vritti_audit}"""

_DATA: List[tuple] = [

# ===== SOFTWARE ENGINEERING =====

("We're choosing between React, Vue, and Svelte for our new SaaS dashboard. The team is split. What should we actually focus on?",
_yoga(
"""1. React's larger ecosystem and community — Explicit
2. Vue's simpler learning curve — Explicit
3. Svelte's superior performance benchmarks — Explicit
4. Team's existing React experience (3 of 5 devs) — Implicit
5. Hiring pool size for each framework — Implicit
6. Bundle size differences — Explicit
7. Component library availability (shadcn, Vuetify, etc.) — Implicit
8. Framework longevity/corporate backing — Assumed
9. Developer satisfaction surveys — Explicit
10. TypeScript support quality — Implicit
11. State management ecosystem — Implicit
12. The team's emotional attachment to their preferences — Emotional
13. Fear of making the "wrong" choice — Emotional
14. SSR/SSG capabilities — Implicit
15. The actual complexity of the dashboard being built — Assumed""",

"""1. React ecosystem: 5/10 — Large ecosystem matters only if you USE many third-party components; most dashboards use a small set.
2. Vue learning curve: 4/10 — Learning curve is a one-time cost amortized over years of development. Short-term factor.
3. Svelte performance: 3/10 — For a SaaS dashboard (not a game or real-time app), performance differences between frameworks are imperceptible to users. Premature optimization.
4. Team React experience: 9/10 — Existing competence directly determines velocity for the next 6-12 months. Retraining cost is real.
5. Hiring pool: 7/10 — Determines ability to scale the team and replace departing members. React's pool is 5-10x larger than Svelte's.
6. Bundle size: 2/10 — For an authenticated SaaS dashboard (not a public marketing page), bundle size is irrelevant to user experience.
7. Component library: 6/10 — Saves time but can be built for any framework.
8. Framework longevity: 4/10 — All three are well-maintained. This is FUD, not analysis.
9. Dev satisfaction: 3/10 — Surveys measure what developers ENJOY, not what produces business outcomes.
10. TypeScript support: 5/10 — All three have good TS support now. Not a differentiator.
11. State management: 4/10 — All have adequate solutions. Not a decisive factor.
12. Emotional attachment: 0/10 — Pure distraction. Actively misleading.
13. Fear of wrong choice: 0/10 — The choice between three competent frameworks is low-risk. The fear is disproportionate to the actual stakes.
14. SSR/SSG: 3/10 — A SaaS dashboard typically doesn't need SSR. Inapplicable.
15. Dashboard complexity: 8/10 — If the dashboard is straightforward CRUD, any framework works. If it has complex real-time data visualization, different factors matter.""",

"""- React ecosystem (5): Rarely leveraged beyond 5-10 core libraries.
- Vue learning curve (4): One-time cost, irrelevant at 12-month horizon.
- Svelte performance (3): Imperceptible for this use case.
- Bundle size (2): Irrelevant for authenticated SaaS.
- Framework longevity (4): FUD. All are well-maintained.
- Dev satisfaction (3): Enjoyment ≠ productivity.
- State management (4): Adequate in all three.
- Emotional attachment (0): Noise.
- Fear of wrong choice (0): The stakes are lower than the team believes.
- SSR/SSG (3): Not needed for this product.
- TypeScript (5): Not a differentiator.""",

"""- Team React experience (9): Directly determines velocity for 6-12 months.
- Dashboard complexity (8): Determines whether framework choice matters at all.
- Hiring pool (7): Determines scaling ability.""",

"""The actual complexity of the dashboard being built.
"If you get the complexity assessment right, the framework choice either becomes obvious or becomes irrelevant."
If the dashboard is standard CRUD with tables/forms/charts, use React (team knows it, hire for it, ship fast). If it requires complex real-time visualization or novel interaction patterns, THEN evaluate frameworks on those specific capabilities. The team is debating frameworks without first characterizing the problem they are solving. The framework debate is a PROXY for the real question: "What are we actually building?" """,

"""- Sub-factors of dharana point:
  1. Data visualization complexity: 8/10 — determines whether Svelte's reactivity or React's ecosystem matters more.
  2. Real-time update requirements: 7/10 — WebSocket-heavy dashboards stress different framework aspects.
  3. User interaction density: 6/10 — Heavy form interactions vs. read-mostly dashboards have different needs.
  4. Customization vs. standard components: 8/10 — If standard components suffice, ecosystem size matters. If custom UIs dominate, framework primitives matter.
- Signal within the signal: Whether the team needs standard components (→ React, largest library ecosystem) or custom interactive visualizations (→ evaluate Svelte's reactivity model). This is determinable in a 2-hour design review, not a multi-week debate.""",

"""- Classification: pramana
- Evidence: The dharana point (characterize what you're building first) is grounded in the specific context (SaaS dashboard, existing team skills, hiring needs) and produces a testable recommendation (do a 2-hour complexity assessment). It does not resort to generic advice ("it depends on your needs").
- The analysis would have been vikalpa if it concluded "consider your team's preferences and the project requirements" — this is true but empty. Instead, it identifies the specific decisive factor: dashboard complexity determines whether the framework choice matters at all."""
)),

("I have too many side projects and can't finish any of them. How should I decide which to focus on?",
_yoga(
"""1. Number of active projects (stated: "too many") — Explicit
2. Completion history — what has been finished before — Implicit
3. Revenue potential of each project — Implicit
4. Personal enjoyment of each project — Implicit
5. Time available per week for side projects — Implicit
6. Skills being developed by each project — Implicit
7. Social validation/external interest in each project — Implicit
8. Sunk cost in each project (time already invested) — Assumed
9. Fear of committing to one (FOMO for others) — Emotional
10. Identity attachment ("I'm a person with many interests") — Emotional
11. Shame about not finishing — Emotional
12. The actual REASON for having side projects — Assumed
13. Whether any project has a deadline or external commitment — Implicit
14. Energy level and motivation patterns — Implicit""",

"""1. Number of projects: 4/10 — The number itself is not the problem; the inability to finish is the symptom.
2. Completion history: 7/10 — Past behavior predicts future behavior. If you've never finished a project, the issue may not be which project to choose but an inability to push through the boring middle of any project.
3. Revenue potential: 5/10 — Relevant only if the goal IS revenue. If it's learning or fun, revenue is noise.
4. Enjoyment: 6/10 — Important but unreliable: enjoyment peaks at the start and drops in the middle of every project, making it a poor selection criterion.
5. Time available: 7/10 — Hard constraint that determines scope feasibility. A project requiring 20 hrs/week with 5 available will fail regardless of priority.
6. Skills developed: 5/10 — Matters for career but does not determine WHICH project to finish NOW.
7. Social validation: 3/10 — External interest is fickle and not a reliable guide to personal commitment.
8. Sunk cost: 1/10 — Classic fallacy. Time already spent is irrelevant to future decisions. Discard entirely.
9. FOMO: 0/10 — This is the core disease, not useful data. The fear of missing out on other projects by committing to one is exactly what prevents finishing any.
10. Identity attachment: 2/10 — "I have many interests" can be a narrative that prevents depth. Relevant to diagnose, not to decide.
11. Shame: 0/10 — Pure noise. Shame about not finishing does not help select which to finish.
12. The reason for side projects: 9/10 — If the reason is learning: pick the one you'll learn most from. If it's income: pick the one closest to revenue. If it's creative expression: pick the one that excites you most. THE GOAL determines the selection criterion.
13. External deadlines: 8/10 — External commitments create accountability that transforms optional into obligatory.
14. Energy patterns: 6/10 — When are you most productive? Which project fits those windows?""",

"""- Revenue potential (5): Only relevant if revenue is the goal.
- Enjoyment (6): Unreliable — drops in every project's middle.
- Skills (5): Background consideration, not decisive.
- Social validation (3): Fickle external signal.
- Sunk cost (1): Fallacy. Discard completely.
- FOMO (0): The disease itself.
- Identity attachment (2): Diagnostic, not actionable.
- Shame (0): Noise.
- Energy patterns (6): Context, not decisive.""",

"""- The reason for having side projects (9): Determines the selection criterion entirely.
- External deadlines (8): Creates the accountability that transforms intention into action.
- Completion history (7): Reveals whether the problem is selection or execution.
- Time available (7): Hard constraint on feasibility.""",

"""Your completion history — specifically, whether you have EVER finished a significant side project.
"If you get your completion pattern right, the project selection takes care of itself."
If you have a history of finishing things, this is a selection problem — pick the one aligned with your goal and commit. If you have NEVER finished a side project, this is NOT a selection problem. It is an execution problem. Choosing "the right project" will not fix an inability to push through the boring, difficult middle phase of any creative work. The correct intervention is: pick the smallest, most finishable project (regardless of which is "best"), complete it, and build the completion muscle. Then use that muscle on a bigger project.""",

"""- Sub-factors of completion history:
  1. Boredom tolerance: 8/10 — Every project has a boring middle. Can you push through?
  2. Scope management: 9/10 — Do you expand scope when you should be shipping?
  3. Definition of done: 7/10 — Do you know what "finished" means for each project?
- Signal within the signal: Scope management. The most common reason side projects die is not loss of interest but scope expansion. Each idea generates sub-ideas that expand the project beyond what is achievable. The intervention: define the MINIMUM viable version and commit to shipping that, even if incomplete. "Done" beats "perfect" because "perfect" is the enemy of "done." """,

"""- Classification: pramana
- Evidence: The dharana point (completion history as diagnostic) is grounded in the specific problem (inability to finish) and produces a concrete, testable recommendation (if never finished → pick smallest project and complete it; if history of finishing → align with your goal). It is not a restatement of the problem ("you need to focus more") but an identification of the actual variable that determines the right intervention."""
)),

("Our startup is running low on cash. We have 6 months of runway. What should we focus on?",
_yoga(
"""1. Current revenue and growth rate — Explicit (implied low)
2. Burn rate and cost structure — Implicit
3. Fundraising possibility — Implicit
4. Product-market fit status — Implicit
5. Customer acquisition cost — Implicit
6. Team size and composition — Implicit
7. Current product features — Implicit
8. Competitor activity — Implicit
9. Market conditions for fundraising — Implicit
10. Founder equity dilution concerns — Emotional
11. Fear of failure — Emotional
12. Attachment to current product vision — Emotional
13. Team morale and retention risk — Implicit
14. Existing customer feedback — Implicit
15. The specific thing that, if proven, would make the company fundable — Assumed""",

"""1. Revenue/growth rate: 8/10 — Directly determines whether organic survival is possible.
2. Burn rate: 7/10 — Only lever that extends runway without external capital.
3. Fundraising: 5/10 — Possible but unreliable as primary strategy with 6 months left. VCs sense desperation.
4. PMF status: 9/10 — If PMF exists, fundraising and revenue follow. If not, nothing else matters.
5. CAC: 6/10 — Relevant but secondary to whether the product is right.
6. Team size: 7/10 — Can burn rate be reduced by cutting to core team?
7. Product features: 4/10 — Features are meaningless without PMF.
8. Competitors: 3/10 — With 6 months, competitive strategy is a luxury.
9. Fundraising market: 4/10 — External factor you cannot control.
10. Dilution concerns: 1/10 — Irrelevant if the company dies.
11. Fear of failure: 0/10 — Actively harmful. Consumes cognitive bandwidth needed for problem-solving.
12. Product vision attachment: 2/10 — May need to pivot. Attachment prevents necessary pivots.
13. Team morale: 5/10 — Important but follows from other factors (progress creates morale).
14. Customer feedback: 8/10 — The direct signal about what is and isn't working.
15. The proof point: 10/10 — What single thing, if demonstrated, would make investors write a check?""",

"""- Fundraising (5): Unreliable as primary plan when desperate.
- CAC (6): Secondary to PMF.
- Product features (4): Meaningless without PMF.
- Competitors (3): Luxury with 6 months.
- Market conditions (4): Uncontrollable.
- Dilution (1): Irrelevant if company dies. Discarded.
- Fear (0): Noise. Discarded.
- Product vision attachment (2): May prevent necessary pivots. Discarded.
- Team morale (5): Follows from progress, not independent variable.""",

"""- The proof point that makes the company fundable (10): Everything depends on this.
- PMF status (9): Determines whether the company has a reason to exist.
- Revenue/growth (8): Can organic survival extend runway?
- Customer feedback (8): Direct signal about what's working.
- Burn rate (7): Only directly controllable lever for runway extension.
- Team size (7): Cutting to core team may double runway.""",

"""The ONE proof point that, if demonstrated, would make an investor write a check.
"If you get the proof point right, fundraising, revenue, and survival take care of themselves."
This is NOT "grow faster" or "improve the product" — those are vague. It is something specific and demonstrable: "5 paying customers with >80% retention" or "Unit economics positive at $X MRR" or "Technology proven to work at Y scale." The 6 months should be spent entirely on achieving this one proof point, and EVERYTHING ELSE should be cut.""",

"""- Sub-factors:
  1. Specificity of proof point: 9/10 — Must be concrete enough that an investor can verify it in one meeting.
  2. Achievability in 4 months (leaving 2 for fundraising): 8/10 — Must be scoped to actually accomplish.
  3. Relevance to investor thesis: 7/10 — Must align with what investors in your space care about.
- Signal within the signal: The proof point must be about CUSTOMER BEHAVIOR, not product capability. "We built X" is not a proof point. "Customers DO Y with X and PAY Z" is. The deepest insight: with 6 months, you cannot build your way to survival. You can only PROVE your way to survival.""",

"""- Classification: pramana
- Evidence: The analysis produces a specific, actionable framework (identify the single proof point, cut everything else, execute for 4 months, fundraise for 2). It is grounded in the specific constraint (6-month runway) and does not resort to vague advice ("focus on growth"). The dharana point (proof point identification) is surprising because it reframes survival from "do more" to "prove one thing." """
)),

# === 27 more examples across all domains, following the same Yoga method ===
# Each with full input inventory, 0-10 scoring, cutoff at 7, dharana point,
# second-order focus, and vritti audit.

("Should we build our own design system or use an existing component library like shadcn/ui?",
_yoga(
"""1. Team size and bandwidth — Implicit
2. Design consistency requirements — Explicit
3. Brand differentiation needs — Implicit
4. shadcn/ui's customizability — Explicit
5. Maintenance burden of custom system — Implicit
6. Time to market pressure — Implicit
7. Developer experience with existing libraries — Implicit
8. Accessibility compliance requirements — Implicit
9. Performance requirements — Implicit
10. Future scalability — Assumed
11. Pride in building "our own" thing — Emotional
12. Fear of vendor lock-in — Emotional
13. The number of unique UI patterns the product actually needs — Assumed""",
"""1. Team bandwidth: 8/10 — A custom design system requires dedicated maintainers; without them it decays.
2. Design consistency: 6/10 — Both approaches can achieve consistency.
3. Brand differentiation: 5/10 — Users don't choose SaaS products for unique button styles.
4. shadcn customizability: 7/10 — shadcn copies components into your project (you OWN them), eliminating typical library constraints.
5. Maintenance burden: 8/10 — Custom design systems are permanent commitments. Under-maintained systems become liabilities.
6. Time to market: 7/10 — Library use saves 3-6 months of foundational work.
7. Dev experience: 6/10 — Learnable in either case.
8. Accessibility: 7/10 — Established libraries have accessibility built in; custom systems frequently get accessibility wrong.
9. Performance: 3/10 — Negligible difference for business apps.
10. Scalability: 4/10 — Premature concern for most startups.
11. Pride: 0/10 — NIH syndrome. Discard.
12. Vendor lock-in fear: 2/10 — shadcn has no lock-in (components are copied, not imported). Discard.
13. Unique UI patterns needed: 9/10 — If the product needs 5 unique patterns, build those 5. If it needs 50, use a library for 45 and build 5.""",
"""Brand differentiation (5), performance (3), scalability (4), pride (0), lock-in fear (2), dev experience (6): all discarded as noise or premature concerns.""",
"""- Unique UI patterns needed (9): Determines the build-vs-buy boundary.
- Team bandwidth (8): Determines maintenance feasibility.
- Maintenance burden (8): Custom systems require permanent investment.
- shadcn customizability (7): Eliminates the usual library constraint.
- Time to market (7): Library saves months.
- Accessibility (7): Libraries get it right; custom often doesn't.""",
"""The number of truly unique UI patterns the product requires that cannot be achieved with a customizable library.
"If you get the unique-pattern count right, the build-vs-buy decision makes itself."
If <10 unique patterns: use shadcn (owns the code, fully customizable), build only the unique components. If 10-30: use shadcn as foundation, build a thin design system layer on top. If 30+: you are building a design tool, not a SaaS product — reconsider your product complexity.""",
"""- Sub-factors: Audit current designs for truly unique patterns (most teams overestimate uniqueness). Count: how many components cannot be achieved by customizing shadcn's primitives?
- Signal within the signal: Most "unique" UI needs are actually standard patterns with custom styling. The actual number of structurally unique components is usually 3-7 for most products.""",
"""- Classification: pramana — Grounded in specific, verifiable analysis (count unique patterns). Not a platitude about "evaluating your needs." """
)),

# Personal decisions
("I'm burnt out at work but afraid to take a break because of career consequences. What should I focus on?",
_yoga(
"""1. Severity of burnout symptoms — Explicit
2. Financial stability/savings — Implicit
3. Career stage and reputation — Implicit
4. Company's leave policies — Implicit
5. Manager's likely reaction — Implicit
6. Job market conditions — Implicit
7. Health deterioration trajectory — Implicit
8. Fear of being seen as weak — Emotional
9. Guilt about leaving team short-staffed — Emotional
10. Comparison to colleagues who seem fine — Emotional
11. The actual health risk if burnout continues — Assumed
12. Whether the burnout is situational or structural — Assumed
13. Recovery time needed — Implicit""",
"""1. Burnout severity: 8/10 — Determines urgency. Clinical burnout causes lasting health damage.
2. Financial stability: 7/10 — Determines feasibility of taking time off.
3. Career stage: 5/10 — Relevant but overweighted by fear. Careers are long; burnout damage is permanent.
4. Leave policies: 6/10 — Tactical, not strategic.
5. Manager reaction: 4/10 — Unpredictable and beyond your control.
6. Job market: 3/10 — Background context only.
7. Health trajectory: 9/10 — Burnout that progresses to clinical depression or anxiety has years-long recovery. Early intervention is dramatically cheaper than late.
8. Fear of weakness: 0/10 — Internalized toxic norm. Actively harmful.
9. Guilt: 1/10 — The team's staffing is the company's problem, not yours.
10. Comparison: 0/10 — You don't know what others are actually experiencing.
11. Actual health risk: 10/10 — The medical consequences of untreated burnout (cardiovascular disease, depression, anxiety disorders, immune dysfunction) are well-documented and potentially irreversible.
12. Situational vs. structural: 8/10 — If situational (bad project, bad quarter), it will pass. If structural (role mismatch, toxic culture), no amount of rest fixes the cause.
13. Recovery time: 7/10 — Mild burnout: 2-4 weeks. Severe: 3-12 months. Early intervention matters enormously.""",
"""Career stage (5), leave policies (6), manager reaction (4), job market (3), fear (0), guilt (1), comparison (0): discarded.""",
"""- Health risk (10): Untreated burnout causes lasting medical harm.
- Health trajectory (9): Early intervention is dramatically more effective.
- Burnout severity (8): Determines urgency.
- Situational vs. structural (8): Determines whether rest alone is sufficient.
- Financial stability (7): Determines feasibility.
- Recovery time (7): Dictates minimum intervention duration.""",
"""Whether the burnout is situational or structural.
"If you get the diagnosis right (situational vs. structural), the intervention becomes obvious."
If SITUATIONAL: a 2-4 week break plus boundaries will restore function. The career "cost" is near zero.
If STRUCTURAL: a break only delays the recurrence. The actual need is role change, job change, or fundamental boundary restructuring. No amount of vacation fixes a fundamentally unsustainable situation.""",
"""- Sub-factors: (1) Has the burnout worsened over 6+ months despite vacations? → structural. (2) Did it start with a specific event/change? → likely situational. (3) Do weekends and holidays restore you? → situational. If not → structural.
- Signal within the signal: Whether weekends restore you. If Saturday morning feels restful: situational. If Saturday morning already carries dread about Monday: structural. This single data point is the most reliable diagnostic.""",
"""- Classification: pramana — Grounded in specific diagnostic criteria (weekend restoration test), produces distinct actionable recommendations for each case. Not vague "self-care" advice."""
)),

# Business strategy
("We have three potential customer segments. How should we choose which to target first?",
_yoga(
"""1. Segment A: Enterprise (high ACV, long sales cycle) — Explicit
2. Segment B: Mid-market (moderate ACV, medium cycle) — Explicit
3. Segment C: SMB/startup (low ACV, short cycle) — Explicit
4. Current product fit for each segment — Implicit
5. Team's sales experience and style — Implicit
6. Capital and runway — Implicit
7. Total addressable market per segment — Implicit
8. Competition intensity per segment — Implicit
9. Referenceability (will segment create social proof?) — Implicit
10. Founder's personal network/access — Implicit
11. Prestige of serving enterprise — Emotional
12. Fear of being "too small" targeting SMB — Emotional
13. Which segment is already using or requesting the product — Assumed""",
"""1. Enterprise segment: 5/10 — High ACV but long cycle may burn 6+ months before first sale.
2. Mid-market: 5/10 — Middle of the road on all dimensions.
3. SMB/startup: 4/10 — Low ACV risks unsustainable unit economics.
4. Product fit: 8/10 — The segment where the product solves the most acute problem TODAY determines fastest path to revenue and learning.
5. Sales experience: 7/10 — Team selling enterprise without enterprise sales experience will fail. Capability determines feasibility.
6. Capital/runway: 7/10 — Short runway → needs short sales cycle → rules out enterprise.
7. TAM: 4/10 — All three segments are large enough. TAM is not a differentiator.
8. Competition: 5/10 — Relevant but secondary to product fit.
9. Referenceability: 6/10 — Useful but not decisive.
10. Founder network: 7/10 — Who can you actually get meetings with? Access determines speed.
11. Enterprise prestige: 0/10 — Pure ego. Discard.
12. Fear of being small: 0/10 — Noise.
13. Who is ALREADY asking for the product: 10/10 — If any segment is already pulling, go there. Demand > strategy.""",
"""Enterprise/mid-market/SMB as categories (4-5): The segment labels are proxies for other factors. TAM (4), competition (5), referenceability (6): secondary. Prestige (0), fear (0): discarded.""",
"""- Who is already asking (10): Existing demand is the strongest signal.
- Product fit (8): Where does the product solve the most acute pain?
- Sales capability (7): Can the team actually close in this segment?
- Founder network (7): Can you get meetings?
- Runway (7): How long can you afford to wait for first sale?""",
"""Which segment is already trying to give you money.
"If you get the demand signal right, everything else follows."
Stop analyzing segments abstractly. Instead: (1) Who has already signed up, requested demos, or asked when the product is available? (2) Among those, who has the most acute pain? (3) Among THOSE, who can make a buying decision fastest? THAT is your first segment — not the one with the biggest TAM or the highest ACV.""",
"""- Sub-factors: Urgency of buyer's pain, decision-making speed, willingness to be a reference.
- Signal within the signal: Whether ANY potential customer has said "I will pay for this today." Not "this is interesting" or "we might budget for this next quarter" — but actual immediate willingness to pay. One customer ready to pay today is worth more than 100 who think it's interesting.""",
"""- Classification: pramana — Based on specific, observable market signals (who is asking, who will pay) rather than abstract market analysis."""
)),

# Scientific analysis
("Our research team disagrees on whether to pursue a novel but risky hypothesis or extend established work. What should we focus on?",
_yoga(
"""1. Novel hypothesis potential impact — Explicit
2. Risk of novel hypothesis failing — Explicit
3. Established work's predictable output — Explicit
4. Grant funding requirements — Implicit
5. Team members' career stages — Implicit
6. Publication timeline pressure — Implicit
7. Lab resources and equipment — Implicit
8. Prior art and competition — Implicit
9. Excitement about the novel idea — Emotional
10. Safety of extending established work — Emotional
11. Fear of wasting a year — Emotional
12. Whether the novel hypothesis is testable with current resources — Assumed
13. The minimum viable experiment to test the hypothesis — Assumed""",
"""1. Impact: 6/10 — Matters but unknowable until you try.
2. Failure risk: 5/10 — All novel research risks failure. This is not diagnostic.
3. Established output: 4/10 — Incremental papers are not career-making.
4. Grant requirements: 7/10 — If grant requires specific deliverables, this constrains choice.
5. Career stages: 7/10 — Junior researchers need publications for career survival. Senior researchers can afford risk.
6. Publication pressure: 6/10 — Real but should not dominate scientific direction.
7. Resources: 7/10 — Can the novel hypothesis be tested with available equipment?
8. Competition: 5/10 — If others are converging on the same novel idea, speed matters.
9. Excitement: 3/10 — Unreliable predictor of scientific value.
10. Safety appeal: 1/10 — The appeal of safety is the enemy of significant science.
11. Fear of waste: 0/10 — Null results are information, not waste.
12. Testability: 9/10 — A hypothesis that cannot be tested with current resources is not a hypothesis — it is a wish.
13. Minimum viable experiment: 10/10 — What is the SMALLEST experiment that would provide evidence for or against the hypothesis?""",
"""Impact (6), failure risk (5), established output (4), competition (5), excitement (3), safety appeal (1), fear (0): all discarded.""",
"""- Minimum viable experiment (10): The cheapest, fastest test of the novel hypothesis.
- Testability (9): Whether the hypothesis can be tested at all with current resources.
- Career stages (7): Determines who can afford risk.
- Grant requirements (7): Hard constraint.
- Resources (7): Feasibility constraint.""",
"""The minimum viable experiment that tests the novel hypothesis.
"If you get the MVP experiment right, you eliminate the false dichotomy."
The team is framing this as binary: pursue novel OR extend established. The Yoga method reveals a third path: design the smallest, cheapest experiment that would provide preliminary evidence for the novel hypothesis while the team continues established work. If the preliminary result is positive, shift resources. If negative, no significant time was lost. The dichotomy dissolves when you find the small experiment.""",
"""- Sub-factors: (1) Can a preliminary test be designed in <2 weeks? (2) What is the single measurement that would most strongly support or refute the hypothesis? (3) Can a junior team member run this while seniors continue established work?
- Signal within the signal: Whether a single measurement exists that would be highly diagnostic. If yes, run it immediately. If no such measurement exists, the hypothesis is not yet well-enough defined to pursue — refine it before committing resources.""",
"""- Classification: pramana — Produces a specific, actionable plan (design minimum viable experiment) that resolves the team's disagreement without choosing sides."""
)),

# Debugging
("Our app crashes intermittently in production but we can't reproduce it locally. Where should we focus?",
_yoga(
"""1. Crash logs/stack traces — Explicit
2. Local vs. production environment differences — Implicit
3. Memory and CPU differences — Implicit
4. Data volume/variety differences — Implicit
5. Concurrent user load differences — Implicit
6. Third-party service behavior differences — Implicit
7. Network conditions — Implicit
8. Deployment configuration — Implicit
9. Time-of-day patterns in crashes — Implicit
10. Recent code changes — Implicit
11. Frustration at inability to reproduce — Emotional
12. Pressure to fix quickly — Emotional
13. The SPECIFIC difference between production and local that causes the crash — Assumed""",
"""1. Crash logs: 8/10 — Direct evidence if available.
2. Environment differences: 9/10 — The crash occurs in production but not locally, so BY DEFINITION something is different. Finding that difference IS finding the bug.
3. Memory/CPU: 6/10 — One possible difference dimension.
4. Data volume: 7/10 — Production has real data; local has test data. Data-dependent bugs are extremely common.
5. Concurrency: 8/10 — Race conditions manifest only under real concurrent load.
6. Third-party services: 6/10 — Different behavior from staging mocks vs. production APIs.
7. Network: 4/10 — Unlikely to cause app crashes.
8. Deployment config: 5/10 — Possible but usually caught in staging.
9. Time patterns: 7/10 — If crashes correlate with time, they correlate with load patterns, cron jobs, or external events.
10. Recent changes: 7/10 — If crashes started after a specific deploy, the change is the suspect.
11. Frustration: 0/10 — Noise.
12. Pressure: 0/10 — Counterproductive.
13. Specific difference: 10/10 — This IS the bug.""",
"""Network (4), deployment config (5), memory (6), third-party (6), frustration (0), pressure (0): discarded.""",
"""- Specific prod-local difference (10): Finding this IS solving the bug.
- Environment differences (9): The systematic search space.
- Concurrency (8): Most common cause of non-reproducible crashes.
- Crash logs (8): Direct evidence.
- Data volume (7): Production data triggers paths test data misses.
- Time patterns (7): Correlates with causal factors.
- Recent changes (7): Temporal correlation.""",
"""Whether the crash is a concurrency bug (race condition, deadlock) or a data-dependent bug.
"If you get this classification right, you know exactly what to look for."
Concurrency: add structured logging around shared state, deploy, wait for crash, examine logs. Data: export a production data sample (anonymized), test locally with production-scale data. These are the two most common non-reproducible crash categories, and each has a different investigation path.""",
"""- Sub-factors: (1) Does the crash happen more under high load? → concurrency. (2) Does it happen with specific users/accounts? → data-dependent. (3) Is it random across time? → likely concurrency.
- Signal within the signal: Whether crashes correlate with LOAD or with SPECIFIC OPERATIONS. Load-correlated → race condition. Operation-correlated → data-dependent edge case.""",
"""- Classification: pramana — Produces specific diagnostic paths based on observable crash patterns."""
)),

# Ethics
("Our AI model shows racial bias in loan approvals. The team is debating whether to adjust the model or adjust the training data. What should we focus on?",
_yoga(
"""1. Model architecture choices — Explicit
2. Training data demographics — Explicit
3. Feature selection (which inputs the model uses) — Implicit
4. Proxy variables (features that correlate with race) — Implicit
5. Historical bias in the training labels — Implicit
6. Regulatory requirements (ECOA, Fair Lending) — Implicit
7. Business impact of changes — Implicit
8. Customer trust — Implicit
9. Model accuracy tradeoffs — Implicit
10. Team's technical comfort with fairness methods — Implicit
11. Fear of reduced accuracy — Emotional
12. Guilt about existing bias — Emotional
13. What the model is ACTUALLY learning that produces the bias — Assumed""",
"""1. Model architecture: 3/10 — Bias rarely comes from architecture. Changing architectures typically does not fix bias.
2. Training data demographics: 7/10 — Underrepresentation amplifies bias but is not the only cause.
3. Feature selection: 8/10 — Which features the model uses determines what it learns. Removing race is insufficient if ZIP code, education, or employment history serve as proxies.
4. Proxy variables: 9/10 — The #1 cause of algorithmic bias in lending. ZIP code is the most common race proxy.
5. Historical label bias: 8/10 — If historical loan approvals were racially biased, the model learns to reproduce that bias. The labels are contaminated.
6. Regulatory: 7/10 — ECOA requires disparate impact testing regardless of model type.
7. Business impact: 4/10 — Secondary to legal and ethical obligations.
8. Customer trust: 5/10 — Important but follows from doing the right thing.
9. Accuracy tradeoffs: 4/10 — Accuracy measured on biased data is itself biased. "Less accurate" on biased benchmarks may be MORE accurate on fair ones.
10. Technical comfort: 3/10 — Skills can be acquired. Not a reason to avoid the work.
11. Fear of reduced accuracy: 1/10 — See #9.
12. Guilt: 0/10 — Not actionable.
13. What the model actually learns: 10/10 — The specific features and feature interactions that produce disparate outcomes.""",
"""Architecture (3), business impact (4), accuracy tradeoffs (4), technical comfort (3), customer trust (5), fear (1), guilt (0): discarded.""",
"""- What the model learns that produces bias (10): This is the root cause.
- Proxy variables (9): Most likely mechanism.
- Historical label bias (8): Data contamination.
- Feature selection (8): Directly controllable.
- Training data demographics (7): Contributing factor.
- Regulatory requirements (7): Non-negotiable constraint.""",
"""The specific proxy variables the model uses to reconstruct protected characteristics.
"If you identify and address the proxy variables, both the model and the data become less biased."
The team is debating model vs. data as if these are independent. They are not. The model learns bias FROM the data THROUGH proxy features. Identify which features the model uses most heavily for applicants from different racial groups (SHAP/LIME analysis), and you will find the proxies. Addressing proxies fixes BOTH the model and the data problem simultaneously.""",
"""- Sub-factors: (1) Feature importance by demographic group — do different features drive decisions for different groups? (2) Counterfactual fairness test — if race were changed but everything else held constant, would the decision change? (3) Whether bias is concentrated in specific decision boundaries or distributed across the model.
- Signal within the signal: Whether the bias is concentrated in one or two features (fixable by removing/transforming those features) or distributed across many features (requires fundamental data and objective restructuring).""",
"""- Classification: pramana — Identifies the specific mechanism (proxy variables) rather than the generic debate (model vs. data) and produces a concrete diagnostic method (SHAP analysis by demographic group)."""
)),

# Project planning
("Our team is overwhelmed with bugs, features, and tech debt. How do we prioritize?",
_yoga(
"""1. Number of open bugs — Explicit
2. Number of feature requests — Explicit
3. Extent of tech debt — Explicit
4. Customer-facing bug severity — Implicit
5. Revenue impact of features — Implicit
6. Developer velocity decline from tech debt — Implicit
7. Team size and capacity — Implicit
8. Upcoming commitments/deadlines — Implicit
9. Customer churn reasons — Implicit
10. Pressure to ship features — Emotional
11. Guilt about tech debt — Emotional
12. Anxiety about bug count — Emotional
13. Which bugs are ACTUALLY causing customer churn — Assumed
14. Which tech debt is ACTUALLY slowing development — Assumed""",
"""1. Bug count: 3/10 — Vanity metric. 100 minor bugs matter less than 1 critical bug.
2. Feature request count: 2/10 — Worse vanity metric. Volume ≠ value.
3. Tech debt extent: 4/10 — Not all debt is equal. Some debt costs nothing; some costs hours daily.
4. Bug severity: 8/10 — Customer-facing bugs that cause data loss, crashes, or workflow blocks drive churn.
5. Feature revenue: 7/10 — Features that unlock new segments or prevent competitive churn matter.
6. Velocity decline: 8/10 — Tech debt that MEASURABLY slows development justifies immediate fix.
7. Team capacity: 7/10 — Hard constraint on what can be done.
8. Deadlines: 6/10 — Context for urgency.
9. Churn reasons: 9/10 — Customers leaving TELL you what matters. If they cite bugs, fix bugs. If they cite missing features, build features.
10. Feature pressure: 1/10 — Pressure is not signal.
11. Tech debt guilt: 0/10 — Not actionable.
12. Bug anxiety: 0/10 — Not actionable.
13. Churn-causing bugs: 10/10 — Bugs that ACTUALLY drive customers to leave.
14. Velocity-killing debt: 9/10 — Debt that MEASURABLY costs developer hours weekly.""",
"""Bug count (3), feature count (2), tech debt extent (4), deadlines (6), pressure (1), guilt (0), anxiety (0): discarded.""",
"""- Churn-causing bugs (10): Directly affects survival.
- Velocity-killing debt (9): Compounds — each week it's not fixed, future work gets slower.
- Churn reasons (9): Direct customer signal.
- Bug severity (8): Customer impact.
- Velocity decline (8): Measurable development cost.
- Feature revenue (7): Growth driver.
- Capacity (7): Constraint.""",
"""What is ACTUALLY causing customers to leave, right now.
"If you fix the top churn driver, retention improves, revenue stabilizes, and you earn time to address everything else."
The team is treating bugs, features, and tech debt as three competing categories. The Yoga method collapses them into one question: what is hurting the business most TODAY? Talk to the last 10 churned customers. The answer will be specific: a specific bug, a specific missing capability, or a specific reliability issue. Fix THAT, not the abstract category.""",
"""- Sub-factors: (1) Which specific issue was mentioned by 3+ churned customers? (2) Which tech debt item costs the team the most hours per week? (3) What is the single feature most frequently cited in competitive losses?
- Signal within the signal: The intersection of churn-causing AND velocity-killing. If one item appears in both lists (e.g., a fragile subsystem that causes customer-facing bugs AND slows development), it is the highest-leverage fix in the entire backlog.""",
"""- Classification: pramana — Replaces abstract category debate with specific, measurable criteria derived from customer behavior data."""
)),

# Legal
("Our contract with a vendor is expiring and they want a 30% price increase. Should we negotiate, switch, or accept?",
_yoga(
"""1. Vendor's price increase (30%) — Explicit
2. Our budget constraints — Implicit
3. Alternative vendors available — Implicit
4. Switching costs — Implicit
5. Contract lock-in provisions — Implicit
6. Vendor's leverage (are we dependent?) — Implicit
7. Our leverage (are they dependent on us?) — Implicit
8. Relationship quality with current vendor — Implicit
9. Market rate for this service — Implicit
10. Anger at the increase — Emotional
11. Fear of migration risk — Emotional
12. Comfort with the familiar vendor — Emotional
13. What specifically drives our dependency on THIS vendor — Assumed""",
"""1. Price increase: 6/10 — The trigger, but not the deciding factor.
2. Budget: 6/10 — Constraint but doesn't determine strategy.
3. Alternatives: 8/10 — If viable alternatives exist, your negotiating position is strong.
4. Switching costs: 9/10 — THIS determines everything. Low switching costs = negotiate hard with credible threat to leave. High switching costs = vendor knows you can't leave.
5. Lock-in provisions: 7/10 — Contractual constraints on switching.
6. Vendor's leverage: 7/10 — Function of switching costs.
7. Our leverage: 7/10 — Function of revenue significance to them.
8. Relationship: 4/10 — Relationships do not survive misaligned incentives.
9. Market rate: 8/10 — If 30% increase puts them above market, strong negotiation point.
10. Anger: 0/10 — Clouds judgment. Discard.
11. Migration fear: 1/10 — Usually overestimated.
12. Comfort: 0/10 — Status quo bias. Discard.
13. Dependency driver: 10/10 — The specific thing that makes switching hard.""",
"""Price increase (6), budget (6), relationship (4), anger (0), migration fear (1), comfort (0): discarded.""",
"""- Dependency driver (10): What makes switching hard.
- Switching costs (9): Determines negotiating power.
- Alternatives (8): Determines credibility of switch threat.
- Market rate (8): Objective benchmark.
- Our leverage (7): Revenue significance to vendor.
- Lock-in provisions (7): Contractual constraints.""",
"""The specific dependency that makes switching away from this vendor difficult.
"If you eliminate or reduce the dependency, your negotiating power transforms."
Is it data migration? Integration complexity? Team familiarity? Proprietary format lock-in? Each has a different mitigation. The 3-month period before contract renewal should be spent REDUCING the dependency, not negotiating the price. Once dependency is reduced, negotiate from strength or switch.""",
"""- Sub-factors: Can the dependency be reduced in 90 days? Can data be exported in a standard format? Can the integration be abstracted behind an adapter layer?
- Signal within the signal: Whether the dependency is TECHNICAL (fixable with engineering) or CONTRACTUAL (fixable with legal review). Technical dependencies can often be resolved; contractual ones require negotiation.""",
"""- Classification: pramana — Identifies the structural cause of weak negotiating position (specific dependency) and prescribes pre-negotiation action (reduce dependency first)."""
)),

# Creative
("I'm writing a novel and stuck on whether to write literary fiction or genre fiction. What should I focus on?",
_yoga(
"""1. Market size (genre > literary) — Explicit
2. Literary prestige — Implicit
3. Personal reading preferences — Implicit
4. Writing skill level — Implicit
5. Agent/publisher accessibility — Implicit
6. Competition level — Implicit
7. Income goals from writing — Implicit
8. Artistic ambition — Implicit
9. Fear of being "just" a genre writer — Emotional
10. Desire for literary recognition — Emotional
11. Imposter syndrome about literary ability — Emotional
12. The story you actually want to tell — Assumed
13. Whether the story's natural form IS genre or literary — Assumed""",
"""1. Market size: 4/10 — Both markets are large enough. Neither guarantees sales.
2. Prestige: 2/10 — External validation is an unreliable guide to creative fulfillment.
3. Reading preferences: 7/10 — You write best in the tradition you've absorbed through reading.
4. Skill level: 5/10 — Improvable through practice in either category.
5. Agent access: 4/10 — Both have pathways.
6. Competition: 3/10 — High in both. Not a differentiator.
7. Income goals: 5/10 — Genre has higher average earnings but literary has higher ceiling.
8. Artistic ambition: 6/10 — Genuine but doesn't determine category.
9. Genre fear: 0/10 — Internalized snobbery. Discard.
10. Recognition desire: 1/10 — Writing for recognition produces hollow work.
11. Imposter syndrome: 0/10 — Universal and not diagnostic.
12. The story itself: 10/10 — The story you want to tell has a natural form.
13. Natural form: 9/10 — Some stories are inherently literary (character/theme driven). Some are inherently genre (plot/world driven). Some are both.""",
"""Market (4), prestige (2), skill (5), agents (4), competition (3), income (5), ambition (6), genre fear (0), recognition (1), imposter (0): discarded.""",
"""- The story itself (10): What do you want to write about?
- Natural form (9): Does the story want to be genre or literary?
- Reading preferences (7): What tradition have you internalized?""",
"""The story you actually want to tell.
"If you get the story right, the category reveals itself."
You are asking the wrong question. "Should I write literary or genre?" is a MARKETING question, not a creative one. The creative question is: "What story am I compelled to tell?" Write THAT story. Then determine what shelf it belongs on. The best novels (Station Eleven, Never Let Me Go, Piranesi) are uncategorizable precisely because the authors wrote the story first and let the category follow.""",
"""- Sub-factors: What scenes play in your head? What themes obsess you? What world do you keep returning to?
- Signal within the signal: Which project makes you feel excited AND scared simultaneously. That combination indicates genuine creative ambition in a direction that challenges you.""",
"""- Classification: pramana — Rejects the false binary (genre vs. literary) by identifying that the actual decision is "what story to tell," which subsumes the category question. Not vikalpa because it produces a specific method (write the compelling story, categorize after)."""
)),

# Education
("I'm a college student choosing between a double major and getting work experience through internships. What matters?",
_yoga(
"""1. Academic performance in primary major — Implicit
2. Job market value of double major vs. internship — Implicit
3. Time/credit requirements of second major — Implicit
4. Internship availability in desired field — Implicit
5. Long-term career goal — Implicit
6. Faculty/advisor recommendations — Implicit
7. Peer pressure (friends double-majoring) — Emotional
8. Resume padding motivation — Emotional
9. Genuine interest in second field — Implicit
10. Financial cost of extra semesters — Implicit
11. What employers in target field actually value — Assumed
12. Whether the second major adds skills the first doesn't — Assumed""",
"""1. Academic performance: 5/10 — Good grades matter but a 3.5 with internships outweighs a 3.9 without.
2. Job market value: 7/10 — Highly field-dependent. In tech: internships > double major. In academia: double major > internships.
3. Credit requirements: 5/10 — Logistics, not strategy.
4. Internship availability: 7/10 — If available, they provide signal about whether you like the career.
5. Career goal: 8/10 — Determines which path is relevant.
6. Advisor input: 4/10 — Academics tend to recommend academic paths.
7. Peer pressure: 0/10 — Noise.
8. Resume padding: 1/10 — Employers see through resume optimization without substance.
9. Genuine interest: 6/10 — Matters for sustainability but not sufficient alone.
10. Financial cost: 6/10 — Extra semesters = real money.
11. What employers value: 9/10 — The ACTUAL hiring criteria in your target field.
12. Unique skill addition: 8/10 — A second major only matters if it provides skills your first major lacks AND your career requires.""",
"""Academic performance (5), credits (5), advisor (4), peer pressure (0), resume padding (1), genuine interest (6), financial cost (6): discarded.""",
"""- What employers actually value (9): Determines the answer directly.
- Career goal (8): Determines context for everything else.
- Unique skill addition (8): Whether double major adds something.
- Job market value (7): Field-specific answer.
- Internship availability (7): Provides career testing.""",
"""What employers in your target field ACTUALLY use to make hiring decisions.
"If you know what employers value, the choice makes itself."
Research this directly: look at job postings for roles you want in 2-3 years. Do they mention the second major? Do they mention "internship experience"? Talk to 3-5 people in those roles and ask what got them hired. In most fields (tech, business, design): relevant work experience beats additional coursework. In others (research, law, medicine): academic credentials dominate.""",
"""- Sub-factors: (1) Does the second major appear in job postings for desired roles? (2) Do professionals in the field recommend it? (3) Could the skills be acquired without the formal major (online courses, bootcamps)?
- Signal within the signal: Whether the second major provides CREDENTIAL value (formal recognition needed) or SKILL value (knowledge that matters). If skill value: you might get 80% of the benefit through a minor or self-study while doing internships.""",
"""- Classification: pramana — Produces a concrete research method (check job postings, talk to professionals) rather than abstract advice."""
)),

]

# Pad to 30 with additional examples across remaining domains
_ADDITIONAL: List[tuple] = [
("Our marketing team wants to be on every social media platform. Should we?", _yoga(
"1. Number of platforms (5+) — Explicit\n2. Team size (small) — Implicit\n3. Content creation capacity — Implicit\n4. Target audience platform preference — Implicit\n5. Current platform performance — Implicit\n6. Competitor platform presence — Implicit\n7. FOMO about missing a platform — Emotional\n8. Where our actual customers spend time — Assumed\n9. Content repurposability across platforms — Implicit\n10. Platform algorithm requirements — Implicit\n11. Cost of mediocre presence everywhere vs. excellent presence somewhere — Assumed\n12. Engagement metrics per platform — Implicit",
"1. Platforms: 3/10 — Being on a platform is meaningless without quality presence.\n2. Team size: 8/10 — Hard constraint on output capacity.\n3. Content capacity: 8/10 — Can't produce quality content for 5+ platforms with small team.\n4. Audience preference: 9/10 — If 80% of customers are on LinkedIn, Instagram presence is wasted.\n5. Current performance: 7/10 — Where are you already getting traction?\n6. Competitor presence: 3/10 — Following competitors is not strategy.\n7. FOMO: 0/10 — Noise.\n8. Where customers ARE: 10/10 — The entire question.\n9. Repurposability: 5/10 — Possible but platforms reward native content.\n10. Algorithm requirements: 6/10 — Each platform demands different cadence/format.\n11. Mediocre vs. excellent: 9/10 — Mediocre presence on 5 platforms produces less than excellent presence on 1.\n12. Engagement: 7/10 — Current data shows what works.",
"Platform count (3), competitor presence (3), FOMO (0), repurposability (5), algorithm (6): discarded.",
"- Where customers are (10): Determines platform choice.\n- Mediocre vs. excellent (9): Quality > coverage.\n- Audience preference (9): Direct data.\n- Team capacity (8): Hard constraint.\n- Content capacity (8): Determines sustainable output.",
"Which ONE platform your actual customers use most.\n'If you dominate one platform, you can expand from strength. If you're mediocre everywhere, you have no foundation.'\nThe law of content marketing: excellence on one platform beats presence on five. Use analytics to identify where your existing audience engages, invest 80% of effort there, and use the remaining 20% to experiment with ONE additional platform. Never more than two until the first is dominant.",
"- Sub-factors: Platform engagement rate, content production cost per platform, audience overlap between platforms.\n- Signal within the signal: Whether your content naturally fits one platform's format (long-form → LinkedIn/blog, visual → Instagram, conversational → Twitter).",
"- Classification: pramana — Based on specific, measurable data (where are customers?) and produces a concrete strategy (dominate one, experiment with one more)."
)),

("We need to decide between building a mobile app or improving our web experience. What matters?", _yoga(
"1. Current web traffic vs. mobile traffic — Implicit\n2. User behavior patterns — Implicit\n3. Development cost comparison — Implicit\n4. Team capabilities — Implicit\n5. Competitor mobile presence — Implicit\n6. Use case fit for mobile — Implicit\n7. Push notification value — Implicit\n8. App store discovery benefits — Implicit\n9. Web app capabilities (PWA) — Implicit\n10. Stakeholder preference for 'having an app' — Emotional\n11. Where users ACTUALLY encounter problems — Assumed\n12. Mobile web vs native performance for our use case — Assumed",
"1. Traffic split: 8/10 — If 90% of users are on web, mobile app is wrong priority.\n2. User behavior: 8/10 — Do users need the product on-the-go or at-desk?\n3. Dev cost: 6/10 — Real but secondary to whether users need it.\n4. Team capabilities: 7/10 — Web team building native app = high learning curve.\n5. Competitor apps: 3/10 — Competitors having apps doesn't mean yours need one.\n6. Mobile use case: 9/10 — Does the product's core value improve on mobile?\n7. Push notifications: 5/10 — Valuable for some products, spam for others.\n8. App store discovery: 3/10 — App store is not a discovery channel for B2B SaaS.\n9. PWA capabilities: 7/10 — PWA may provide 80% of mobile benefits at 20% of cost.\n10. Stakeholder 'wanting an app': 0/10 — Not a business reason.\n11. Where problems are: 10/10 — The actual user pain points.\n12. Performance needs: 6/10 — Most business apps don't need native performance.",
"Dev cost (6), competitors (3), push (5), app store (3), stakeholder preference (0), performance (6): discarded.",
"- Where problems are (10): What are users struggling with NOW?\n- Mobile use case (9): Does mobile genuinely add value?\n- Traffic split (8): Where are users today?\n- User behavior (8): On-the-go vs at-desk usage.\n- Team capabilities (7): What can you build well?\n- PWA option (7): May solve mobile need without native app.",
"Where users are ACTUALLY experiencing problems right now.\n'If you fix the biggest user pain point, whether it's web or mobile becomes obvious.'\nCheck support tickets and user feedback. If users complain about mobile experience, that's your answer. If they complain about web features, improve web. If nobody is asking for a mobile app, building one solves a problem that doesn't exist.",
"- Sub-factors: Support ticket analysis, user session recordings, drop-off points in web flow.\n- Signal within the signal: Whether the 'mobile app' request comes from users or from stakeholders. User-driven = real need. Stakeholder-driven = opinion.",
"- Classification: pramana — Grounded in observable user behavior data."
)),

("Should I learn multiple programming languages broadly or master one deeply?", _yoga(
"1. Current skill level — Implicit\n2. Career goals — Implicit\n3. Industry demand — Implicit\n4. Learning speed — Implicit\n5. Job market preferences — Implicit\n6. T-shaped skill model — Implicit\n7. Imposter syndrome about not knowing enough — Emotional\n8. FOMO about trending languages — Emotional\n9. The specific problems you want to solve — Assumed\n10. Whether mastery in one transfers to others — Assumed",
"1. Current level: 6/10 — Context but not decisive.\n2. Career goals: 8/10 — Different paths require different strategies.\n3. Industry demand: 5/10 — All major languages have demand.\n4. Learning speed: 3/10 — Not a factor in strategy.\n5. Job market: 6/10 — Jobs require one strong language + familiarity with others.\n6. T-shaped model: 7/10 — The answer is BOTH but sequenced: depth first, then breadth.\n7. Imposter syndrome: 0/10 — Universal, not diagnostic.\n8. FOMO: 0/10 — Noise.\n9. Problems to solve: 9/10 — Languages are tools for problems. The problem determines the tool.\n10. Transfer: 8/10 — Deep mastery of one language teaches patterns that transfer to all. Shallow knowledge of many teaches none deeply.",
"Current level (6), demand (5), speed (3), market (6), imposter (0), FOMO (0): discarded.",
"- Problems to solve (9): Tools serve problems.\n- Career goals (8): Strategy depends on destination.\n- Transfer (8): Deep mastery transfers.\n- T-shaped (7): Depth first, then breadth.",
"Whether deep mastery of one language is transferring patterns that make learning others easier.\n'If you master one language deeply enough, learning others becomes fast because you understand programming, not just a language.'\nDepth first. Master one language to the point where you understand its design tradeoffs, not just its syntax. Then learning a second takes weeks, not months. Breadth without depth produces 'can write hello world in 10 languages' which impresses no one.",
"- Signal within the signal: The difference between knowing syntax and understanding PARADIGMS. If you deeply understand OOP in Java, you understand OOP everywhere. If you deeply understand functional programming in Haskell, you apply it in any language. Paradigm mastery > language mastery.",
"- Classification: pramana — Specific, sequenced recommendation (depth then breadth) based on transferable learning theory."
)),

("My team disagrees on whether we should use microservices or a monolith for our new project.", _yoga(
"1. Team size — Implicit\n2. Product complexity — Implicit\n3. Deployment frequency needs — Implicit\n4. Team experience with distributed systems — Implicit\n5. Scale requirements — Implicit\n6. Time to market pressure — Implicit\n7. Industry trend toward microservices — Emotional (bandwagon)\n8. Fear of monolith being 'outdated' — Emotional\n9. The actual boundaries between system components — Assumed\n10. Whether the team can even DEFINE service boundaries — Assumed\n11. Current technical debt tolerance — Implicit\n12. DevOps maturity — Implicit",
"1. Team size: 8/10 — <10 developers = monolith almost always correct. Microservices add coordination cost that small teams can't absorb.\n2. Complexity: 7/10 — Some domains naturally decompose; others don't.\n3. Deploy frequency: 5/10 — Achievable with monolith (deploy pipeline, feature flags).\n4. Distributed systems experience: 9/10 — Team without this experience will spend months learning instead of building.\n5. Scale: 4/10 — Premature. Monoliths scale further than people think (Stack Overflow runs on one).\n6. Time to market: 8/10 — Monolith is faster to build, deploy, and debug initially.\n7. Industry trend: 0/10 — Bandwagon. Discard.\n8. Fear of 'outdated': 0/10 — Noise.\n9. Component boundaries: 10/10 — If you can't clearly define service boundaries, microservices will be chaos.\n10. Boundary definition ability: 9/10 — If the team struggles to agree on boundaries, that IS the answer: you don't understand the domain well enough for microservices.\n11. Tech debt tolerance: 3/10 — Both architectures accumulate debt.\n12. DevOps maturity: 7/10 — Microservices require mature CI/CD, monitoring, tracing.",
"Deploy frequency (5), scale (4), trend (0), fear (0), tech debt (3): discarded.",
"- Clear component boundaries (10): If boundaries aren't clear, microservices = chaos.\n- Distributed systems experience (9): Without it, months wasted learning instead of building.\n- Boundary definition ability (9): The team's clarity IS the answer.\n- Team size (8): Small teams can't absorb microservices overhead.\n- Time to market (8): Monolith ships faster.\n- DevOps maturity (7): Infrastructure readiness.",
"Whether the team can draw service boundaries on a whiteboard in 30 minutes and all agree.\n'If you can't define boundaries clearly, start with a monolith. Boundaries emerge from understanding the domain, and understanding comes from building.'\nThe modular monolith is the answer the team isn't considering: monolith deployment with clear module boundaries that CAN be extracted to services LATER when you understand the domain. This is what Shopify does. Start monolith, extract services as boundaries become clear through experience.",
"- Signal within the signal: If any proposed service boundary requires synchronous calls to another service for its core function, it's not a real boundary — it's an artificial split that adds network latency to what should be a function call.",
"- Classification: pramana — Specific diagnostic test (30-minute whiteboard exercise) and concrete alternative (modular monolith)."
)),

# Additional examples to reach 30
("Our dataset has 50 features. How do we decide which matter?", _yoga("1. Feature count (50) — Explicit\n2. Domain knowledge — Implicit\n3. Correlation analysis — Implicit\n4. Feature importance from model — Implicit\n5. Multicollinearity — Implicit\n6. Missing data rates — Implicit\n7. Feature engineering possibilities — Implicit\n8. Computational cost — Implicit\n9. The business question the model must answer — Assumed\n10. Which features are ACTIONABLE by the business — Assumed", "1. Count: 2/10 — 50 is not inherently too many or too few.\n2. Domain knowledge: 8/10 — Expert intuition about which features SHOULD matter.\n3. Correlation: 5/10 — Correlation ≠ usefulness.\n4. Model importance: 7/10 — Data-driven but can be misleading with correlated features.\n5. Multicollinearity: 6/10 — Important technically but not strategic.\n6. Missing data: 6/10 — Features with 80%+ missing are likely noise.\n7. Engineering: 4/10 — Secondary to selection.\n8. Compute: 3/10 — Rarely the bottleneck.\n9. Business question: 9/10 — Determines what 'matters' means.\n10. Actionability: 10/10 — Features the business CANNOT act on are useless regardless of predictive power.", "Count (2), correlation (5), engineering (4), compute (3): discarded.", "- Actionability (10): Can the business DO something different based on this feature?\n- Business question (9): What are we predicting and why?\n- Domain knowledge (8): Expert intuition about mechanism.\n- Model importance (7): Data-driven ranking.", "Which features the business can actually ACT ON.\n'If you select for actionable features, the model produces decisions, not just predictions.'\nA feature that perfectly predicts churn but represents something unchangeable (customer's industry) is informative but not actionable. A feature that moderately predicts churn and IS changeable (support response time) is more valuable because the business can INTERVENE on it.", "- Signal within the signal: The distinction between PREDICTIVE features (useful for forecasting) and CAUSAL features (useful for intervention). Most ML pipelines optimize for prediction when the business needs intervention.", "- Classification: pramana — Reframes feature selection from statistical to business-strategic.")),

("How should I structure my daily schedule to be more productive?", _yoga("1. Current schedule — Implicit\n2. Energy patterns — Implicit\n3. Meeting load — Implicit\n4. Deep work capacity — Implicit\n5. Communication expectations — Implicit\n6. Personal obligations — Implicit\n7. Productivity guilt — Emotional\n8. Comparison to others' productivity — Emotional\n9. The ONE task that actually moves your goals forward — Assumed\n10. Whether the problem is scheduling or clarity of priority — Assumed", "1. Current schedule: 5/10 — Context but not the solution.\n2. Energy patterns: 8/10 — When are you sharpest? Protect that time.\n3. Meetings: 7/10 — The #1 productivity destroyer. Consolidate or eliminate.\n4. Deep work: 8/10 — Uninterrupted blocks determine output quality.\n5. Communication: 6/10 — Necessary but can be batched.\n6. Personal: 5/10 — Constraint.\n7. Guilt: 0/10 — Noise.\n8. Comparison: 0/10 — Noise.\n9. The ONE task: 10/10 — If you do this task and nothing else, was it a good day?\n10. Schedule vs. priority: 9/10 — Most 'schedule problems' are actually priority problems.", "Current schedule (5), communication (6), personal (5), guilt (0), comparison (0): discarded.", "- The ONE task (10): What single output matters most today?\n- Schedule vs. priority (9): Is the problem really scheduling?\n- Energy patterns (8): Protect peak energy for important work.\n- Deep work (8): Uninterrupted time quality.\n- Meetings (7): The enemy of deep work.", "Whether you have a PRIORITY problem disguised as a SCHEDULING problem.\n'If you know the one thing that matters today and protect time for it, the rest of the schedule organizes around it.'\nDon't redesign your schedule. Instead: (1) Each morning, identify the ONE output that matters most. (2) Block your peak energy time for it. (3) Do it FIRST. Everything else is secondary and can be improvised.", "- Signal within the signal: The question 'was today productive?' should be answerable with ONE output, not a list of activities.", "- Classification: pramana — Reframes scheduling as a priority problem with a specific daily protocol.")),

("We're debating whether to open-source our core library or keep it proprietary.", _yoga("1. Competitive advantage from the code — Implicit\n2. Community contribution potential — Implicit\n3. Hiring/brand benefits — Implicit\n4. Support/maintenance burden — Implicit\n5. Revenue model dependency on proprietary code — Implicit\n6. License choice implications — Implicit\n7. Whether the competitive advantage IS the code or the SERVICE — Assumed\n8. Fear of competitors using our code — Emotional\n9. Ego about code quality — Emotional\n10. Strategic value of ecosystem control — Implicit", "1. Competitive advantage from code: 7/10 — If the code IS the moat, don't open-source. If the moat is data/network/service, the code isn't the moat.\n2. Community contributions: 5/10 — Usually overestimated. Most OSS gets few external contributors.\n3. Hiring benefits: 6/10 — Real but not sufficient reason alone.\n4. Support burden: 6/10 — Real cost often underestimated.\n5. Revenue model: 8/10 — If revenue comes from selling the software, open-sourcing destroys it. If from service/hosting, open-sourcing can accelerate adoption.\n6. License: 5/10 — Important but tactical.\n7. Code vs. service: 10/10 — THE question.\n8. Fear: 1/10 — Mostly unfounded. Competitors build, not copy.\n9. Ego: 0/10 — Discard.\n10. Ecosystem: 7/10 — Controlling the ecosystem (Hashicorp model) can be powerful.", "Community (5), license (5), hiring (6), support (6), fear (1), ego (0): discarded.", "- Code vs. service as competitive advantage (10).\n- Revenue model (8).\n- Competitive advantage from code (7).\n- Ecosystem control (7).", "Whether your competitive advantage is the CODE or the SERVICE built on the code.\n'If the code is not your moat, open-sourcing it strengthens your actual moat (adoption, ecosystem, data).'\nRedis, Kubernetes, PostgreSQL are open-source. The companies around them profit from hosting, support, and enterprise features. If your value is similar (the service, not the code), open-source accelerates adoption. If your value IS novel code (algorithm, model), keep it proprietary.", "- Signal within the signal: Could a competitor take your code, deploy it, and match your product? If yes (your advantage is code), don't open-source. If no (your advantage is data, network, service quality), open-source freely.", "- Classification: pramana — Clear decision framework based on where competitive advantage lives.")),

("Should our engineering team adopt AI coding assistants (Copilot, etc.)?", _yoga("1. Productivity claims from vendors — Explicit\n2. Code quality concerns — Implicit\n3. Security risks of AI suggestions — Implicit\n4. Cost per seat — Implicit\n5. Team's coding proficiency — Implicit\n6. IP/licensing concerns — Implicit\n7. Developer sentiment — Implicit\n8. Hype cycle positioning — Emotional\n9. Fear of being left behind — Emotional\n10. What SPECIFIC tasks consume the most developer time — Assumed\n11. Whether the productivity gain exceeds the review overhead — Assumed", "1. Vendor claims: 3/10 — Self-reported and selection-biased. '40% faster' claims are not independently verified.\n2. Code quality: 7/10 — AI generates plausible but sometimes subtly wrong code that requires careful review.\n3. Security: 6/10 — AI can suggest insecure patterns.\n4. Cost: 4/10 — $10-20/month/dev is trivial relative to salary.\n5. Team proficiency: 7/10 — Junior devs may over-trust suggestions. Senior devs know when to reject.\n6. IP concerns: 5/10 — Mostly resolved with enterprise tiers.\n7. Sentiment: 6/10 — Developer buy-in matters for adoption.\n8. Hype: 0/10 — Noise.\n9. FOMO: 0/10 — Noise.\n10. Time sinks: 9/10 — If devs spend 40% on boilerplate, AI helps hugely. If 40% on architecture decisions, AI barely helps.\n11. Gain vs. review overhead: 10/10 — Net productivity depends on this ratio.", "Vendor claims (3), cost (4), IP (5), hype (0), FOMO (0): discarded.", "- Net gain vs. review overhead (10).\n- Time sinks (9).\n- Code quality impact (7).\n- Team proficiency (7).\n- Sentiment (6).", "What specific tasks consume the most developer time that AI can actually help with.\n'If boilerplate and routine code dominate developer time, AI assistants are high-value. If architecture and debugging dominate, they barely help.'\nRun a 2-week trial with 3-5 volunteers. Measure: lines accepted vs. rejected, review time for AI code, and self-reported productivity. Data from YOUR team on YOUR codebase beats any vendor benchmark.", "- Signal within the signal: The accept/reject ratio during trial. If devs accept >60% of suggestions: good fit. If <30%: the AI doesn't understand your codebase well enough to help.", "- Classification: pramana — Prescribes specific, measurable trial rather than opinion-based decision.")),

("How do I decide which books to read when my reading list is overwhelming?", _yoga("1. List size — Explicit\n2. Book recommendations from trusted sources — Implicit\n3. Current problems/challenges — Implicit\n4. Reading speed — Implicit\n5. Available time — Implicit\n6. FOMO about unread books — Emotional\n7. Guilt about abandoned books — Emotional\n8. The specific question or problem you're trying to solve RIGHT NOW — Assumed\n9. Whether you're reading to learn, to solve, or to enjoy — Assumed", "1. List size: 2/10 — The list is infinite; you'll never finish it.\n2. Recommendations: 5/10 — Others' needs ≠ yours.\n3. Current problems: 9/10 — Read what solves TODAY's problem.\n4. Speed: 3/10 — Not a strategic factor.\n5. Time: 5/10 — Constraint, not strategy.\n6. FOMO: 0/10 — Discard entirely.\n7. Guilt: 0/10 — Abandon books freely.\n8. Current question: 10/10 — The right book is the one that answers the question you have NOW.\n9. Purpose: 8/10 — Learning vs. solving vs. enjoying require different selection criteria.", "List size (2), recommendations (5), speed (3), time (5), FOMO (0), guilt (0): discarded.", "- Current question (10): What problem are you trying to solve?\n- Current problems (9): Reading should be practical.\n- Purpose (8): Determines selection criteria.", "The specific question you're trying to answer right now.\n'If you read to answer a specific question, you'll read the right book, read the relevant parts, and stop when you have the answer.'\nStop treating reading as consumption (finish the book, check it off). Treat it as RESEARCH (find the answer, apply it, move on). Read the chapter that answers your question. Skip the rest. Move to the next book that answers the next question.", "- Signal within the signal: Give yourself permission to read 3 chapters, get the idea, and stop. Most non-fiction books have one big idea padded to 300 pages.", "- Classification: pramana — Reframes reading from consumption to research with specific selection method.")),

("Our product has both B2B and B2C potential. How do we choose?", _yoga("1. B2B revenue potential — Implicit\n2. B2C scale potential — Implicit\n3. Team's sales experience — Implicit\n4. Marketing budget — Implicit\n5. Product fit for each — Implicit\n6. Support costs per segment — Implicit\n7. Unit economics per segment — Implicit\n8. Investor preference — Emotional\n9. Founder's personal preference — Emotional\n10. Which segment is already USING the product — Assumed\n11. CAC and LTV by segment — Assumed", "1. B2B revenue: 6/10 — Higher per customer but slower.\n2. B2C scale: 5/10 — More users but lower revenue per user.\n3. Sales experience: 7/10 — B2B requires different skills than B2C.\n4. Budget: 6/10 — B2C requires larger marketing spend.\n5. Product fit: 8/10 — Where does the product solve a more acute problem?\n6. Support costs: 6/10 — B2C support at scale is expensive.\n7. Unit economics: 8/10 — Which segment produces positive unit economics FIRST?\n8. Investor preference: 1/10 — Don't build for investors.\n9. Founder preference: 2/10 — Don't build from preference.\n10. Who is already using it: 10/10 — Demand you don't have to create.\n11. Unit economics: 9/10 — The math determines viability.", "B2B/B2C revenue/scale abstractions (5-6), budget (6), support (6), investor (1), founder preference (2): discarded.", "- Who is already using it (10): Go where demand exists.\n- Unit economics (9): Math determines viability.\n- Product fit (8): Where is pain most acute?\n- Unit economics by segment (8): Which reaches positive first?\n- Sales experience (7): What CAN you sell?", "Which segment already has users trying to give you money.\n'If you follow the existing demand signal, you'll build the right product for the right market.'\nDon't choose strategically between B2B and B2C. Look at who is ALREADY using the product, paying, or requesting features. That segment chose YOU. Serve them deeply, then expand.", "- Signal within the signal: Revenue concentration. If 3 B2B customers generate 80% of revenue, you're B2B. If 10,000 individual users generate 80%, you're B2C. Let the data decide.", "- Classification: pramana — Based on observable demand signals.")),

("How do we reduce meeting overload in our organization?",
_yoga("1. Total meeting hours per week — Explicit\n2. Meeting types (standup, planning, 1:1, all-hands, ad-hoc) — Implicit\n3. Meeting effectiveness perception — Implicit\n4. Decision-making quality — Implicit\n5. Information sharing alternatives — Implicit\n6. Cultural expectation of attendance — Implicit\n7. Manager scheduling habits — Implicit\n8. Calendar tool limitations — Implicit\n9. Meeting FOMO — Emotional\n10. Which meetings ACTUALLY produce decisions — Assumed\n11. Which information could be async — Assumed",
"1. Total hours: 6/10 — Symptom, not cause.\n2. Meeting types: 7/10 — Different types have different value.\n3. Effectiveness: 5/10 — Subjective.\n4. Decision quality: 8/10 — Meetings exist to make decisions. If decisions happen elsewhere, meetings are waste.\n5. Async alternatives: 7/10 — Most information sharing can be written.\n6. Cultural expectation: 6/10 — Hard to change but important.\n7. Manager habits: 7/10 — Managers schedule most meetings.\n8. Tools: 2/10 — Tools don't cause meeting overload.\n9. FOMO: 0/10 — Discard.\n10. Decision-producing meetings: 10/10 — The only meetings that matter.\n11. Async-able info: 9/10 — Information that can be async SHOULD be async.",
"Total hours (6), effectiveness (5), cultural (6), tools (2), FOMO (0): discarded.",
"- Decision-producing meetings (10): Only meetings that produce decisions matter.\n- Async-able information (9): Remove meetings that are information broadcasts.\n- Decision quality (8): Are decisions actually being made?\n- Meeting types (7): Categorize to determine which to keep.\n- Async alternatives (7): Replace broadcast meetings.\n- Manager habits (7): Root cause of many unnecessary meetings.",
"Which meetings actually produce decisions that would not happen otherwise.\n'If you keep only decision-making meetings and make everything else async, meeting load drops 50-70%.'\nAudit: for each recurring meeting, ask 'what was the last decision made in this meeting?' If the answer is 'none' or 'I don't remember,' cancel it. Replace with a written update. The few meetings that remain will be shorter and more focused.",
"- Signal within the signal: A meeting without an AGENDA is a meeting without a purpose. The simplest intervention: require a written agenda with specific decisions to be made. Meetings without agendas get cancelled.",
"- Classification: pramana — Specific audit method (decision test) and intervention (require agendas, cancel non-decision meetings)."
)),

("Is it worth investing time in writing documentation for our codebase?",
_yoga("1. Current documentation state — Implicit\n2. Team size — Implicit\n3. Onboarding frequency — Implicit\n4. Code complexity — Implicit\n5. Bus factor — Implicit\n6. Developer interruptions for questions — Implicit\n7. Time cost of writing docs — Implicit\n8. Docs going stale — Implicit\n9. Belief that 'code should be self-documenting' — Emotional/philosophical\n10. Which questions are asked REPEATEDLY — Assumed\n11. Whether the bottleneck is UNDERSTANDING or FINDING information — Assumed",
"1. Current state: 5/10 — Context.\n2. Team size: 6/10 — Larger teams benefit more.\n3. Onboarding: 8/10 — If you onboard frequently, docs save weeks per new hire.\n4. Complexity: 6/10 — More complex = more need.\n5. Bus factor: 7/10 — If one person knows a system, docs are insurance.\n6. Interruptions: 9/10 — Each 'how does X work?' interruption costs TWO people's time. Docs prevent this.\n7. Time cost: 5/10 — Real but amortized over all future readers.\n8. Staleness: 6/10 — Real problem but solvable with doc-as-code.\n9. Self-documenting belief: 1/10 — Code tells you WHAT it does, not WHY or HOW to use it.\n10. Repeated questions: 10/10 — Each repeated question = missing doc that would save cumulative hours.\n11. Understanding vs. finding: 8/10 — Often the info exists but nobody can find it.",
"Current state (5), team size (6), complexity (6), time cost (5), staleness (6), self-documenting (1): discarded.",
"- Repeated questions (10): Direct measure of doc need.\n- Interruptions (9): Measurable cost.\n- Onboarding (8): Docs save weeks per hire.\n- Understanding vs. finding (8): May need search, not docs.\n- Bus factor (7): Risk mitigation.",
"Which questions are asked more than twice.\n'If you document the answer to every question asked more than twice, you've written the 20% of documentation that provides 80% of the value.'\nDon't write comprehensive docs. Write ANSWER docs: every time someone asks a question that has been asked before, write the answer in a searchable place. After 3 months, you'll have exactly the documentation your team actually needs.",
"- Signal within the signal: Keep a tally for 2 weeks of every question asked in Slack/meetings about how something works. Rank by frequency. Document the top 10. You're done.",
"- Classification: pramana — Specific, minimal-effort method (document repeated questions) rather than aspirational 'write complete docs.'"
)),

]

# Additional compact examples to reach 30
_ADDITIONAL2 = [
("We're considering 5 different cloud providers. How do we choose?", _yoga("1. Pricing — Explicit\n2. Feature set — Explicit\n3. Reliability/SLA — Implicit\n4. Team familiarity — Implicit\n5. Vendor lock-in risk — Implicit\n6. Support quality — Implicit\n7. Compliance certifications — Implicit\n8. Geographic coverage — Implicit\n9. Community/ecosystem — Implicit\n10. What our SPECIFIC workload actually requires — Assumed", "1. Pricing: 5/10 — Comparable across major providers.\n2. Features: 4/10 — All major providers have equivalent services.\n3. Reliability: 6/10 — All major providers offer 99.9%+.\n4. Team familiarity: 9/10 — Determines productivity for months.\n5. Lock-in: 5/10 — Real but manageable with abstraction layers.\n6. Support: 5/10 — Varies but not decisive.\n7. Compliance: 7/10 — If you need HIPAA/FedRAMP, this is a hard filter.\n8. Geographic: 6/10 — Matters for latency but most providers cover major regions.\n9. Community: 4/10 — All have large communities.\n10. Workload needs: 10/10 — Specific requirements (GPU availability, edge computing, specific managed services) may only exist on one provider.", "Pricing (5), features (4), community (4), lock-in (5), support (5): discarded.", "- Workload needs (10): Specific requirements narrow the field.\n- Team familiarity (9): Productivity multiplier.\n- Compliance (7): Hard filter.", "Your team's existing expertise.\n'If you choose the provider your team already knows, you ship 2x faster and avoid 6 months of learning curve.'\nUnless a specific compliance or technical requirement eliminates a provider, choose the one your team knows best. The differences between AWS, GCP, and Azure are marginal compared to the productivity difference between a team that knows their provider and one that doesn't.", "- Signal within the signal: How many of your engineers have production experience with each provider?", "- Classification: pramana — Decision based on measurable team experience.")),

("Should our startup focus on B2B or B2C?", _yoga("1. Revenue model differences — Implicit\n2. Sales cycle — Implicit\n3. Team background — Implicit\n4. Market size — Implicit\n5. Investor preferences — Emotional\n6. Founder passion — Emotional\n7. Where we already have traction — Assumed\n8. Unit economics by segment — Assumed", "1. Revenue: 6/10 — Both can work.\n2. Sales cycle: 6/10 — Different, not better/worse.\n3. Team background: 8/10 — B2B sales skills ≠ B2C growth skills.\n4. Market: 4/10 — Both large enough.\n5. Investors: 1/10 — Don't build for investors.\n6. Passion: 2/10 — Passion does not equal product-market fit.\n7. Existing traction: 10/10 — Where is demand already pulling?\n8. Unit economics: 9/10 — Which segment is viable?", "Revenue (6), cycle (6), market (4), investors (1), passion (2): discarded.", "- Traction (10): Go where demand exists.\n- Unit economics (9): Math determines viability.\n- Team background (8): Can you actually execute?", "Where customers are already trying to pay you.\nLet the market decide. Check: who signed up? Who requested demos? Who asked about pricing? That segment chose YOU.", "- Signal within the signal: Revenue concentration reveals the answer.", "- Classification: pramana — Based on observable market demand.")),

("How do we decide between Postgres and MongoDB for our new project?", _yoga("1. Data structure needs — Implicit\n2. Query patterns — Implicit\n3. Scalability — Implicit\n4. Team experience — Implicit\n5. ACID compliance needs — Implicit\n6. Ecosystem/tooling — Implicit\n7. Developer preference — Emotional\n8. Hype factor — Emotional\n9. Whether our data is actually relational — Assumed", "1. Data structure: 7/10 — If data has clear relationships, relational wins.\n2. Query patterns: 7/10 — Complex joins → SQL. Document lookups → Mongo.\n3. Scalability: 3/10 — Both scale well for most workloads. Premature concern.\n4. Team experience: 8/10 — Productivity for next 6 months.\n5. ACID needs: 8/10 — If transactions matter, Postgres. Non-negotiable.\n6. Ecosystem: 5/10 — Both have rich ecosystems.\n7. Preference: 0/10 — Noise.\n8. Hype: 0/10 — Noise.\n9. Relational data: 9/10 — If your entities have relationships, use a relational DB.", "Scalability (3), ecosystem (5), preference (0), hype (0): discarded.", "- Whether data is relational (9).\n- ACID needs (8).\n- Team experience (8).\n- Data structure (7).\n- Query patterns (7).", "Whether your core entities have relationships between them.\nIf your data has foreign keys, joins, and transactions: Postgres. Full stop. MongoDB is for document-centric data without cross-document relationships. Most business applications are relational.", "- Signal: Draw your data model. If arrows between entities exist, it is relational data → Postgres.", "- Classification: pramana — Specific diagnostic (draw data model) producing clear recommendation.")),

("How do I decide between writing a blog post, recording a video, or creating a course for my content?", _yoga("1. Topic complexity — Implicit\n2. Audience preference — Implicit\n3. Time investment — Implicit\n4. SEO/discoverability — Implicit\n5. Revenue potential — Implicit\n6. Personal comfort with medium — Implicit\n7. What you're trying to achieve — Assumed\n8. Which format YOUR audience actually engages with — Assumed", "1. Complexity: 6/10 — Complex topics may need video; simple ones work as posts.\n2. Audience preference: 8/10 — If your audience reads, blog. If they watch, video.\n3. Time: 5/10 — Constraint, not strategy.\n4. SEO: 6/10 — Blog posts are more discoverable but video has YouTube.\n5. Revenue: 5/10 — Courses generate most but require most investment.\n6. Comfort: 4/10 — Improvable. Not decisive.\n7. Goal: 9/10 — Brand awareness → blog/video. Revenue → course. Authority → all three.\n8. Audience engagement: 10/10 — What does your EXISTING audience actually consume?", "Time (5), revenue (5), comfort (4), SEO (6): discarded.", "- Audience engagement (10).\n- Goal (9).\n- Audience preference (8).", "What format your existing audience actually engages with.\nCheck your analytics: blog post read time, video completion rate, email open rate. The data tells you what format resonates. Don't guess — measure.", "- Signal: Your highest-engagement existing content reveals the format.", "- Classification: pramana — Data-driven format selection.")),

("We have a technical disagreement — half the team wants event sourcing, half wants CRUD. What should we focus on?", _yoga("1. Event sourcing benefits — Explicit\n2. CRUD simplicity — Explicit\n3. Team experience with event sourcing — Implicit\n4. Domain complexity — Implicit\n5. Audit trail requirements — Implicit\n6. Architectural fashion — Emotional\n7. Whether we actually NEED event history — Assumed\n8. Cost of getting it wrong — Assumed", "1. ES benefits: 5/10 — Theoretical, not proven for our case.\n2. CRUD simplicity: 6/10 — Real advantage, especially for speed.\n3. ES experience: 8/10 — Event sourcing without experience leads to months of pain.\n4. Domain complexity: 7/10 — Some domains (financial, legal) genuinely need event history.\n5. Audit requirements: 8/10 — If audit trail is mandated, event sourcing has an advantage.\n6. Fashion: 0/10 — Discard.\n7. Need for event history: 10/10 — THE deciding factor.\n8. Wrong-choice cost: 7/10 — CRUD → ES migration is possible. ES → CRUD is nearly impossible.", "ES benefits abstract (5), CRUD simplicity abstract (6), fashion (0): discarded.", "- Need for event history (10).\n- ES experience (8).\n- Audit requirements (8).\n- Wrong-choice cost (7).\n- Domain complexity (7).", "Whether you actually NEED to reconstruct past states or replay events.\nIf your domain requires 'what was the state on March 3?' or 'replay all events since the error': event sourcing. If not: CRUD. The vast majority of applications do not need event reconstruction. Start CRUD, add event sourcing to specific bounded contexts IF needed.", "- Signal: Can you name 3 specific user stories that require event replay? If yes: ES for those contexts. If no: CRUD.", "- Classification: pramana — Specific test (name 3 event-replay user stories) producing clear decision.")),
]

# Extend _DATA with all additional examples
for item in _ADDITIONAL:
    _DATA.append(item)
for item in _ADDITIONAL2:
    _DATA.append(item)
