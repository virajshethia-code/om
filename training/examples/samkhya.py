"""Samkhya training examples — 30 exhaustive enumeration examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "samkhya"


def generate_samkhya_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples


def _enum(system_name: str, boundaries: str, target: int,
          components: List[str], non_obvious: List[str],
          chain: str, audit: str) -> str:
    """Build a full Samkhya response."""
    lines = [f"SYSTEM: {system_name}"]
    lines.append(f"Boundaries: {boundaries}")
    lines.append(f"TARGET COUNT: {target}")
    lines.append("\nENUMERATION:")
    for i, c in enumerate(components, 1):
        lines.append(f"{i}. {c}")
    lines.append("\nNON-OBVIOUS COMPONENTS:")
    for i, n in enumerate(non_obvious, len(components) + 1):
        lines.append(f"{i}. [NON-OBVIOUS] {n}")
    lines.append(f"\nCAUSAL CHAIN:\n{chain}")
    lines.append(f"\nCOMPLETENESS AUDIT:\n{audit}")
    lines.append(f"\nTOTAL COUNT: {len(components) + len(non_obvious)}")
    return "\n".join(lines)


_DATA: List[tuple] = [

# ===== SOFTWARE ENGINEERING (3) =====

("Enumerate all components involved when a user clicks 'Buy Now' and an order is fulfilled.",
_enum(
    "E-commerce purchase-to-fulfillment pipeline.",
    "INSIDE — all systems from click to delivery. OUTSIDE — manufacturing, returns.",
    25,
    [
        "User Intent — The cognitive decision to purchase, preceding the click.\n   Emerges from: root (prior browsing, need) | Gives rise to: Click Event | Evidence: Inferred from action.",
        "Click Event — Browser DOM event on Buy Now button.\n   Emerges from: User Intent | Gives rise to: Client Validation, Analytics Event | Evidence: Browser event listeners.",
        "Client-Side Validation — JS checks: cart non-empty, session valid, fields populated.\n   Emerges from: Click Event | Gives rise to: API Request or Error State | Evidence: Browser console.",
        "Analytics Event — Tracking beacon to analytics system recording purchase intent.\n   Emerges from: Click Event | Gives rise to: Analytics Pipeline | Evidence: Network requests.",
        "DNS Resolution — Browser resolves domain to IP through DNS cache hierarchy.\n   Emerges from: API Request (transport) | Gives rise to: TCP Connection | Evidence: DNS timing in DevTools.",
        "TLS Handshake — Cryptographic channel establishment between browser and server.\n   Emerges from: TCP Connection | Gives rise to: Encrypted transmission | Evidence: SSL timing.",
        "Load Balancer Routing — Request distribution to available application server.\n   Emerges from: TLS completion | Gives rise to: App Server Processing | Evidence: LB logs.",
        "Authentication/Authorization — Session token verification and permission check.\n   Emerges from: App Server | Gives rise to: Order Validation or Rejection | Evidence: Auth logs.",
        "Order Validation — Business logic: inventory check, price consistency, address validation, fraud screening.\n   Emerges from: Auth | Gives rise to: Payment Processing or Error | Evidence: App logs.",
        "Inventory Reservation — Temporary hold preventing overselling during payment.\n   Emerges from: Order Validation | Gives rise to: Payment Processing | Evidence: Inventory DB state.",
        "Tax Calculation — Real-time API (Avalara/TaxJar) computing jurisdiction-specific sales tax.\n   Emerges from: Order Validation (shipping address) | Gives rise to: Final Price | Evidence: Tax API logs.",
        "Payment Gateway Request — API call to Stripe/PayPal with payment token and amount.\n   Emerges from: Inventory Reservation + Tax | Gives rise to: Bank Network Processing | Evidence: Gateway logs.",
        "Bank Network Processing — Card network routes authorization to issuing bank; fraud check, fund verification.\n   Emerges from: Gateway Request | Gives rise to: Authorization Response | Evidence: Inferred; outcome visible.",
        "Authorization Response — Approve/decline with authorization code or reason.\n   Emerges from: Bank Network | Gives rise to: Order Confirmation or Failure Handling | Evidence: Gateway response.",
        "Order Record Creation — Persistent storage with status 'confirmed', linking customer, items, payment, shipping.\n   Emerges from: Authorization (approved) | Gives rise to: Confirmation Event, Warehouse Notification | Evidence: DB record.",
        "Order Confirmation Event — Async event published to message queue notifying downstream systems.\n   Emerges from: Order Record | Gives rise to: Email, WMS trigger, Analytics update | Evidence: Queue logs.",
        "Confirmation Email — Transactional email with order details, ETA, receipt.\n   Emerges from: Confirmation Event | Gives rise to: Customer awareness | Evidence: Email delivery logs.",
        "WMS Notification — Order details transmitted to warehouse management system.\n   Emerges from: Confirmation Event | Gives rise to: Pick List | Evidence: WMS intake logs.",
        "Pick List Generation — WMS calculates optimal picking route and worker instructions.\n   Emerges from: WMS Notification | Gives rise to: Physical Picking | Evidence: WMS records.",
        "Physical Picking — Worker retrieves items from shelving guided by pick list.\n   Emerges from: Pick List | Gives rise to: Packing | Evidence: Scan confirmation.",
        "Packing — Items verified, packaged, sealed with packing slip.\n   Emerges from: Picking | Gives rise to: Label Generation | Evidence: Pack station scan.",
        "Shipping Label — Carrier API generates label with tracking number.\n   Emerges from: Packing | Gives rise to: Carrier Pickup | Evidence: Carrier API response.",
        "Carrier Network — Package enters sort, route, and delivery pipeline.\n   Emerges from: Label/Pickup | Gives rise to: Last-Mile Delivery | Evidence: Scan events at each sort.",
        "Last-Mile Delivery — Carrier delivers to customer address.\n   Emerges from: Carrier Network | Gives rise to: Delivery Confirmation | Evidence: Driver scan, photo.",
        "Delivery Confirmation — Status propagated back to merchant via carrier webhook.\n   Emerges from: Delivery | Gives rise to: Order Complete, Post-purchase flows | Evidence: Webhook, DB update.",
    ],
    [
        "Fraud Scoring Model — Real-time ML model scoring transaction risk during Order Validation. Invisible when passing (vast majority). Load-bearing: without it, chargeback losses exceed margins. Silently blocks 1-3% of transactions, adds 50-200ms to every order.",
        "Idempotency Layer — Ensures double-click or network retry creates exactly one order. Prevents duplicate charges and shipments. Missed because it prevents something from happening rather than causing something.",
        "Payment Capture Timing — Distinction between authorization (hold) and capture (actual charge). Some merchants capture only at shipment. Missed because it is a temporal detail, but incorrect timing creates accounting, refund, and chargeback complications.",
    ],
    """User Intent → Click → Validation → DNS → TLS → LB → Auth → Order Validation
                                                                    ↘ Fraud Score + Tax Calc
→ Inventory Reservation → Payment Gateway → Bank → Auth Response → Order Record
→ Confirmation Event → Email + WMS + Analytics
WMS → Pick List → Picking → Packing → Label → Carrier → Last-Mile → Delivery Confirmation
Idempotency Layer (guards: Click → Order Record, preventing duplicates)""",
    """- Suspected: CDN layer, database replication lag, circuit breakers, retry/backoff, gift cards, promo codes.
- Gaps: Error recovery paths (payment fails, inventory unavailable). Monitoring/alerting (Datadog, PagerDuty).
- Outside view: The system is a TRUST PIPELINE — each step trusts previous output. Fragility comes from trust violations: fraud, corrupted inter-service data, race conditions.
- Estimated completeness: 78%"""
)),

("Enumerate all components of a CI/CD pipeline from commit to production.",
_enum(
    "CI/CD pipeline from source commit through production deployment.",
    "INSIDE — all pipeline stages, tools, and processes. OUTSIDE — development process before commit, production monitoring after deploy.",
    20,
    [
        "Source Commit — Developer pushes code changes to version control (Git).\n   Emerges from: root (development work) | Gives rise to: Webhook Trigger | Evidence: Git log.",
        "Webhook Trigger — VCS event fires to CI server (GitHub Actions, Jenkins, GitLab CI).\n   Emerges from: Source Commit | Gives rise to: Pipeline Initialization | Evidence: Webhook delivery logs.",
        "Pipeline Configuration — YAML/Groovy file defining stages, steps, environment, secrets.\n   Emerges from: root (checked into repo) | Gives rise to: Pipeline behavior | Evidence: Config file in repo.",
        "Runner Provisioning — CI server allocates a build runner (container, VM, or bare metal).\n   Emerges from: Webhook Trigger + Config | Gives rise to: Build Environment | Evidence: Runner logs.",
        "Dependency Installation — Package manager (npm, pip, maven) installs project dependencies.\n   Emerges from: Build Environment + lockfile | Gives rise to: Buildable Project | Evidence: Install logs, cache hit rate.",
        "Dependency Cache — Cached node_modules/venv from previous runs to skip reinstallation.\n   Emerges from: Previous pipeline runs | Gives rise to: Faster Dependency Installation | Evidence: Cache hit/miss metrics.",
        "Static Analysis/Linting — Code style, complexity, and pattern checks (ESLint, Pylint, Ruff).\n   Emerges from: Buildable Project | Gives rise to: Style Gate (pass/fail) | Evidence: Lint output.",
        "Type Checking — Static type verification (TypeScript, mypy, Flow).\n   Emerges from: Buildable Project | Gives rise to: Type Safety Gate | Evidence: Type checker output.",
        "Unit Tests — Isolated tests of individual functions/modules.\n   Emerges from: Buildable Project + Test Config | Gives rise to: Unit Test Gate, Coverage Report | Evidence: Test output, JUnit XML.",
        "Integration Tests — Tests of component interactions, API contracts, database queries.\n   Emerges from: Unit Tests pass + Test Infrastructure | Gives rise to: Integration Gate | Evidence: Test output.",
        "Test Coverage Report — Measurement of code lines/branches exercised by tests.\n   Emerges from: Test execution + Coverage tool | Gives rise to: Coverage Gate (minimum threshold) | Evidence: Coverage percentage.",
        "Build/Compile — Transform source into deployable artifact (Docker image, binary, bundle).\n   Emerges from: All tests pass | Gives rise to: Artifact | Evidence: Build output, image tag.",
        "Artifact Storage — Built artifact pushed to registry (Docker Hub, ECR, Artifactory, S3).\n   Emerges from: Build | Gives rise to: Deployment availability | Evidence: Registry listing.",
        "Security Scanning — Vulnerability scan of dependencies (Snyk, Dependabot) and container image (Trivy).\n   Emerges from: Artifact | Gives rise to: Security Gate | Evidence: Scan report, CVE list.",
        "Staging Deployment — Artifact deployed to staging/pre-production environment.\n   Emerges from: All gates pass + Artifact | Gives rise to: Staging Environment | Evidence: Deployment logs.",
        "Smoke Tests / E2E Tests — Automated tests against staging verifying critical paths work.\n   Emerges from: Staging Deployment | Gives rise to: Release Gate | Evidence: Test output.",
        "Approval Gate — Manual or automated approval for production deployment.\n   Emerges from: Smoke tests pass | Gives rise to: Production Deploy | Evidence: Approval record.",
        "Production Deployment — Artifact deployed to production (blue/green, canary, rolling).\n   Emerges from: Approval + Artifact | Gives rise to: Live System Update | Evidence: Deployment logs, health checks.",
        "Health Checks — Post-deploy verification: HTTP health endpoints, error rate monitoring, latency checks.\n   Emerges from: Production Deploy | Gives rise to: Confirmation or Rollback | Evidence: Health endpoint responses.",
        "Rollback Mechanism — Automated or manual revert to previous version if health checks fail.\n   Emerges from: Health Check failure | Gives rise to: System restoration | Evidence: Rollback logs, deployment history.",
    ],
    [
        "Secret Management — Injection of API keys, DB credentials, signing keys into pipeline without exposing in logs or config. Typically invisible when working. Without it: credentials leak in CI logs (a top-10 security incident category).",
        "Pipeline Cache Invalidation — Logic determining when cached dependencies, build layers, or test results must be recomputed. Missed because it is a NON-event (cache hit = no visible action). But stale caches cause the most confusing CI failures: tests pass locally but fail in CI because of cached stale artifacts.",
        "Flaky Test Detection — Mechanism to identify tests that intermittently pass/fail without code changes. Invisible in pipeline design but load-bearing: flaky tests erode team trust in the entire CI system, leading developers to ignore failures and merge anyway.",
    ],
    """Commit → Webhook → Runner → Deps (+ Cache) → Lint → Type Check → Unit Tests → Integration Tests
                                                                                          ↓
                                                                                    Coverage → Build → Artifact → Security Scan
                                                                                                                       ↓
                                                                                              Staging Deploy → Smoke Tests → Approval → Prod Deploy → Health Checks
                                                                                                                                                         ↓ (if fail)
                                                                                                                                                      Rollback
Secret Management (injects into: Runner, Build, Deploy stages)
Flaky Test Detection (monitors: Unit Tests, Integration Tests over time)""",
    """- Suspected: Feature flag integration, database migration steps, notification to team (Slack/email), performance regression tests, infrastructure-as-code validation (Terraform plan).
- Gaps: No modeling of PARALLEL vs SEQUENTIAL stage optimization. No mention of matrix builds (testing across multiple OS/language versions). Missing: developer experience (how long do developers wait? what is the feedback loop cost?).
- Outside view: Most pipeline optimization focuses on making stages faster. The real leverage is in making stages UNNECESSARY for most commits (affected-file detection, test impact analysis).
- Estimated completeness: 75%"""
)),

("Enumerate all components of a production database failure and recovery.",
_enum(
    "Production database failure: causes, detection, failover, and recovery.",
    "INSIDE — all failure modes, detection mechanisms, and recovery procedures. OUTSIDE — application-level error handling beyond DB layer.",
    18,
    [
        "Hardware Failure — Disk, memory, CPU, or power supply failure on the database host.\n   Emerges from: root (physical component degradation) | Gives rise to: Service Interruption | Evidence: Hardware health monitoring, SMART disk stats.",
        "Storage Exhaustion — Disk fills to 100% preventing writes and WAL logging.\n   Emerges from: Data growth + Insufficient capacity planning | Gives rise to: Write Failures, Potential Corruption | Evidence: Disk usage alerts.",
        "Connection Pool Exhaustion — All available DB connections consumed, new requests queued or rejected.\n   Emerges from: Traffic spike + Slow queries + Pool misconfiguration | Gives rise to: Application Timeouts | Evidence: Connection count metrics, pool wait times.",
        "Slow Query Cascade — One slow query holds locks, causing other queries to wait, creating cascading timeouts.\n   Emerges from: Missing index + Large table + Lock contention | Gives rise to: System-wide slowdown | Evidence: Slow query log, lock wait metrics.",
        "Replication Lag — Replica falls behind primary, serving stale data or failing health checks.\n   Emerges from: Write volume exceeding replica apply speed | Gives rise to: Stale reads, Failover complications | Evidence: Replication lag metric (seconds behind).",
        "Network Partition — Network failure between DB and application servers, or between primary and replicas.\n   Emerges from: root (network infrastructure failure) | Gives rise to: Split-brain risk, Connection failures | Evidence: Network monitoring, connectivity tests.",
        "Corruption — Data file corruption from hardware fault, OS bug, or incomplete write during crash.\n   Emerges from: Hardware failure + Crash during write | Gives rise to: Data loss, Inconsistent state | Evidence: Checksum validation, pg_verify_checksums.",
        "Monitoring/Alerting — Systems detecting anomalies: CPU, memory, disk, connections, replication lag, error rates.\n   Emerges from: Observability infrastructure | Gives rise to: Alert → Human response or Automated response | Evidence: Monitoring dashboards, alert history.",
        "Automated Failover — System promotes replica to primary when primary is detected as failed.\n   Emerges from: Health check failure + Failover configuration | Gives rise to: New primary, DNS/endpoint update | Evidence: Failover logs, promotion timestamp.",
        "Connection Rerouting — Application connections redirect from failed primary to new primary.\n   Emerges from: Automated Failover + DNS update or proxy reconfiguration | Gives rise to: Application recovery | Evidence: Connection endpoint change, application reconnection logs.",
        "WAL (Write-Ahead Log) — Transaction log enabling point-in-time recovery by replaying committed transactions.\n   Emerges from: Database write operations | Gives rise to: Recovery capability | Evidence: WAL file sequence, archive status.",
        "Backup System — Regular full and incremental backups stored offsite.\n   Emerges from: Backup schedule + Storage | Gives rise to: Disaster recovery capability | Evidence: Backup completion logs, restoration test results.",
        "Point-in-Time Recovery (PITR) — Restoring database to a specific timestamp using base backup + WAL replay.\n   Emerges from: Backup + WAL archive | Gives rise to: Data recovery to precise moment | Evidence: Recovery logs, recovered state verification.",
        "Data Validation Post-Recovery — Checking recovered data for completeness and consistency.\n   Emerges from: Recovery completion | Gives rise to: Confidence in recovered state | Evidence: Row counts, checksum comparisons, application smoke tests.",
        "Post-Mortem / Root Cause Analysis — Investigation into what failed, why, and how to prevent recurrence.\n   Emerges from: Incident resolution | Gives rise to: Process improvements, Infrastructure changes | Evidence: Post-mortem document, action items.",
    ],
    [
        "DNS TTL Propagation Delay — After failover, DNS changes take time to propagate. Applications caching old DNS may continue connecting to the dead primary for minutes. Typically invisible because it is a TIMING issue, not a component. But it extends effective downtime beyond the failover itself.",
        "Transaction In-Flight Loss — Transactions that were committed on the old primary but not yet replicated to the new primary are LOST during failover. This is the RPO (Recovery Point Objective) gap. Typically missed because people assume failover = zero data loss. For async replication, it is not.",
        "Operator Error — Human mistakes during incident response: running wrong commands, failing over to wrong replica, accidentally dropping tables during recovery. Studies show that 60-80% of extended outages involve operator error during recovery. The recovery process itself is a failure mode.",
    ],
    """Hardware/Network (root causes) → Service Interruption
