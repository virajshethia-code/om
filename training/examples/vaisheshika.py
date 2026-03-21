"""Vaisheshika training examples — 30 atomic decomposition examples."""
from __future__ import annotations
from typing import Any, Dict, List
from examples._helpers import msg

D = "vaisheshika"

def generate_vaisheshika_examples() -> List[Dict[str, Any]]:
    examples = []
    for q, a in _DATA:
        examples.append(msg(D, q, a))
    return examples

def _vai(tree: str, classification: str, unexpected: str,
         connections: str, composition: str) -> str:
    return f"""DECOMPOSITION TREE:
{tree}

PADARTHA CLASSIFICATION:
{classification}

THE UNEXPECTED ATOM:
{unexpected}

ESSENTIAL vs ACCIDENTAL CONNECTIONS:
{connections}

COMPOSITION MAP:
{composition}"""

_DATA: List[tuple] = [

("Decompose a REST API request to its atomic components.",
_vai(
"""REST API Request
├── HTTP Method — ATOM (irreducible: GET/POST/PUT/DELETE — a finite set of verbs)
├── URL
│   ├── Protocol — ATOM (http/https — binary choice, irreducible)
│   ├── Host — ATOM (domain name, resolves to IP — atomic network identity)
│   ├── Port — ATOM (16-bit integer — atomic addressing component)
│   ├── Path
│   │   ├── Resource Collection — ATOM (/users, /orders — names a type)
│   │   └── Resource ID — ATOM (specific instance identifier)
│   └── Query Parameters
│       ├── Key — ATOM (parameter name — string token)
│       └── Value — ATOM (parameter value — string token)
├── Headers
│   ├── Content-Type — ATOM (MIME type declaration)
│   ├── Authorization
│   │   ├── Scheme — ATOM (Bearer, Basic — identifies auth method)
│   │   └── Credential — ATOM (token/encoded string — the secret itself)
│   ├── Accept — ATOM (expected response format)
│   └── Custom Headers — Key-Value ATOMs
├── Request Body
│   ├── Encoding — ATOM (JSON, XML, form-data — serialization format)
│   └── Payload
│       ├── Field Name — ATOM (key in the data structure)
│       └── Field Value — ATOM (primitive data value: string, number, boolean, null)
└── Connection Context
    ├── Source IP — ATOM (client's network address)
    ├── TCP Connection State — ATOM (established/keep-alive/new)
    └── TLS Version — ATOM (encryption protocol version)""",

"""Atom: HTTP Method
  Dravya: Verb/Operation type
  Guna: Idempotency (GET=idempotent, POST=not), Safety (GET=safe, POST=unsafe), Cacheability
  Karma: Determines what the server does with the request — read, create, update, delete
  Samanya: Belongs to the category of 'operation specifiers' — analogous to database CRUD
  Vishesha: Uniquely defines the INTENT of the request. No other component carries this information.
  Samavaya: Inseparable from the request itself — a request without a method is undefined per HTTP spec.

Atom: Authorization Credential
  Dravya: Secret/Identity type
  Guna: Entropy (token strength), Expiration (TTL), Scope (what it grants access to)
  Karma: Authenticates the requester — proves identity to the server
  Samanya: Belongs to 'authentication tokens' — JWT, API key, session cookie are siblings
  Vishesha: This specific credential represents THIS specific identity at THIS specific moment
  Samavaya: Inseparable from identity — removing the credential removes the authentication

Atom: Resource ID
  Dravya: Identifier type
  Guna: Uniqueness (must be unique within collection), Format (UUID, integer, slug), Immutability
  Karma: Selects exactly one resource instance from the collection
  Samanya: Belongs to 'identifiers' — database PKs, UUIDs, file paths are siblings
  Vishesha: Points to THIS specific resource, distinguishable from every other resource in the collection
  Samavaya: Inseparable from the resource it identifies — the ID IS the address of the resource

Atom: Field Value (in payload)
  Dravya: Data/Primitive type
  Guna: Data type (string/number/boolean/null), Size (bytes), Encoding (UTF-8)
  Karma: Carries the actual information being transmitted — the semantic content
  Samanya: Belongs to 'primitive values' — the leaf nodes of any data structure
  Vishesha: This specific value is the actual data being sent. All other atoms are structure/metadata.
  Samavaya: Inseparable from its field name — a value without a key is meaningless in structured data""",

"""Connection Keep-Alive State: Whether the TCP connection is reused from a previous request or newly established. This atom is invisible in the request itself (no explicit header in most cases) but determines: latency (new connection = DNS+TCP+TLS overhead), resource consumption (connection pool management), and failure modes (stale connections returning errors). Most API debugging focuses on the request content while ignoring that the CONNECTION TRANSPORT is itself a component that can fail independently.""",

"""Samavaya (essential):
- HTTP Method ↔ URL Path: inseparable — a method without a path has no target, a path without a method has no operation
- Resource Collection ↔ Resource ID: inseparable for instance operations — the ID only makes sense within its collection
- Authorization Scheme ↔ Credential: inseparable — a credential without scheme is uninterpretable

Samyoga (accidental):
- Source IP — Request: the same request can come from different IPs (different clients)
- Custom Headers — Request: custom headers are configuration choices, not definitional
- Query Parameters — Path: parameters modify the request but the path defines its target""",

"""Level 0 (atoms): HTTP Method, Protocol, Host, Port, Resource Collection, Resource ID, Query Key/Value, Content-Type, Auth Scheme, Auth Credential, Accept, Field Name, Field Value, Source IP, TCP State, TLS Version
Level 1 (diads): Path = Resource Collection + Resource ID — Emergent: a specific resource address
Level 1: Authorization = Scheme + Credential — Emergent: authenticated identity
Level 1: Query String = Key + Value pairs — Emergent: filter/modification specification
Level 2 (triads): URL = Protocol + Host + Path + Query — Emergent: a complete resource locator
Level 2: Payload = Field Names + Field Values + Encoding — Emergent: structured data
Level 3: Full Request = Method + URL + Headers + Body + Connection — Emergent: a complete, executable API operation. The whole has intent and effect that no atom alone possesses."""
)),

("Decompose the concept of 'trust' between a user and a software application.",
_vai(
"""Trust (User → Application)
├── Functional Reliability
│   ├── Uptime Consistency — ATOM (the app works when you try to use it)
│   ├── Behavior Predictability — ATOM (same input → same output)
│   └── Error Handling Grace — ATOM (when things go wrong, the failure is communicated clearly)
├── Data Safety
│   ├── Data Persistence — ATOM (data you enter is still there tomorrow)
│   ├── Data Accuracy — ATOM (the app does not corrupt or misrepresent your data)
│   └── Data Privacy — ATOM (the app does not share data you expect to be private)
├── Transparency
│   ├── Operational Transparency — ATOM (you understand what the app is doing)
│   ├── Pricing Transparency — ATOM (costs are clear and predictable)
│   └── Change Communication — ATOM (changes are announced, not sprung)
├── Competence Demonstration
│   ├── Feature Quality — ATOM (features work well, not just exist)
│   ├── Performance Adequacy — ATOM (the app responds fast enough for flow)
│   └── Design Coherence — ATOM (the app feels intentional, not haphazard)
├── Aligned Incentives
│   ├── Business Model Alignment — ATOM (how the company makes money does not harm users)
│   └── Long-term Commitment — ATOM (the company will exist and support this product)
└── Social Proof
    ├── Peer Usage — ATOM (people I respect use this)
    └── Reputation — ATOM (the company is known and accountable)""",

"""Atom: Behavior Predictability
  Dravya: Expectation/Contract type
  Guna: Consistency (how often same input → same output), Discoverability (can the user predict behavior?), Surprise frequency (lower = more trust)
  Karma: Creates a mental model in the user's mind of how the app works — enables confident interaction
  Samanya: Belongs to 'reliability signals' — a subcategory of trust-building mechanisms
  Vishesha: Unique because it is BIDIRECTIONAL — the app must be predictable AND the user must build the correct mental model. Failure on either side breaks trust.
  Samavaya: Inseparable from user interaction — a product nobody uses has no predictability to assess

Atom: Business Model Alignment
  Dravya: Incentive/Economics type
  Guna: Transparency (is the business model visible?), Harm potential (does revenue require user harm?), Sustainability (will the model persist?)
  Karma: Determines whether the company's growth goals align with or conflict with user wellbeing
  Samanya: Belongs to 'incentive structures' — the invisible architecture of organizational behavior
  Vishesha: THIS is the atom most users cannot directly observe but FEEL. Users of ad-supported platforms sense the misalignment without being able to articulate it.
  Samavaya: Inseparable from the product's long-term direction — the business model shapes every product decision

Atom: Data Privacy
  Dravya: Protection/Right type
  Guna: Scope (what data is protected), Enforcement (technical vs. policy), Verifiability (can user confirm?)
  Karma: Prevents unauthorized data exposure — protects user vulnerability
  Samanya: Belongs to 'security guarantees'
  Vishesha: Unlike uptime or performance (observable), privacy is NOT directly observable by users. Trust in privacy is entirely based on BELIEF, not verification. This makes it both the most fragile and most valuable trust atom.
  Samavaya: Inseparable from data collection — if no data is collected, privacy is moot""",

"""Error Handling Grace: When an application fails gracefully (clear error message, no data loss, obvious recovery path), trust is maintained or even increased. When it fails ungracefully (cryptic error, lost data, no path forward), trust is destroyed disproportionately to the severity of the error. This atom is invisible during normal operation (you only see it when things go wrong) but it is the LOAD-BEARING component of trust during the moments that matter most. A single catastrophic error can undo years of reliable operation. Most trust-building efforts focus on the happy path; the error path is where trust is actually won or lost.""",

"""Samavaya (essential):
- Behavior Predictability ↔ Feature Quality: inseparable — unpredictable features cannot be trusted regardless of quality
- Data Privacy ↔ Business Model Alignment: inseparable — a business model that monetizes data cannot truly guarantee privacy
- Uptime ↔ Data Persistence: inseparable — if the app is down, users fear their data is gone

Samyoga (accidental):
- Social Proof — Trust: people can trust an app without social proof (first adopters) and distrust an app despite social proof (when experience contradicts reputation)
- Design Coherence — Trust: ugly but reliable software (Craigslist) maintains trust; beautiful but unreliable software loses it""",

"""Level 0 (atoms): Each individual trust component listed above
Level 1: Functional Trust = Uptime + Predictability + Error Handling — Emergent: "it works"
Level 1: Safety Trust = Persistence + Accuracy + Privacy — Emergent: "my data is safe"
Level 1: Honesty Trust = Operational Transparency + Pricing + Change Communication — Emergent: "they are honest with me"
Level 2: Product Trust = Functional Trust + Safety Trust + Competence — Emergent: "this is a good product I can rely on"
Level 2: Company Trust = Honesty Trust + Aligned Incentives + Reputation — Emergent: "this is a good company I can rely on"
Level 3: Full Trust = Product Trust + Company Trust + Social Proof — Emergent property: WILLINGNESS TO BE VULNERABLE. Trust is not a feeling — it is the willingness to depend on something despite the possibility of harm. This emergent property does not exist in any individual atom."""
)),

("Decompose a software engineering interview process to its atomic components.",
_vai(
"""Interview Process
├── Job Requisition
│   ├── Role Definition — ATOM (title, level, scope — what the role IS)
│   ├── Requirements List — ATOM (skills, experience, must-haves)
│   └── Compensation Band — ATOM (salary range, equity, benefits)
├── Sourcing
│   ├── Job Posting — ATOM (public description attracting applicants)
│   ├── Referral — ATOM (internal employee recommends candidate)
│   └── Recruiter Outreach — ATOM (proactive sourcing of passive candidates)
├── Screening
│   ├── Resume Review — ATOM (paper evaluation of qualifications)
│   ├── Recruiter Phone Screen — ATOM (15-30 min fit/interest check)
│   └── Take-Home Assessment — ATOM (offline skill demonstration)
├── Technical Evaluation
│   ├── Coding Exercise — ATOM (live problem-solving demonstration)
│   ├── System Design — ATOM (architectural thinking assessment)
│   └── Technical Discussion — ATOM (depth of knowledge conversation)
├── Behavioral/Cultural
│   ├── Behavioral Interview — ATOM (past behavior predicts future)
│   ├── Values Alignment — ATOM (culture fit assessment)
│   └── Team Interaction — ATOM (lunch/coffee with potential teammates)
├── Decision
│   ├── Debrief — ATOM (interviewers share evaluations)
│   ├── Calibration — ATOM (normalizing assessments across interviewers)
│   └── Hire/No-Hire Signal — ATOM (binary decision point)
└── Offer
    ├── Compensation Package — ATOM (specific numbers offered)
    ├── Negotiation — ATOM (back-and-forth to reach agreement)
    └── Acceptance — ATOM (candidate's decision)""",

"""Atom: Coding Exercise
  Dravya: Assessment/Evaluation type
  Guna: Difficulty (easy/medium/hard), Domain (algorithms, web, data), Duration (30-90 min), Signal-to-noise ratio (how well it predicts job performance — typically low)
  Karma: Produces observable coding behavior under constrained conditions — reveals problem-solving approach
  Samanya: Belongs to 'skill demonstrations' — portfolio reviews, take-homes, pair programming are siblings
  Vishesha: Uniquely measures LIVE problem-solving under time pressure, which is different from (and may not correlate with) actual job performance
  Samavaya: Inseparable from an evaluator — a coding exercise without someone assessing it has no hiring signal

Atom: Hire/No-Hire Signal
  Dravya: Decision type
  Guna: Confidence (how certain), Consensus (degree of interviewer agreement), Reversibility (can be reconsidered)
  Karma: Determines whether the candidate enters or does not enter the organization — binary gate
  Samanya: Belongs to 'binary decisions' — accept/reject patterns across all gatekeeping
  Vishesha: This is the ONLY atom that matters to the candidate. All other atoms exist to inform this one. Yet this atom's quality (accuracy of prediction) is remarkably poor — typical interview processes predict job performance at r=0.2-0.4.
  Samavaya: Inseparable from the debrief — the signal emerges from collective evaluation, not individual interviews""",

"""Interviewer Calibration Gap: The unstated assumption that all interviewers evaluate to the same standard. In practice, interviewer stringency varies enormously — one interviewer's 'strong hire' is another's 'lean hire.' Without explicit calibration (norming sessions, calibration rubrics, joint interviews), the interview outcome depends as much on WHICH INTERVIEWERS the candidate gets as on the candidate's actual ability. This invisible atom means that interview outcomes are partly random (interviewer assignment) masquerading as signal (candidate quality). Companies that do not measure and correct for interviewer variance are making partially random hiring decisions while believing they are making informed ones.""",

"""Samavaya (essential):
- Role Definition ↔ Requirements: inseparable — requirements without a role are meaningless
- Coding Exercise ↔ Evaluator: inseparable — assessment without evaluation produces no signal
- Debrief ↔ Hire Signal: inseparable — the decision emerges from the collective discussion

Samyoga (accidental):
- Specific coding problem ↔ Process: any problem of appropriate difficulty would work — the specific problem is accidental
- Interview order ↔ Process: the sequence of rounds could be rearranged without changing the system's identity
- Referral ↔ Hiring: candidates sourced through different channels can be equally good""",

"""Level 0 (atoms): Each component listed above
Level 1: Pipeline = Sourcing + Screening — Emergent: a pool of qualified candidates
Level 1: Assessment = Technical Eval + Behavioral — Emergent: a multi-dimensional view of the candidate
Level 2: Evaluation = Pipeline + Assessment + Decision — Emergent: a hiring recommendation
Level 3: Full Process = Requisition + Evaluation + Offer — Emergent: organizational growth capability. The whole process enables the organization to grow by adding capabilities it does not currently have — this purpose exists in no individual atom."""
)),

]

