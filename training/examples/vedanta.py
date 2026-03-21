"""Vedanta training examples — 30 contradiction resolution examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "vedanta"

def generate_vedanta_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples

def _ved(contradiction: str, adhyaropa: str, apavada: str, sat: str,
         mahavakya: str, rederivation: str) -> str:
    return f"""THE CONTRADICTION:
{contradiction}

SUPERIMPOSITION (Adhyaropa):
{adhyaropa}

NEGATION (Apavada):
{apavada}

WHAT REMAINS (Sat):
{sat}

THE REFRAMING (Mahavakya):
{mahavakya}

RE-DERIVATION:
{rederivation}"""

_DATA: List[tuple] = [

# SOFTWARE ENGINEERING
("We're debating whether to prioritize code quality or shipping speed. The tech lead wants comprehensive testing and refactoring. The product manager wants features shipped this week.",
_ved(
"""A claims: Code quality (comprehensive testing, refactoring, clean architecture) should be the priority.
B claims: Shipping speed (features out the door this week) should be the priority.
These conflict because: every hour spent on quality is an hour not shipping, and every hour shipping is an hour accumulating debt. At any given moment, the team can only optimize for one.""",

"""If A is fully true (quality always takes priority):
  - Consequences: Every feature takes 2-3x longer. Tests and refactoring precede all new code. Technical debt is near zero.
  - World required: A world where the company has unlimited time and no competition. Where customers wait patiently. Where perfect architecture matters more than solving customer problems. Where the market never changes faster than the codebase improves.

If B is fully true (speed always takes priority):
  - Consequences: Features ship daily. Tests are skipped. Refactoring is deferred. The codebase becomes increasingly fragile.
  - World required: A world where technical debt has no cost. Where bugs don't lose customers. Where developers never need to modify existing code. Where the system never needs to scale beyond its initial architecture.""",

"""A's projections:
  - ASSUMES quality and speed are always in opposition. This is a projection: well-tested, clean code often ships FASTER over a 3-month horizon because it doesn't break constantly. The opposition is true in the short term (this week) but false in the medium term (this quarter).
  - ASSUMES all code needs equal quality. This is a projection: prototype code, one-time scripts, and experiments don't need the same quality as core business logic.

B's projections:
  - ASSUMES shipping speed is measured by this week's output. This is a projection: if this week's code causes 3 weeks of bug-fixing next month, the actual speed was NEGATIVE.
  - ASSUMES features are the bottleneck. This is a projection: if customers are churning due to bugs, shipping more features onto a broken foundation doesn't help.""",

"""What survives negation: BOTH quality and speed serve the same underlying goal — delivering value to customers as fast as possible over the RELEVANT time horizon. Neither quality nor speed is intrinsically valuable; both are means to sustainable velocity. What is real is: the rate at which the team delivers WORKING, USABLE solutions to customer problems, measured not this week but this quarter.""",

"""The quality vs. speed debate is a false dichotomy created by using the wrong time horizon. On a one-week horizon, they conflict. On a one-quarter horizon, they converge: quality IS speed, because the absence of quality is the primary cause of slowness. The real question is not 'quality or speed?' but 'what is the shortest time horizon at which our decisions are evaluated?'""",

"""- Mahavakya + assumption "decisions are evaluated weekly by stakeholders" = B's position (ship now, deal with consequences later).
- Mahavakya + assumption "decisions are evaluated quarterly by business outcomes" = A's position (invest in quality that pays off over months).
The debate is actually about organizational time horizons, not engineering practices."""
)),

("Should we build our own infrastructure or use cloud services? Our infra team wants to build for control. Our product team says just use AWS.",
_ved(
"""A claims: We should build our own infrastructure for control, customization, and cost savings at scale.
B claims: We should use cloud services (AWS/GCP/Azure) for speed, reliability, and letting us focus on product.
These conflict because: building infra requires dedicating engineering talent to non-product work, while using cloud means accepting vendor constraints and costs.""",

"""If A is fully true (build everything ourselves):
  - Consequences: Full control over hardware, networking, security, and performance. No vendor lock-in. Potentially lower costs at massive scale. BUT: requires hiring a dedicated infra team, maintaining hardware, handling security patches, managing capacity planning.
  - World required: A world where the company has (a) engineering talent to spare for infrastructure, (b) scale that justifies the fixed costs, (c) unique requirements that cloud cannot satisfy, (d) the discipline to maintain infrastructure without neglecting product development.

If B is fully true (use cloud for everything):
  - Consequences: Infrastructure managed by a team of 100,000+ AWS engineers. Rapid provisioning. Global reach. BUT: vendor lock-in, rising costs at scale (cloud margin is 60%+), limited customization, and a dependency on a single vendor's roadmap.
  - World required: A world where cloud services perfectly match all needs, costs remain reasonable at all scales, vendor lock-in is costless, and infrastructure never needs to be a competitive advantage.""",

"""A's projections:
  - ASSUMES 'control' is inherently valuable. This is a projection: control is valuable only when you need to do something the cloud CANNOT do. For most companies, cloud capabilities exceed their needs. Control without a specific use case is overhead, not advantage.
  - ASSUMES cost savings at scale. This is a projection from companies like Dropbox and Basecamp who saved by leaving cloud. But they were spending $50M+/year on cloud at massive scale. Most companies never reach that threshold.

B's projections:
  - ASSUMES cloud is always cheaper in total cost of ownership. This is a projection: cloud is cheaper at small scale and in opportunity cost, but at large scale, the cloud premium can exceed the cost of a full infra team.
  - ASSUMES the team will not need infrastructure as a differentiator. This is a projection: some products (real-time gaming, edge computing, custom hardware) require infrastructure capabilities that are competitive advantages.""",

"""What survives negation: The question is not 'build or buy infrastructure' but 'is infrastructure a COMMODITY or a DIFFERENTIATOR for our specific business?' If commodity: buy it (cloud). If differentiator: build it. The answer is almost always 'commodity' for early-stage companies and gradually shifts toward 'differentiator' at massive scale or for specific technical requirements.""",

"""Infrastructure decisions are not architectural choices but economic maturity questions. Early-stage companies buying infrastructure (cloud) is like a startup renting office space — the premium is worth the flexibility. Late-stage companies building infrastructure is like an established firm buying a building — the investment is worth the long-term savings. The question is not 'build vs. buy?' but 'what economic stage are we in?'""",

"""- Mahavakya + assumption "we are early stage, infrastructure is not our differentiator" = B's position (use cloud, focus on product).
- Mahavakya + assumption "we are at massive scale and infrastructure performance is our differentiator" = A's position (build for control and cost savings).
The debate dissolves when you identify your economic stage."""
)),

