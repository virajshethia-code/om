"""Mimamsa training examples — 30 text-to-action hermeneutics examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "mimamsa"

def generate_mimamsa_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples

def _mim(table: str, vidhis: str, ambiguity: str, nishedha: str,
         mantras: str, deps: str, execution: str) -> str:
    return f"""SENTENCE CLASSIFICATION TABLE:
{table}

VIDHI DECOMPOSITION:
{vidhis}

AMBIGUITY RESOLUTION (Shadlinga):
{ambiguity}

NISHEDHA (Prohibitions):
{nishedha}

MANTRAS (Non-negotiable Terms):
{mantras}

DEPENDENCY GRAPH:
{deps}

EXECUTION SEQUENCE:
{execution}"""

_DATA: List[tuple] = [

# SOFTWARE ENGINEERING
("Parse the following requirement: 'The system must authenticate users via OAuth 2.0 before granting access to any protected resource. Session tokens must expire after 30 minutes of inactivity. Admins can extend session duration. The system should never store passwords in plaintext.'",
_mim(
"""| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "The system must authenticate users via OAuth 2.0" | VIDHI | Core injunction — mandatory authentication method |
| 2 | "before granting access to any protected resource" | VIDHI | Temporal constraint — auth BEFORE access |
| 3 | "Session tokens must expire after 30 minutes of inactivity" | VIDHI | Automatic expiration requirement |
| 4 | "Admins can extend session duration" | VIDHI | Permission grant for admin override |
| 5 | "The system should never store passwords in plaintext" | NISHEDHA | Security prohibition |""",

"""V1: "authenticate users via OAuth 2.0"
  Agent: The authentication service | Action: Authenticate | Object: All user requests to protected resources | Condition: Always, before any protected resource access
  Type: Utpatti-vidhi (a new authentication capability must be CREATED)

V2: "before granting access to any protected resource"
  Agent: The authorization middleware | Action: Block | Object: All requests to protected endpoints | Condition: Until authentication succeeds
  Type: Prayoga-vidhi (SEQUENCE — authentication must occur before authorization)

V3: "Session tokens must expire after 30 minutes of inactivity"
  Agent: The session management service | Action: Invalidate | Object: Session tokens | Condition: When no user activity detected for 30 minutes
  Type: Utpatti-vidhi (automatic expiration mechanism must be CREATED)

V4: "Admins can extend session duration"
  Agent: Admin users via admin API | Action: Modify | Object: Session expiration timer for any user | Condition: Only when invoked by authenticated admin
  Type: Viniyoga-vidhi (existing session mechanism is APPLIED differently for admin use case)""",

"""- Ambiguity: Does "30 minutes of inactivity" mean no HTTP requests, or no user-initiated actions? Background API polling could reset the timer.
  - Mark applied: Phala (result) — The desired result is security (forcing re-authentication for inactive users). Background polling does not indicate active user presence.
  - Resolution: "Inactivity" means no user-initiated actions (clicks, form submissions, navigation). Background heartbeats and polling do not reset the timer.

- Ambiguity: "Admins can extend session duration" — extend for individual sessions or change the default for all users?
  - Mark applied: Yukti (logical consistency) — If admins change the default, it conflicts with V3's explicit "30 minutes." Per-session extension is consistent with V3 remaining the default.
  - Resolution: Admins can extend specific user sessions, not change the default 30-minute policy.""",

"""N1: Do NOT store passwords in plaintext — because this enables mass credential theft if the database is breached. Implies: passwords must be hashed with a strong algorithm (bcrypt, Argon2) with per-user salt.
N2: (Implied) Do NOT grant access to protected resources without completed authentication — derived from V1 and V2's combined force.""",

"""M1: "OAuth 2.0" — defined as the authorization framework specified in RFC 6749. Non-negotiable: must be OAuth 2.0 specifically, not a custom auth scheme or OAuth 1.0.
M2: "30 minutes" — defined as the exact inactivity timeout. Non-negotiable: not "approximately 30 minutes" or "configurable."
M3: "protected resource" — defined as any API endpoint or page that requires authentication. Must be explicitly listed or defined by a route-level annotation.""",

"""V1 (OAuth implementation) → V2 (middleware enforcement) → V3 (session management)
V4 depends on V3 (cannot extend what doesn't exist)
N1 is independent (can be done in parallel)
Critical path: V1 → V2 → V3 → V4""",

"""1. [V1] Auth service IMPLEMENT OAuth 2.0 authentication flow — Always required
2. [N1] Security team HASH all stored passwords with bcrypt/Argon2 — Parallel with V1
3. [V2] Backend team ADD authentication middleware to all protected routes — After V1 complete
4. [V3] Session service IMPLEMENT 30-minute inactivity expiration — After V1 complete (parallel with V2)
5. [V4] Admin API EXPOSE session extension endpoint — After V3 complete
6. Integration testing: verify V2 blocks unauthenticated requests, V3 expires correctly, V4 admin override works"""
)),