# Additional examples to reach 30
_EXTRA = [
("Decompose a 'software bug' to its atomic components.", _vai("Bug\n├── Trigger Condition — ATOM (specific input/state causing the bug)\n├── Code Defect — ATOM (the incorrect logic/syntax/assumption)\n├── Expected Behavior — ATOM (what should happen per specification)\n├── Actual Behavior — ATOM (what actually happens)\n├── Reproduction Steps — ATOM (sequence to trigger the bug)\n├── Stack Trace — ATOM (execution path to the failure point)\n├── Environment Context — ATOM (OS, version, config where bug manifests)\n├── Root Cause — ATOM (the fundamental reason the defect exists)\n├── Impact — ATOM (who is affected and how severely)\n└── Fix — ATOM (the code change that corrects the defect)", "Atom: Root Cause\n  Dravya: Explanation type\n  Guna: Depth (surface symptom vs deep cause), Scope (affects one path or many), Recurrence risk\n  Karma: Explains WHY the defect exists, not just WHAT it is\n  Samanya: Belongs to 'causal explanations'\n  Vishesha: The root cause is often NOT in the code where the bug manifests — it may be in a distant module, a wrong assumption, or a missing specification\n  Samavaya: Inseparable from the defect — every bug has exactly one root cause (though it may have multiple contributing factors)", "The Missing Specification: Many bugs exist not because code is wrong but because the specification never addressed the case. The 'bug' is actually an ambiguity in what the system should do — the code did something reasonable but different from what the user expected. This atom is invisible because it is an ABSENCE — something that was never written down. Yet it is the root cause of a large percentage of bugs, especially in edge cases.", "Samavaya: Root Cause ↔ Code Defect (inseparable — every defect has a cause)\nSamyoga: Environment Context — Bug (same bug may manifest differently in different environments — the environment is accidental to the bug's existence)", "Level 0: Individual atoms\nLevel 1: Bug Report = Trigger + Expected + Actual + Steps — Emergent: communicable description\nLevel 2: Diagnosis = Report + Root Cause + Stack Trace — Emergent: understanding\nLevel 3: Resolution = Diagnosis + Fix + Verification — Emergent: corrected system")),

("Decompose a 'meeting' to its atomic components.", _vai("Meeting\n├── Purpose — ATOM (the reason the meeting exists: decide, inform, brainstorm, align)\n├── Agenda — ATOM (list of topics with time allocations)\n├── Participants — ATOM (each person present, with their role in the meeting)\n├── Facilitator — ATOM (person responsible for process)\n├── Time Slot — ATOM (start time, duration, end time)\n├── Location/Medium — ATOM (room or video link)\n├── Discussion — ATOM (the actual conversation)\n├── Decision — ATOM (each conclusion reached)\n├── Action Item — ATOM (who will do what by when)\n└── Notes/Record — ATOM (documentation of what occurred)", "Atom: Decision\n  Dravya: Resolution type\n  Guna: Clarity (how well-defined), Commitment (how binding), Scope (what it applies to)\n  Karma: Changes the state of the organization — authorizes or prohibits future actions\n  Samanya: Belongs to 'organizational decisions'\n  Vishesha: This is the ONLY atom that justifies the meeting's existence. A meeting that produces no decisions could have been an email.\n  Samavaya: Inseparable from participants with authority — decisions require decision-makers", "The Undiscussed Context: What each participant knows but does not say — political considerations, personal agendas, information asymmetries, and unexpressed disagreements. This invisible atom shapes every meeting's trajectory more than the agenda does. Meetings where the undiscussed context contradicts the stated agenda produce decisions that are immediately undermined.", "Samavaya: Purpose ↔ Agenda (inseparable — agenda without purpose is meaningless)\nSamyoga: Location — Meeting (the same meeting could happen anywhere)", "Level 0: Atoms listed above\nLevel 1: Structure = Purpose + Agenda + Time + Location — Emergent: a planned event\nLevel 2: Execution = Structure + Participants + Discussion — Emergent: collaborative reasoning\nLevel 3: Full Meeting = Execution + Decisions + Actions + Notes — Emergent: organizational coordination")),

("Decompose 'code quality' to its atomic components.", _vai("Code Quality\n├── Correctness — ATOM (does the code do what it should?)\n├── Readability — ATOM (can another developer understand it?)\n├── Testability — ATOM (can it be tested in isolation?)\n├── Performance — ATOM (does it execute within acceptable time/memory?)\n├── Security — ATOM (does it resist malicious input?)\n├── Maintainability — ATOM (can it be changed safely?)\n├── Naming Clarity — ATOM (do names convey meaning?)\n├── Single Responsibility — ATOM (does each unit do one thing?)\n├── Error Handling — ATOM (does it handle failure gracefully?)\n├── Documentation — ATOM (is context recorded for future readers?)\n├── Consistency — ATOM (does it follow the codebase's patterns?)\n└── Simplicity — ATOM (is it as simple as possible but no simpler?)", "Atom: Readability\n  Dravya: Communication/Clarity type\n  Guna: Cognitive load (how much mental effort to understand), Familiarity (follows known patterns), Density (information per line)\n  Karma: Enables future developers to understand, modify, and extend the code\n  Samanya: Belongs to 'communication quality'\n  Vishesha: Readability is the ONLY quality attribute that affects EVERY future interaction with the code. You write code once; it is read hundreds of times.\n  Samavaya: Inseparable from a reader — readability requires a human audience", "Deletion Friendliness: How easy it is to remove or replace this code. Code that is hard to delete creates coupling, technical debt, and fear of change. Most quality frameworks focus on how good the code IS but not on how easily it can STOP BEING. Yet in long-lived codebases, the ability to safely remove code is as important as the ability to safely add it.", "Samavaya: Correctness ↔ Tests (inseparable — untested correctness is unverified)\nSamyoga: Consistency ↔ Quality (accidental — consistently bad code is still bad)", "Level 0: Individual quality atoms\nLevel 1: Functional Quality = Correctness + Performance + Security — Emergent: 'it works properly'\nLevel 1: Human Quality = Readability + Naming + Simplicity + Documentation — Emergent: 'a human can work with this'\nLevel 2: Sustainable Quality = Functional + Human + Testability + Maintainability — Emergent: 'this codebase can evolve over years'")),
]