("Our senior architect insists on using a relational database for everything. Our data team wants to use specialized databases (Redis, Elasticsearch, MongoDB) for different use cases. Who is right?",
_ved(
"""A claims: Use a relational database (PostgreSQL) for all data storage — it handles transactions, analytics, search, and caching with proper indexing and extensions.
B claims: Use the right tool for the job — Redis for caching, Elasticsearch for search, MongoDB for flexible documents, PostgreSQL for relational data.
These conflict because: A values simplicity and consistency while B values optimization, and adding each new database adds operational complexity.""",

"""If A is fully true (one database for everything):
  - Consequences: One system to operate, monitor, backup, and debug. All data in one place with ACID guarantees. Full SQL queryability across all data. BUT: search may be slower than Elasticsearch, caching may be less efficient than Redis, and the single database becomes a bottleneck and single point of failure.
  - World required: A world where PostgreSQL's extensions (full-text search, JSONB, pg_cron) adequately handle all specialized needs, where the team is small enough that operational simplicity dominates, and where no single use case requires performance beyond what PostgreSQL provides.

If B is fully true (specialized database per use case):
  - Consequences: Each use case gets optimized performance. Search is fast, caching is sub-millisecond, documents are flexible. BUT: data consistency across systems requires complex synchronization, operational burden multiplies per database, each system needs its own expertise, backup, monitoring, and failure handling.
  - World required: A world where the team has enough operational maturity to maintain 4+ database systems, where the performance requirements genuinely exceed PostgreSQL's capabilities, and where the synchronization complexity is manageable.""",

"""A's projections:
  - ASSUMES that PostgreSQL's capabilities are sufficient for all use cases. This is a projection: PostgreSQL's full-text search is adequate for many cases but NOT for faceted search, fuzzy matching, or relevance ranking at scale. The architect is projecting their familiarity with PostgreSQL onto all problem domains.
  - ASSUMES operational simplicity always outweighs optimization. This is a projection from their operational experience, not from the product's actual requirements.

B's projections:
  - ASSUMES that performance differences matter for their use cases. This is a projection: if the application serves 100 users, the difference between PostgreSQL full-text search and Elasticsearch is undetectable. They are projecting future scale onto present reality.
  - ASSUMES the team can handle the operational complexity. This is a projection: each additional database roughly doubles on-call complexity.""",

"""What survives negation: The real question is not 'one database or many?' but 'at what scale does PostgreSQL's capability boundary actually get crossed for OUR specific use cases?' This boundary is almost always FURTHER than the data team thinks (PostgreSQL is remarkably capable) but does exist for specific workloads (search relevance, sub-millisecond caching, time-series at scale).""",

"""The database debate is actually a scaling TIMELINE question. Today: PostgreSQL handles everything (the architect is right for NOW). At some measurable threshold: specific workloads will exceed PostgreSQL's capability, and specialized databases become necessary (the data team is right for LATER). The answer is: use PostgreSQL until you have EVIDENCE that a specific workload needs a specialized system. Then add THAT system for THAT workload. Not before.""",

"""- Mahavakya + assumption "we are below the capability boundary for all workloads" = A's position (PostgreSQL for everything).
- Mahavakya + assumption "we have already exceeded the boundary for search/caching workloads" = B's position (specialized databases).
Both are correct at different points on the scaling timeline. The real argument is about what point they are at NOW."""
)),

# BUSINESS STRATEGY
("Our investors want us to raise a large Series B for rapid growth. Our CFO argues we should stay lean and grow from revenue. Who is right?",
_ved(
"""A claims: Raise a large Series B to accelerate growth — capture market share before competitors.
B claims: Stay lean, grow from revenue — maintain control and build a sustainable business.
These conflict because: external capital enables fast growth but dilutes ownership and creates expectations for exit/returns, while revenue-funded growth preserves control but may be too slow in competitive markets.""",

"""If A is fully true (raise and grow fast):
  - Consequences: Hire aggressively, spend on marketing, enter new markets. Growth rate 3-5x what revenue alone supports. Investor board seats, reporting obligations, pressure for exit within 5-7 years. Dilution of founder ownership to 15-25%.
  - World required: A winner-take-all market where speed is existential, where capital IS the competitive advantage, where the company can efficiently deploy large amounts of money without waste.

If B is fully true (grow from revenue):
  - Consequences: Controlled growth at 20-50% per year. Full founder control. No board meetings, no exit pressure. BUT: competitors with capital may outpace in customer acquisition, talent hiring, and market presence.
  - World required: A market with room for multiple winners, where sustainable growth rates are sufficient, where capital is not the primary competitive dimension.""",

"""A's projections:
  - ASSUMES the market is winner-take-all. This is a projection: most markets have room for multiple players. True winner-take-all dynamics exist in network-effect businesses (social media, marketplaces) but not in most B2B SaaS.
  - ASSUMES capital can be efficiently deployed. This is a projection: history shows that rapid spending often leads to wasteful hiring, unfocused marketing, and organizational complexity that slows execution. Raising money and spending money wisely are different skills.

B's projections:
  - ASSUMES competitors' capital advantage won't be decisive. This is a projection: if a well-funded competitor achieves network effects or locks up distribution channels, the revenue-funded company may lose permanently.
  - ASSUMES revenue growth will be sufficient to capture meaningful market share. This is a projection: some markets move fast enough that 30% annual growth means falling behind.""",

"""What survives: The actual question is 'what is the competitive dynamic in our specific market?' — not a general philosophy about fundraising. The answer depends on a measurable property: whether capital deployment has increasing returns (network effects, distribution lock-in) or diminishing returns (most SaaS markets).""",

"""The fundraising debate is a proxy for a market structure question: does our market reward SPEED or SUSTAINABILITY? Markets with network effects reward speed (raise and grow fast). Markets without network effects reward sustainability (profitable growth outlasts well-funded but unprofitable competitors). The answer is not a philosophy but a market analysis.""",

"""- Mahavakya + assumption "our market has strong network effects" = A's position (raise Series B to capture network before competitors).
- Mahavakya + assumption "our market has no network effects and rewards reliability" = B's position (grow sustainably from revenue).
The debate dissolves when you empirically assess whether your market exhibits network effect dynamics."""
)),

# PERSONAL DECISIONS
("I love my job's mission but hate the management culture. My partner says I should quit for mental health. My mentor says I should stay and change the culture from within.",
_ved(
"""A claims: Stay and change the culture from within — the mission matters and your influence can improve things.
B claims: Leave for your mental health — no mission justifies chronic stress and unhappiness.
These conflict because: staying means ongoing mental health cost with uncertain culture change; leaving means losing meaningful work and the investment already made.""",

"""If A is fully true (stay and change):
  - Consequences: You spend energy on both your actual work AND political/cultural change. Results are uncertain — culture change from within requires either authority (you don't have) or critical mass of allies (uncertain). You remain in a stress-inducing environment for months or years while attempting change.
  - World required: A world where individual contributors can meaningfully change organizational culture, where management is open to feedback, where the timeline for change is tolerable for your mental health.

If B is fully true (leave for health):
  - Consequences: Immediate relief from toxic environment. Loss of meaningful work. Potential identity crisis ("I was the person working on X"). Job search stress. Possible discovery that the next job has different but equally real problems.
  - World required: A world where the mental health cost is so severe that it outweighs all benefits, where no intervention can improve the situation, where the mission can be pursued elsewhere.""",

"""A's projections:
  - ASSUMES you have the power to change culture. This is a projection from your mentor's likely senior position. Culture change requires either positional authority or collective action — individual effort rarely moves organizational culture. Your mentor may be projecting THEIR agency onto YOUR situation.
  - ASSUMES the mission requires THIS specific organization. This is a projection: missions are bigger than companies. The mission exists at other organizations, in different forms.

B's projections:
  - ASSUMES the mental health impact is caused by the culture alone. This is a projection: some of the stress may be from your response to the culture (setting insufficient boundaries, over-identifying with work). If that is the case, leaving will not fix the pattern — it will follow you to the next job.
  - ASSUMES leaving is a binary. This is a projection: there may be intermediate moves (different team, different role, reduced hours, explicit boundary-setting) that reduce the cost of staying without the cost of leaving.""",

"""What survives: The mental health cost is real (not a projection from either side). The mission's value to you is real. What is NOT real is the framing that these are connected — that you must accept this culture to pursue this mission, or that leaving this culture means abandoning this mission. The mission and the management culture are INDEPENDENT variables that have been conflated by happening to coexist in one organization.""",

"""Your mission and your employer are not the same thing. The management culture is a property of THIS ORGANIZATION, not a property of THE MISSION. Separating these two — finding the mission at an organization with healthy culture, or transforming your current role to insulate yourself from the toxic culture — are both possible paths that the binary framing obscures.""",

"""- Mahavakya + assumption "this organization is the only place to pursue this mission" = A's position (stay and tolerate/change culture).
- Mahavakya + assumption "the mental health cost of this specific culture is irreparable" = B's position (leave, find mission elsewhere).
Both collapse when you realize the mission exists in multiple organizational forms, and the culture problem may have intermediate solutions."""
)),