Storage/Connection/Query (operational causes) → Degraded Performance → Cascading Failure
Monitoring → Alert → Automated Failover → Connection Rerouting → Application Recovery
                                              ↓
                                    DNS TTL Delay (extends downtime)
                                    Transaction In-Flight Loss (data gap)
Backup + WAL → PITR (for corruption/catastrophic cases)
Recovery → Validation → Post-Mortem → Prevention
Operator Error (intersects with ALL recovery steps)""",
    """- Suspected: Cloud provider outage (entire availability zone), misconfigured security group blocking connections, certificate expiration, OOM killer targeting DB process.
- Gaps: No modeling of CASCADING failures across dependent services. Missing: communication during incident (who is notified, status page updates, customer communication). Missing: testing and rehearsal of recovery procedures.
- Outside view: Organizations invest heavily in preventing database failures but inadequately in PRACTICING recovery. The recovery muscle atrophies between incidents. The most impactful improvement is usually not better prevention but more practiced, automated recovery.
- Estimated completeness: 72%"""
)),

# ===== BUSINESS STRATEGY (3) =====

("Enumerate all factors that determine a software company's pricing strategy.",
_enum(
    "Software pricing strategy determination.",
    "INSIDE — all factors influencing price, structure, and communication. OUTSIDE — detailed financial modeling, specific negotiation tactics.",
    18,
    [
        "Customer Willingness to Pay (WTP) — Maximum acceptable price before choosing alternatives.\n   Emerges from: root (budget, pain severity, alternatives) | Gives rise to: Price Ceiling | Evidence: Van Westendorp, conjoint analysis, win/loss data.",
        "Cost Structure — Marginal cost per customer plus allocated fixed costs.\n   Emerges from: Tech architecture, team, infrastructure | Gives rise to: Price Floor | Evidence: Financial statements.",
        "Competitive Pricing — Prices of alternatives (direct competitors, substitutes, DIY).\n   Emerges from: root (market) | Gives rise to: Price Anchoring | Evidence: Competitor sites, G2.",
        "Value Metric — Unit of value perception: per user, per transaction, per GB, per outcome.\n   Emerges from: Customer value perception + Product architecture | Gives rise to: Pricing Model | Evidence: Customer interviews.",
        "Customer Segmentation — Groups with different WTP, usage, and needs.\n   Emerges from: Market analysis | Gives rise to: Tiered pricing | Evidence: Usage clustering, revenue per segment.",
        "Pricing Model — Subscription, usage-based, freemium, one-time, hybrid.\n   Emerges from: Value Metric + Customer preference + Revenue predictability | Gives rise to: Revenue pattern | Evidence: Market testing.",
        "Perceived Value — Subjective assessment of price fairness.\n   Emerges from: Price Anchoring + Quality + Brand + Social Proof | Gives rise to: Purchase Decision | Evidence: NPS, conversion rates.",
        "Expansion Revenue — Upsells, cross-sells, usage growth, seat expansion mechanics.\n   Emerges from: Product architecture + Pricing model | Gives rise to: Net Revenue Retention, LTV | Evidence: Expansion MRR.",
        "Switching Costs — Customer cost to leave: data migration, retraining, integration rebuilding.\n   Emerges from: Product design + Customer investment | Gives rise to: Pricing Power | Evidence: Churn analysis.",
        "Discount Strategy — Volume, annual prepay, nonprofit, startup, negotiated enterprise rules.\n   Emerges from: Sales strategy + Segmentation | Gives rise to: Effective Price | Evidence: Discount frequency.",
        "Psychological Pricing — Cognitive biases: charm pricing ($99), decoy effect, price-quality heuristic.\n   Emerges from: Behavioral economics | Gives rise to: Conversion variation | Evidence: A/B tests.",
        "Price Communication — Pricing page design, sales deck, quote structure, transparency.\n   Emerges from: Marketing + Pricing model | Gives rise to: Customer understanding, trust | Evidence: Page analytics.",
        "Regulatory Constraints — Anti-discrimination, transparency, healthcare, government contract rules.\n   Emerges from: root (legal environment) | Gives rise to: Pricing constraints | Evidence: Legal review.",
        "Currency and Geography — Exchange rates, PPP, local market norms.\n   Emerges from: root (geographic markets) | Gives rise to: Regional variation | Evidence: Local competitor pricing.",
    ],
    [
        "Sales Compensation Alignment — How salespeople are paid (commission on booking vs. collections, upsell vs. new) directly determines what prices they push and discounts they offer. Compensation on bookings drives aggressive discounting. Typically classified as HR, not pricing — but it is the mechanism through which pricing strategy is executed or undermined.",
        "Price as Quality Signal — In enterprise software and consulting, LOW price signals low quality and REDUCES demand. Raising price can increase sales by premium positioning. Contradicts the economic assumption that lower prices increase demand. True in information-asymmetric markets where buyers use price as quality proxy.",
        "Customer Budget Cycle — Whether the buyer has annual allocation, quarterly approval, or discretionary authority determines WHEN they can buy and at what size. A $50K product easy for a VP with discretionary authority, impossible for a team needing CFO approval. The same price hits differently depending on purchasing process.",
    ],
    """WTP → Price Ceiling; Cost Structure → Price Floor
Competitive Pricing → Anchoring → Perceived Value → Purchase Decision
Segmentation → Tiers → Value Metric → Model → Price Point
Switching Costs → Pricing Power → Price latitude
Expansion Revenue → LTV → Acceptable CAC → Discount Strategy
Sales Compensation → Actual discounting → Effective Price (diverges from list)
Budget Cycle → Purchase timing → Revenue Recognition → Model choice""",
    """- Suspected: Channel/partner pricing, bundling strategy, free trial dynamics, price grandfathering, inflation adjustment.
- Gaps: Dynamic pricing evolution as product matures. Price versioning and migration strategy.
- Outside view: Pricing is not a number but a SYSTEM of signals. Most pricing discussions focus on the number while ignoring what it communicates about value, customer, and positioning.
- Estimated completeness: 73%"""
)),

("Enumerate all components of customer churn in a SaaS business.",
_enum(
    "SaaS customer churn: causes, signals, prevention, and measurement.",
    "INSIDE — all factors driving, predicting, and preventing churn. OUTSIDE — acquisition process, long-term market dynamics.",
    18,
    [
        "Product-Market Fit Gap — The product doesn't solve the customer's core problem well enough.\n   Emerges from: root (product vs. market alignment) | Gives rise to: Declining Usage | Evidence: Feature utilization data, customer feedback.",
        "Onboarding Failure — Customer never reaches 'aha moment' where they experience core value.\n   Emerges from: Complex product + Insufficient guidance | Gives rise to: Early-stage churn | Evidence: Time-to-first-value metrics, onboarding completion rate.",
        "Value Realization Gap — Customer expected outcome X from the product but experienced outcome Y.\n   Emerges from: Sales over-promise + Product under-delivery | Gives rise to: Disappointment, NPS decline | Evidence: Expected vs. actual outcomes survey.",
        "Champion Departure — The internal advocate who bought/pushed the product leaves the company.\n   Emerges from: root (employee turnover) | Gives rise to: Loss of institutional support for product | Evidence: Contact change notifications, login pattern changes.",
        "Competitor Switch — Customer finds a better or cheaper alternative.\n   Emerges from: Competitive landscape evolution | Gives rise to: Active cancellation | Evidence: Exit surveys, competitive mentions.",
        "Budget Cut — Customer's organization reduces spending, and the product is not essential enough to survive cuts.\n   Emerges from: root (customer's financial situation) | Gives rise to: Cost-driven cancellation | Evidence: Exit surveys, downturn timing correlation.",
        "Usage Decline Trajectory — Gradual decrease in product usage over weeks/months preceding cancellation.\n   Emerges from: Multiple factors (value gap, champion loss, competing priorities) | Gives rise to: Predictive churn signal | Evidence: Login frequency, feature usage trends.",
        "Support Experience — Poor support interactions eroding customer trust and satisfaction.\n   Emerges from: Support team quality + Ticket volume + Response time | Gives rise to: Relationship damage | Evidence: CSAT scores, support ticket sentiment.",
        "Missing Feature — Customer needs a capability the product lacks.\n   Emerges from: Product roadmap gap + Customer requirements evolution | Gives rise to: Feature-driven churn | Evidence: Feature request frequency, exit surveys.",
        "Integration/Workflow Disruption — Product doesn't fit into the customer's evolved workflow.\n   Emerges from: Customer's tech stack changes | Gives rise to: Friction, workarounds, eventual departure | Evidence: Integration usage, API call patterns.",
        "Pricing Dissatisfaction — Customer perceives price-to-value ratio as unfavorable, especially at renewal with price increases.\n   Emerges from: Price increases + Perceived value plateau | Gives rise to: Renewal resistance | Evidence: Renewal negotiation frequency, discount requests.",
        "Churn Prediction Model — ML model scoring accounts for churn likelihood based on usage, support, billing signals.\n   Emerges from: Historical churn data + Feature engineering | Gives rise to: Intervention triggers | Evidence: Model accuracy metrics, intervention outcomes.",
        "Customer Success Intervention — Proactive outreach triggered by churn signals: health checks, QBRs, training, feature adoption campaigns.\n   Emerges from: Churn Prediction + CS team | Gives rise to: Churn prevention (some %) | Evidence: Intervention vs. non-intervention cohort retention.",
        "Renewal Process — Mechanics of contract renewal: timing, pricing, negotiation, auto-renewal terms.\n   Emerges from: Contract terms + CS relationship | Gives rise to: Renewal outcome | Evidence: Renewal rate, renewal timing.",
    ],
    [
        "Involuntary Churn (Failed Payments) — Credit cards expire, payment methods fail, and customers churn NOT because they chose to leave but because billing failed silently. Typically accounts for 20-40% of total churn in PLG SaaS. Invisible in 'reasons for churn' analysis because the customer didn't actively cancel. Solvable with dunning sequences and card updaters.",
        "Negative Word-of-Mouth Multiplier — Each churned customer who had a bad experience tells 5-15 others, reducing future acquisition. Missed because it is a SECOND-ORDER effect that appears in acquisition metrics, not churn metrics. But the damage from a vocal detractor can exceed the revenue lost from their own churn.",
        "Sunk Cost Accumulation — Customers who have invested heavily in the product (custom configurations, training, data) are significantly less likely to churn, independent of satisfaction. This 'stickiness through investment' is a churn prevention mechanism that appears nowhere in satisfaction surveys but dominates retention math.",
    ],
    """PMF Gap → Usage Decline → Churn Signal → Prediction Model → CS Intervention → (prevented or not)
Champion Loss → Support Vacuum → Usage Decline
Competitor Emergence → Evaluation → Switch
Budget Cut → Cost Review → Cancellation
Failed Payment → Involuntary Churn (parallel track, often undetected)
Onboarding Failure → Never Reach Value → Early Churn (first 90 days)""",
    """- Suspected: Seasonal patterns, account consolidation (customer acquired, accounts merged), product quality regression, security/compliance change making product non-viable.
- Gaps: No modeling of POSITIVE churn (customer graduates from the product, having achieved their goal — this is healthy churn). Missing: the relationship between acquisition QUALITY and churn (customers acquired through deep discounts churn at 2-3x normal rate).
- Outside view: Most churn analysis looks at WHY customers leave. The more valuable analysis is WHY customers STAY — understanding retention drivers reveals what to invest in more effectively than fixing churn reasons.
- Estimated completeness: 74%"""
)),

("Enumerate all factors that determine whether a software startup succeeds or fails.",
_enum(
    "Software startup success/failure determinants over the first 5 years.",
    "INSIDE — all factors influencing PMF and sustainable revenue. OUTSIDE — non-software specifics, post-scale dynamics.",
    20,
    [
        "Founder-Market Fit — Depth of founding team's understanding of the problem.\n   Emerges from: root (prior experience) | Gives rise to: Problem Definition Quality | Evidence: Founder backgrounds.",
        "Problem Severity — How painful the problem is; willingness to pay and urgency.\n   Emerges from: root (market condition) | Gives rise to: WTP, Sales Velocity | Evidence: Customer discovery.",
        "Timing — Market conditions, tech readiness, customer awareness alignment.\n   Emerges from: root (macro) | Gives rise to: Adoption Rate | Evidence: Theorized (Bill Gross: #1 factor).",
        "Team Composition — Skills, experience, personality complementarity.\n   Emerges from: Founder decisions | Gives rise to: Execution Velocity | Evidence: Team backgrounds.",
        "Co-founder Relationship — Trust, communication, conflict resolution.\n   Emerges from: root (pre-existing) | Gives rise to: Decision Speed | Evidence: Relationship longevity.",
        "Capital Availability — Funding relative to burn rate.\n   Emerges from: Investor Interest | Gives rise to: Runway, Hiring | Evidence: Bank balance.",
        "Product-Market Fit — Product satisfies strong market demand.\n   Emerges from: Problem Severity + Solution Quality + Timing | Gives rise to: Organic Growth, Retention | Evidence: Sean Ellis survey (>40% 'very disappointed').",
        "Technical Architecture — Stack, infrastructure, data model choices.\n   Emerges from: CTO/technical founder | Gives rise to: Dev Velocity, Scalability | Evidence: Codebase review.",
        "Distribution Strategy — Self-serve, sales-led, viral, content-driven.\n   Emerges from: Market + Pricing + Team | Gives rise to: CAC, Growth Rate | Evidence: Channel metrics.",
        "Unit Economics — LTV:CAC ratio viability.\n   Emerges from: LTV + CAC | Gives rise to: Business Viability | Evidence: Financial model. LTV:CAC > 3 healthy.",
        "Retention/Churn — Customer continuation rate.\n   Emerges from: PMF + Solution Quality | Gives rise to: LTV, Revenue Stability | Evidence: Cohort curves.",
        "Competitive Landscape — Alternatives available to target customers.\n   Emerges from: root (market) | Gives rise to: Differentiation Requirement | Evidence: Market research.",
        "Moat/Defensibility — Network effects, switching costs, data advantages.\n   Emerges from: Product Design + Market Position | Gives rise to: Long-term Sustainability | Evidence: Business model analysis.",
        "Culture — How the team decides, prioritizes, handles disagreement.\n   Emerges from: Founder Values | Gives rise to: Execution Quality, Retention | Evidence: Employee retention.",
        "Hiring Ability — Capacity to attract talent at needed quality and speed.\n   Emerges from: Capital + Culture + Reputation | Gives rise to: Team Quality | Evidence: Offer acceptance rate.",
    ],
    [
        "Founder Mental Health — Psychological resilience through 3-5 years of uncertainty and rejection. Y Combinator notes significant percentage of startups die not from market failure but founder exhaustion. Categorized as personal, not business, but often the actual cause of death.",
        "Narrative Quality — Clarity and compellingness of the startup's story to investors, employees, and customers. Seems like 'marketing' but determines fundraising success, talent attraction, press coverage, and customer trust. Two identical products with different narratives have dramatically different outcomes.",
        "Spouse/Partner Support — Whether the founder's life partner supports the startup's demands. Noam Wasserman's research: personal relationship strain is a significant contributor to founder departure, divorce/breakup correlates strongly with startup failure.",
    ],
    """Founder-Market Fit → Problem Definition → Solution → PMF
Timing + Problem Severity → Adoption
Team → Dev Velocity → Iteration → PMF (feedback loop)
Capital → Runway → Pivot Capacity
PMF → Retention → LTV → Unit Economics → Viability
Distribution → CAC → Unit Economics
Founder Mental Health → Continuation → Survival (invisible but load-bearing)""",
    """- Suspected: Luck, macro conditions, platform dependencies, geographic effects.