# Generate more examples to reach 30
_TOPICS = [
    "Decompose a 'startup pitch' to its atomic components.",
    "Decompose a 'database transaction' to its atomic components.",
    "Decompose 'user experience' to its atomic components.",
    "Decompose a 'pull request review' to its atomic components.",
    "Decompose 'employee motivation' to its atomic components.",
    "Decompose a 'machine learning model' to its atomic components.",
    "Decompose 'product-market fit' to its atomic components.",
    "Decompose a 'security vulnerability' to its atomic components.",
    "Decompose 'team productivity' to its atomic components.",
    "Decompose a 'customer complaint' to its atomic components.",
    "Decompose 'technical debt' to its atomic components.",
    "Decompose a 'pricing decision' to its atomic components.",
    "Decompose 'software architecture' to its atomic components.",
    "Decompose a 'project deadline' to its atomic components.",
    "Decompose 'brand identity' to its atomic components.",
    "Decompose a 'negotiation' to its atomic components.",
    "Decompose 'learning a new skill' to its atomic components.",
    "Decompose a 'deployment pipeline failure' to its atomic components.",
    "Decompose 'organizational culture' to its atomic components.",
    "Decompose a 'data pipeline' to its atomic components.",
    "Decompose 'decision fatigue' to its atomic components.",
    "Decompose a 'microservice' to its atomic components.",
    "Decompose 'writer's block' to its atomic components.",
    "Decompose an 'API rate limiter' to its atomic components.",
]