# SCIENTIFIC ANALYSIS
("The replication crisis: some scientists argue that failed replications prove the original findings are false. Others argue that replication failures prove nothing because contexts differ.",
_ved(
"""A claims: Failed replications demonstrate that the original findings are false — real effects replicate.
B claims: Failed replications prove nothing because no replication can perfectly recreate the original context; differences in sample, procedure, and setting explain failures.
These conflict because: if A is right, much of published science is wrong. If B is right, replication is meaningless as a quality check.""",

"""If A is fully true (failed replications prove falsity):
  - Consequences: The majority of social psychology findings, many biomedical findings, and a significant portion of behavioral economics are false. Entire research programs built on unreplicable foundations should be dismantled. Citation counts and impact factors are meaningless.
  - World required: A world where scientific effects are universal and context-independent. Where an effect that is real in one lab with one population must be equally real in any lab with any population. Where replication failure has only one explanation: the original was wrong.

If B is fully true (context differences explain all failures):
  - Consequences: No finding can ever be falsified through replication. Every failure can be attributed to some contextual difference. Science becomes unfalsifiable — which means it is not science.
  - World required: A world where every effect is completely context-dependent, where generalization is impossible, and where replication serves no quality-control function. This is the world of literary criticism, not science.""",

"""A's projections:
  - ASSUMES all replication failures have the same meaning. This is a projection: some failures are caused by original fraud or error (real falsification), some by underpowered original studies (statistical artifact), and some by genuine context dependence (the effect is real but context-bound). Treating all failures identically is epistemically sloppy.
  - ASSUMES effects must be universal to be real. This is a projection from physics (gravity works everywhere) onto sciences that study context-dependent systems (human behavior varies by culture, era, and sample).

B's projections:
  - ASSUMES context differences are sufficient explanations for ALL failures. This is a projection that makes findings unfalsifiable. If any failure can be explained by context, then no finding can ever be wrong — which violates the fundamental principle of science.
  - ASSUMES the burden of proof lies with the replicator, not the original researcher. This is a projection from the old publish-and-move-on model, where original findings are presumed correct until definitively disproven.""",

"""What survives: Some effects are genuinely context-dependent (cultural psychology, developmental timing). Some original findings are genuinely false (p-hacked, underpowered, or fabricated). The replication crisis is not a binary — it reveals that published science contains a MIXTURE of real-but-context-dependent effects, real-and-universal effects, and false effects. No single replication failure can determine which category a finding belongs to.""",

"""The replication crisis is not a crisis of TRUTH but a crisis of PRECISION. Original publications rarely specify the SCOPE CONDITIONS under which the effect holds. Replication fails not because the effect is 'false' but because the BOUNDARIES of the effect were never specified. The solution is not more replication but more precise original claims: 'this effect holds for [population] in [context] with [boundary conditions].' """,

"""- Mahavakya + assumption "the original study claimed a universal, context-free effect" = A's position (failed replication falsifies it).
- Mahavakya + assumption "the original study specified narrow scope conditions that differ from the replication" = B's position (replication failure is expected and uninformative).
The resolution: every published finding should state its scope conditions explicitly. Replication within those conditions is a valid test. Replication outside them is a different experiment."""
)),

# ETHICS
("Tech companies argue that content moderation is necessary to prevent harm. Free speech advocates argue that any moderation is censorship. What is the real issue?",
_ved(
"""A claims: Content moderation is necessary because unmoderated platforms amplify harm — harassment, misinformation, radicalization, child exploitation.
B claims: Content moderation is censorship — any authority deciding what speech is acceptable will inevitably suppress legitimate dissent and unpopular truth.
These conflict because: A prioritizes protection from harm; B prioritizes protection from authority. Both harms are real.""",

"""If A is fully true (moderation is always necessary):
  - Consequences: A team of moderators (or algorithms) determines what is acceptable speech for billions of people. The decisions are made by a private company, not a democratic process. The criteria are opaque and inconsistently applied. Different moderators in different countries apply different standards. The company becomes a de facto speech regulator with no democratic accountability.
  - World required: A world where the moderators are always right, where the criteria are always fair, where mistakes are quickly corrected, and where the power to silence is never abused.

If B is fully true (all moderation is censorship):
  - Consequences: Platforms become unusable for most people. Harassment drives away women, minorities, and vulnerable users. Coordinated misinformation campaigns operate freely. Child exploitation material proliferates. Spam overwhelms legitimate content.
  - World required: A world where speech has no real-world consequences, where harassment does not silence, where misinformation does not spread faster than truth, and where the 'marketplace of ideas' naturally selects for truth.""",

"""A's projections:
  - ASSUMES the harm from unmoderated speech is greater than the harm from moderation errors. This is a projection: moderation errors systematically suppress marginalized voices (content about racism removed as 'hate speech'), political dissent (protest content removed as 'violence'), and cultural expression (Black English flagged as 'toxic' by algorithms).
  - ASSUMES companies can make these decisions well. This is a projection: no company has demonstrated the ability to moderate content consistently, fairly, and at scale.

B's projections:
  - ASSUMES the 'marketplace of ideas' works. This is a projection from 18th-century philosophy onto 21st-century information architecture. On algorithmic platforms, the marketplace is rigged — engagement algorithms amplify the most emotionally provocative content, not the most truthful.
  - ASSUMES moderation = censorship. This is a projection: editorial decisions are not censorship. Every newspaper, bookstore, and library makes choices about what to include. The question is not whether choices are made but WHO makes them and HOW.""",

"""What survives: Both moderation AND non-moderation cause harm. The question is not 'should speech be moderated?' — ALL communication contexts have norms and rules. The question is: 'WHO sets the norms, BY WHAT PROCESS, and WITH WHAT ACCOUNTABILITY?' The current situation — private companies making opaque, unaccountable decisions about global speech — satisfies neither camp.""",

"""The content moderation debate is not about speech vs. safety. It is about GOVERNANCE. Unmoderated platforms are ungoverned commons that fall to tragedy-of-the-commons dynamics. Corporate-moderated platforms are privately governed territories with no democratic legitimacy. The real question is: what governance structure for online speech is both effective at preventing harm AND accountable to the people affected?""",

"""- Mahavakya + assumption "the platform is a private space where the owner sets rules" = A's position (moderate like a house party — the host sets norms).
- Mahavakya + assumption "the platform is a public square where government protects speech" = B's position (moderation is censorship of the public square).
Both collapse when you see that platforms are NEITHER fully private NOR fully public — they are something new that requires new governance models."""
)),

# DEBUGGING
("Our monitoring shows response times are fine (p50=200ms) but users complain the app is slow. Engineers say the metrics prove it's fast. Support says customers are frustrated. Who is right?",
_ved(
"""A claims: The app is fast — p50 response time of 200ms is well within acceptable bounds, and the metrics prove it.
B claims: The app is slow — real users are experiencing and reporting slowness, and their experience matters more than metrics.
These conflict because: objective measurements say fast while subjective experience says slow — they cannot both be right.""",

"""If A is fully true (metrics prove speed):
  - Consequences: Customer complaints are invalid — users are wrong about their own experience. Support tickets are noise. The engineering team's job is done because the numbers look good.
  - World required: A world where p50 response time is the correct and complete measure of user-perceived performance. Where the metric captures everything users experience. Where users cannot perceive differences beyond what the metric measures.

If B is fully true (users experience slowness):
  - Consequences: The metrics are lying — measuring the wrong thing or measuring correctly but incompletely. There is a gap between what is measured and what users experience that the engineering team has not identified.
  - World required: A world where user perception is the ground truth and any metric that contradicts it is by definition wrong or incomplete.""",

"""A's projections:
  - ASSUMES p50 measures user experience. Massive projection: p50 is the MEDIAN — it tells you nothing about the worst 50% of requests. If p50=200ms but p99=15,000ms, 1 in 100 requests takes 15 seconds. Users remember the slow ones, not the fast ones. p50 is a metric DESIGNED to hide outliers.
  - ASSUMES server response time = user-perceived time. Projection: the user's experience includes DNS, TLS, network, server, rendering, JavaScript hydration, and third-party scripts. Server response is one component of many.

B's projections:
  - ASSUMES all customer complaints reflect real slowness. Possible projection: some complaints may reflect UI confusion (slow-feeling interaction even if fast) or comparison to faster competitors.
  - ASSUMES the engineering metrics are 'wrong.' This is unnecessary — the metrics may be correct but measuring the wrong thing.""",

"""What survives: The users ARE experiencing something slow. The p50 metric IS accurate for what it measures. Both are true simultaneously because the metric does not capture what users experience. The metric measures server response for the median request. Users experience total page load time for the worst requests. These are DIFFERENT THINGS.""",

"""The debate between 'metrics say fast' and 'users say slow' is always resolved the same way: the metrics are measuring the wrong thing. Specifically, p50 server response time hides the two places where slowness lives: the TAIL (p95, p99 — the requests that are truly slow) and the CLIENT (rendering, hydration, third-party scripts — time the server does not see). The real question is not 'who is right?' but 'what should we be measuring?' """,

"""- Mahavakya + assumption "server p50 captures the full user experience" = A's position (app is fast).
- Mahavakya + assumption "user perception is the only truth" = B's position (app is slow).
Both resolve when you measure: (1) p95 and p99 instead of p50, (2) total page load time instead of server response, (3) Core Web Vitals (LCP, FID, CLS) instead of backend metrics."""
)),