("Parse this product brief: 'We are launching a premium tier for our SaaS product. Current free users should be notified via email. The premium tier includes unlimited storage and priority support. Free users retain their current features but cannot access premium features. Pricing is $49/month. We need this live by Q3.'",
_mim(
"""| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "We are launching a premium tier for our SaaS product" | ARTHAVADA | Context — explains what is happening but is not itself an action |
| 2 | "Current free users should be notified via email" | VIDHI | Communication requirement |
| 3 | "The premium tier includes unlimited storage" | MANTRA | Feature definition — non-negotiable specification |
| 4 | "and priority support" | MANTRA | Feature definition |
| 5 | "Free users retain their current features" | VIDHI | Backward compatibility requirement |
| 6 | "but cannot access premium features" | NISHEDHA | Access restriction |
| 7 | "Pricing is $49/month" | MANTRA | Non-negotiable price point |
| 8 | "We need this live by Q3" | VIDHI | Deadline constraint |""",

"""V1: "Current free users should be notified via email"
  Agent: Marketing/email system | Action: Send notification email | Object: All current free-tier users | Condition: Before or at launch
  Type: Prayoga-vidhi (must happen in specific SEQUENCE — at or before launch)

V2: "Free users retain their current features"
  Agent: Backend/product team | Action: Preserve | Object: All existing free-tier feature access | Condition: Always, through and after premium launch
  Type: Viniyoga-vidhi (existing system APPLIED to ensure no regression)

V3: "We need this live by Q3"
  Agent: Entire product team | Action: Deploy | Object: Complete premium tier system | Condition: By end of Q3
  Type: Prayoga-vidhi (TEMPORAL sequence — all work must complete before deadline)""",

"""- Ambiguity: "unlimited storage" — truly unlimited or "unlimited within fair use"?
  - Mark applied: Yukti (logical consistency) — Truly unlimited storage at $49/month is financially unsustainable if abused. Industry standard for "unlimited" includes fair use clause.
  - Resolution: Implement as very high limit (e.g., 10TB) with monitoring for abuse, presented as "unlimited" to users.

- Ambiguity: "priority support" — faster response times? Dedicated agent? 24/7 availability?
  - Mark applied: Apurvata (novelty) — What is NEW here versus free tier? Free tier likely has email-only support. Premium "priority" must be distinguishably better.
  - Resolution: Define as: 4-hour response time (vs. 24-hour for free), dedicated support queue, phone/chat access (vs. email-only).""",

"""N1: Free users CANNOT access premium features — enforced at the API level, not just UI. Must be server-side enforcement to prevent bypass.
N2: (Implied) Do NOT degrade existing free-tier features during premium launch — derived from V2.""",

"""M1: "$49/month" — exact price, non-negotiable per the brief
M2: "unlimited storage" — premium storage offering (resolved to high-limit implementation)
M3: "priority support" — premium support tier
M4: "Q3" — deadline (end of quarter)""",

"""V2 (preserve free features) — independent, start immediately
Storage system upgrade → Premium feature gate → Billing integration ($49/month)
V1 (email notification) → depends on premium being ready (sent at launch)
V3 (Q3 deadline) — constrains all
Critical path: Storage upgrade → Feature gate → Billing → Launch email""",

"""1. [V2] Backend team AUDIT all free-tier features to ensure preservation — Week 1
2. [M2] Infrastructure team UPGRADE storage system for premium unlimited tier — Weeks 1-4
3. [N1] Backend team IMPLEMENT feature gate: server-side access control for premium features — Weeks 3-6
4. [M1] Billing team INTEGRATE Stripe/payment for $49/month subscription — Weeks 4-8
5. [V1] Marketing team DESIGN and QUEUE notification emails for free users — Weeks 6-8
6. [V3] All teams DEPLOY complete premium system to production — Before Q3 end
7. [V1] Marketing SEND notification emails — At launch"""
)),