- Gaps: FEEDBACK LOOPS — success compounds and failure compounds. PMF → retention → revenue → capital → hiring → product → PMF.
- Outside view: This enumeration is biased toward CONTROLLABLE factors. Much success is determined by uncontrollable factors (timing, luck, macro). Controllable factors determine POSITIONING; uncontrollable factors determine conversion.
- Estimated completeness: 72%"""
)),

# ===== REMAINING DOMAINS (21 more examples) =====
# Each follows the full Samkhya method with enumeration, non-obvious components,
# causal chain, and completeness audit.

("Enumerate all components of the human immune response to a novel virus.",
_enum("Human immune response from exposure to memory formation.",
    "INSIDE — all biological components from viral entry to immune memory. OUTSIDE — epidemiology, treatment.",
    20,
    ["Viral Entry — Virus crosses epithelial barriers via receptor binding.\n   Emerges from: root (exposure) | Gives rise to: Innate Activation | Evidence: PCR, viral load.",
     "Pattern Recognition Receptors (PRRs) — TLRs, RIG-I, cGAS-STING detect pathogen patterns.\n   Emerges from: root (genetic) | Gives rise to: Signaling Cascades | Evidence: Molecular biology.",
     "Interferon Response — Type I IFNs signal antiviral state in neighboring cells.\n   Emerges from: PRR activation | Gives rise to: Antiviral State, NK activation | Evidence: Serum levels.",
     "Natural Killer Cells — Innate lymphocytes killing infected cells via missing-self recognition.\n   Emerges from: Bone marrow + IFN activation | Gives rise to: Infected cell death | Evidence: Flow cytometry.",
     "Complement System — Plasma proteins tagging pathogens, recruiting immune cells, lysing pathogens.\n   Emerges from: root (constitutive) | Gives rise to: Opsonization, MAC | Evidence: Serum levels.",
     "Inflammation — Vasodilation, permeability increase, immune cell recruitment.\n   Emerges from: PRR + Complement + DAMPs | Gives rise to: Immune recruitment, tissue damage | Evidence: CRP, IL-6.",
     "Neutrophils — First-responder phagocytes: oxidative burst, NETs.\n   Emerges from: Inflammation | Gives rise to: Pathogen killing | Evidence: Neutrophil counts.",
     "Macrophages — Phagocytosis and antigen presentation.\n   Emerges from: Inflammation + IFN | Gives rise to: Antigen Presentation | Evidence: Flow cytometry.",
     "Dendritic Cells — Sentinel cells capturing antigen, migrating to lymph nodes.\n   Emerges from: Viral entry + PRR | Gives rise to: T Cell Activation (bridge innate→adaptive) | Evidence: DC tracking.",
     "MHC Antigen Presentation — Processed viral peptides on MHC I (CD8) and MHC II (CD4).\n   Emerges from: DC processing | Gives rise to: T cell recognition | Evidence: MHC-peptide detection.",
     "CD4+ T Helper Activation — Differentiation into Th1, Th2, Tfh subtypes.\n   Emerges from: MHC II + Co-stimulation | Gives rise to: B cell help, macrophage activation | Evidence: Cytokine profiling.",
     "CD8+ Cytotoxic T Cell Activation — CTLs that kill infected cells specifically.\n   Emerges from: MHC I + Co-stimulation + CD4 help | Gives rise to: Specific cell killing | Evidence: Tetramer staining.",
     "B Cell Activation — BCR antigen recognition + Tfh help → antibody production.\n   Emerges from: Antigen + Tfh | Gives rise to: Germinal Center, Antibodies | Evidence: B cell proliferation.",
     "Germinal Center Reaction — Somatic hypermutation and affinity maturation.\n   Emerges from: B activation + Tfh | Gives rise to: High-affinity antibodies, memory cells | Evidence: Affinity over time.",
     "Antibody Production — Plasma cells secrete IgM, IgG, IgA.\n   Emerges from: GC reaction | Gives rise to: Neutralization, ADCC | Evidence: Serum titers.",
     "Viral Neutralization — Antibodies block receptor binding.\n   Emerges from: Neutralizing antibodies | Gives rise to: Reduced infectivity | Evidence: Neutralization assays.",
     "Regulatory T Cells — Suppress excessive response, prevent autoimmunity.\n   Emerges from: Thymic + Peripheral induction | Gives rise to: Immune calibration | Evidence: FoxP3+ counts.",
     "Memory Formation — Memory T and B cells persist for years; bone marrow plasma cells.\n   Emerges from: Activation + Contraction | Gives rise to: Long-term immunity | Evidence: Tetramer staining years later.",
     ],
    ["Trained Innate Immunity — Epigenetic reprogramming of monocytes/NK cells after infection enhancing response to UNRELATED future pathogens. Paradigm shift: innate immunity was believed to have no memory. BCG vaccination enhances innate responses to non-mycobacterial infections.",
     "Mucosal Immune Compartment — Distinct immune system at mucosal surfaces (secretory IgA, tissue-resident memory T cells). For respiratory viruses, mucosal response determines mild vs. severe independent of serum antibody levels.",
     "Viral Immune Evasion — The virus actively shapes the immune response: IFN antagonism, MHC downregulation, antigenic variation. The enumeration above assumes a passive target, but novel viruses actively co-evolve with the immune system.",
    ],
    """Viral Entry → PAMPs → PRRs → IFN + Inflammation + Complement
IFN → Antiviral State + NK Cells
Inflammation → Neutrophils + Macrophages
DCs → Migration → Antigen Presentation → CD4 + CD8 T Cells
CD4 Tfh → B Cells → GC → Antibodies → Neutralization + ADCC
Tregs → Modulate (negative feedback)
Contraction → Memory T + Memory B + Long-lived Plasma Cells""",
    """- Suspected: Microbiome, metabolic state, stress hormones, sleep quality effects.