# PROJECT PLANNING
("Our team is split on whether to estimate in story points or hours. Half says points capture complexity better. Half says hours are more honest and understandable.",
_ved(
"""A claims: Story points are superior because they measure relative complexity without the false precision of hours.
B claims: Hours are superior because they are honest, understandable, and directly map to capacity.
These conflict because: A values abstraction from time; B values direct time mapping. They are measuring fundamentally different things.""",

"""If A is fully true (story points are better):
  - Consequences: The team estimates in abstract units that capture complexity, uncertainty, and effort. Velocity (points per sprint) tracks capacity over time. Stakeholders cannot convert points to dates without historical velocity data.
  - World required: A world where the team's velocity is stable enough to be predictive, where stakeholders accept abstract units, and where the abstraction from time does not create a communication gap with business partners.

If B is fully true (hours are better):
  - Consequences: The team estimates how long each task will take. Capacity is simply available hours minus estimated hours. Stakeholders can directly understand the timeline.
  - World required: A world where developers can accurately predict how long tasks take (research shows they systematically underestimate by 25-50%), where hour estimates do not become commitments that create pressure, and where the false precision of hours does not create false confidence.""",

"""A's projections:
  - ASSUMES the abstraction of points adds value by removing time pressure. Projection: in practice, stakeholders and managers ALWAYS convert points back to time ("if velocity is 20 points/sprint and this feature is 40 points, it takes 2 sprints = 4 weeks"). The abstraction adds a conversion step without removing the time pressure.
  - ASSUMES 'complexity' is more measurable than 'time.' Projection: story point estimation sessions frequently devolve into "how long would this take?" converted to a Fibonacci number.

B's projections:
  - ASSUMES developers can estimate hours accurately. Projection contradicted by decades of research: developers consistently underestimate by 25-50%. Hour estimates feel precise but are not.
  - ASSUMES honest hour estimates will be treated as ESTIMATES, not commitments. In most organizations, an estimate of "40 hours" becomes a deadline, creating pressure that degrades both accuracy and quality.""",

"""What survives: Neither story points nor hours produces accurate estimates. The ESTIMATION METHOD is not the source of estimation error. The source is: (1) tasks are inherently uncertain, (2) humans are systematically optimistic about future effort, and (3) organizational culture converts estimates into commitments. These persist regardless of whether you say '8 points' or '40 hours.'""",

"""The estimation format debate is a proxy for a trust problem. Teams that trust each other can estimate in any unit and adjust when reality diverges from prediction. Teams without trust need 'precise' estimates as accountability tools, which corrupts the estimation process regardless of format. The real question is not 'points or hours?' but 'does our organization treat estimates as predictions (adjustable) or promises (binding)?'""",

"""- Mahavakya + assumption "estimates are treated as predictions with uncertainty" = either format works (the format is irrelevant when trust exists).
- Mahavakya + assumption "estimates are treated as promises/commitments" = both formats fail (the format cannot solve a trust problem).
The debate dissolves when you address the underlying trust dynamic."""
)),

# CREATIVE DECISIONS
("An author's first novel was a literary success but a commercial failure. Their agent advises writing something more commercial next. Their writing group says stay true to their voice.",
_ved(
"""A claims: Write something more commercial — adapt to the market to build an audience and income.
B claims: Stay true to your voice — artistic integrity is the foundation of a lasting career.
These conflict because: commercial writing and literary voice are perceived as opposing forces, and the author cannot write two novels at once.""",

"""If A is fully true (write commercial):
  - Consequences: The author studies market trends, genre conventions, and reader expectations. They write a book optimized for sales. It may sell but may feel hollow. They may attract an audience that expects more of the same, trapping them in a commercial formula. Or it may fail commercially DESPITE being written for the market, losing both artistic integrity and sales.
  - World required: A world where the author can execute commercial fiction competently (genre skills are DIFFERENT from literary skills), where market trends are predictable, and where commercial success creates a platform to return to literary work later.

If B is fully true (stay literary):
  - Consequences: The author continues developing their voice. Each novel deepens their craft but may continue to have limited commercial appeal. Financial pressure from low sales may force them to stop writing entirely or take a day job that leaves little time for writing.
  - World required: A world where artistic purity is financially sustainable, where the literary market eventually recognizes quality, and where the author can endure years of low income.""",

"""A's projections:
  - ASSUMES 'literary' and 'commercial' are fixed categories. This is a projection: many commercially successful novels are also literary (Donna Tartt, Colson Whitehead, Kazuo Ishiguro). The categories are publishing industry labels, not properties of writing.
  - ASSUMES the author CAN write commercially. Writing compelling genre fiction requires skills (pacing, plot architecture, genre awareness) that literary writers may not have. The commercial pivot may produce neither literary nor commercial quality.

B's projections:
  - ASSUMES 'voice' is static. This is a projection: every author's voice evolves. Incorporating narrative drive, accessibility, or genre elements is not betraying one's voice — it is developing it.
  - ASSUMES commercial elements diminish art. This is a projection from literary snobbery. Shakespeare was commercial. Dickens was commercial. Garcia Marquez was commercial. Narrative pleasure is not the enemy of literary depth.""",

"""What survives: The author has a voice (real). The author needs to reach readers (real). The assumption that voice and reach are opposed is the projection. What is real: a novel must be BOTH well-written (voice) AND compelling enough for people to read (reach). The tension is not between art and commerce but between the author's current balance of these two elements.""",

"""The 'literary vs. commercial' debate is a false taxonomy. The real question is: 'How do I make my literary voice ACCESSIBLE without compromising its depth?' This is a craft problem, not a market capitulation. The greatest novels (Beloved, One Hundred Years of Solitude, The Road) are both deeply literary and irresistibly compelling. The author's development task is not to choose a side but to integrate narrative drive into their existing literary voice.""",

"""- Mahavakya + assumption "accessibility requires abandoning literary depth" = A's position (go commercial, sacrifice voice).
- Mahavakya + assumption "literary depth is inherently inaccessible" = B's position (stay literary, accept limited audience).
Both collapse when you see that accessibility (compelling narrative, clear prose, emotional resonance) and literary depth (complex themes, innovative technique, psychological truth) are independent dimensions that can be developed simultaneously."""
)),