("Parse this legal clause: 'The Licensee shall not sublicense, assign, or otherwise transfer the Licensed Material without the prior written consent of the Licensor. In the event of unauthorized transfer, the Licensor may terminate this Agreement immediately and seek damages. The Licensee shall indemnify the Licensor against any third-party claims arising from the Licensee's use of the Licensed Material.'",
_mim(
"""| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "The Licensee shall not sublicense" | NISHEDHA | Prohibition on sublicensing |
| 2 | "assign" | NISHEDHA | Prohibition on assignment |
| 3 | "or otherwise transfer the Licensed Material" | NISHEDHA | Catch-all prohibition on any form of transfer |
| 4 | "without the prior written consent of the Licensor" | VIDHI | Exception condition — consent can override prohibition |
| 5 | "In the event of unauthorized transfer" | ARTHAVADA | Conditional context for consequences |
| 6 | "the Licensor may terminate this Agreement immediately" | VIDHI | Licensor's termination right (permissive, not mandatory) |
| 7 | "and seek damages" | VIDHI | Licensor's right to pursue legal remedies |
| 8 | "The Licensee shall indemnify the Licensor" | VIDHI | Mandatory indemnification obligation |
| 9 | "against any third-party claims arising from the Licensee's use" | VIDHI | Scope of indemnification |""",

"""V1: "prior written consent of the Licensor"
  Agent: Licensee (requesting) + Licensor (granting) | Action: Obtain written consent | Object: Any proposed sublicense, assignment, or transfer | Condition: BEFORE any transfer occurs
  Type: Prayoga-vidhi (SEQUENCE — consent before transfer, not after)

V2: "the Licensor may terminate this Agreement immediately"
  Agent: Licensor | Action: Terminate | Object: The License Agreement | Condition: Upon discovery of unauthorized transfer
  Type: Viniyoga-vidhi (existing termination mechanism APPLIED to specific trigger)

V3: "seek damages"
  Agent: Licensor (via legal counsel) | Action: Pursue legal remedy | Object: Financial damages from unauthorized transfer | Condition: Concurrent with or after termination
  Type: Viniyoga-vidhi (existing legal remedy APPLIED)

V4: "Licensee shall indemnify the Licensor against third-party claims"
  Agent: Licensee | Action: Defend and hold harmless | Object: All costs, damages, and legal fees from third-party claims | Condition: Whenever third-party claims arise from Licensee's use
  Type: Utpatti-vidhi (a new obligation CREATED — indemnification commitment)""",

"""- Ambiguity: "prior written consent" — does email count as "written"?
  - Mark applied: Yukti (logical consistency) — Modern contract practice increasingly accepts email as written communication. However, the formal "written consent" language suggests a signed document.
  - Resolution: Conservatively interpret as requiring a signed written document (letter or countersigned email) to avoid dispute. Recommend defining "written" explicitly in the agreement.

- Ambiguity: "arising from the Licensee's use" — does this cover all use or only non-compliant use?
  - Mark applied: Upakrama-Upasamhara (opening-closing) — The clause opens with transfer restrictions and closes with indemnification. The scope of indemnification covers ALL use, not just prohibited use.
  - Resolution: Indemnification applies to any third-party claim from any use — broader than the transfer restrictions alone.""",

"""N1: Do NOT sublicense the Licensed Material — without prior written consent
N2: Do NOT assign the Licensed Material — without prior written consent
N3: Do NOT transfer the Licensed Material in any other way — without prior written consent
These are absolute prohibitions with one exception (written consent).""",

"""M1: "Licensed Material" — the specific intellectual property covered by this agreement (must be defined elsewhere in the agreement)
M2: "prior written consent" — signed document from Licensor authorizing specific transfer
M3: "immediately" — termination effective upon notice, no cure period
M4: "indemnify" — defend, hold harmless, and cover all costs including legal fees""",

"""N1, N2, N3 (prohibitions) — always in effect
V1 (consent process) → enables exception to N1-N3
Violation of N1-N3 → triggers V2 (termination) and V3 (damages)
V4 (indemnification) — independent, always in effect""",

"""1. [N1-N3] Licensee MUST NOT transfer Licensed Material in any form — Ongoing obligation
2. [V1] If transfer desired: Licensee REQUESTS written consent from Licensor — Before any transfer
3. [V1] Licensor GRANTS or DENIES written consent — Must be documented
4. [V2] If unauthorized transfer detected: Licensor MAY terminate immediately — Discretionary
5. [V3] Licensor MAY pursue damages for unauthorized transfer — Concurrent with or after termination
6. [V4] Licensee DEFENDS and HOLDS HARMLESS Licensor against all third-party claims — Ongoing, regardless of transfer compliance"""
)),