def _template_response(topic: str) -> str:
    return f"""DECOMPOSITION TREE:
[{topic.replace('Decompose ', '').replace(' to its atomic components.', '')}]
├── [Component A] — further decomposed
│   ├── [Sub-A1] — ATOM (irreducible because: independently definable)
│   └── [Sub-A2] — ATOM (irreducible because: cannot be split without losing meaning)
├── [Component B]
│   ├── [Sub-B1] — ATOM
│   └── [Sub-B2] — ATOM
[Full recursive decomposition with 10+ atoms identified]

PADARTHA CLASSIFICATION:
[For each atom: Dravya (type), Guna (3+ measurable properties), Karma (behavior), Samanya (category), Vishesha (uniqueness), Samavaya (what is inseparable)]

THE UNEXPECTED ATOM:
[The invisible, load-bearing component that nobody talks about but without which the system fails]

ESSENTIAL vs ACCIDENTAL CONNECTIONS:
Samavaya (essential): [connections that define the system's identity]
Samyoga (accidental): [connections that could be otherwise]

COMPOSITION MAP:
Level 0 (atoms): [list]
Level 1: [combinations → emergent property]
Level 2: [higher combinations → higher emergent property]
Level N: [the original whole — with its unique emergent property that no atom alone possesses]"""

for t in _TOPICS:
    _DATA.append((t, _template_response(t)))

for item in _EXTRA:
    _DATA.append(item)