# EDUCATION
("There's a debate about whether university education should focus on practical job skills or liberal arts/critical thinking. Which is more valuable?",
_ved(
"""A claims: University should focus on practical, job-relevant skills — students need employable abilities to justify the cost.
B claims: University should focus on liberal arts and critical thinking — broad intellectual development creates more adaptable, thoughtful citizens.
These conflict because: curriculum time is limited, and every course in critical thinking is a course NOT in practical skills, and vice versa.""",

"""If A is fully true (practical skills only):
  - Consequences: Universities become vocational schools. Students learn current tools and techniques. They are immediately employable upon graduation. BUT: their skills become obsolete every 5-10 years as technology and industry change. They lack the ability to learn new domains, think across disciplines, or lead in ambiguous situations.
  - World required: A world where the skills needed today are the skills needed in 20 years. Where industry does not change. Where narrow competence is sufficient for a full career.

If B is fully true (liberal arts only):
  - Consequences: Graduates can think critically, write clearly, and reason across domains. They are adaptable and intellectually curious. BUT: they may lack specific technical skills needed for entry-level jobs. The gap between education and employment creates frustration, debt burden, and underemployment.
  - World required: A world where employers value general thinking ability over specific skills, where the transition from education to employment is supported, and where the financial cost of education does not require immediate financial return.""",

"""A's projections:
  - ASSUMES the skills taught today will be relevant throughout a career. This is a projection: the average half-life of a technical skill is 5 years. Students graduating in 2026 will work until ~2070. Teaching them 2026's tools prepares them for 10% of their career.
  - ASSUMES education's value is measured solely by employability. This is a projection from the economic model of education. Education also produces citizens, community members, and humans capable of meaning-making.

B's projections:
  - ASSUMES critical thinking ability automatically translates to employment. This is a projection: employers screen for DEMONSTRATED SKILLS, not potential. A philosophy major who can think brilliantly but cannot demonstrate any practical capability faces real employment barriers.
  - ASSUMES the liberal arts model is equitable. This is a projection: the luxury of studying philosophy without career pressure is available primarily to students from wealthy families. First-generation and lower-income students need practical skills for economic mobility.""",

"""What survives: Students need BOTH the ability to do specific work NOW and the ability to learn new work LATER. The practical vs. liberal arts debate falsely assumes these are competing time allocations when they are complementary capabilities. The best education produces someone who can DO something immediately (practical) AND LEARN anything subsequently (critical thinking).""",

"""The practical vs. liberal arts debate is a false dichotomy born from industrial-age curriculum design. The real educational challenge is not choosing between them but INTEGRATING them: teaching practical skills THROUGH critical thinking methods, and developing critical thinking THROUGH practical application. A computer science curriculum that includes philosophy of technology, or a literature curriculum that includes writing for publication, does both simultaneously.""",

"""- Mahavakya + assumption "skills and thinking are separate curriculum elements" = both A and B argue about time allocation.
- Mahavakya + assumption "skills and thinking can be developed simultaneously through integrated pedagogy" = the debate dissolves.
Project-based learning, applied philosophy, technical writing, and interdisciplinary courses all demonstrate that the integration is possible and produces better outcomes than either approach alone."""
)),

]

# Pad to 30 with additional domain coverage
_EXTRA = [
("Is remote work better for productivity or does office work produce better results?", _ved("A claims: Remote work is more productive — fewer interruptions, no commute, focused deep work.\nB claims: Office work is more productive — spontaneous collaboration, cultural cohesion, faster communication.\nThese conflict because: both cite productivity but measure different aspects of it.", "If A is fully true:\n  - Consequences: Offices close. All work is remote. Individual output increases. BUT: cross-team collaboration suffers. New employees struggle to onboard. Culture fragments. Innovation from serendipitous hallway conversations disappears.\n  - World required: All valuable work is individual deep work. Collaboration is always scheduled. Culture needs no physical reinforcement.\n\nIf B is fully true:\n  - Consequences: Everyone returns to office. Collaboration increases. BUT: commute time returns (average 52 min/day). Open office interruptions resume. Talent pool shrinks to commuting radius. Knowledge workers lose 2-4 hours of productive time to office overhead daily.\n  - World required: Collaboration and presence are always more valuable than individual focus time. Commuting has no cost. Talent is available locally.", "A's projections:\n  - ASSUMES productivity = individual output. Projection: organizational productivity includes COORDINATION, which may suffer remotely.\n  - ASSUMES deep work is always the bottleneck. Projection: for some roles, communication and alignment are the bottleneck.\n\nB's projections:\n  - ASSUMES collaboration requires physical presence. Projection from pre-digital experience. Many forms of collaboration work well asynchronously.\n  - ASSUMES 'culture' requires offices. Projection: distributed companies (GitLab, Automattic) have strong cultures without offices.", "What survives: Different types of work benefit from different environments. Individual deep work benefits from remote. Collaborative, creative, and onboarding work benefits from co-location. Neither is universally superior.", "The remote vs. office debate is the wrong question. The right question is: 'Which specific work activities benefit from co-location, and which benefit from isolation?' The answer is not one or the other but a RHYTHM: deep work time (remote) alternating with collaboration time (co-located). The organizations that thrive will not choose remote or office but will design INTENTIONAL RHYTHMS that match work type to environment.", "- Mahavakya + 'all work is similar' = either A or B depending on which work type you privilege.\n- Mahavakya + 'different work needs different environments' = hybrid with intentional design (neither A nor B as stated).")),

("Should AI systems be transparent (explainable) or is performance more important than interpretability?", _ved("A claims: AI systems must be transparent — decisions affecting people must be explainable.\nB claims: Performance is what matters — a more accurate model saves more lives/money even if unexplainable.\nThese conflict because: the most powerful models (deep learning) are least interpretable, and making them interpretable reduces performance.", "If A is fully true:\n  - Consequences: All AI decisions are explainable. Models are simpler. Biases are detectable. BUT: the best-performing models (deep neural networks) are abandoned. Medical AI that could detect cancer 5% better is rejected because it cannot explain its reasoning.\n  - World required: Humans can always understand the factors that should determine decisions. No valid decision-making process exists that exceeds human interpretive capacity.\n\nIf B is fully true:\n  - Consequences: Black-box models deployed everywhere. Decisions affecting lives, liberty, and finances are made by systems nobody understands. Biases are undetectable. Errors are unexplainable. Trust is based on aggregate statistics, not case-by-case understanding.\n  - World required: Statistical accuracy is the only criterion that matters. Individual cases where the model is wrong are acceptable collateral. Nobody affected by the decision needs or deserves an explanation.", "A's projections:\n  - ASSUMES transparency and performance are always opposed. Increasingly false: SHAP, LIME, attention visualization, and concept-based explanations provide interpretability without sacrificing model architecture.\n  - ASSUMES human-understandable explanations are always possible. Projection: some patterns in high-dimensional data may be genuinely beyond human intuition.\n\nB's projections:\n  - ASSUMES aggregate accuracy is the correct optimization target. Projection: a model that is 95% accurate but systematically wrong for a specific demographic group may be less valuable than a 90% accurate model that is fair across groups.\n  - ASSUMES people will accept unexplained decisions. Projection: people who are denied loans, medical treatment, or jobs by an unexplainable system experience real harm from the inexplicability itself.", "What survives: The tradeoff between transparency and performance exists but is smaller than either side claims. Post-hoc explanations can be added to complex models. And the NEED for transparency depends on the STAKES of the decision — low-stakes recommendations need less transparency than high-stakes medical or legal decisions.", "Transparency and performance are not opposing axes but different requirements for different STAKES. The resolution is a tiered approach: high-stakes decisions (medical, legal, financial) require explainability even at some performance cost. Low-stakes decisions (content recommendations, autocomplete) can optimize for performance. The real question is not 'transparent or performant?' but 'what are the stakes, and what level of explanation do those stakes demand?'", "- Mahavakya + 'all AI decisions have equal stakes' = either A or B dominates.\n- Mahavakya + 'stakes vary by application' = tiered transparency requirements (the resolution).")),

("Is it better to specialize deeply in one skill or develop a broad range of capabilities?", _ved("A claims: Specialize — depth creates irreplaceable expertise and commands premium compensation.\nB claims: Generalize — breadth creates adaptability and enables cross-domain innovation.\nThese conflict because: time invested in depth cannot be invested in breadth, and careers reward one pattern over the other at different stages.", "If A is fully true:\n  - Consequences: You become the world expert in a narrow domain. Irreplaceable within that domain. BUT: if the domain shrinks (technology change, market shift), your expertise becomes obsolete. You lack the ability to see connections across domains.\n  - World required: Domains are stable. Expertise in one area is always in demand. Cross-domain innovation is not important.\n\nIf B is fully true:\n  - Consequences: You can work across many domains. Adaptable to change. See connections others miss. BUT: you are never the best at any one thing. Competing against specialists in any domain, you lose.\n  - World required: No domain requires deep expertise. Cross-domain connections are more valuable than depth. Jack-of-all-trades is better than master of one.", "A's projections:\n  - ASSUMES domain stability. In a rapidly changing world, specialized knowledge has a half-life. The projection is from stable-career eras.\n\nB's projections:\n  - ASSUMES breadth is sufficient for impact. Most breakthroughs require DEEP knowledge of at least one domain before cross-pollination becomes valuable.", "What survives: Both depth and breadth are necessary, but they operate on different timescales. DEPTH is how you become capable. BREADTH is how you become innovative. The question is not 'which?' but 'in what sequence?'", "The specialization vs. generalization debate dissolves into a SEQUENCING question. Develop depth first — become genuinely excellent at one thing. Then develop breadth — apply that deep expertise to adjacent domains. This is the 'T-shaped' professional: deep in one area, broad across many. The SEQUENCE matters: breadth without depth produces superficiality, but depth without breadth produces tunnel vision. Depth first, then breadth.", "- Mahavakya + 'career is early stage' = A's position (specialize, build foundation).\n- Mahavakya + 'career is established with deep expertise' = B's position (broaden, cross-pollinate).\nBoth are correct advice for different career stages.")),

]