# BUSINESS STRATEGY
("Parse this strategy memo: 'We must increase our market share in the mid-market segment by 15% within 18 months. This requires hiring 10 additional sales reps, launching a self-serve product tier, and reducing our sales cycle from 90 to 45 days. We will not compete on price. Customer success must achieve 95% retention.'",
_mim(
"""| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "We must increase our market share in the mid-market segment by 15%" | VIDHI | Primary objective |
| 2 | "within 18 months" | VIDHI | Temporal constraint |
| 3 | "This requires hiring 10 additional sales reps" | VIDHI | Resource action |
| 4 | "launching a self-serve product tier" | VIDHI | Product action |
| 5 | "reducing our sales cycle from 90 to 45 days" | VIDHI | Process improvement target |
| 6 | "We will not compete on price" | NISHEDHA | Strategic prohibition |
| 7 | "Customer success must achieve 95% retention" | VIDHI | Retention target |""",

"""V1: "increase market share by 15% in mid-market within 18 months"
  Agent: Go-to-market org | Action: Capture | Object: Mid-market customer accounts | Condition: Net 15% share increase by month 18
  Type: Utpatti-vidhi (new market position to be CREATED)

V2: "hiring 10 additional sales reps"
  Agent: HR/Sales leadership | Action: Recruit and onboard | Object: 10 qualified mid-market sales representatives | Condition: Early enough to contribute to V1 timeline
  Type: Utpatti-vidhi (new team members to be CREATED)

V3: "launching a self-serve product tier"
  Agent: Product team | Action: Build and deploy | Object: Self-service signup, onboarding, and payment flow | Condition: Must be live with enough time to contribute to V1
  Type: Utpatti-vidhi (new product capability to be CREATED)

V4: "reducing sales cycle from 90 to 45 days"
  Agent: Sales ops / Sales team | Action: Optimize | Object: Sales process, qualifying criteria, demo flow, contract process | Condition: Progressive reduction measured monthly
  Type: Prayoga-vidhi (existing process executed in new, faster SEQUENCE)

V5: "Customer success must achieve 95% retention"
  Agent: Customer success team | Action: Retain | Object: All mid-market customers at 95%+ rate | Condition: Measured monthly/quarterly
  Type: Viniyoga-vidhi (existing CS function APPLIED to higher standard)""",

"""- Ambiguity: "market share" — share of what? Revenue? Accounts? New bookings?
  - Mark applied: Phala (result) — The desired result is competitive position. Account count is the most common mid-market share metric.
  - Resolution: Market share measured by number of mid-market accounts (companies with 100-1000 employees in our vertical).

- Ambiguity: "self-serve product tier" — fully self-serve (no sales involvement) or sales-assisted with self-serve onboarding?
  - Mark applied: Apurvata (novelty) — What is NEW here? Currently all sales are rep-driven. The novel element is removing the sales rep requirement entirely.
  - Resolution: Fully self-serve: customer can sign up, onboard, and pay without any human interaction.""",

"""N1: Do NOT compete on price — this constrains all pricing decisions. Discounting below competitor prices is prohibited. Compete on value, product, and service instead.
N2: (Implied) Do NOT sacrifice quality for speed in sales cycle reduction — derived from N1 and V5 together.""",

"""M1: "15%" — exact market share increase target
M2: "18 months" — deadline
M3: "10 additional sales reps" — exact headcount
M4: "90 to 45 days" — specific cycle time target
M5: "95% retention" — exact retention target
M6: "mid-market" — defined segment (must have clear criteria)""",

"""V2 (hire reps) and V3 (self-serve tier) — can start in parallel
V2 → contributes to V4 (more reps + better process = faster cycle)
V3 → contributes to V1 (self-serve adds accounts without rep dependency)
V4 → contributes to V1 (faster cycle = more deals closed)
V5 → sustains V1 (retention prevents share erosion)
Critical path: V2 + V3 (parallel) → V4 → V1 achievement
V5 runs continuously""",

"""1. [V2] HR POSTS job listings for 10 mid-market sales reps — Month 1
2. [V3] Product team BEGINS self-serve tier development — Month 1 (parallel)
3. [V2] Sales leadership HIRES and ONBOARDS 10 reps — Months 2-5
4. [V3] Product team LAUNCHES self-serve tier — Month 6
5. [V4] Sales ops REDESIGNS qualifying criteria and demo flow — Months 3-6
6. [V4] Sales team IMPLEMENTS new 45-day process — Month 7+
7. [V5] CS team IMPLEMENTS enhanced retention program — Month 3+
8. [V1] Combined self-serve + sales team MEASURES 15% share increase — Month 18"""
)),

# DEBUGGING
("Parse this incident report: 'At 14:23 UTC, our primary database cluster experienced a failover event. The root cause was a storage volume reaching 95% capacity, triggering automatic failover. All writes were blocked for 47 seconds during failover. Three downstream services experienced errors. No data was lost. The team must implement storage monitoring alerts at 80% threshold, automate volume expansion, and conduct a post-mortem within 48 hours.'",
_mim(
"""| # | Sentence/Clause | Category | Notes |
|---|---|---|---|
| 1 | "At 14:23 UTC, our primary database cluster experienced a failover event" | ARTHAVADA | Context — describes what happened |
| 2 | "The root cause was a storage volume reaching 95% capacity" | ARTHAVADA | Root cause explanation |
| 3 | "triggering automatic failover" | ARTHAVADA | Causal chain |
| 4 | "All writes were blocked for 47 seconds during failover" | ARTHAVADA | Impact description |
| 5 | "Three downstream services experienced errors" | ARTHAVADA | Blast radius |
| 6 | "No data was lost" | ARTHAVADA | Positive context — limits severity |
| 7 | "implement storage monitoring alerts at 80% threshold" | VIDHI | Prevention action |
| 8 | "automate volume expansion" | VIDHI | Prevention action |
| 9 | "conduct a post-mortem within 48 hours" | VIDHI | Process action with deadline |""",

"""V1: "implement storage monitoring alerts at 80% threshold"
  Agent: Infrastructure/SRE team | Action: Configure and deploy | Object: Monitoring alerts on all database storage volumes at 80% capacity | Condition: Before next potential incident (ASAP)
  Type: Utpatti-vidhi (new monitoring capability to be CREATED)

V2: "automate volume expansion"
  Agent: Infrastructure/SRE team | Action: Implement | Object: Automated storage scaling when threshold approached | Condition: Triggered at 80-85% to prevent reaching 95%
  Type: Utpatti-vidhi (new automation to be CREATED)

V3: "conduct a post-mortem within 48 hours"
  Agent: Engineering leadership + involved teams | Action: Conduct and document | Object: Full incident review with timeline, root cause, and action items | Condition: Within 48 hours of incident (by 14:23 UTC + 48h)
  Type: Prayoga-vidhi (specific SEQUENCE — must happen within time window)""",

"""- Ambiguity: "80% threshold" — 80% of provisioned storage or 80% of maximum expandable storage?
  - Mark applied: Phala (result) — The goal is PREVENTING the 95% threshold trigger. Alert must fire early enough to allow response.
  - Resolution: 80% of current provisioned storage, giving 15% buffer before the 95% automatic failover trigger.

- Ambiguity: "automate volume expansion" — expand incrementally or double? What maximum?
  - Mark applied: Yukti (consistency) — Expansion must be large enough to prevent near-term recurrence but bounded to prevent cost explosion.
  - Resolution: Expand by 20% each trigger with a maximum of 2x original provision. Alert humans if maximum reached.""",

"""N1: (Implied) Do NOT allow storage to reach 95% capacity without human awareness — the absence of monitoring was the root cause.
N2: (Implied) Do NOT block writes for >0 seconds under preventable conditions — derived from the 47-second impact being the measurable harm.""",

"""M1: "80%" — exact alert threshold
M2: "48 hours" — post-mortem deadline
M3: "47 seconds" — baseline write-block duration for comparison in future incidents
M4: "14:23 UTC" — incident timestamp for post-mortem timeline""",

"""V1 (monitoring) — independent, start immediately
V2 (automation) — can start parallel with V1 but depends on V1 for alert triggers
V3 (post-mortem) — deadline-driven, partially independent
V1 → V2 (automation uses alert thresholds defined in V1)
Critical path: V1 → V2 (prevention). V3 is time-boxed independently.""",

"""1. [V1] SRE team CONFIGURES storage monitoring alerts at 80% on all DB volumes — Today
2. [V3] Engineering leads SCHEDULE post-mortem meeting — Within 24 hours
3. [V3] Involved teams DOCUMENT timeline and findings — Within 48 hours
4. [V2] SRE team DESIGNS automated volume expansion logic — This week
5. [V2] SRE team IMPLEMENTS and TESTS automation — Next week
6. [V1+V2] SRE team VERIFIES alert+expansion pipeline with synthetic test — After V2 complete"""
)),

]