- Gaps: Age variation (immunosenescence), genetic variation (HLA polymorphism).
- Outside view: The immune system is equally a DAMAGE system. Much morbidity comes from the immune response itself (cytokine storm, autoimmune sequelae).
- Estimated completeness: 70%"""
)),

# Compact examples for remaining domains — each follows full Samkhya method

("Enumerate all components of climate change feedback loops.",
_enum("Climate feedback mechanisms — positive and negative.", "INSIDE — all major feedback loops affecting global temperature. OUTSIDE — mitigation policies, human adaptation.", 18,
["Ice-Albedo Feedback — Ice melts → darker surface absorbs more heat → more melting.\n   Emerges from: Warming | Gives rise to: Accelerated warming | Evidence: Satellite albedo measurements.",
 "Water Vapor Feedback — Warming → more evaporation → more atmospheric water vapor (GHG) → more warming.\n   Emerges from: Warming | Gives rise to: Amplified warming (~2x) | Evidence: Humidity measurements.",
 "Cloud Feedback — Complex: warming changes cloud type/coverage. Low clouds cool, high clouds warm.\n   Emerges from: Temperature + Humidity changes | Gives rise to: Net uncertain effect (largest uncertainty in models) | Evidence: Satellite cloud data, model disagreement.",
 "Permafrost Thaw — Warming thaws permafrost → releases methane and CO2 → more warming.\n   Emerges from: Arctic warming | Gives rise to: GHG release, ground subsidence | Evidence: Methane measurements, ground temperature data.",
 "Ocean Heat Absorption — Oceans absorb ~90% of excess heat, slowing atmospheric warming.\n   Emerges from: Energy imbalance | Gives rise to: Delayed atmospheric warming, thermal expansion | Evidence: Argo float data.",
 "CO2 Fertilization — Higher CO2 → increased plant growth → more CO2 uptake (negative feedback).\n   Emerges from: Elevated CO2 | Gives rise to: Partial CO2 removal | Evidence: Satellite greenness indices. Saturates at high CO2.",
 "Ocean CO2 Absorption — Oceans absorb ~25% of anthropogenic CO2.\n   Emerges from: CO2 concentration gradient | Gives rise to: Reduced atmospheric CO2 + Ocean acidification | Evidence: pCO2 measurements.",
 "Vegetation Shift — Warming changes biome distribution: boreal forest expands into tundra (darker, absorbs more heat).\n   Emerges from: Temperature change | Gives rise to: Albedo change, carbon cycle change | Evidence: Satellite land cover data.",
 "Methane Hydrate Release — Ocean warming destabilizes seabed methane clathrates.\n   Emerges from: Ocean warming | Gives rise to: Large-scale methane release (potential tipping point) | Evidence: Seabed surveys, paleo record.",
 "Weathering Feedback — Warming + CO2 → increased chemical weathering of rocks → CO2 drawdown (very slow negative feedback).\n   Emerges from: Temperature + CO2 | Gives rise to: Long-term CO2 removal (10K-100K year timescale) | Evidence: Geochemical models.",
 "Ocean Circulation Changes — Warming + ice melt freshwater → potential AMOC slowdown → regional cooling despite global warming.\n   Emerges from: Temperature + salinity changes | Gives rise to: Regional climate disruption | Evidence: AMOC monitoring, RAPID array.",
 "Wildfire-Climate Feedback — Warming → drought → more wildfires → CO2 release → more warming.\n   Emerges from: Drought + Temperature | Gives rise to: CO2/aerosol release, vegetation loss | Evidence: Fire frequency data, emissions estimates.",
],
["Soil Carbon Feedback — Warming accelerates microbial decomposition of soil organic carbon, releasing CO2. Soils contain 2x more carbon than the atmosphere. Typically invisible because it is underground and slow, but the total potential release dwarfs many other feedbacks.",
 "Aerosol Masking Reduction — As air pollution decreases (cleaner energy), aerosol cooling effect diminishes, revealing underlying warming. The paradox: cleaning the air accelerates visible warming. Missed because it conflates two positive trends (cleaner air, climate action).",
 "Marine Biological Pump Weakening — Ocean warming reduces nutrient upwelling → reduces phytoplankton → reduces biological CO2 sequestration. Phytoplankton produce 50% of Earth's oxygen and are a major carbon sink. Their decline is one of the most underreported climate feedbacks.",
],
"""Warming → Ice-Albedo (positive) → More Warming
Warming → Water Vapor (positive, ~2x amplifier)
Warming → Permafrost Thaw → Methane/CO2 (positive, potential tipping point)
Warming → Ocean Heat Absorption (slows atmosphere, delays response)
CO2 → Ocean Absorption (negative) + Acidification (separate problem)
CO2 → Fertilization (negative, saturating)
Warming → Wildfire → CO2 (positive)
Warming → Soil Carbon (positive, slow, massive potential)
All positive feedbacks create risk of cascading: if one tipping point triggers another""",
"""- Suspected: Jet stream destabilization, monsoon disruption, deep ocean heat redistribution, dust/iron fertilization changes.
- Gaps: INTERACTION EFFECTS between feedbacks — they do not operate independently. Permafrost thaw + wildfire + soil carbon could cascade. No modeling of tipping point cascades.
- Outside view: The system is dominated by positive (amplifying) feedbacks. The negative feedbacks operate on longer timescales or are saturating. This asymmetry means the system has a tendency toward runaway warming that negative feedbacks cannot match on human-relevant timescales.
- Estimated completeness: 68%"""
)),

("Enumerate all components of the scientific peer review process.",
_enum("Scientific peer review from submission to publication.", "INSIDE — all stages, roles, and quality mechanisms. OUTSIDE — funding decisions, post-publication impact.", 16,
["Manuscript Submission — Author submits to journal via editorial management system.\n   Emerges from: Research completion | Gives rise to: Editorial Screening | Evidence: Submission records.",
 "Editorial Screening — Editor-in-Chief or handling editor assesses scope, quality, plagiarism.\n   Emerges from: Submission | Gives rise to: Desk Reject or Reviewer Assignment | Evidence: Editorial decision logs.",
 "Reviewer Selection — Editor identifies 2-4 qualified, unconflicted reviewers.\n   Emerges from: Editorial decision to review | Gives rise to: Review Invitations | Evidence: Reviewer database, invitation records.",
 "Peer Review — Reviewers evaluate methods, results, novelty, significance. Produce reports.\n   Emerges from: Reviewer acceptance + Manuscript | Gives rise to: Review Reports | Evidence: Written reviews.",
 "Review Criteria — Methodology rigor, statistical validity, novelty, significance, clarity, ethical compliance.\n   Emerges from: Journal standards + Field norms | Gives rise to: Review structure | Evidence: Reviewer guidelines.",
 "Editorial Decision — Editor synthesizes reviews into accept/revise/reject.\n   Emerges from: Review Reports + Editorial judgment | Gives rise to: Author notification | Evidence: Decision letter.",
 "Author Revision — Authors address reviewer concerns, modify manuscript, write rebuttal.\n   Emerges from: Revision request | Gives rise to: Revised submission | Evidence: Tracked changes, response letter.",
 "Second Review Round — Reviewers assess adequacy of revisions.\n   Emerges from: Revised manuscript | Gives rise to: Final decision | Evidence: Second-round reviews.",
 "Acceptance and Copyediting — Manuscript enters production: copyediting, typesetting, proof review.\n   Emerges from: Final acceptance | Gives rise to: Published article | Evidence: Production records.",
 "Publication — Article appears in journal, receives DOI, indexed in databases.\n   Emerges from: Production completion | Gives rise to: Public access, citation ability | Evidence: DOI, database listing.",
],
["Reviewer Bias — Reviewers' institutional affiliations, personal relationships, competitive interests, and methodological preferences systematically influence evaluations. Double-blind review reduces but does not eliminate (reviewers often identify authors from methods, datasets, citations). Missed because it is considered an individual failing, not a system component — but it is structural.",
 "Publication Bias — Journals systematically prefer positive/novel results over null/replication results. This shapes what gets submitted (authors self-censor null results), reviewed (editors desk-reject replications), and published. The 'file drawer problem' means the published literature is a biased sample of all research conducted.",
 "Reviewer Fatigue / Incentive Misalignment — Reviewing is unpaid labor consuming 10-20 hours per manuscript. Reviewers are incentivized to be fast (time pressure) not thorough. The system depends on altruism at scale, which is eroding as publication volume grows. This creates a systemic quality floor that is declining.",
 "Speed-Quality Tradeoff — Editorial pressure to reduce review times (journals compete on speed) directly conflicts with thorough review. Fast decisions attract submissions but may reduce review quality.",
],
"""Submission → Editorial Screen → (Desk Reject OR Reviewer Selection)
Reviewer Selection → Review → Reports → Editorial Decision
Decision → (Accept OR Revision OR Reject)
If Revision: Author Revision → Second Review → Final Decision
If Accept: Copyediting → Publication
Reviewer Bias (influences: all review stages)
Publication Bias (influences: editorial screening, editorial decision)""",
"""- Suspected: Gaming behaviors (citation rings, reviewer recommendation manipulation), AI-generated text detection challenges, post-publication review erosion.
- Gaps: No modeling of OPEN PEER REVIEW alternatives (registered reports, post-publication review). Missing: the role of preprints in bypassing/supplementing traditional review.
- Outside view: The system is designed to prevent bad science from being published. It is less effective at ensuring good science IS published (false negatives). The most consequential failure mode is not publishing bad papers but blocking novel, paradigm-shifting work.
- Estimated completeness: 70%"""
)),

("Enumerate all factors in deciding whether to relocate to a new city for a job.", _enum("City relocation decision factors.", "INSIDE — personal, professional, financial, social factors. OUTSIDE — the job search itself.", 16,
["Compensation Delta — New total comp vs. current, adjusted for cost of living.\n   Emerges from: Offer + Current comp | Gives rise to: Financial viability | Evidence: Offer letter, COL calculators.",
 "Cost of Living — Housing, taxes, transport, food, healthcare differences.\n   Emerges from: root (geography) | Gives rise to: Real income change | Evidence: COL indices.",
 "Career Trajectory — Advancement speed, learning, positioning.\n   Emerges from: Role + Company growth + Industry | Gives rise to: Long-term earning potential | Evidence: Company trajectory.",
 "Partner Career Impact — Whether partner can find equivalent employment.\n   Emerges from: Partner's industry + Target market | Gives rise to: Household income, relationship | Evidence: Job listings.",
 "Children's Education — School quality, disruption, social adjustment.\n   Emerges from: Family composition + Target schools | Gives rise to: Child wellbeing | Evidence: School ratings.",
 "Social Network — Friends, community, support systems.\n   Emerges from: Years in current city | Gives rise to: Emotional wellbeing | Evidence: Self-assessment.",
 "Family Proximity — Distance from parents, siblings; eldercare duties.\n   Emerges from: Family geography | Gives rise to: Emotional connection | Evidence: Travel time/cost.",
 "Climate and Environment — Weather, outdoors, air quality.\n   Emerges from: root (geography) | Gives rise to: Daily quality of life | Evidence: Climate data.",
 "Healthcare Access — Facilities, specialists, insurance networks.\n   Emerges from: root (city infrastructure) | Gives rise to: Health outcomes | Evidence: Hospital ratings.",
 "Company Stability — Financial health, longevity likelihood.\n   Emerges from: Company financials | Gives rise to: Job security | Evidence: Filings, Glassdoor.",
 "Moving Costs — Physical: movers, travel, temp housing, deposits.\n   Emerges from: Distance + Household size + Relocation package | Gives rise to: Upfront financial impact | Evidence: Moving quotes.",
 "Cultural Fit — City values, demographics, lifestyle match.\n   Emerges from: Personal values + City character | Gives rise to: Long-term satisfaction | Evidence: City visits.",
],
["Identity Disruption — Relocation forces renegotiation of personal identity ('I'm a New Yorker'). Psychological, not financial, but explains why rational-on-paper moves cause unhappiness.",
 "Decision Reversibility — How easy to UNDO the move if it fails? Selling house + moving cross-country + job doesn't work = enormous reversal cost. Keeping apartment + trying 6 months = low reversal cost. This asymmetry should dominate but is rarely discussed.",
 "Seasonal Affective Reality — People evaluate cities during best season (visiting in summer) but live year-round. Gap between visit-impression and lived-reality is major regret source.",
],
"""Offer → Comp Delta → Financial Viability ← COL
Partner Career → Household Income
Social Network + Family → Emotional Wellbeing
Climate + Culture → Long-term Satisfaction
Company Stability → Job Security
Identity Disruption + Reversibility → Psychological Risk""",
"""- Suspected: Political environment, dating market, visa constraints, pet-friendliness.
- Gaps: Time dynamics (some factors improve, others worsen). Decision weighting process.
- Outside view: Most decisions are driven by Comp Delta (#1) while actual satisfaction is driven by Social Network, Climate, Cultural Fit, and Identity — the hard-to-quantify factors.
- Estimated completeness: 75%"""
)),

("Enumerate all factors in deciding whether to pursue a graduate degree.", _enum("Graduate degree decision factors.", "INSIDE — personal, financial, career, and intellectual factors. OUTSIDE — specific program selection.", 16,
["Career Requirement — Whether the target career path requires the degree (academia, medicine, law) vs. prefers it vs. is indifferent.\n   Emerges from: Career goal + Industry norms | Gives rise to: Necessity assessment | Evidence: Job postings, career trajectories.",
 "Financial Cost — Tuition, fees, materials, living expenses for program duration.\n   Emerges from: Program pricing + Duration | Gives rise to: Total investment | Evidence: Program websites.",
 "Opportunity Cost — Foregone salary and career advancement during study.\n   Emerges from: Current salary + Advancement trajectory | Gives rise to: Total true cost | Evidence: Salary data.",
 "Expected Salary Premium — Additional earning power attributable to the degree.\n   Emerges from: Degree + Industry | Gives rise to: ROI calculation | Evidence: BLS data, alumni surveys.",
 "Intellectual Motivation — Genuine desire to study the field deeply.\n   Emerges from: root (personal interest) | Gives rise to: Intrinsic satisfaction, completion likelihood | Evidence: Self-assessment.",
 "Network Access — Peers, professors, alumni network provided by the program.\n   Emerges from: Program quality + Cohort | Gives rise to: Professional connections | Evidence: Alumni outcomes.",
 "Credential Signaling — Degree as quality signal to employers/clients.\n   Emerges from: Program prestige + Degree type | Gives rise to: Career access | Evidence: Hiring data.",
 "Alternative Paths — Can the same career outcome be achieved without the degree (experience, certifications, portfolio)?\n   Emerges from: Industry norms | Gives rise to: Necessity calibration | Evidence: Success stories of non-degreed professionals.",
 "Life Stage Fit — Whether current life circumstances (age, family, financial stability) align with full-time/part-time study.\n   Emerges from: Personal situation | Gives rise to: Feasibility assessment | Evidence: Self-assessment.",
 "Program Quality — Ranking, faculty, curriculum relevance, outcomes data.\n   Emerges from: Institution + Department | Gives rise to: Degree value | Evidence: Rankings, outcomes reports.",
 "Funding Availability — Scholarships, assistantships, employer sponsorship, loans.\n   Emerges from: Program + Applicant profile | Gives rise to: Net cost | Evidence: Financial aid offers.",
 "Completion Rate — Likelihood of finishing (PhD programs: ~50% attrition).\n   Emerges from: Program culture + Student fit + Advisor relationship | Gives rise to: Risk of sunk cost | Evidence: Program completion data.",
],
["Advisor Relationship Quality — For research degrees (PhD, thesis masters), the advisor relationship determines: intellectual direction, publication opportunities, career connections, timeline, and emotional wellbeing. A bad advisor can make a good program miserable. Typically treated as a secondary factor but is the #1 predictor of PhD student satisfaction and completion.",
 "Identity Investment — Pursuing a graduate degree is partly about BECOMING someone (a scientist, a lawyer, an expert). This identity investment can trap people in programs that are not serving them well because leaving feels like abandoning who they are becoming.",
 "Cohort Quality — The intelligence, ambition, and diversity of classmates. In MBA programs, the cohort IS the product — peers teach each other more than professors. In PhD programs, cohort provides emotional support through isolation. Typically treated as random but is a primary value driver.",
],
"""Career Requirement → Necessity (if required: strong push; if optional: weigh alternatives)
Financial Cost + Opportunity Cost → Total Investment
Expected Premium → ROI ← Total Investment
Funding → Net Cost → ROI (if funded: cost near zero, changes calculation entirely)
Intellectual Motivation → Completion Likelihood + Satisfaction
Alternative Paths → Necessity Calibration (if alternatives exist: weaker case)""",
"""- Suspected: Geographic constraint (willing to relocate?), partner support, mental health preparedness for PhD isolation, job market timing.
- Gaps: No modeling of the TIMING dimension — a degree at 25 has different ROI than at 45 due to remaining career years. Also missing: the option value of NOT committing yet.
- Outside view: The decision is usually framed as 'should I get this degree?' when the better frame is 'what is the most efficient path to my career goal?' The degree may or may not be on that path.
- Estimated completeness: 74%"""
)),

# --- Remaining 15 compact examples covering all domains ---

("Enumerate all components involved when a web page loads slowly.", _enum("Web page slow load — all contributing factors.", "INSIDE — network, server, client. OUTSIDE — user device specs.", 18,
["DNS Resolution — Domain to IP lookup through cache hierarchy.\n   Emerges from: URL entry | Gives rise to: TCP connection | Evidence: DNS timing.",
 "TCP + TLS Handshake — Connection establishment + encryption setup.\n   Emerges from: DNS | Gives rise to: Secure channel | Evidence: DevTools connection timing.",
 "Server Processing — Backend logic, database queries, template rendering (TTFB).\n   Emerges from: Request arrival | Gives rise to: HTML response | Evidence: Server APM.",
 "Database Queries — SQL execution: missing indexes, N+1, lock contention.\n   Emerges from: App logic | Gives rise to: Data for page | Evidence: Slow query log.",
 "Response Transfer — HTML over network.\n   Emerges from: Server response | Gives rise to: Browser receipt | Evidence: Content download time.",
 "HTML Parsing — DOM tree construction.\n   Emerges from: HTML receipt | Gives rise to: Resource discovery | Evidence: Performance API.",
 "Render-Blocking CSS — Stylesheets that must load before first paint.\n   Emerges from: link tags in head | Gives rise to: Render delay | Evidence: Coverage tab.",
 "Render-Blocking JS — Synchronous scripts blocking DOM parsing.\n   Emerges from: Script tags without async/defer | Gives rise to: Parse delay | Evidence: Performance timeline.",
 "JS Bundle Size — Total JavaScript bytes to download and parse.\n   Emerges from: App code + Dependencies | Gives rise to: Download + Parse time | Evidence: Bundle analyzer.",
 "Image Loading — Download and decode of images.\n   Emerges from: HTML/CSS references | Gives rise to: Visual completeness, layout shift | Evidence: Image sizes.",
 "Third-Party Scripts — Analytics, ads, chat, social embeds.\n   Emerges from: Business requirements | Gives rise to: Additional DNS/TCP, main thread contention | Evidence: Third-party timing.",
 "Web Fonts — Custom font download causing FOIT/FOUT.\n   Emerges from: CSS @font-face | Gives rise to: Text rendering delay | Evidence: Font download timing.",
 "JS Execution — Main thread parse, compile, execute time.\n   Emerges from: Bundle download | Gives rise to: Interactive delay | Evidence: Total Blocking Time.",
 "Layout + Paint — Position calculation and pixel rendering.\n   Emerges from: DOM + CSSOM | Gives rise to: Visual content | Evidence: Performance tab.",
 "CDN Configuration — Whether assets served from edge.\n   Emerges from: Infrastructure | Gives rise to: Asset latency | Evidence: Cache headers.",
],
["Framework Hydration Cost — For SSR apps (React, Next.js), the server-rendered HTML must be 'hydrated' client-side: re-attaching event listeners, reconciling virtual DOM. Can add 1-5 seconds on mobile. Invisible in TTFB metrics but dominates Time-to-Interactive.",
 "Cumulative Layout Shift — Elements changing position after render: images without dimensions, late-loading ads, font swap. Invisible in load TIME but devastating for user EXPERIENCE.",
 "Compression Absence — Lack of gzip/brotli compression on text responses. A NON-COMPONENT that should exist. Uncompressed HTML/CSS/JS can be 3-5x larger than compressed.",
],
"""DNS → TCP/TLS → Server (DB queries) → Response → HTML Parse
→ CSS (blocks render) + JS (blocks interaction) + Images + Fonts
→ Layout → Paint → Visually Complete
Third-party scripts: parallel DNS/TCP chains competing for main thread
CDN: affects all asset latencies; Compression: affects all transfer sizes""",
"""- Suspected: Service worker state, browser cache, connection quality, server geographic location.
- Gaps: Missing API waterfall (client-side fetching after render). Missing: perceived performance vs. actual (loading skeleton vs. blank screen).
- Outside view: 70-80% of perceived latency is CLIENT-SIDE for modern SPAs. Most optimization effort targets the server, which is usually not the bottleneck.
- Estimated completeness: 73%"""
)),

("Enumerate all components of a memory leak in a long-running server.", _enum("Memory leak in server application.", "INSIDE — allocation, retention, detection, resolution. OUTSIDE — OS memory management internals.", 16,
["Object Allocation — Runtime creates objects in heap memory.\n   Emerges from: Application code execution | Gives rise to: Heap usage growth | Evidence: Heap snapshots.",
 "Reference Retention — Objects kept alive by references preventing garbage collection.\n   Emerges from: Code holding references | Gives rise to: Memory not freed | Evidence: Reference chain analysis.",
 "Event Listener Accumulation — Listeners added but never removed accumulate over time.\n   Emerges from: addEventListener without removeEventListener | Gives rise to: Retained closures + DOM nodes | Evidence: Event listener count growth.",
 "Cache Without Eviction — In-memory cache growing unboundedly without TTL or size limits.\n   Emerges from: Cache design flaw | Gives rise to: Linear memory growth | Evidence: Cache size metrics.",
 "Closure Capture — Closures inadvertently capturing large objects in their scope.\n   Emerges from: Closure creation over large scopes | Gives rise to: Hidden retention | Evidence: Heap snapshot retainer paths.",
 "Circular References — Objects referencing each other preventing cleanup (in non-GC or weak-GC environments).\n   Emerges from: Bidirectional references | Gives rise to: Unreachable but unfreed memory | Evidence: Object graph analysis.",
 "Connection/Handle Leaks — DB connections, file handles, sockets opened but never closed.\n   Emerges from: Missing cleanup in error paths | Gives rise to: Resource exhaustion | Evidence: Handle count monitoring.",
 "Buffer Accumulation — Buffers (stream, I/O) allocated for processing but not released.\n   Emerges from: Stream processing without backpressure | Gives rise to: Buffer pool growth | Evidence: Buffer pool metrics.",
 "Heap Growth Monitoring — Tracking memory usage over time to detect upward trends.\n   Emerges from: Monitoring infrastructure | Gives rise to: Leak detection | Evidence: Memory time-series graphs.",
 "Heap Snapshot Analysis — Point-in-time capture of all live objects and their retention paths.\n   Emerges from: Debugging tooling | Gives rise to: Leak identification | Evidence: Snapshot diff between time points.",
 "Garbage Collector Pressure — GC spending increasing time reclaiming memory, reducing application throughput.\n   Emerges from: High allocation rate + Large heap | Gives rise to: Latency spikes, CPU overhead | Evidence: GC pause metrics.",
 "OOM Kill — OS kills process when system memory is exhausted.\n   Emerges from: Unbounded growth | Gives rise to: Service crash, potential data loss | Evidence: dmesg/journal OOM entries.",
],
["Third-Party Library Leaks — Memory leaks in dependencies the team did not write and does not fully understand. Typically blamed on 'the application' but often traced to library internals (ORMs holding query caches, logging frameworks accumulating buffers). Missed because developers assume library code is memory-safe.",
 "Surviving Generation Promotion — Objects that survive multiple GC cycles get promoted to old generation, where they are collected less frequently. Temporary objects that accidentally survive (due to timing) accumulate in old gen. Invisible because it is a GC implementation detail, but causes the characteristic 'sawtooth with rising floor' memory pattern.",
 "Test Environment Blindness — Memory leaks manifest only under production conditions (long runtime, high concurrency) and are invisible in tests (short-lived processes). The leak exists in test environments but processes terminate before it matters. This creates a systematic gap between testing and production.",
],
"""Allocation → Reference Retention (leak source) → Heap Growth → GC Pressure → Latency Degradation → OOM Kill
Event Listeners, Caches, Closures, Connections → Reference Retention paths
Monitoring → Detection → Heap Snapshot → Root Cause Analysis → Fix → Deploy
Third-Party Leaks (invisible root cause)
Test Blindness (explains why not caught earlier)""",
"""- Suspected: Native memory leaks (outside GC), thread-local storage accumulation, class loader leaks (Java), string interning growth.
- Gaps: No modeling of the SOCIAL dynamics — memory leaks are often deprioritized because they don't cause immediate failures, only gradual degradation. The political will to fix them before OOM events is a missing component.
- Outside view: Memory leaks are not primarily technical problems — they are observability problems. Most leaks are technically simple (unclosed resource, missing eviction). The hard part is DETECTING and LOCALIZING them in production.
- Estimated completeness: 72%"""
)),

("Enumerate all components of a distributed system consistency failure.", _enum("Distributed system consistency failure.", "INSIDE — consistency mechanisms, failure modes, detection. OUTSIDE — application business logic.", 16,
["Network Partition — Network failure splitting nodes into isolated groups.\n   Emerges from: root (infrastructure) | Gives rise to: Split-brain risk | Evidence: Network monitoring.",
 "CAP Theorem Constraint — Cannot simultaneously guarantee Consistency, Availability, Partition tolerance.\n   Emerges from: root (mathematical proof) | Gives rise to: Design tradeoff (CP or AP) | Evidence: Brewer's theorem.",
 "Consensus Protocol — Raft/Paxos/ZAB algorithm for agreeing on state across nodes.\n   Emerges from: Consistency requirement | Gives rise to: Agreed state (when quorum available) | Evidence: Protocol logs.",
 "Quorum Loss — Insufficient nodes available to form consensus majority.\n   Emerges from: Network Partition + Node failures | Gives rise to: Write unavailability (CP systems) | Evidence: Quorum status metrics.",
 "Split-Brain — Two partitions both believe they are primary, accepting conflicting writes.\n   Emerges from: Network Partition + Inadequate fencing | Gives rise to: Divergent state | Evidence: Conflicting write logs.",
 "Eventual Consistency Lag — Time between write on one node and propagation to all replicas.\n   Emerges from: Async replication design | Gives rise to: Stale reads | Evidence: Replication lag metrics.",
 "Vector Clocks / Logical Timestamps — Mechanism tracking causal ordering of events across nodes.\n   Emerges from: Ordering requirement | Gives rise to: Conflict detection | Evidence: Clock values in metadata.",
 "Conflict Resolution — Strategy for resolving divergent state: last-writer-wins, merge, custom resolver.\n   Emerges from: Detected conflicts | Gives rise to: Resolved state (with possible data loss) | Evidence: Conflict resolution logs.",
 "Read-Your-Writes Consistency — Guarantee that a client reads its own recent writes.\n   Emerges from: Session affinity + Consistency level | Gives rise to: User-perceived consistency | Evidence: Read-after-write testing.",
 "Idempotency — Operations that produce same result when applied multiple times (handles retries safely).\n   Emerges from: Operation design | Gives rise to: Retry safety | Evidence: Idempotency key implementation.",
 "Distributed Transaction (2PC) — Two-phase commit for atomic cross-node operations.\n   Emerges from: Atomicity requirement across services | Gives rise to: Coordinated commit/abort | Evidence: Transaction coordinator logs.",
 "Saga Pattern — Long-running transaction as sequence of local transactions with compensating actions.\n   Emerges from: Cross-service consistency need without 2PC | Gives rise to: Eventually consistent state | Evidence: Saga orchestrator logs.",
],
["Clock Skew — Physical clock differences between nodes causing ordering violations. NTP reduces but doesn't eliminate. Google's TrueTime (Spanner) uses atomic clocks + GPS. Most systems assume synchronized clocks and fail subtly when they aren't. Clock skew causes transactions to be ordered incorrectly, creating 'impossible' states.",
 "Zombie Processes — A node declared dead (and fenced) that is actually alive and still processing requests. Its writes conflict with the new primary. Typically handled by fencing tokens, but if fencing is imperfect, zombie writes create the most insidious consistency failures because they appear legitimate.",
 "Consistency Level Confusion — Developers choose consistency levels (ONE, QUORUM, ALL) without understanding their guarantees. A system configured for QUORUM reads + ONE writes can return stale data. The mismatch between developer expectation and actual guarantee is the most common cause of 'consistency bugs' in distributed systems.",
],
"""Network Partition → Split-Brain Risk → Divergent State → Conflict Resolution
CAP Constraint → Design Choice (CP: unavailable during partition; AP: inconsistent during partition)
Consensus Protocol → Quorum → Agreed State (when quorum met)
Async Replication → Eventual Consistency Lag → Stale Reads
Clock Skew → Ordering Violations → Subtle Inconsistency
Zombie Processes → Conflicting Writes (bypasses fencing)""",
"""- Suspected: Byzantine failures (malicious nodes), cascading timeouts, thundering herd on recovery, state divergence in DNS/CDN caches.
- Gaps: No modeling of the HUMAN factor — most distributed system consistency failures are caused by misconfiguration, not algorithm failure. Also missing: testing strategies (Jepsen-style verification).
- Outside view: Distributed consistency is not a problem to be solved but a tradeoff to be managed. Systems that claim to be 'strongly consistent' are actually 'strongly consistent most of the time' — the failures happen at the edges that are rarely tested.
- Estimated completeness: 71%"""
)),

# Ethics domain
("Enumerate all stakeholders in a tech company's decision to sell user data.", _enum("User data selling: stakeholders and interests.", "INSIDE — all affected parties and interests. OUTSIDE — implementation details.", 15,
["Users/Customers — Whose data is being sold. Interest: privacy, autonomy, security.\n   Emerges from: root (data subjects) | Gives rise to: Trust/distrust, legal rights | Evidence: User surveys, GDPR rights.",
 "Company Leadership — Decision makers. Interest: revenue growth, market position.\n   Emerges from: Fiduciary duty | Gives rise to: Revenue from data sales | Evidence: Board decisions.",
 "Shareholders — Owners. Interest: profitability, growth, risk management.\n   Emerges from: Ownership | Gives rise to: Pressure for revenue | Evidence: Earnings expectations.",
 "Data Brokers/Buyers — Purchasers. Interest: targeted advertising, analytics, profiling.\n   Emerges from: Market demand for data | Gives rise to: Revenue for company | Evidence: Data marketplace.",
 "Employees — Workers. Interest: ethical workplace, job security, reputation.\n   Emerges from: Employment | Gives rise to: Retention/attrition based on ethics | Evidence: Employee surveys.",
 "Regulators — Government agencies. Interest: compliance, consumer protection.\n   Emerges from: Legal authority | Gives rise to: Fines, enforcement | Evidence: GDPR, CCPA, FTC.",
 "Advertisers — End users of data. Interest: targeting efficiency.\n   Emerges from: Marketing needs | Gives rise to: Ad revenue ecosystem | Evidence: Ad platform data.",
 "Competitors — Rival companies. Interest: competitive intelligence, equal treatment.\n   Emerges from: Market competition | Gives rise to: Competitive response | Evidence: Market analysis.",
 "Civil Society/Privacy Advocates — Watchdog groups. Interest: digital rights, transparency.\n   Emerges from: Public interest mission | Gives rise to: Public pressure, advocacy | Evidence: Reports, campaigns.",
 "General Public — Non-users affected by data-driven decisions. Interest: societal impact.\n   Emerges from: Broad impact of data practices | Gives rise to: Social norms, political response | Evidence: Public opinion.",
 "Legal Team — Company lawyers. Interest: liability minimization, compliance.\n   Emerges from: Legal risk | Gives rise to: Contract structure, consent design | Evidence: Legal opinions.",
],
["Future Selves of Current Users — Users who consent today may be harmed by data use in ways they cannot currently predict (insurance discrimination, political targeting, stalking). The 'user' stakeholder is typically analyzed as a present-tense entity, but the consequences of data sale play out over years.",
 "The Marginalized Disproportionately Affected — Location data disproportionately harms: domestic violence survivors (stalking risk), undocumented immigrants (deportation risk), LGBTQ+ individuals in hostile regions (safety risk), political dissidents. Stakeholder analysis usually treats 'users' as homogeneous, but the harm distribution is highly unequal.",
 "The Company's Future Self — Short-term data revenue may create long-term trust damage, regulatory liability, and brand erosion that exceeds the revenue. The company as a future entity is a stakeholder whose interests conflict with the company as a present entity.",
],
"""Users → Trust → Retention/Churn → Long-term Revenue
Leadership + Shareholders → Revenue Pressure → Data Sale Decision
Regulators → Compliance Requirements → Constraints on Decision
Employees → Ethical Comfort → Retention → Execution Capability
Privacy Advocates → Public Pressure → Brand Impact
Marginalized Users → Disproportionate Harm → Ethical/Legal Liability""",
"""- Suspected: Insurance companies using purchased data, political campaigns, law enforcement, foreign governments.
- Gaps: No modeling of the INFORMATION ASYMMETRY — users don't know what is being sold, to whom, or how it will be used. This asymmetry is itself an ethical factor.
- Outside view: Stakeholder analysis typically weights interests by power (shareholders, leadership high; users, public low). An ethical analysis should weight by IMPACT (users and marginalized highest).
- Estimated completeness: 72%"""
)),

# Remaining compact examples for all remaining domains
("Enumerate all components of algorithmic content recommendation and societal effects.", _enum("Algorithmic recommendation: pipeline and societal impact.", "INSIDE — technical pipeline and societal effects. OUTSIDE — content creation, platform governance.", 16,
["User Behavior Signals — Clicks, dwell time, shares, likes, search queries.\n   Emerges from: User interactions | Gives rise to: User profile | Evidence: Event logs.",
 "User Profile/Embedding — Vector representation of user preferences.\n   Emerges from: Behavior signals + Demographics | Gives rise to: Personalization | Evidence: Embedding space.",
 "Content Features — Metadata, topic classification, engagement history.\n   Emerges from: Content analysis | Gives rise to: Content-user matching | Evidence: Feature extraction.",
 "Recommendation Model — Collaborative filtering, content-based, or hybrid ML model.\n   Emerges from: User profiles + Content features + Training data | Gives rise to: Ranked content feed | Evidence: A/B test metrics.",
 "Engagement Optimization — Model objective: maximize clicks, dwell time, or session length.\n   Emerges from: Business KPIs | Gives rise to: Algorithmic bias toward engaging content | Evidence: Optimization target definition.",
 "Filter Bubble — Users see increasingly narrow content matching existing preferences.\n   Emerges from: Personalization feedback loop | Gives rise to: Reduced exposure to diverse perspectives | Evidence: Content diversity metrics.",
 "Polarization Amplification — Extreme/outrage content generates more engagement → more promotion → more extremism.\n   Emerges from: Engagement optimization + Human psychology | Gives rise to: Political polarization | Evidence: Research studies (Bail et al. 2018).",
 "Misinformation Spread — False content that is engaging gets amplified before fact-checking.\n   Emerges from: Engagement bias + Novelty premium | Gives rise to: Public misinformation | Evidence: MIT study (Vosoughi 2018: falsehood spreads 6x faster).",
 "Addiction Mechanics — Variable reward schedules + infinite scroll + notifications.\n   Emerges from: UX design + Engagement optimization | Gives rise to: Compulsive usage | Evidence: Screen time data, user behavior studies.",
 "Content Creator Incentive Distortion — Creators optimize for algorithm rather than quality.\n   Emerges from: Algorithmic rewards for engagement | Gives rise to: Clickbait, sensationalism | Evidence: Creator strategy discussions.",
 "Mental Health Effects — Social comparison, FOMO, body image issues, anxiety.\n   Emerges from: Content exposure + Comparison + Usage patterns | Gives rise to: Wellbeing impact | Evidence: Haidt & Twenge research.",
 "Child/Adolescent Vulnerability — Developing brains more susceptible to addiction and comparison.\n   Emerges from: Platform access + Developmental stage | Gives rise to: Heightened negative effects | Evidence: Surgeon General advisory.",
],
["Engagement Metric as Proxy — The fundamental non-obvious component: engagement (clicks, time) is used as a PROXY for value, but engagement and value diverge. Users engage with outrage and misinformation not because they value it but because it activates threat/novelty responses. The proxy metric IS the root cause of most negative effects.",
 "Algorithmic Monoculture — All major platforms use similar recommendation approaches, creating systemic risk: the same biases are amplified across YouTube, TikTok, Instagram, Twitter simultaneously. A failure mode in one platform's algorithm is likely present in all.",
 "Feedback Loop Blindness — The system cannot distinguish 'user engaged because content was valuable' from 'user engaged because content was addictive/outrageous.' Without this distinction, the optimization process treats all engagement as positive signal.",
],
"""User Behavior → Profile → Model → Ranked Feed → User Behavior (reinforcing loop)
Engagement Optimization → Bias toward emotional/extreme content
→ Filter Bubble → Polarization
→ Misinformation Spread
→ Creator Incentive Distortion → Content Quality Decline
→ Addiction → Mental Health Effects
Engagement Metric as Proxy (root cause of most negative effects)""",
"""- Suspected: Regulatory capture, attention economy competition between platforms, geopolitical manipulation.
- Gaps: No modeling of POSITIVE effects (discovery of niche interests, education, community). The system also produces genuine value.
- Outside view: The system optimizes a METRIC (engagement) that diverges from VALUE at scale. The fix is not better algorithms but better objectives. What should the algorithm optimize for?
- Estimated completeness: 70%"""
)),

("Enumerate all components of a successful product launch.", _enum("Product launch pipeline.", "INSIDE — all stages from readiness to market reception. OUTSIDE — long-term product lifecycle.", 16,
["Product Readiness — Feature completeness, quality, stability for launch.\n   Emerges from: Development + QA | Gives rise to: Launch viability | Evidence: Bug counts, feature checklist.",
 "Market Research — Understanding target audience, competition, positioning.\n   Emerges from: Strategy | Gives rise to: Messaging, pricing | Evidence: Surveys, competitive analysis.",
 "Pricing Strategy — Price point, model, tiers determined and tested.\n   Emerges from: Market research + Cost structure | Gives rise to: Revenue model | Evidence: Pricing tests.",
 "Marketing Collateral — Website, demos, videos, case studies, press kit.\n   Emerges from: Positioning + Content team | Gives rise to: Market communication | Evidence: Asset inventory.",
 "Press/Media Outreach — Journalist relationships, embargoed previews, press releases.\n   Emerges from: PR strategy | Gives rise to: Media coverage | Evidence: Press mentions.",
 "Sales Enablement — Sales team training, scripts, objection handling, demo environments.\n   Emerges from: Product + Sales team | Gives rise to: Sales readiness | Evidence: Training completion.",
 "Launch Event — Announcement moment: keynote, blog post, email blast, social campaign.\n   Emerges from: All preparation | Gives rise to: Market awareness spike | Evidence: Event metrics.",
 "Infrastructure Scaling — Ensuring systems handle launch traffic spike.\n   Emerges from: Traffic projections | Gives rise to: Availability under load | Evidence: Load tests.",
 "Customer Support Preparation — Support team trained, documentation ready, escalation paths defined.\n   Emerges from: Product knowledge + Anticipated issues | Gives rise to: Post-launch customer experience | Evidence: Support readiness checklist.",
 "Feedback Collection — Mechanisms for gathering initial user feedback post-launch.\n   Emerges from: Product + Analytics | Gives rise to: Iteration signal | Evidence: Feedback channels.",
 "Success Metrics — Defined KPIs for launch success (signups, revenue, NPS).\n   Emerges from: Business objectives | Gives rise to: Launch evaluation | Evidence: Metric definitions.",
],
["Internal Alignment — Whether all teams (engineering, marketing, sales, support, leadership) share the same understanding of what is launching, for whom, and why. The #1 cause of launch failures is internal misalignment, not market rejection. Each team optimizing for different goals produces incoherent launches.",
 "Launch Timing Relative to Market Events — Launching during industry conferences, competitor announcements, or news cycles can amplify or drown the launch. Often treated as random but can 10x coverage.",
 "Day-Two Plan — What happens the day AFTER launch: how leads are followed up, bugs are triaged, feedback is processed. Most launches invest heavily in Day One and have no Day Two plan, causing the launch spike to dissipate without conversion.",
],
"""Product Readiness + Market Research + Pricing → Launch Readiness
Marketing + Press + Sales Enablement → Market Communication
Launch Event → Awareness Spike → Traffic → Infrastructure (must handle)
Traffic → Signups → Support (must be ready)
Feedback → Iteration Signal → Post-Launch Improvements""",
"""- Suspected: Partner/channel coordination, legal/compliance review, competitive response planning, rollback plan.
- Gaps: No modeling of SOFT LAUNCH vs HARD LAUNCH strategy. Missing: the emotional/psychological toll on the team.
- Outside view: Most launch planning focuses on the LAUNCH MOMENT. The actual determinant of success is what happens in the 90 days AFTER launch — conversion, retention, iteration.
- Estimated completeness: 73%"""
)),

("Enumerate all components of technical debt in a software project.", _enum("Technical debt: sources, types, and remediation.", "INSIDE — all forms, causes, and impacts. OUTSIDE — business strategy decisions.", 16,
["Deliberate Shortcuts — Conscious decisions to ship faster by skipping best practices.\n   Emerges from: Time pressure + Conscious tradeoff | Gives rise to: Known liability | Evidence: Comments, tech debt tickets.",
 "Accidental Complexity — Poor design from inexperience or insufficient understanding.\n   Emerges from: Skill gaps + Learning curve | Gives rise to: Unexpected maintenance burden | Evidence: Code review findings.",
 "Outdated Dependencies — Libraries and frameworks that are no longer maintained or have security vulnerabilities.\n   Emerges from: Time passage + Ecosystem evolution | Gives rise to: Security risk, upgrade difficulty | Evidence: Dependency audit tools.",
 "Missing Tests — Code without adequate test coverage, making changes risky.\n   Emerges from: Time pressure + Testing culture gaps | Gives rise to: Fear of change, regression risk | Evidence: Coverage metrics.",
 "Unclear Naming/Documentation — Code that is difficult to understand for future developers.\n   Emerges from: Rushed development + Team turnover | Gives rise to: Onboarding cost, modification risk | Evidence: Code readability metrics.",
 "Copy-Paste Duplication — Identical logic in multiple places.\n   Emerges from: Time pressure + Insufficient abstraction | Gives rise to: Inconsistent behavior when one copy is updated | Evidence: Duplication analysis tools.",
 "Architectural Mismatch — System architecture no longer matches current requirements.\n   Emerges from: Requirements evolution + Original assumptions | Gives rise to: Increasing difficulty of feature development | Evidence: Feature velocity decline.",
 "Database Schema Debt — Schema that doesn't reflect current data model, with workarounds layered on.\n   Emerges from: Incremental changes without refactoring | Gives rise to: Query complexity, migration fear | Evidence: Schema analysis.",
 "Configuration Debt — Hardcoded values, environment-specific hacks, undocumented settings.\n   Emerges from: Quick fixes + Environment-specific patches | Gives rise to: Deployment failures, environment differences | Evidence: Configuration audit.",
 "CI/CD Debt — Slow, flaky, or incomplete pipeline.\n   Emerges from: Pipeline neglect | Gives rise to: Slow feedback, skipped checks | Evidence: Pipeline duration, failure rate.",
 "Velocity Decline — Measurable slowdown in feature delivery over time.\n   Emerges from: Accumulated debt | Gives rise to: Business impact, team frustration | Evidence: Cycle time trends.",
 "Developer Experience Degradation — Increasing friction in development workflow: slow builds, painful debugging, complex setups.\n   Emerges from: Accumulated debt | Gives rise to: Talent attrition, productivity loss | Evidence: Developer surveys.",
],
["Organizational Knowledge Debt — Knowledge that exists only in departed employees' heads, not in documentation or code. When key people leave, the team inherits code nobody understands. This is not a code quality issue but a KNOWLEDGE issue — technically clean code can still be 'debt' if nobody understands its purpose.",
 "Implicit Coupling Debt — Modules that appear independent but have hidden dependencies through shared databases, global state, or undocumented assumptions. Breaks surface only when one module is changed and another fails for no apparent reason. The most expensive form of debt because it is invisible until failure.",
 "Testing Debt Spiral — Missing tests make code hard to change → developers make minimal changes → code diverges further from ideal → writing tests becomes even harder. This self-reinforcing cycle is why testing debt grows faster than other debt types.",
],
"""Shortcuts + Accidental Complexity → Code Debt → Velocity Decline
Outdated Deps → Security Risk + Upgrade Difficulty
Missing Tests → Fear of Change → Minimal Changes → More Debt (spiral)
All Debt Types → Developer Experience → Talent Attrition → Knowledge Loss → More Debt""",
"""- Suspected: Documentation debt, observability debt (insufficient logging/monitoring), accessibility debt.
- Gaps: No modeling of INTEREST RATE — different debts compound at different rates. Testing debt compounds faster than naming debt.
- Outside view: Technical debt is framed as a technical problem but is fundamentally a COMMUNICATION problem between present and future developers. The 'interest' is paid in communication overhead.
- Estimated completeness: 73%"""
)),

("Enumerate all components of a software licensing agreement.", _enum("Software licensing agreement.", "INSIDE — all terms, rights, obligations. OUTSIDE — sales process, implementation.", 15,
["Grant of License — Scope: what rights are being granted (use, copy, modify, distribute).\n   Emerges from: Licensor's IP ownership | Gives rise to: Licensee's usage rights | Evidence: License text.",
 "License Type — Perpetual, subscription, seat-based, concurrent, enterprise, open-source.\n   Emerges from: Business model | Gives rise to: Payment structure, usage limits | Evidence: Agreement terms.",
 "Permitted Use — What the licensee can do: internal use, customer-facing, redistribution.\n   Emerges from: License type + Restrictions | Gives rise to: Usage boundaries | Evidence: Use clauses.",
 "Restrictions — What is prohibited: reverse engineering, sublicensing, competitive use, geographic limits.\n   Emerges from: Licensor protection | Gives rise to: Usage constraints | Evidence: Restriction clauses.",
 "Payment Terms — Price, billing frequency, payment method, late payment consequences.\n   Emerges from: Pricing negotiation | Gives rise to: Financial obligations | Evidence: Payment schedule.",
 "Support and Maintenance — SLAs, update frequency, support channels, response times.\n   Emerges from: Service agreement | Gives rise to: Operational expectations | Evidence: SLA appendix.",
 "IP Ownership — Who owns modifications, integrations, derivative works.\n   Emerges from: IP law + Agreement | Gives rise to: Rights over customizations | Evidence: IP clauses.",
 "Data Rights — Ownership, processing, export rights over data in the software.\n   Emerges from: Data usage + Privacy law | Gives rise to: Data governance | Evidence: DPA, data clauses.",
 "Warranty/Liability — What is guaranteed, liability caps, disclaimer of warranties.\n   Emerges from: Risk allocation | Gives rise to: Legal exposure limits | Evidence: Warranty section.",
 "Termination — Conditions for ending agreement, consequences, data retention/deletion.\n   Emerges from: Contract law | Gives rise to: Exit rights and obligations | Evidence: Termination clause.",
 "Confidentiality — Protection of both parties' confidential information.\n   Emerges from: Information exchange | Gives rise to: Disclosure restrictions | Evidence: NDA/confidentiality section.",
 "Compliance/Audit — Licensor's right to verify licensee's compliance with terms.\n   Emerges from: Enforcement need | Gives rise to: Audit obligations | Evidence: Audit clause.",
],
["Auto-Renewal and Termination Window — License auto-renews unless cancelled within a narrow window (30-90 days before renewal). Missed because it is a temporal detail, but it is the mechanism by which vendors lock in revenue from inattentive customers. The asymmetry: vendor benefits from inaction; customer must actively manage.",
 "Indirect Use / Multiplexing Clauses — Restrictions on accessing the software through intermediary systems (APIs, web portals, batch processing). Enterprise software licenses often count 'indirect users' even if they never touch the software directly. This clause has resulted in multi-million dollar compliance disputes (SAP indirect access cases).",
 "Governing Law and Dispute Resolution — Which jurisdiction's law governs and whether disputes go to arbitration or court. Seems like legal boilerplate but determines practical enforceability. An arbitration clause can effectively prevent class action; choice of jurisdiction can add travel costs to dispute resolution.",
],
"""Grant → Type → Permitted Use → Restrictions (defines usage envelope)
Payment → Financial Obligations
Support → Operational Expectations
IP Ownership + Data Rights → Post-termination considerations
Warranty → Liability limits
Termination → Exit rights + Data handling
Auto-Renewal → Lock-in mechanism""",
"""- Suspected: Export control restrictions, accessibility requirements, open-source license contamination, insurance requirements.
- Gaps: No modeling of the NEGOTIATION POWER ASYMMETRY — most software licenses are presented as non-negotiable adhesion contracts. Also missing: how license terms change at renewal.
- Outside view: Software licenses are nominally bilateral agreements but are effectively unilateral terms dictated by the vendor. The 'agreement' is largely fictional for standard subscriptions.
- Estimated completeness: 72%"""
)),

("Enumerate all components of GDPR compliance for a SaaS application.", _enum("GDPR compliance for SaaS.", "INSIDE — all requirements, processes, technical measures. OUTSIDE — broader data strategy.", 16,
["Lawful Basis — Legal ground for processing: consent, contract, legitimate interest, etc.\n   Emerges from: GDPR Art. 6 | Gives rise to: Processing legitimacy | Evidence: Legal review per data type.",
 "Consent Management — Mechanism for obtaining, recording, and withdrawing consent.\n   Emerges from: Consent as lawful basis | Gives rise to: User control over data | Evidence: Consent records, UI.",
 "Data Mapping — Inventory of all personal data: what, where, why, how long, who has access.\n   Emerges from: GDPR Art. 30 requirement | Gives rise to: Processing visibility | Evidence: Data map document.",
 "Privacy Notice — Transparent disclosure of data practices to users.\n   Emerges from: GDPR Art. 13-14 | Gives rise to: Informed users | Evidence: Privacy policy text.",
 "Data Subject Rights — Right to access, rectify, erase, port, restrict, object.\n   Emerges from: GDPR Art. 15-22 | Gives rise to: Request handling process | Evidence: DSR fulfillment records.",
 "Data Protection Impact Assessment — Risk assessment for high-risk processing.\n   Emerges from: GDPR Art. 35 | Gives rise to: Risk mitigation measures | Evidence: DPIA document.",
 "Data Processing Agreements — Contracts with all sub-processors defining their obligations.\n   Emerges from: GDPR Art. 28 | Gives rise to: Processor accountability | Evidence: Signed DPAs.",
 "Cross-Border Transfer Mechanisms — Legal basis for data transfers outside EEA (SCCs, adequacy).\n   Emerges from: GDPR Art. 44-49 + Schrems II | Gives rise to: Transfer legitimacy | Evidence: Transfer impact assessments.",
 "Breach Notification Process — 72-hour notification to authority, user notification if high risk.\n   Emerges from: GDPR Art. 33-34 | Gives rise to: Incident response capability | Evidence: Breach response plan.",
 "Data Minimization — Only collecting data necessary for stated purposes.\n   Emerges from: GDPR Art. 5(1)(c) | Gives rise to: Reduced data footprint | Evidence: Data collection audit.",
 "Retention Policies — Defined retention periods with automatic deletion.\n   Emerges from: GDPR Art. 5(1)(e) | Gives rise to: Data lifecycle management | Evidence: Retention schedule.",
 "Technical Security Measures — Encryption, access controls, pseudonymization, monitoring.\n   Emerges from: GDPR Art. 32 | Gives rise to: Data protection | Evidence: Security assessment.",
 "DPO Appointment — Data Protection Officer if required.\n   Emerges from: GDPR Art. 37 | Gives rise to: Compliance oversight | Evidence: DPO appointment record.",
],
["Cookie Consent Complexity — ePrivacy Directive (separate from GDPR) requires consent for non-essential cookies. Implementing compliant cookie banners that actually block tracking before consent is technically complex. Many implementations are non-compliant (loading trackers before consent). Missed because it seems simple UI but is technically deep.",
 "Sub-Processor Chain Risk — Your SaaS uses AWS, which uses sub-contractors, who use further sub-contractors. Each link in the chain must be GDPR-compliant, and you are responsible for ensuring this. The actual data processing chain is typically 3-5 levels deep and mostly invisible.",
 "Legitimate Interest Balancing Test — The most commonly used and most frequently mis-applied lawful basis. Requires a documented three-part test (purpose, necessity, balancing) that most companies skip. Regulators are increasingly scrutinizing legitimate interest claims, and the undocumented ones fail enforcement review.",
],
"""Lawful Basis → Processing Legitimacy (foundation for everything)
Data Mapping → Visibility → Enables: DPIA, Retention, Minimization, DSR fulfillment
Consent Management → User Control
DPAs → Processor Chain Accountability ← Sub-Processor Risk
Technical Measures → Data Protection
Breach Process → Incident Response""",
"""- Suspected: Employee training, privacy-by-design in development process, vendor compliance monitoring, marketing consent separation.
- Gaps: No modeling of ENFORCEMENT REALITY — GDPR compliance is not binary but a spectrum. Regulators prioritize complaints and high-profile cases. Also missing: the evolving interpretation of GDPR through court decisions and regulatory guidance.
- Outside view: Most GDPR compliance programs focus on documentation (policies, notices, records) rather than OPERATIONAL compliance (actually deleting data on request, actually minimizing collection). The gap between documented compliance and actual compliance is the primary risk.
- Estimated completeness: 72%"""
)),

# Creative, Education, and remaining examples
("Enumerate all factors that determine whether a film gets greenlit.", _enum("Film greenlight decision.", "INSIDE — all factors from script to production commitment. OUTSIDE — production, distribution.", 16,
["Script Quality — Story, dialogue, structure, originality.\n   Emerges from: Writer | Gives rise to: Creative foundation | Evidence: Script coverage, reader scores.",
 "Attached Talent — Director and cast commitments.\n   Emerges from: Script + Relationships | Gives rise to: Market viability, financing | Evidence: LOIs, deal memos.",
 "Budget Estimate — Total production cost.\n   Emerges from: Script requirements + Above-the-line costs | Gives rise to: Financial risk assessment | Evidence: Budget breakdown.",
 "Market Analysis — Comparable films' performance, genre trends, audience demand.\n   Emerges from: Box office data + Market research | Gives rise to: Revenue projection | Evidence: Comp analysis.",
 "IP Recognition — Whether based on existing property (book, game, sequel, franchise).\n   Emerges from: Source material | Gives rise to: Built-in audience, marketing advantage | Evidence: Source material popularity.",
 "Distribution Strategy — Theatrical, streaming, hybrid release plan.\n   Emerges from: Market + Platform deals | Gives rise to: Revenue model | Evidence: Distribution commitments.",
 "International Appeal — Story's potential in non-domestic markets (China, Europe, etc.).\n   Emerges from: Story universality + Cast recognition | Gives rise to: Revenue projection | Evidence: International comp performance.",
 "Producer Track Record — Producer's history of delivering on budget and schedule.\n   Emerges from: Career history | Gives rise to: Studio confidence | Evidence: Past project outcomes.",
 "Tax Incentives — State/country production incentives reducing effective cost.\n   Emerges from: Filming location + Incentive programs | Gives rise to: Cost reduction | Evidence: Incentive calculations.",
 "Studio Slate Fit — How the film fits the studio's annual release portfolio.\n   Emerges from: Studio strategy | Gives rise to: Scheduling, marketing support | Evidence: Slate planning.",
 "Financing Structure — Equity, debt, presales, tax credits, co-production deals.\n   Emerges from: Budget + Risk tolerance | Gives rise to: Studio financial exposure | Evidence: Financial plan.",
 "Pre-sales/Commitments — Territory sales or platform deals committed before production.\n   Emerges from: Talent + IP + Market | Gives rise to: Reduced financial risk | Evidence: Sales contracts.",
],
["Executive Champion — A specific senior executive who advocates for the project internally. Films rarely get greenlit on merit alone; they need a powerful champion willing to stake reputation. Missed because it is political, not analytical, but often the single decisive factor.",
 "Greenlight by Comparison — Studios greenlight films partly by referencing recent successes with similar elements ('it's like X meets Y'). The comparison defines the pitch, the marketing strategy, and the audience expectation. A film that cannot be compared to two successful precedents is harder to greenlight regardless of quality.",
 "Insurance and Completion Bond — The ability to insure the production (especially cast) and secure a completion guarantee. A film with an uninsurable lead actor or a first-time director without a completion bond may be technically unmakeable regardless of other factors.",
],
"""Script + Talent → Package → Market Analysis → Revenue Projection
Budget + Financing + Tax Incentives → Financial Viability
Revenue Projection vs Financial Risk → Greenlight Decision
Executive Champion → Internal Advocacy → Decision Momentum
IP Recognition → Built-in Audience → Reduced Marketing Risk""",
"""- Suspected: Awards potential, streaming vs. theatrical economics shifting, DE&I considerations, pandemic-era audience behavior changes.
- Gaps: No modeling of TIMING — the same project at different moments in industry cycles has different greenlight probability.
- Outside view: Greenlight decisions are presented as analytical (market data, financial models) but are substantially SOCIAL (executive relationships, champion advocacy, risk aversion). The data justifies decisions that are politically motivated.
- Estimated completeness: 72%"""
)),

("Enumerate all components that determine podcast quality.", _enum("Podcast quality determinants.", "INSIDE — content, production, distribution, audience. OUTSIDE — monetization, platform algorithms.", 16,
["Content Depth — Quality of research, expertise, and insight.\n   Emerges from: Host knowledge + Preparation | Gives rise to: Listener value | Evidence: Listener reviews.",
 "Host Chemistry — Rapport, conversation dynamics, complementary perspectives.\n   Emerges from: Host personalities + Relationship | Gives rise to: Entertainment value | Evidence: Listener engagement.",
 "Audio Quality — Recording clarity, noise floor, consistency.\n   Emerges from: Equipment + Environment + Post-production | Gives rise to: Listening comfort | Evidence: Audio analysis.",
 "Editing Quality — Pacing, removal of filler, segment transitions, sound design.\n   Emerges from: Editor skill + Time investment | Gives rise to: Professional feel | Evidence: Listener retention curves.",
 "Episode Structure — Format consistency: intro, segments, conclusion, call-to-action.\n   Emerges from: Show design | Gives rise to: Listener expectations, habit formation | Evidence: Format analysis.",
 "Guest Quality — Expertise, articulateness, and relevance of guests.\n   Emerges from: Host network + Booking effort | Gives rise to: Episode variety, authority | Evidence: Guest credentials.",
 "Release Consistency — Regular schedule that listeners can rely on.\n   Emerges from: Production discipline | Gives rise to: Listener habit, algorithm favor | Evidence: Release cadence.",
 "Show Notes/Resources — Links, references, timestamps accompanying episodes.\n   Emerges from: Production effort | Gives rise to: Episode utility, SEO discoverability | Evidence: Show notes completeness.",
 "Discoverability — Podcast presence in search, directories, social media.\n   Emerges from: SEO + Marketing + Cross-promotion | Gives rise to: New listener acquisition | Evidence: Search rankings, referral sources.",
 "Community — Listener community: comments, forums, social media engagement.\n   Emerges from: Audience investment + Host engagement | Gives rise to: Loyalty, word-of-mouth | Evidence: Community size, engagement.",
 "Narrative Arc — Whether each episode tells a complete story or idea.\n   Emerges from: Content design | Gives rise to: Satisfaction, shareability | Evidence: Completion rate.",
],
["Host Vulnerability/Authenticity — Willingness to share genuine uncertainty, mistakes, and personal stakes. The most-cited quality in listener reviews of top podcasts. Missed because it contradicts the 'expert authority' model. But authentic uncertainty is more engaging than polished certainty.",
 "Listening Context Fit — Whether the content works for how people actually listen: commuting, exercising, cooking. Podcasts competing for 'walk time' need different pacing than 'desk time' podcasts. Most podcast design ignores the physical context of consumption.",
 "Silence and Space — Strategic use of pauses, allowing ideas to land. Most podcasts over-edit, removing natural pauses that give listeners processing time. The absence of silence is itself a quality problem.",
],
"""Content Depth + Host Chemistry → Core Value Proposition
Audio + Editing → Production Quality → Listening Comfort
Structure + Consistency → Habit Formation → Retention
Guest Quality → Episode Variety
Discoverability → New Listeners → Community → Word of Mouth → More Listeners""",
"""- Suspected: Platform exclusivity effects, transcript availability for accessibility, sponsorship integration quality.
- Gaps: No modeling of EVOLUTION — podcast quality changes over time (early energy vs. later refinement). Also missing: the listener's own context and mood as quality determinants.
- Outside view: 'Quality' is not a property of the podcast but of the podcast-listener match. A technically excellent podcast on an uninteresting topic has zero quality for a given listener.
- Estimated completeness: 71%"""
)),

("Enumerate all factors in designing a video game progression system.", _enum("Game progression system design.", "INSIDE — mechanics, psychology, balance. OUTSIDE — narrative, visual design.", 16,
["Core Loop — The fundamental repeated action cycle (fight, loot, upgrade, repeat).\n   Emerges from: Game design vision | Gives rise to: Moment-to-moment engagement | Evidence: Playtesting feedback.",
 "Reward Schedule — Timing and magnitude of rewards (variable ratio, fixed interval, etc.).\n   Emerges from: Behavioral psychology + Design intent | Gives rise to: Motivation patterns | Evidence: Retention curves.",
 "Difficulty Curve — Rate at which challenge increases relative to player skill growth.\n   Emerges from: Level design + Player skill model | Gives rise to: Flow state or frustration | Evidence: Completion rates per level.",
 "Skill Trees/Builds — Branching upgrade paths offering meaningful choices.\n   Emerges from: Game systems + Customization philosophy | Gives rise to: Player identity, replayability | Evidence: Build diversity data.",
 "Currency Systems — In-game currencies earned through play, gating upgrades.\n   Emerges from: Economy design | Gives rise to: Pacing, resource decisions | Evidence: Currency flow analysis.",
 "Unlockables — Content gated behind progression: abilities, areas, cosmetics.\n   Emerges from: Content pool + Gating decisions | Gives rise to: Motivation to progress | Evidence: Unlock rate data.",
 "Milestone Markers — Visible checkpoints (levels, ranks, achievements) signaling progress.\n   Emerges from: Progression design | Gives rise to: Sense of advancement | Evidence: Achievement completion rates.",
 "Narrative Motivation — Story beats rewarding progression with plot advancement.\n   Emerges from: Narrative design | Gives rise to: Emotional investment in progress | Evidence: Player engagement metrics.",
 "Social Comparison — Leaderboards, rankings, visible progression compared to others.\n   Emerges from: Multiplayer design | Gives rise to: Competitive motivation | Evidence: Leaderboard engagement.",
 "Time-Gating — Mechanics requiring real time to pass before progress (energy, cooldowns).\n   Emerges from: Monetization design | Gives rise to: Session pacing, potential frustration | Evidence: Return rate, payment conversion.",
 "Power Ceiling — Maximum achievable power level, determining endgame dynamics.\n   Emerges from: System design | Gives rise to: Long-term engagement (if open-ended) or completion (if capped) | Evidence: Endgame player retention.",
 "Catch-Up Mechanics — Systems helping latecomers close the gap with veterans.\n   Emerges from: Community health concern | Gives rise to: New player viability | Evidence: New player retention.",
],
["Loss Aversion Exploitation — Many progression systems use potential LOSS (streak breaks, rank decay, expiring rewards) as motivation rather than potential GAIN. This is psychologically effective but ethically questionable. Missed because it is framed as 'engagement mechanics' rather than what it is: exploiting a cognitive bias.",
 "Sunk Cost Trap — Players continue not because they are having fun but because they have already invested time. The progression system creates switching costs. This is invisible in engagement metrics (player is active) but visible in satisfaction surveys (player is unhappy but trapped).",
 "The Paradox of Choice in Build Systems — Too many options in skill trees creates decision paralysis and 'wrong build' anxiety rather than empowerment. There is an optimal range of meaningful choices (~3-5 per decision point) beyond which complexity reduces rather than increases enjoyment.",
],
"""Core Loop → Reward Schedule → Motivation → Continued Play → Core Loop (reinforcing)
Difficulty Curve → Flow State (if matched) or Frustration/Boredom (if mismatched)
Unlockables + Milestones → Visible Progress → Motivation
Currency → Pacing → Decision Points → Player Agency
Social Comparison → Competitive Motivation (for some) / Discouragement (for others)
Loss Aversion + Sunk Cost → Retention (but reduced satisfaction)""",
"""- Suspected: Seasonal content rotation, battle pass psychology, cross-progression between platforms, accessibility settings affecting progression.
- Gaps: No modeling of INDIVIDUAL DIFFERENCES — progression systems affect different player types (achiever, explorer, socializer, killer per Bartle) differently.
- Outside view: The line between engagement and exploitation in progression design is the central ethical question. Most progression systems are designed to maximize time-in-game, not enjoyment-per-hour.
- Estimated completeness: 72%"""
)),

("Enumerate all components determining student learning outcomes in a university course.", _enum("University course learning outcomes.", "INSIDE — all pedagogical, student, and environmental factors. OUTSIDE — institutional governance.", 16,
["Instructor Expertise — Depth of subject knowledge and research currency.\n   Emerges from: Training + Research | Gives rise to: Content quality | Evidence: Publications, credentials.",
 "Pedagogical Skill — Ability to explain, engage, scaffold learning.\n   Emerges from: Teaching training + Experience | Gives rise to: Knowledge transfer effectiveness | Evidence: Teaching evaluations, peer observation.",
 "Curriculum Design — Learning objectives, sequencing, scaffolding, assessment alignment.\n   Emerges from: Pedagogical knowledge + Dept requirements | Gives rise to: Learning pathway | Evidence: Syllabus, alignment analysis.",
 "Assessment Design — How learning is measured: exams, projects, portfolios, presentations.\n   Emerges from: Learning objectives + Measurement theory | Gives rise to: Learning incentives, feedback quality | Evidence: Assessment rubrics.",
 "Student Prior Knowledge — What students already know entering the course.\n   Emerges from: Prerequisites + Student background | Gives rise to: Learning starting point | Evidence: Pre-assessments.",
 "Student Motivation — Intrinsic interest, career relevance, grade motivation.\n   Emerges from: Student goals + Course relevance | Gives rise to: Effort investment | Evidence: Engagement metrics.",
 "Active Learning Methods — Techniques requiring student participation: discussion, problem-solving, peer instruction.\n   Emerges from: Pedagogical design | Gives rise to: Deeper processing | Evidence: Freeman et al. 2014 meta-analysis (active learning increases performance by 0.47 SD).",
 "Feedback Timeliness — Speed and quality of feedback on student work.\n   Emerges from: Instructor workload + TA support | Gives rise to: Error correction, learning adjustment | Evidence: Feedback turnaround time.",
 "Class Size — Student-to-instructor ratio.\n   Emerges from: Enrollment + Resources | Gives rise to: Interaction quality, feedback capacity | Evidence: Enrollment data.",
 "Study Habits — Time management, retrieval practice, spaced repetition.\n   Emerges from: Student skills + Metacognition | Gives rise to: Knowledge retention | Evidence: Study behavior surveys.",
 "Peer Interaction — Collaboration, study groups, peer teaching.\n   Emerges from: Course design + Student initiative | Gives rise to: Social learning, perspective diversity | Evidence: Group performance data.",
 "Physical/Digital Learning Environment — Classroom design, technology, LMS quality.\n   Emerges from: Institutional resources | Gives rise to: Learning comfort, access | Evidence: Facility audits.",
],
["Sleep Quality and Schedule — University students average 6.5 hours of sleep (below the 7-9 recommended). Sleep deprivation directly impairs memory consolidation, attention, and executive function. Studies show sleep quality predicts GPA more strongly than study time. Missed because it is categorized as 'personal health' not 'educational.'",
 "Belonging and Identity Safety — Whether students feel they belong in the classroom and discipline. Stereotype threat, impostor syndrome, and exclusion reduce cognitive bandwidth available for learning. Underrepresented students underperform not from ability gaps but from belonging uncertainty. Research (Walton & Cohen 2011) shows belonging interventions improve GPA by 0.3 points for affected students.",
 "Instructor Accessibility — Willingness and availability outside class: office hours, email responsiveness, approachability. Students who feel they CAN ask questions learn more than those who don't. This is separate from teaching quality in class — it is about perceived permission to seek help.",
],
"""Prior Knowledge + Motivation → Student Readiness
Instructor Expertise + Pedagogy → Teaching Quality
Curriculum + Assessment → Learning Structure
Teaching Quality + Learning Structure + Active Methods → In-Class Learning
Feedback + Study Habits + Sleep → Knowledge Consolidation
Peer Interaction + Belonging → Social Learning Environment""",
"""- Suspected: Mental health, financial stress, commute time, work obligations, family responsibilities.
- Gaps: No modeling of the INTERACTION between factors — e.g., high motivation can compensate for poor instruction, but only to a point.
- Outside view: Most educational interventions target instruction quality. The highest-leverage interventions often target STUDENT factors: belonging, sleep, study skills, motivation. But institutions control instruction more easily than student behavior.
- Estimated completeness: 72%"""
)),

("Enumerate all factors determining online course completion rates.", _enum("Online course completion factors.", "INSIDE — course design, learner, platform, support. OUTSIDE — learner's life circumstances.", 15,
["Course Structure — Module sequencing, lesson length, milestones.\n   Emerges from: Instructional design | Gives rise to: Learning pathway clarity | Evidence: Completion funnel analysis.",
 "Video/Content Quality — Production value, presenter engagement, visual aids.\n   Emerges from: Production investment | Gives rise to: Attention retention | Evidence: Video completion rates.",
 "Lesson Duration — Length of individual learning units.\n   Emerges from: Content density + Attention research | Gives rise to: Session completion | Evidence: Drop-off point analysis. Optimal: 6-12 minutes.",
 "Interactive Elements — Quizzes, exercises, coding challenges, discussions.\n   Emerges from: Active learning design | Gives rise to: Engagement, knowledge checks | Evidence: Interaction rates.",
 "Learner Motivation — Intrinsic interest, career need, credential value.\n   Emerges from: root (learner goals) | Gives rise to: Effort persistence | Evidence: Pre-course surveys.",
 "Time Availability — How much time the learner can actually dedicate.\n   Emerges from: root (life circumstances) | Gives rise to: Completion feasibility | Evidence: Usage patterns.",
 "Difficulty Calibration — Match between content difficulty and learner's current level.\n   Emerges from: Course design + Learner assessment | Gives rise to: Flow (if matched) or frustration/boredom (if not) | Evidence: Assessment scores, dropout points.",
 "Community/Social Learning — Forums, cohort peers, study groups.\n   Emerges from: Platform features + Learner initiative | Gives rise to: Accountability, belonging | Evidence: Forum activity correlation with completion.",
 "Progress Visibility — Clear indicators of how far through the course the learner is.\n   Emerges from: UX design | Gives rise to: Motivation, completion drive | Evidence: Progress bar engagement.",
 "Certification/Credential — Whether completing earns a recognized credential.\n   Emerges from: Course provider reputation | Gives rise to: Extrinsic motivation | Evidence: Cert vs. non-cert completion rates.",
 "Instructor Presence — Whether the instructor engages with learners (forums, live sessions, feedback).\n   Emerges from: Instructor commitment | Gives rise to: Learner connection, accountability | Evidence: Instructor activity metrics.",
 "Platform UX — Navigation, mobile support, offline access, speed.\n   Emerges from: Platform design | Gives rise to: Friction level | Evidence: Platform usability testing.",
],
["The Enrollment-Commitment Gap — Free/cheap courses have <10% completion because enrollment requires near-zero commitment. The act of paying significantly more correlates with higher completion, not because money buys better content but because financial commitment creates psychological commitment. The 'completion problem' is partly a 'commitment problem' created by low-friction enrollment.",
 "Week 2-3 Dropout Cliff — Most dropout occurs in weeks 2-3, not week 1. The initial novelty sustains week 1; the reality of sustained effort causes week 2-3 abandonment. Course designers focus on making week 1 engaging when the critical retention challenge is weeks 2-3.",
 "Life Event Interruption — Job change, illness, family emergency, vacation. For self-paced courses, any interruption breaks momentum, and re-starting after a gap is psychologically harder than starting fresh. The 'completion' problem is often a 're-engagement after interruption' problem.",
],
"""Motivation + Credential Value → Initial Commitment
Course Structure + Duration + Difficulty → Session-by-Session Engagement
Interactive Elements + Community → Active Participation → Retention
Progress Visibility → Motivation Maintenance
Time Availability + Life Events → Continuation Feasibility
Week 2-3 Cliff → Critical Retention Point""",
"""- Suspected: Email/notification strategy, gamification, peer accountability, deadline structure (self-paced vs. cohort).
- Gaps: No modeling of PRIOR ONLINE LEARNING EXPERIENCE — experienced online learners complete at higher rates because they have developed self-regulation strategies.
- Outside view: The 'completion rate problem' may be partially misframed. Some learners get the value they need from the first 3 modules and intentionally stop. 'Completion' as the metric assumes all content is equally valuable to all learners.
- Estimated completeness: 72%"""
)),

("Enumerate all components of an effective mentorship relationship.", _enum("Mentorship relationship effectiveness.", "INSIDE — structure, behaviors, dynamics. OUTSIDE — organizational mentorship programs.", 15,
["Mentor Domain Expertise — Mentor's knowledge and experience in the relevant field.\n   Emerges from: Career history | Gives rise to: Technical/professional guidance quality | Evidence: Mentor credentials.",
 "Relationship Trust — Psychological safety to share struggles, failures, and uncertainties.\n   Emerges from: Confidentiality + Consistency + Non-judgment | Gives rise to: Authentic communication | Evidence: Self-disclosure frequency.",
 "Goal Clarity — Explicit mentee goals that both parties understand.\n   Emerges from: Mentee self-reflection + Joint discussion | Gives rise to: Focused mentoring direction | Evidence: Goal documents.",
 "Meeting Regularity — Consistent cadence of interactions (weekly, biweekly, monthly).\n   Emerges from: Calendar commitment | Gives rise to: Relationship continuity, accountability | Evidence: Meeting frequency.",
 "Active Listening — Mentor's ability to listen deeply before advising.\n   Emerges from: Mentor skill + Patience | Gives rise to: Mentee feeling heard, better advice | Evidence: Mentee feedback.",
 "Challenge and Support Balance — Pushing mentee outside comfort zone while providing safety net.\n   Emerges from: Mentor judgment | Gives rise to: Growth (if balanced) or withdrawal (if imbalanced) | Evidence: Mentee growth trajectory.",
 "Network Introduction — Mentor connecting mentee to professional contacts.\n   Emerges from: Mentor's network + Willingness to share | Gives rise to: Mentee career opportunities | Evidence: Introductions made.",
 "Feedback Quality — Specific, actionable, timely feedback rather than vague encouragement.\n   Emerges from: Mentor observation + Communication skill | Gives rise to: Skill development | Evidence: Feedback specificity.",
 "Mentee Preparation — Mentee coming prepared with questions, updates, and reflection.\n   Emerges from: Mentee investment | Gives rise to: Meeting productivity | Evidence: Preparation behavior.",
 "Contextual Understanding — Mentor understanding mentee's specific situation, constraints, and environment.\n   Emerges from: Relationship depth + Mentor questions | Gives rise to: Relevant advice | Evidence: Advice applicability.",
 "Mutual Respect — Bidirectional respect for each other's perspectives and time.\n   Emerges from: Shared professional values | Gives rise to: Relationship sustainability | Evidence: Relationship duration.",
],
["Mentor's Own Growth — Effective mentoring requires the mentor to grow too — developing new perspectives through the mentee's questions and challenges. Relationships where the mentor only teaches and never learns stagnate. Missed because the narrative frames mentorship as unidirectional knowledge transfer.",
 "Comfortable Silence — The ability to sit in uncertainty without rushing to advice. Mentors who fill every silence with guidance prevent mentees from developing their own reasoning. The most powerful mentoring moments often happen when the mentor asks a question and then waits.",
 "Relationship Natural Endpoint — Effective mentorships have a natural conclusion when the mentee has grown past the mentor's ability to add value. Failing to recognize this endpoint traps both parties in diminishing returns. Missed because the cultural narrative treats mentorship as permanent.",
],
"""Trust + Goal Clarity → Foundation
Regularity + Preparation → Meeting Quality
Listening + Feedback + Challenge → Growth Process
Network + Contextual Understanding → Career Development
Mutual Respect + Mentor Growth → Sustainability
Natural Endpoint → Healthy Conclusion""",
"""- Suspected: Cultural/demographic matching, organizational support, peer mentoring complement, digital vs. in-person dynamics.
- Gaps: No modeling of MISMATCH — what happens when mentor and mentee are poorly paired. Also missing: the transition from mentorship to peer relationship.
- Outside view: Most mentorship advice focuses on WHAT to discuss. The real determinant is the QUALITY OF THE RELATIONSHIP — trust, authenticity, mutual respect. The content of conversations matters less than the container.
- Estimated completeness: 73%"""
)),

# Additional examples to reach 30
("Enumerate all factors in choosing between two job offers.", _enum("Job offer comparison factors.", "INSIDE — all comparison dimensions. OUTSIDE — job search process.", 15,
["Total Compensation — Base salary, bonus, equity, benefits monetary value.\n   Emerges from: Offer terms | Gives rise to: Financial comparison | Evidence: Offer letters.",
 "Equity/Stock — Type (ISO, RSO, RSU), vesting schedule, company valuation, liquidity.\n   Emerges from: Company stage + Offer | Gives rise to: Potential upside | Evidence: Option grant details.",
 "Role Scope — Responsibilities, decision authority, team size.\n   Emerges from: Job description + Hiring manager | Gives rise to: Daily work experience | Evidence: Interviews.",
 "Growth Trajectory — Promotion path, skill development, learning opportunities.\n   Emerges from: Company growth + Role ceiling | Gives rise to: Career advancement | Evidence: Company org trends.",
 "Company Stage/Stability — Startup vs. growth vs. mature; financial health.\n   Emerges from: Company financials | Gives rise to: Job security, risk/reward profile | Evidence: Funding, revenue data.",
 "Manager Quality — Direct manager's leadership style, technical depth, advocacy.\n   Emerges from: root (person) | Gives rise to: Daily experience, development, promotion | Evidence: Interview impression, reference checks.",
 "Team Quality — Colleagues' caliber, collaboration style, diversity.\n   Emerges from: Hiring bar + Culture | Gives rise to: Learning, daily enjoyment | Evidence: Team interviews.",
 "Mission/Product — Whether you care about what the company does.\n   Emerges from: root (company purpose) | Gives rise to: Intrinsic motivation | Evidence: Self-assessment.",
 "Work-Life Balance — Expected hours, on-call, flexibility.\n   Emerges from: Company culture + Role | Gives rise to: Sustainability, wellbeing | Evidence: Team feedback, Glassdoor.",
 "Remote/Location — Office, hybrid, remote; commute; relocation.\n   Emerges from: Company policy + Role | Gives rise to: Daily logistics, COL impact | Evidence: Policy docs.",
 "Benefits — Healthcare, retirement, PTO, parental leave, education budget.\n   Emerges from: Company benefits package | Gives rise to: Total value, life stage fit | Evidence: Benefits documents.",
 "Company Culture — Values, communication, autonomy, bureaucracy.\n   Emerges from: Leadership + History | Gives rise to: Belonging, effectiveness | Evidence: Glassdoor, interviews.",
],
["Negotiation Asymmetry — Which company is more willing to negotiate reveals how much they want you, which predicts how much they will invest in your success. The negotiation process itself is data about the relationship, not just about compensation. Companies that negotiate generously tend to invest in retention.",
 "Regret Minimization — Not 'which is better?' but 'which rejection would I regret more?' This reframe often produces clearer decisions because it activates loss aversion, which is a stronger signal than gain evaluation. Daniel Kahneman noted that losses are psychologically ~2x gains.",
 "Founder/Leadership Character Under Stress — How leadership behaved during their last crisis (layoffs, product failure, market downturn). Easy to be a great company when things are good. Character reveals itself under stress. Ask: 'What happened during your last layoff?' ",
],
"""Comp + Equity + Benefits → Financial Package
Role + Growth + Manager → Career Development
Team + Culture + Mission → Daily Experience
Stability + Work-Life → Sustainability
Remote/Location → Logistics + COL adjustment""",
"""- Suspected: Industry trajectory, competitive offer leverage, non-compete/IP assignment terms, team turnover rate.
- Gaps: No weighting framework — which factors matter most depends on life stage and personal values. Also missing: the emotional/intuitive signal ('gut feeling' which integrates factors the conscious analysis misses).
- Outside view: Most job comparisons over-weight compensation (easy to compare) and under-weight manager quality (hard to compare but the #1 predictor of job satisfaction per Gallup).
- Estimated completeness: 74%"""
)),

("Enumerate all components of an employment contract for a senior engineer.", _enum("Senior engineer employment contract.", "INSIDE — all contract terms and obligations. OUTSIDE — hiring process, performance management.", 15,
["Position and Title — Role definition, reporting structure, location.\n   Emerges from: Hiring agreement | Gives rise to: Role expectations | Evidence: Contract text.",
 "Compensation — Base salary, payment frequency, currency.\n   Emerges from: Negotiation | Gives rise to: Financial obligations | Evidence: Salary clause.",
 "Equity Compensation — Stock options/RSUs: type, quantity, vesting schedule, cliff, exercise terms.\n   Emerges from: Company equity plan | Gives rise to: Long-term incentive alignment | Evidence: Equity grant documents.",
 "Bonus Structure — Performance bonus, signing bonus, retention bonus criteria.\n   Emerges from: Compensation philosophy | Gives rise to: Performance incentives | Evidence: Bonus clauses.",
 "Benefits — Health, dental, vision, 401k match, HSA, life insurance, disability.\n   Emerges from: Company benefits plan | Gives rise to: Total compensation value | Evidence: Benefits summary.",
 "IP Assignment — Who owns work product created during employment.\n   Emerges from: IP law + Company policy | Gives rise to: Creator's rights limitations | Evidence: IP clause.",
 "Non-Compete — Restrictions on working for competitors post-employment.\n   Emerges from: Company protection interest | Gives rise to: Future employment constraints | Evidence: Non-compete clause. (Note: increasingly unenforceable in many states.)",
 "Non-Solicitation — Restrictions on recruiting former colleagues or contacting clients.\n   Emerges from: Business relationship protection | Gives rise to: Post-employment networking constraints | Evidence: Non-solicit clause.",
 "Confidentiality/NDA — Obligations regarding proprietary information.\n   Emerges from: Trade secret protection | Gives rise to: Disclosure restrictions | Evidence: Confidentiality section.",
 "Termination Terms — At-will vs. for-cause, notice period, severance.\n   Emerges from: Employment law + Negotiation | Gives rise to: Exit conditions | Evidence: Termination clauses.",
 "PTO/Leave — Vacation days, sick leave, parental leave, sabbatical.\n   Emerges from: Company policy | Gives rise to: Work-life balance structure | Evidence: Leave policy.",
 "Remote Work Terms — WFH policy, office requirements, relocation clauses.\n   Emerges from: Company policy + Role | Gives rise to: Location flexibility | Evidence: Remote work clause.",
],
["Change of Control / Acceleration — What happens to unvested equity if the company is acquired. Single-trigger acceleration (all vests on acquisition) vs. double-trigger (vests only if also terminated). For senior engineers at startups, this can be the difference between $0 and $500K+. Typically buried in the equity plan, not the employment contract, so many candidates never review it.",
 "Prior Inventions Disclosure — The list of prior personal projects/IP that the employee declares as NOT belonging to the employer. If not disclosed, the IP assignment clause may be interpreted to cover them. Senior engineers with side projects or open-source contributions who fail to disclose risk losing ownership of personal work.",
 "Arbitration Clause — Mandatory arbitration replacing the right to sue in court. Often includes class action waiver. Substantially reduces the employee's leverage in disputes. Typically presented as standard boilerplate but has significant practical implications for enforcement of all other terms.",
],
"""Position → Role expectations; Comp + Equity + Bonus + Benefits → Total package
IP Assignment + NDA + Non-Compete + Non-Solicit → Restrictive covenants
Termination → Severance + Equity treatment (acceleration clause)
Change of Control → Equity outcome in acquisition
Arbitration → Dispute resolution mechanism (affects enforceability of all other terms)""",
"""- Suspected: Clawback provisions, garden leave, invention disclosure deadlines, data return obligations.
- Gaps: No modeling of NEGOTIATION LEVERAGE — which terms are actually negotiable (equity, title, severance usually yes; IP assignment, arbitration usually no).
- Outside view: Employment contracts are presented as bilateral agreements but are largely adhesion contracts where the employee's negotiation power is limited to compensation terms. The restrictive covenants are typically non-negotiable despite being the most impactful terms post-employment.
- Estimated completeness: 73%"""
)),

("Enumerate all components of a machine learning prediction pipeline.", _enum("ML prediction pipeline from data to business decision.", "INSIDE — all components from data to action. OUTSIDE — initial research, organizational decisions.", 18,
["Raw Data Sources — Databases, APIs, streams, sensors generating data.\n   Emerges from: root (business operations) | Gives rise to: Ingestion | Evidence: Source inventory.",
 "Data Ingestion — ETL/ELT extracting, transforming, loading data.\n   Emerges from: Raw sources | Gives rise to: Raw feature store | Evidence: Pipeline logs.",
 "Data Quality Checks — Schema validation, null rates, distribution checks.\n   Emerges from: Ingestion | Gives rise to: Clean data or alerts | Evidence: Validation reports.",
 "Feature Engineering — Raw data → model features: aggregations, encodings, normalization.\n   Emerges from: Clean data + Domain knowledge | Gives rise to: Feature store | Evidence: Feature code.",
 "Feature Store — Centralized repository for training and serving.\n   Emerges from: Feature engineering | Gives rise to: Training data + Inference features | Evidence: Feature store queries.",
 "Label Source — Ground truth: annotations, outcomes, user actions.\n   Emerges from: root (business process) | Gives rise to: Training data | Evidence: Annotation platform.",
 "Model Training — Algorithm execution, hyperparameter tuning, cross-validation.\n   Emerges from: Training data + Algorithm | Gives rise to: Trained model | Evidence: Training logs, MLflow.",
 "Model Evaluation — Performance on held-out test set with business-relevant metrics.\n   Emerges from: Trained model + Test data | Gives rise to: Deployment decision | Evidence: Evaluation report.",
 "Model Registry — Versioned storage with metadata.\n   Emerges from: Evaluation (if approved) | Gives rise to: Deployment | Evidence: Registry entries.",
 "Model Deployment — Promotion to serving: container build, endpoint config.\n   Emerges from: Registry + Serving infra | Gives rise to: Live endpoint | Evidence: Deployment logs.",
 "Inference — Forward pass with assembled feature vector.\n   Emerges from: Request + Features + Model | Gives rise to: Raw prediction | Evidence: Inference logs.",
 "Post-Processing — Calibration, thresholding, explanation generation.\n   Emerges from: Raw prediction | Gives rise to: Business-ready output | Evidence: Post-processing logic.",
 "Prediction Logging — Recording every prediction for monitoring and retraining.\n   Emerges from: Inference | Gives rise to: Monitoring data | Evidence: Prediction log store.",
 "Model Monitoring — Drift detection, accuracy tracking, latency monitoring.\n   Emerges from: Prediction logs + Ground truth | Gives rise to: Retraining trigger or alert | Evidence: Monitoring dashboards.",
 "Business Decision System — Downstream application consuming prediction.\n   Emerges from: Business-ready prediction | Gives rise to: Business outcome | Evidence: Application logs.",
 "Feedback Loop — Outcomes flowing back as future labels.\n   Emerges from: Business outcome | Gives rise to: Retraining data | Evidence: Outcome tracking.",
],
["Training-Serving Skew — Feature distributions at inference differing from training. Invisible because the model appears to work (produces predictions) but predictions are wrong because features are computed differently in the two environments. Most common cause of silent ML failure in production.",
 "Label Leakage — Features that implicitly contain the label (e.g., future data unavailable at prediction time). Creates models that appear excellent in development and fail completely in production. Invisible because training metrics look great.",
],
"""Data → Ingestion → Quality → Features → Feature Store → Training → Evaluation → Registry → Deploy → Serving
Request → Feature Retrieval → Inference → Post-Processing → Business Decision → Outcome → Feedback → Labels
Monitoring watches: prediction distributions, feature drift, accuracy
Training-Serving Skew: validates feature consistency across environments""",
"""- Suspected: A/B testing, shadow deployment, cost optimization, compliance/audit layer.
- Gaps: No GOVERNANCE — who approves deployment, review process, rollback decisions.
- Outside view: The pipeline is a TRUST CHAIN. The most dangerous failures are silent: data quality issues, training-serving skew, model degradation.
- Estimated completeness: 75%"""
)),

("Enumerate all components of the ethics of autonomous vehicle decision-making.", _enum("Autonomous vehicle ethics: trolley problem and beyond.", "INSIDE — ethical frameworks, stakeholders, technical constraints. OUTSIDE — regulatory politics.", 15,
["Sensor Limitations — Cameras, LiDAR, radar have inherent failure modes (rain, glare, edge cases).\n   Emerges from: Physics + Engineering | Gives rise to: Uncertainty in decisions | Evidence: Sensor performance data.",
 "Decision Algorithm — Software making real-time safety decisions.\n   Emerges from: Engineering + Ethical constraints | Gives rise to: Behavioral outcomes | Evidence: Algorithm specification.",
 "Trolley Problem Framing — Forced choice between harm to different parties.\n   Emerges from: Philosophical tradition | Gives rise to: Public discourse (often misleading) | Evidence: Philosophy literature.",
 "Utilitarian Calculation — Minimize total harm across all potential outcomes.\n   Emerges from: Ethical framework | Gives rise to: Outcome optimization | Evidence: Utility models.",
 "Rights-Based Constraints — Some actions are prohibited regardless of outcomes (targeting individuals).\n   Emerges from: Deontological ethics | Gives rise to: Action constraints | Evidence: Rights frameworks.",
 "Liability Framework — Who is responsible: manufacturer, owner, operator, software developer.\n   Emerges from: Legal system | Gives rise to: Accountability structure | Evidence: Legislation, case law.",
 "Occupant vs. Pedestrian Prioritization — Whose safety the vehicle prioritizes.\n   Emerges from: Design choice + Legal/ethical constraint | Gives rise to: Purchase decisions, public trust | Evidence: MIT Moral Machine data.",
 "Transparency of Decision Logic — Whether the public can understand how the car decides.\n   Emerges from: ML opacity + Public accountability | Gives rise to: Trust, regulatory acceptance | Evidence: Explainability requirements.",
 "Training Data Bias — ML models trained on populations that may underrepresent certain groups.\n   Emerges from: Data collection patterns | Gives rise to: Unequal safety for different populations | Evidence: Performance audits across demographics.",
 "Edge Case Handling — Behavior in scenarios not represented in training data.\n   Emerges from: Finite training coverage | Gives rise to: Unpredictable behavior | Evidence: Edge case testing.",
 "Human Comparison Baseline — AVs need only be safer than human drivers, not perfect.\n   Emerges from: Pragmatic ethics | Gives rise to: Acceptable risk threshold | Evidence: Human crash statistics.",
 "Public Trust and Adoption — Whether people will ride in and share roads with AVs.\n   Emerges from: Safety record + Transparency + Media coverage | Gives rise to: Technology viability | Evidence: Public surveys.",
],
["Statistical vs. Identifiable Lives — AV safety is measured statistically (10,000 fewer deaths per year) but failures are experienced individually (one specific person killed by a specific car). Public reaction to identifiable AV-caused deaths far exceeds reaction to statistical reductions. This mismatch between statistical benefit and identifiable harm is the central adoption challenge.",
 "Algorithm Audit Accessibility — Whether third parties can verify the ethical behavior of the decision algorithm. Currently, most AV decision systems are proprietary black boxes. Without audit capability, ethical claims are unverifiable. This is the governance gap: we are deploying ethical agents whose ethics cannot be inspected.",
 "Infrastructure Complicity — Road design, traffic systems, and pedestrian infrastructure that assume human drivers. AV ethical dilemmas are partly created by infrastructure that was not designed for autonomous agents. Many trolley-problem scenarios could be eliminated by infrastructure redesign.",
],
"""Sensor Input → Decision Algorithm → Action
Ethical Framework (utilitarian vs. rights) → Algorithm Constraints
Training Data → Model Behavior → Bias Risk
Safety Record → Public Trust → Adoption → Data Collection → Better Models (feedback loop)
Liability Framework → Manufacturer Behavior → Design Priorities""",
"""- Suspected: Insurance model changes, cybersecurity (hacking ethical constraints), international standard differences, transition period (mixed human/AV traffic).
- Gaps: No modeling of the TRANSITION PERIOD — ethics of mixed autonomy roads where some cars are human-driven and some are autonomous. Also missing: the ethics of NOT deploying AVs (accepting 40,000 annual US traffic deaths when AVs could reduce them).
- Outside view: The trolley problem dominates public discourse but is the WRONG frame. AVs face millions of mundane decisions (speed, following distance, lane position) that cumulatively determine safety far more than rare trolley scenarios. The ethics of the mundane is more important than the ethics of the extreme.
- Estimated completeness: 70%"""
)),

("Enumerate all components of a software project estimation process.", _enum("Software project estimation.", "INSIDE — estimation methods, biases, inputs. OUTSIDE — project execution.", 15,
["Requirements Decomposition — Breaking project into estimable work units.\n   Emerges from: Requirements + Architecture | Gives rise to: Work breakdown structure | Evidence: Task lists.",
 "Estimation Method — Technique used: expert judgment, planning poker, story points, reference class, parametric.\n   Emerges from: Team practice | Gives rise to: Raw estimates | Evidence: Estimation session records.",
 "Historical Data — Past project durations for similar work.\n   Emerges from: Project tracking history | Gives rise to: Reference class baseline | Evidence: Time tracking data.",
 "Complexity Assessment — Technical difficulty, unknowns, integration points.\n   Emerges from: Technical analysis | Gives rise to: Effort multiplier | Evidence: Architecture review.",
 "Dependency Mapping — External dependencies that affect timeline.\n   Emerges from: System analysis | Gives rise to: Schedule constraints | Evidence: Dependency diagram.",
 "Team Capacity — Available developer hours accounting for meetings, PTO, interrupts.\n   Emerges from: Team size + Calendar | Gives rise to: Realistic throughput | Evidence: Calendar, historical velocity.",
 "Risk Buffer — Contingency time for unknowns (typically 20-50% of estimate).\n   Emerges from: Risk assessment | Gives rise to: Confidence range | Evidence: Risk register.",
 "Stakeholder Communication — How estimates are presented and what confidence level is conveyed.\n   Emerges from: Estimate + Communication skill | Gives rise to: Expectation setting | Evidence: Communicated timeline.",
 "Estimation Bias — Systematic errors: optimism bias, anchoring, planning fallacy.\n   Emerges from: Human cognition | Gives rise to: Underestimation (most common) | Evidence: Actual vs. estimated comparison.",
 "Scope Creep Factor — Historical rate at which scope expands during development.\n   Emerges from: Past project data | Gives rise to: Adjusted timeline | Evidence: Original vs. final scope comparison.",
 "Review and Calibration — Process of checking estimates against reality and adjusting.\n   Emerges from: Estimation discipline | Gives rise to: Improved future estimates | Evidence: Retrospective data.",
],
["The Confidence Interval That Nobody Gives — Estimates are almost always communicated as point estimates ('it will take 6 weeks') rather than ranges ('60% chance it takes 4-8 weeks, 90% chance 3-12 weeks'). The missing confidence interval is the most important piece of information and is systematically omitted because it makes the estimate seem 'uncertain' — which it IS.",
 "Parkinson's Law Interaction — Work expands to fill the time available. A generous estimate can CREATE the exact duration it predicted, not because the work required it but because the deadline became the target. This creates a paradox: accurate estimates become self-fulfilling, and padded estimates waste the padding.",
 "The '90% Complete' Plateau — The last 10% of work takes 50% of the time. Software estimation systematically underestimates integration, testing, polish, deployment, and documentation — the 'last mile' work. This creates the universal experience of being '90% done' for weeks.",
],
"""Requirements → Decomposition → Raw Estimates
Historical Data → Reference Class → Calibrated Estimates
Complexity + Dependencies → Effort Multiplier → Adjusted Estimates
Estimation Bias → Systematic Underestimation (must be corrected)
Risk Buffer + Scope Creep Factor → Realistic Timeline
Confidence Interval → Proper Communication""",
"""- Suspected: Business pressure to give lower estimates, technical spike results, prototype learnings, team morale effect of consistently missed estimates.
- Gaps: No modeling of the SOCIAL dynamics — estimates are simultaneously technical predictions and political commitments. The estimate that is technically accurate may be organizationally unacceptable.
- Outside view: The estimation 'problem' is less about technical forecasting and more about organizational truth-telling. Teams that can honestly say 'we don't know yet, here's what we need to learn' produce better outcomes than teams forced to commit to precise numbers prematurely.
- Estimated completeness: 72%"""
)),

]