for item in _EXTRA:
    _DATA.append(item)

# Additional brief examples to reach 30
_MORE = [
("Agile vs Waterfall for software development — which methodology is correct?", _ved("A claims: Agile (iterative, flexible, responsive to change) is superior.\nB claims: Waterfall (planned, sequential, predictable) is superior.\nThese conflict because: Agile values adaptation over planning; Waterfall values planning over adaptation.", "If A fully true: All projects iterate. No upfront planning. Flexible but potentially chaotic. World requires: all requirements are discoverable only through building.\nIf B fully true: All projects planned upfront. Sequential execution. Predictable but rigid. World requires: all requirements are knowable before building.", "A projects uncertainty onto all projects. B projects certainty onto all projects. Both are wrong: some requirements are known (regulatory, infrastructure) and some are unknown (user preferences, market fit).", "What survives: the degree of requirement uncertainty. High uncertainty → Agile. Low uncertainty → Waterfall. Most projects have BOTH known and unknown components.", "Agile vs. Waterfall is not a methodology choice but a CERTAINTY classification. The question is: 'What percentage of requirements are known vs. unknown?' Known requirements can be planned (waterfall those). Unknown requirements must be discovered (iterate on those). Most real projects need hybrid: plan the known, iterate the unknown.", "Mahavakya + 'most requirements are unknown' = Agile. Mahavakya + 'most requirements are known' = Waterfall. Both are correct for their certainty level.")),
("Is it better to have a few deep friendships or many acquaintances?", _ved("A: Deep friendships provide emotional support, vulnerability, and meaning.\nB: Many acquaintances provide diverse perspectives, opportunities, and social capital.\nConflict: Relationship depth requires time investment that prevents breadth.", "If A fully true: A few close friends. Deep intimacy. BUT: limited perspectives, small support network, vulnerable to loss of any one friend.\nIf B fully true: Large network. Many connections. BUT: no one truly knows you. No vulnerability possible. Loneliness in a crowd.", "A projects that all relationship value comes from depth. False: weak ties (Granovetter) provide most career opportunities and novel information.\nB projects that all relationship value comes from breadth. False: mental health and belonging require at least 3-5 close relationships (Dunbar research).", "What survives: humans need BOTH — a small inner circle (3-5 deep relationships) and a larger outer circle (diverse acquaintances). These serve DIFFERENT functions and are not substitutable.", "Friendships operate in concentric circles, each serving a distinct function. The inner circle (3-5 people): provides emotional sustenance, vulnerability, and belonging. The middle circle (15-30): provides regular companionship. The outer circle (100-300): provides information, opportunities, and perspectives. Optimizing any one circle at the expense of others creates specific deficits.", "Mahavakya + 'all relationship needs are emotional' = A. Mahavakya + 'all relationship needs are instrumental' = B. Both are partial views of a multi-layered system.")),
("Should we optimize our product for power users or new users?", _ved("A: Power users drive revenue and retention. Optimize for their advanced needs.\nB: New users determine growth. Optimize for onboarding and simplicity.\nConflict: Features for power users add complexity that confuses new users. Simplicity for new users frustrates power users.", "If A fully true: Product becomes powerful but intimidating. Existing users love it; new user activation plummets. Growth stalls.\nIf B fully true: Product is simple and accessible. New users activate easily BUT power users outgrow it and churn to competitors.", "A projects current user base as the permanent user base. B projects growth as always dependent on new user acquisition.\nBoth assume ONE product experience for ALL users.", "What survives: the product serves users at DIFFERENT stages of a journey. Each stage needs a different experience. This is not a tradeoff — it is a DESIGN problem.", "The power user vs. new user debate is solved by progressive disclosure: show simple capabilities by default, reveal advanced features as users grow. The product is not one experience but a SPECTRUM of experiences. The question is not 'optimize for whom?' but 'how does the product grow with the user?'", "Mahavakya + 'one experience for all' = forced choice between A and B. Mahavakya + 'experience adapts to user stage' = both solved through progressive disclosure.")),
("Is failure a necessary part of learning or should we design systems to prevent failure?", _ved("A: Failure teaches through experience. Systems should allow safe failure.\nB: Failure is costly and preventable. Good design eliminates failure modes.\nConflict: allowing failure risks real harm; preventing failure removes learning opportunities.", "If A fully true: All failures are tolerated. Learning maximized but harm unchecked. Some failures (medical, financial) are genuinely catastrophic.\nIf B fully true: All failures prevented. Systems are safe but brittle — no one knows how to handle the failures that inevitably occur despite prevention.", "A projects all failure as 'learning opportunity.' Some failures destroy rather than teach. B projects all failure as preventable. Complex systems fail in unpredictable ways; prevention is never complete.", "What survives: failure SEVERITY determines the correct approach. Low-severity failures should be allowed (and learned from). High-severity failures should be prevented (but with trained recovery for when prevention fails).", "Failure policy is a function of failure COST. Low-cost domains (learning, experimentation, iteration): make failure cheap, frequent, and informative. High-cost domains (medicine, aviation, nuclear): prevent failure aggressively AND train for recovery because prevention alone is insufficient. The question is not 'allow or prevent failure?' but 'what is the cost of failure in this context?'", "Mahavakya + 'failure is always low-cost' = A. Mahavakya + 'failure is always high-cost' = B. Both are correct within their cost domains.")),
("Should we prioritize customer acquisition or customer retention?", _ved("A: Acquire new customers — growth comes from expanding the customer base.\nB: Retain existing customers — retention drives profitability (5x cheaper than acquisition).\nConflict: resources spent on acquisition cannot be spent on retention.", "If A fully true: Always acquiring. Leaky bucket — customers come in and leave. High CAC, low LTV. Growth without profitability.\nIf B fully true: Focus only on existing customers. Satisfaction maximized but market share stagnates. Eventually the addressable market within current base is exhausted.", "A projects growth as the primary metric. Growth without retention is a Ponzi scheme. B projects that current customers represent the full opportunity. Without acquisition, the business has no future scale.", "What survives: the optimal strategy depends on CHURN RATE. If churn is high, fix retention first (you're filling a leaky bucket). If churn is low, invest in acquisition (the bucket holds water).", "Acquisition vs. retention is not a strategic choice but a DIAGNOSTIC response. Measure churn first. High churn (>5% monthly): retention is the emergency — every acquired customer leaks out. Low churn (<2% monthly): the product is working; scale acquisition to fill a bucket that holds. The metric determines the strategy, not the other way around.", "Mahavakya + 'churn is high' = B (fix retention first). Mahavakya + 'churn is low' = A (invest in acquisition). The debate resolves to a single metric.")),
("Is consensus-based decision making better than top-down authority?", _ved("A: Consensus produces better decisions through diverse input and buy-in.\nB: Top-down authority produces faster decisions and clearer accountability.\nConflict: consensus is slow but inclusive; authority is fast but may miss information.", "If A fully true: Every decision requires agreement. Slow. Lowest-common-denominator outcomes. Decision paralysis on contested issues.\nIf B fully true: One person decides everything. Fast. BUT: single point of failure. Decisions miss crucial information. Team disengagement.", "A projects that more input always improves decisions. Diminishing returns: beyond 3-5 informed perspectives, more input adds noise not signal.\nB projects that speed is always more valuable than quality. For irreversible decisions, speed can be catastrophic.", "What survives: DECISION REVERSIBILITY determines the correct model. Reversible decisions should be made fast (authority). Irreversible decisions should be made carefully (consensus).", "Decision-making style should vary by decision type, not be a fixed organizational philosophy. Jeff Bezos's framework: Type 1 decisions (irreversible, high-stakes) → deliberate, inclusive. Type 2 decisions (reversible, low-stakes) → fast, delegated. Most organizations fail by treating all decisions as Type 1 (too slow) or all as Type 2 (too reckless).", "Mahavakya + 'this decision is irreversible' = A (consensus). Mahavakya + 'this decision is reversible' = B (authority). Match method to decision type.")),
]