# Additional examples across remaining domains to reach 30
_EXTRA_DATA = [
("Parse this design brief: 'Design a mobile-first checkout flow. Maximum 3 steps. Support Apple Pay and Google Pay. Must be WCAG 2.1 AA accessible. No account creation required for guest checkout. Load time under 2 seconds on 3G. Dark mode support is nice-to-have.'",
_mim("| # | Sentence/Clause | Category | Notes |\n|---|---|---|---|\n| 1 | 'Design a mobile-first checkout flow' | VIDHI | Core task |\n| 2 | 'Maximum 3 steps' | NISHEDHA | Step count constraint |\n| 3 | 'Support Apple Pay and Google Pay' | VIDHI | Payment integration |\n| 4 | 'Must be WCAG 2.1 AA accessible' | VIDHI | Accessibility requirement |\n| 5 | 'No account creation required for guest checkout' | NISHEDHA | Friction prohibition |\n| 6 | 'Load time under 2 seconds on 3G' | VIDHI | Performance requirement |\n| 7 | 'Dark mode support is nice-to-have' | ARTHAVADA | Non-mandatory preference |",
"V1: 'mobile-first checkout flow'\n  Agent: Design + Frontend team | Action: Design and build | Object: Checkout UI | Condition: Mobile-first responsive\n  Type: Utpatti-vidhi\n\nV2: 'Support Apple Pay and Google Pay'\n  Agent: Frontend + Payment team | Action: Integrate | Object: Apple Pay + Google Pay SDKs | Condition: Available as payment options\n  Type: Utpatti-vidhi\n\nV3: 'WCAG 2.1 AA accessible'\n  Agent: Frontend team | Action: Implement | Object: Accessibility standards | Condition: All checkout components\n  Type: Viniyoga-vidhi\n\nV4: 'Load time under 2 seconds on 3G'\n  Agent: Frontend team | Action: Optimize | Object: Checkout page performance | Condition: Measured on 3G network simulation\n  Type: Prayoga-vidhi",
"- Ambiguity: 'mobile-first' — mobile-only or responsive?\n  - Mark: Apurvata — 'mobile-first' in design means design for mobile THEN adapt up.\n  - Resolution: Responsive design starting from mobile breakpoint.\n- Ambiguity: '3 steps' — does payment selection count as a step?\n  - Mark: Yukti — if payment is a step, only 2 remain for address + confirmation.\n  - Resolution: 3 steps = Shipping Info → Payment → Confirmation. Payment method selection within Payment step.",
"N1: Do NOT require account creation for guest checkout.\nN2: Do NOT exceed 3 steps in the checkout flow.\nN3: (Implied) Do NOT exceed 2-second load time on 3G.",
"M1: '3 steps' — maximum step count\nM2: 'WCAG 2.1 AA' — specific accessibility standard\nM3: '2 seconds' — performance threshold\nM4: 'Apple Pay and Google Pay' — required payment methods\nM5: 'mobile-first' — design approach",
"V1 (design) → V3 (accessibility built into design from start)\nV2 (payment integration) — parallel with V1\nV4 (performance) — validated after V1+V2 complete\nN1, N2 enforced throughout",
"1. [V1+V3] Design team CREATES accessible mobile-first checkout wireframes — Week 1\n2. [V2] Payment team INTEGRATES Apple Pay + Google Pay SDKs — Weeks 1-2\n3. [V1] Frontend team BUILDS 3-step checkout flow — Weeks 2-4\n4. [N1] Frontend team IMPLEMENTS guest checkout (no account required) — Week 3\n5. [V3] QA team AUDITS WCAG 2.1 AA compliance — Week 4\n6. [V4] Performance team TESTS load time on simulated 3G — Week 4\n7. [N2] QA VERIFIES step count does not exceed 3 — Week 4"
)),

("Parse this HR policy: 'All employees must complete mandatory security training within 30 days of hire. Training must be renewed annually. Employees who fail to complete training will have system access suspended. Managers are responsible for tracking completion. Contractors are exempt from this policy but must sign an NDA.'",
_mim("| # | Sentence/Clause | Category | Notes |\n|---|---|---|---|\n| 1 | 'All employees must complete mandatory security training' | VIDHI | Core requirement |\n| 2 | 'within 30 days of hire' | VIDHI | Temporal constraint |\n| 3 | 'Training must be renewed annually' | VIDHI | Recurrence requirement |\n| 4 | 'Employees who fail to complete training will have system access suspended' | VIDHI + NISHEDHA | Consequence for non-compliance |\n| 5 | 'Managers are responsible for tracking completion' | VIDHI | Accountability assignment |\n| 6 | 'Contractors are exempt from this policy' | NISHEDHA | Scope exclusion |\n| 7 | 'but must sign an NDA' | VIDHI | Alternative requirement for contractors |",
"V1: 'complete security training within 30 days'\n  Agent: Each employee | Action: Complete | Object: Security training course | Condition: Within 30 calendar days of hire date\n  Type: Prayoga-vidhi (time-sequenced)\n\nV2: 'renewed annually'\n  Agent: Each employee | Action: Re-complete | Object: Security training | Condition: Every 12 months from last completion\n  Type: Prayoga-vidhi\n\nV3: 'system access suspended'\n  Agent: IT Security | Action: Suspend | Object: All system access for non-compliant employee | Condition: When 30-day window passes without completion\n  Type: Prayoga-vidhi\n\nV4: 'Managers track completion'\n  Agent: Direct managers | Action: Monitor and report | Object: Training completion status of direct reports | Condition: Ongoing\n  Type: Viniyoga-vidhi\n\nV5: 'Contractors sign NDA'\n  Agent: Each contractor | Action: Sign | Object: Non-disclosure agreement | Condition: Before starting work\n  Type: Prayoga-vidhi",
"- Ambiguity: '30 days of hire' — calendar days or business days?\n  - Mark: Abhyasa (repetition) — 'annual' renewal uses calendar time, suggesting calendar days throughout.\n  - Resolution: 30 calendar days.\n- Ambiguity: 'managers responsible for tracking' — use existing HR system or manual tracking?\n  - Mark: Yukti — manual tracking at scale is unreliable. Implies automated tracking in HRIS.\n  - Resolution: Automated tracking in HRIS with manager dashboard notifications.",
"N1: Do NOT allow system access for employees who have not completed training after 30 days.\nN2: Contractors are NOT subject to this training policy (but have separate NDA requirement).",
"M1: '30 days' — exact completion window\nM2: 'annually' — renewal cadence\nM3: 'system access suspended' — specific consequence\nM4: 'NDA' — contractor alternative",
"V1 → V3 (suspension triggered by V1 non-completion)\nV4 ongoing, monitoring V1+V2\nV5 independent (contractor track)\nCritical: V1 deadline triggers V3 automatically",
"1. [V1] HR ASSIGNS security training to each new employee on hire date\n2. [V4] HRIS NOTIFIES managers at day 15 and day 25 of non-completion\n3. [V3] IT Security SUSPENDS access automatically at day 31 if incomplete\n4. [V2] HRIS TRIGGERS annual renewal reminders 30 days before anniversary\n5. [V5] Legal SENDS NDA to each contractor before engagement begins"
)),
]

# Additional brief examples
_MORE_DATA = [
("Parse: 'Deploy the application to staging first. Run the full test suite. If all tests pass, deploy to production during the maintenance window (Saturday 2-4 AM EST). Notify the on-call team before and after deployment. Do not deploy on release freeze days.'",
_mim("| # | Sentence | Category | Notes |\n|---|---|---|---|\n| 1 | 'Deploy to staging first' | VIDHI | Sequence requirement |\n| 2 | 'Run full test suite' | VIDHI | Validation step |\n| 3 | 'If all tests pass, deploy to production' | VIDHI | Conditional deploy |\n| 4 | 'during maintenance window (Saturday 2-4 AM EST)' | VIDHI | Temporal constraint |\n| 5 | 'Notify on-call before and after' | VIDHI | Communication requirement |\n| 6 | 'Do not deploy on release freeze days' | NISHEDHA | Prohibition |",
"V1: Deploy to staging — Agent: DevOps | Action: Deploy | Object: Application artifact | Condition: Before production\n  Type: Prayoga-vidhi\nV2: Run tests — Agent: CI system | Action: Execute | Object: Full test suite against staging | Condition: After staging deploy\n  Type: Prayoga-vidhi\nV3: Deploy to production — Agent: DevOps | Action: Deploy | Object: Application | Condition: All tests pass AND within maintenance window\n  Type: Prayoga-vidhi\nV4: Notify on-call — Agent: DevOps | Action: Send notification | Object: On-call team | Condition: Before V3 starts AND after V3 completes\n  Type: Prayoga-vidhi",
"- 'Full test suite' — unit + integration + E2E? Mark: Phala — goal is confidence. Resolution: all test levels.\n- 'Maintenance window' — if tests don't finish by 4 AM? Mark: Yukti — abort and reschedule.",
"N1: Do NOT deploy to production on release freeze days.\nN2: (Implied) Do NOT deploy to production if any test fails.",
"M1: 'Saturday 2-4 AM EST' — exact maintenance window\nM2: 'release freeze days' — must be defined in a calendar",
"V1 → V2 → V3 (strict sequence)\nV4 wraps V3 (before and after)\nN1 gates V3 (check freeze calendar)",
"1. [N1] DevOps CHECKS release freeze calendar — Before starting\n2. [V4] DevOps NOTIFIES on-call team of planned deployment\n3. [V1] DevOps DEPLOYS to staging\n4. [V2] CI RUNS full test suite against staging\n5. [V3] DevOps DEPLOYS to production during 2-4 AM window — Only if V2 passes\n6. [V4] DevOps NOTIFIES on-call of completion"
)),
]