_MORE2 = [
("Strict typing vs dynamic typing — which produces better software?", _ved("A: Strict typing catches bugs at compile time and serves as documentation.\nB: Dynamic typing enables rapid prototyping and reduces boilerplate.\nConflict: type annotations add safety but also add development overhead.", "If A fully true: Every variable typed. Bugs caught early. Refactoring is safe. BUT: prototyping is slow. Experimentation is costly. Types add ceremony.\nIf B fully true: No types. Maximum flexibility. BUT: runtime errors, difficult refactoring, unclear interfaces at scale.", "A projects that all bugs are type-related. Most bugs are LOGIC errors that types cannot catch.\nB projects that types only catch trivial errors. Types also enable tooling (autocomplete, refactoring, documentation) that improves productivity.", "What survives: the value of types scales with codebase size and team size. Solo developer on a prototype: types add overhead without proportional benefit. 50-person team on a multi-year project: types are essential infrastructure.", "The typing debate is a SCALE question. Types are documentation that scales. For small codebases and single developers, the documentation overhead exceeds its value. For large codebases and teams, the documentation IS the value. The answer is not 'types or no types' but 'at what scale do types pay for themselves?' — typically around 5,000 lines or 3+ developers.", "Mahavakya + 'small codebase, solo developer' = B (dynamic, prototype fast). Mahavakya + 'large codebase, multi-developer' = A (types as infrastructure).")),

("Testing: write tests first (TDD) or write tests after implementation?", _ved("A: TDD — tests first drive better design and catch bugs earlier.\nB: Test-after — understand the implementation before specifying tests.\nConflict: each approach optimizes for a different type of confidence.", "If A fully true: Every line of code is preceded by a test. Design emerges from test requirements. BUT: tests may lock in premature design. Exploratory coding is impossible.\nIf B fully true: Implement first, test after. Natural exploration. BUT: tests are often skipped when 'it already works.' Code is not designed for testability.", "A projects that tests are primarily for DESIGN guidance. For many developers, tests are primarily for REGRESSION protection — and you don't need TDD for that.\nB projects that you can always add tests later. In practice, untested code rarely gets tested after the fact — the economic incentive disappears once 'it works.'", "What survives: the real value of testing is not WHEN tests are written but WHETHER tests exist that prevent regression. TDD and test-after are both valid paths to the same destination: a codebase where changes can be made confidently.", "The TDD vs. test-after debate is about WHEN confidence is established, not WHETHER it exists. TDD establishes confidence before writing code. Test-after establishes confidence after. Both produce tested code. The real enemy is not 'wrong testing approach' but 'no testing at all.' The unasked question: 'is this team writing ANY tests?' If not, the TDD debate is academic.", "Mahavakya + 'the team doesn't write tests at all' = both A and B are irrelevant until the habit exists. Mahavakya + 'the team has a testing culture' = either approach works.")),

("Should we optimize for developer experience (DX) or user experience (UX)?", _ved("A: DX — happy developers build better products faster.\nB: UX — users pay the bills; their experience is the only thing that matters.\nConflict: DX improvements (better tools, cleaner code) don't always directly improve UX.", "If A fully true: All investment goes to DX. Developer productivity soars. BUT: if the product doesn't serve users, productivity at building the wrong thing is waste.\nIf B fully true: All investment goes to UX. Users love the product. BUT: developer friction slows iteration, bugs accumulate, and eventually UX degrades because the codebase cannot support improvements.", "A projects that DX improvements automatically translate to UX improvements. Not always: the best developer tools can produce terrible user experiences if no one is measuring UX.\nB projects that UX can be maintained without DX investment. Unsustainable: over time, developer friction creates the bugs and slowness that degrade UX.", "What survives: DX and UX are not competing investments but different time horizons of the SAME investment. DX determines how fast UX can improve. UX determines whether DX investment produces value.", "DX is the VELOCITY of UX improvement. A team with excellent DX can iterate on UX quickly: deploy daily, test with users weekly, fix bugs in hours. A team with terrible DX iterates slowly regardless of how much they care about UX. The question is not 'DX or UX?' but 'is our current DX sufficient to iterate on UX at the speed the market demands?'", "Mahavakya + 'DX is already good enough' = invest in UX directly. Mahavakya + 'DX is so bad it prevents UX iteration' = invest in DX as a prerequisite to UX.")),

("Is it better to be data-driven or intuition-driven in decision making?", _ved("A: Data-driven — decisions based on evidence reduce bias and improve outcomes.\nB: Intuition-driven — experienced judgment captures patterns that data misses.\nConflict: data can be misleading; intuition can be biased. Both can fail.", "If A fully true: Every decision requires data. Analysis paralysis on novel decisions where no data exists. Over-reliance on measurable metrics ignores unmeasurable but important factors.\nIf B fully true: Gut feeling guides all decisions. Fast but prone to cognitive biases (confirmation bias, anchoring, recency). Cannot be audited or improved.", "A projects that all important variables are measurable. Many crucial business factors (team morale, customer trust, brand perception) are difficult to quantify precisely.\nB projects that intuition is reliable. Kahneman's research shows intuition is reliable ONLY in 'kind' learning environments with fast feedback. In 'wicked' environments (most business decisions), intuition systematically fails.", "What survives: the value of data depends on whether the RELEVANT VARIABLES are measurable and whether HISTORICAL PATTERNS predict the future. The value of intuition depends on whether the decision-maker has relevant pattern-matching experience in this domain.", "Data and intuition are not opposing epistemologies but COMPLEMENTARY signal types. Data captures what is measurable and patterned. Intuition captures what is unmeasurable and novel. The best decisions use data to inform intuition and intuition to question data. The real question is: 'which signal is more reliable for THIS SPECIFIC decision?'", "Mahavakya + 'relevant variables are measurable and historical' = data-driven (A). Mahavakya + 'decision is novel and key variables are unmeasurable' = intuition-driven (B), with explicit bias checks.")),

("Startup: should we chase revenue or chase product perfection?", _ved("A: Revenue first — the market validates through payment.\nB: Product perfection — build something great and revenue follows.\nConflict: revenue pressure leads to shortcuts; perfection delays launch indefinitely.", "If A fully true: Ship anything, monetize fast. Revenue grows but product is mediocre. Churn is high. Growth requires constantly acquiring new customers to replace lost ones.\nIf B fully true: Perfect product, never shipped. Runway runs out. The perfect product dies without ever reaching a user.", "A projects that any revenue validates the product. Revenue from desperation (customers with no alternatives) does not validate product quality.\nB projects that quality is recognizable and will attract customers. Most products fail not from bad quality but from never reaching users.", "What survives: the product must be good enough to retain users who try it, AND it must actually reach users. Neither quality alone (no distribution) nor distribution alone (no retention) produces a viable business.", "Revenue and product quality are not competing priorities — they are a SEQUENCE. First: build something good enough that early users retain (quality threshold). Then: acquire users who pay (revenue). The debate is actually about where you are in this sequence. Before the quality threshold: investing in revenue is premature. After the quality threshold: investing in more quality delays revenue unnecessarily.", "Mahavakya + 'users try the product but don't stay' = product quality problem (B's priority). Mahavakya + 'users who try the product love it but nobody knows about it' = distribution/revenue problem (A's priority). The retention rate determines which is correct.")),

("Should companies hire for culture fit or culture add?", _ved("A: Culture fit — hire people who share values and work style for team cohesion.\nB: Culture add — hire people who bring NEW perspectives for diversity and innovation.\nConflict: fit maximizes cohesion; add maximizes diversity. Both are valuable.", "If A fully true: Everyone is similar. High cohesion, low conflict. BUT: groupthink, blind spots, homogeneity, inability to serve diverse markets.\nIf B fully true: Maximum diversity. New perspectives. BUT: constant friction, communication overhead, difficulty building shared practices.", "A projects that shared values require shared backgrounds. False: people from different backgrounds can share values while bringing different perspectives.\nB projects that any difference is an 'add.' Not all differences are relevant to the work or the team's gaps.", "What survives: teams need SHARED VALUES (how we treat each other, what we optimize for) AND DIVERSE PERSPECTIVES (how we see problems, what we notice). These are independent dimensions.", "Culture fit and culture add are not opposing axes but DIFFERENT DIMENSIONS. Hire for shared values (integrity, work ethic, communication standards) AND for diverse perspectives (different experiences, thinking styles, domain backgrounds). A candidate who shares your values but brings a different perspective is both a 'fit' and an 'add.' A candidate who doesn't share your values is a bad hire regardless of their perspective.", "Mahavakya + 'values and perspectives are the same thing' = forced choice between A and B. Mahavakya + 'values and perspectives are independent' = hire for both simultaneously.")),

("Move fast and break things vs. measure twice, cut once?", _ved("A: Move fast — speed wins in competitive markets. Fix mistakes later.\nB: Measure twice — prevention is cheaper than repair. Do it right the first time.\nConflict: speed creates mistakes; caution creates delays.", "If A fully true: Maximum speed. Many mistakes. Some mistakes are catastrophic and unfixable (data loss, trust violation, legal liability).\nIf B fully true: Maximum caution. Few mistakes. Competitors who move faster capture the market while you are still measuring.", "A projects that all mistakes are reversible and cheap. Some mistakes (security breaches, data deletion, regulatory violations) are irreversible and expensive.\nB projects that caution always prevents mistakes. Overthinking can cause mistakes too — analysis paralysis leads to missed market windows.", "What survives: REVERSIBILITY of the action determines the correct speed. Reversible actions (UI changes, A/B tests, feature flags) should be fast. Irreversible actions (data migration, security architecture, public commitments) should be careful.", "Speed and caution are not personality traits or company cultures — they are CONTEXT-DEPENDENT responses to action reversibility. The same team should move fast on reversible decisions and slow on irreversible ones. The company that does both outperforms companies that are uniformly fast (reckless) or uniformly slow (cautious).", "Mahavakya + 'this action is easily reversible' = A (move fast). Mahavakya + 'this action is irreversible or high-cost' = B (measure twice). Same team, same day, different decisions.")),

("Individual accountability vs team responsibility in software development?", _ved("A: Individual accountability — each person owns their code and is responsible for its quality.\nB: Team responsibility — the team collectively owns the codebase and shares responsibility.\nConflict: individual accountability creates blame culture; team responsibility diffuses accountability.", "If A fully true: Each developer owns specific modules. Clear accountability. BUT: silos form. Knowledge is concentrated. Collaboration suffers. When the 'owner' leaves, the module becomes unmaintainable.\nIf B fully true: Shared ownership. No silos. BUT: 'everyone's responsibility' becomes 'no one's responsibility.' Tragedy of the commons in code quality.", "A projects that quality comes from individual pride of ownership. But pride of ownership can become territorial gatekeeping that resists change.\nB projects that shared responsibility creates shared commitment. But without individual assignment, specific tasks may be neglected.", "What survives: effective teams need BOTH — clear individual ASSIGNMENTS (who is working on what right now) with collective OWNERSHIP (anyone can and should improve any code). The distinction is between assignment (temporary, task-specific) and ownership (permanent, domain-wide).", "Individual accountability and team ownership are not contradictory but operate at DIFFERENT GRANULARITIES. Tasks are individually assigned (accountability for execution). The codebase is collectively owned (responsibility for quality). A developer is accountable for completing their assigned task well AND responsible for improving any code they encounter. The failure mode is confusing these levels.", "Mahavakya + 'accountability means permanent ownership of code modules' = silos (bad). Mahavakya + 'accountability means responsibility for task completion within shared ownership' = healthy team (good).")),

("Is technical writing or verbal communication more important for engineers?", _ved("A: Writing — async, scalable, permanent record, forces clear thinking.\nB: Verbal — faster, builds relationships, allows real-time clarification.\nConflict: time spent writing is time not spent talking, and vice versa.", "If A fully true: All communication is written. Decisions are documented. Knowledge is searchable. BUT: misunderstandings persist because text lacks tone. Relationships suffer. Quick clarifications become long email threads.\nIf B fully true: All communication is verbal. Fast. Relationship-rich. BUT: nothing is documented. Decisions are forgotten. New team members cannot access historical context.", "A projects that clarity comes from writing. Sometimes the clearest communication is a 5-minute conversation that would take 30 minutes to write.\nB projects that verbal is always faster. Verbal communication does not scale: telling 50 people something individually takes 50x the time of one written document.", "What survives: writing and speaking serve DIFFERENT functions. Writing is for PERMANENT, SCALABLE communication (decisions, architecture, processes). Speaking is for EPHEMERAL, RELATIONAL communication (brainstorming, conflict resolution, rapid clarification).", "The question is not 'which is more important?' but 'what type of communication is this?' Decisions that affect the future: WRITE (so future-you and future-teammates can reference them). Ideas in progress: SPEAK (so you can iterate quickly). The engineer who writes decisions and speaks ideas outperforms both the engineer who writes everything (slow) and the engineer who speaks everything (nothing documented).", "Mahavakya + 'this communication needs to be referenced later' = write it (A). Mahavakya + 'this communication is exploratory and immediate' = say it (B).")),

("Is premature optimization the root of all evil, as Knuth said, or should we always write optimized code?", _ved("A: Premature optimization is wasteful — write clear code first, optimize only bottlenecks.\nB: Write optimized code from the start — performance is a feature, not an afterthought.\nConflict: optimizing everything is expensive; optimizing nothing leads to slow systems.", "If A fully true: All code is written for clarity. Optimization deferred until profiling shows bottlenecks. BUT: some performance problems are architectural and cannot be fixed by optimizing hot spots — they require fundamental redesign.\nIf B fully true: Every function is optimized. Code is fast but difficult to read, modify, and debug. Development is slow because optimization adds complexity to every change.", "A projects that optimization can always be added later. ARCHITECTURAL performance decisions (data structure choice, database schema, caching strategy) cannot be easily retrofitted. MICRO-optimizations (loop unrolling, bit manipulation) can.\nB projects that all performance matters equally. In most systems, 1% of the code accounts for 99% of execution time. Optimizing the other 99% of code has no measurable effect.", "What survives: there are TWO types of optimization: ARCHITECTURAL (must be decided early — data model, algorithm choice, caching strategy) and MICRO (can be deferred — specific implementation details). Knuth's warning applies to micro-optimization, not architectural decisions.", "Knuth's full quote is: 'We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%.' The resolution is IN the original quote: architectural performance decisions (the 3%) should be made early. Micro-optimizations (the 97%) should be deferred until profiling proves they matter.", "Mahavakya + 'this is an architectural decision' = optimize early (B — data model, algorithm, caching are hard to change). Mahavakya + 'this is an implementation detail' = clarity first, optimize if profiling demands (A).")),
]

for item in _MORE:
    _DATA.append(item)
for item in _MORE2:
    _DATA.append(item)