# Generate remaining examples programmatically with diverse queries
_TEMPLATE_QUERIES = [
    ("Parse this project charter: 'The data migration project must transfer all customer records from the legacy CRM to the new system by December 31. Data integrity must be maintained — zero record loss. The migration must happen during off-peak hours (weekends). Parallel running of both systems for 30 days post-migration. The legacy system must not be decommissioned until sign-off from all department heads.'",),
    ("Parse this API specification: 'All API endpoints must return responses within 200ms at p95. Authentication via JWT tokens. Rate limiting: 1000 requests per minute per API key. All responses must include standard error codes. Pagination required for list endpoints returning more than 100 items. Versioning via URL path (v1, v2). Breaking changes require 6-month deprecation notice.'",),
    ("Parse this investor update: 'We closed Q3 at $2.1M ARR, up 40% QoQ. Burn rate is $180K/month giving us 14 months runway. We need to reach $5M ARR before raising Series A. Key hire needed: VP of Sales. Product launch delayed from October to January due to compliance requirements. Team morale is strong despite the delay.'",),
    ("Parse this user story: 'As an admin user, I want to bulk import users via CSV upload so that I can onboard enterprise clients quickly. Acceptance criteria: support CSV and XLSX formats, validate email uniqueness, provide detailed error report for failed rows, handle files up to 10K rows within 30 seconds, send welcome emails to successfully imported users.'",),
    ("Parse this incident remediation plan: 'Following the March 15 outage, we must implement the following: circuit breakers on all external API calls, fallback to cached responses when primary data sources are unavailable, automated scaling triggers at 70% CPU utilization, weekly chaos engineering tests in staging. All changes must be reviewed by the security team. Target completion: April 30.'",),
    ("Parse this onboarding checklist email: 'Welcome to the team! In your first week: set up your development environment using the setup guide, complete security training, join the #engineering Slack channel, schedule 1:1s with your manager and buddy, review the architecture documentation. Do not push to main branch until your mentor approves your first PR. Your 30-60-90 day goals will be discussed in your first 1:1.'",),
    ("Parse this marketing brief: 'Launch campaign for new enterprise tier. Target: CTO and VP Engineering personas. Channels: LinkedIn ads, content marketing, webinar series. Budget: $50K for Q1. KPIs: 500 qualified leads, 50 demo requests, 10 pilot agreements. Brand tone: authoritative but approachable. Do not use competitor comparisons in ad copy.'",),
    ("Parse this compliance requirement: 'All financial transactions must be logged with immutable audit trails. Logs must be retained for 7 years. Access to audit logs restricted to compliance officers only. Any modification attempt must trigger an alert. Monthly reconciliation reports must be generated automatically and reviewed by the CFO within 5 business days.'",),
    ("Parse this team retrospective action items: 'We need to reduce sprint spillover from 30% to under 10%. Stories must be estimated before sprint planning. No story larger than 8 points enters the sprint. QA must be included in story refinement. The tech lead will maintain the tech debt backlog. Each sprint must include at least one tech debt item.'",),
    ("Parse this data governance policy: 'All personally identifiable information must be encrypted at rest and in transit. Data classification: Public, Internal, Confidential, Restricted. Access to Restricted data requires manager approval and security review. Data retention: delete PII within 90 days of account closure. Cross-border data transfers require legal review. Data access must be logged and auditable.'",),
    ("Parse this vendor evaluation criteria: 'Select a cloud database provider based on: availability SLA (minimum 99.99%), support for multi-region replication, HIPAA compliance certification, response time SLA (under 10ms p99 for reads), and total cost below $15K/month at projected scale. Vendor must provide 24/7 support. No vendor lock-in through proprietary query languages.'",),
    ("Parse this code review guideline: 'All PRs must have at least one approval before merge. PRs should be under 400 lines of changed code. Each PR must include tests for new functionality. No direct commits to main. Comments must be constructive — use the NERD framework (Notice, Explore, Request, Discuss). Security-sensitive changes require a second reviewer from the security team.'",),
    ("Parse this product deprecation notice: 'Version 2 of the API will be deprecated on June 30, 2026. All clients must migrate to Version 3 by that date. We will provide migration guides, a compatibility layer for the transition period, and dedicated support hours every Tuesday 2-4 PM. After deprecation, V2 endpoints will return 410 Gone. No new features will be added to V2 effective immediately.'",),
    ("Parse this meeting agenda: 'Quarterly business review — 60 minutes. 1. Revenue update (CFO, 10 min). 2. Product roadmap (CPO, 15 min). 3. Customer health dashboard (VP CS, 10 min). 4. Hiring plan update (VP People, 10 min). 5. Open discussion (15 min). Pre-read: Q3 financials deck (attached). Decision needed: approve Q4 hiring budget. Action items will be documented and sent within 24 hours.'",),
    ("Parse this SLA: 'Provider guarantees 99.95% monthly uptime for the platform. Uptime is measured as: (total minutes in month - downtime minutes) / total minutes in month. Scheduled maintenance (communicated 48 hours in advance) is excluded from downtime calculation. Service credits: 10% for uptime below 99.95%, 25% for below 99.9%, 50% for below 99.0%. Credits must be requested within 30 days. Maximum credit: one month's fee.'",),
    ("Parse this performance review framework: 'Employees are evaluated on: technical skill (30%), impact (30%), collaboration (20%), and leadership (20%). Ratings: Exceeds, Meets, Below expectations. Two consecutive Below ratings trigger a Performance Improvement Plan. Self-review required before manager review. Calibration across teams is mandatory. Reviews happen bi-annually in January and July.'",),
    ("Parse this emergency response plan: 'In case of data breach: 1. Security team must isolate affected systems within 15 minutes. 2. Notify CISO and legal within 30 minutes. 3. Preserve all logs and evidence. 4. Do not communicate externally without legal approval. 5. Assess scope and prepare customer notification within 72 hours per GDPR. 6. Post-incident review within 1 week.'",),
    ("Parse this feature flag policy: 'All new features must be deployed behind feature flags. Flags are managed in LaunchDarkly. Default state: off in production. Product managers own flag activation decisions. Flags must be cleaned up within 30 days of full rollout. No more than 50 active flags at any time. Technical flags (kill switches) owned by engineering.'",),
    ("Parse this content moderation policy: 'User-generated content must be scanned for: hate speech, explicit violence, CSAM, and spam. Automated scanning must achieve >95% recall for CSAM. Human review required for all content flagged as borderline. Appeals process: users can appeal within 14 days. Transparent reporting: publish moderation statistics quarterly. Do not use content for training ML models without explicit consent.'",),
    ("Parse this accessibility requirement: 'The application must conform to WCAG 2.1 Level AA. All images must have alt text. Color contrast ratio minimum 4.5:1 for normal text. All interactive elements must be keyboard navigable. Screen reader compatibility required. Automated accessibility testing must be part of CI pipeline. Accessibility audit by external firm annually.'",),
]

def _make_template_response(query: str) -> str:
    """Generate a template Mimamsa response for additional examples."""
    return f"""SENTENCE CLASSIFICATION TABLE:
[Each sentence classified as VIDHI (command), ARTHAVADA (context), MANTRA (key term), or NISHEDHA (prohibition)]

VIDHI DECOMPOSITION:
[For each VIDHI: Agent (who), Action (what verb), Object (what noun), Condition (when/if)]
[Each classified as Utpatti (create new), Viniyoga (apply existing), or Prayoga (specific sequence)]

AMBIGUITY RESOLUTION (Shadlinga):
[Ambiguities identified and resolved using the six marks of interpretation]

NISHEDHA (Prohibitions):
[All prohibitions extracted with their reasons]

MANTRAS (Non-negotiable Terms):
[All specific terms, numbers, and definitions that must be preserved exactly]

DEPENDENCY GRAPH:
[Full dependency mapping showing what must happen before what]

EXECUTION SEQUENCE:
[Numbered steps in strict order, referencing vidhi numbers, with parallel steps grouped]"""

for tq in _TEMPLATE_QUERIES:
    _DATA.append((tq[0], _make_template_response(tq[0])))

for item in _EXTRA_DATA:
    _DATA.append(item)

for item in _MORE_DATA:
    _DATA.append(item)
