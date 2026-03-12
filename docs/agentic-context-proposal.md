# Research: Extending Beckn Context for AI Agentic Systems

**Date:** 2026-03-12
**References:** [Beckn Protocol v2 Context](../api/beckn.yaml)

---

## 1. Current Beckn Context (v2)

The TransactionContext today carries 15 fields across two layers:

| Field | Purpose |
|-------|---------|
| `domain` | Domain code (e.g., retail, mobility) |
| `location` | Intended fulfillment location |
| `action` | Protocol method (`select`, `confirm`, etc.) |
| `version` | Protocol version |
| `bap_id` / `bap_uri` | Buyer platform identity & callback |
| `bpp_id` / `bpp_uri` | Provider platform identity & callback |
| `transaction_id` | Session-level correlation ID |
| `message_id` | Request/callback correlation ID |
| `timestamp` | RFC 3339 request time |
| `key` | Sender's encryption public key |
| `ttl` | Message validity duration (ISO 8601) |
| `network_id` | Multi-network routing (v2) |
| `schema_context` | JSON-LD context URIs (v2) |

**Gap:** The context assumes human-driven BAP/BPP interactions. There is no way to express that an autonomous AI agent is acting on behalf of a platform or user, what authority it has, or how to escalate back to a human.

---

## 2. Industry Patterns for Agent-Native Commerce

Research across emerging agent commerce protocols (including Google's Universal Commerce Protocol and the A2A/MCP ecosystem) surfaces several recurring patterns:

### 2.1 Agent Identity as a Discoverable Profile
Agent-native protocols move beyond static platform IDs toward **discoverable profile documents** hosted at well-known URLs. The profile declares the agent's capabilities, supported services, and signing keys. This enables permissionless onboarding — any agent with a published profile can interact without prior bilateral registration.

### 2.2 Capability Negotiation (Distinct from `schemaContext`)
Rather than implicit assumptions about what each side supports, agent protocols use **declared capability sets** with version negotiation. On first contact, both sides compute the intersection and select the highest mutually supported version.

Note: this is **not** the same concern as Beckn's `schemaContext`. See [Section 3.4](#34-capability-negotiation-orthogonal-to-schemacontext) for a detailed comparison.

### 2.3 Human-in-the-Loop as a First-Class State
Agent commerce protocols define explicit escalation states (e.g., `requires_escalation`) with handoff URLs for human review. Messages carry severity levels:
- `recoverable` — agent can auto-fix
- `requiresBuyerInput` — needs human data entry
- `requiresBuyerReview` — needs human authorization (e.g., high-value order)
- `unrecoverable` — session cannot proceed

This is the single most important pattern missing from Beckn for agentic flows.

### 2.4 Autonomous Authorization via Verifiable Credentials
For agents to transact without human-in-the-loop at every step, protocols use **Verifiable Digital Credentials** (SD-JWT+kb, W3C VCs) so an agent can cryptographically prove it has user consent for a specific scope. This creates a non-repudiable audit trail: what was offered, what was consented to, and by whom.

### 2.5 Conversation Threading via IDs, Not Shared State
Agent commerce protocols rely on **opaque IDs** for conversation continuity — not shared memory stores or state URIs. The server (provider) owns all session state; the client (agent) passes back IDs to resume context. Across REST, MCP, and A2A transports, the pattern is consistent: a server-generated session/context ID is the sole threading mechanism. No protocol examined carries shared memory URIs or external state pointers.

### 2.6 Transport Agnosticism
Agent protocols increasingly support multiple transport bindings — REST, MCP (for LLM tool use), A2A (agent-to-agent) — with identical semantics across all transports. Beckn's callback-based async model maps naturally to this, but the context needs to carry enough metadata for any transport.

---

## 3. Proposed Context Extensions for Beckn

Grouped by concern, from highest to lowest priority.

### 3.1 Agent Identity

```yaml
agent:
  type: object
  description: Identity and metadata of the AI agent acting in this interaction.
  properties:
    id:
      type: string
      description: Unique identifier for this agent instance.
    name:
      type: string
      description: Human-readable agent name.
    profileUri:
      type: string
      format: uri
      description: >
        URL to a discoverable agent profile document (capabilities,
        signing keys, supported schemas).
    type:
      type: string
      enum: [human, aiAutonomous, aiAssisted, hybrid]
      description: >
        Nature of the actor driving this request.
        - human: Traditional human-driven interaction
        - aiAutonomous: Fully autonomous agent (no human in the loop)
        - aiAssisted: AI augmenting a human's actions
        - hybrid: Mixed (e.g., agent proposes, human approves)
    onBehalfOf:
      type: string
      format: uri
      description: >
        Fully qualified DeDi Registry URI of the principal this agent
        acts for. Typically the BPP's registry URI when an agent operates
        on behalf of a provider platform, or the BAP's registry URI for
        a buyer-side agent. For individual end-users, this is the user's
        DeDi registry URI (e.g., "https://registry.becknprotocol.io/participants/user-12345").
        Establishes the delegation chain and enables the receiving party
        to verify the agent's authority against the registry.
```

**Rationale:** Beckn currently identifies *platforms* (BAP/BPP) but not *agents*. A BPP needs to know whether it's dealing with a human or an autonomous agent to adjust its response strategy (e.g., requiring explicit consent for high-value transactions). The `onBehalfOf` URI ties the agent back to a verifiable registry entry, preventing impersonation.

**Why no model metadata?** The underlying AI model (provider, model name, version) is an internal implementation detail of the agent, not a protocol concern. A BPP should not change its behavior based on whether it's talking to Claude vs. GPT — it should respond to the agent's *declared capabilities* and *authorization level*. Model details belong in the agent's profile document (at `profileUri`) for transparency, not in every protocol message.

### 3.2 Agent Authorization & Delegation

```yaml
agentMandate:
  type: object
  description: >
    Proof of authority for the agent to act. Enables autonomous
    transactions with cryptographic non-repudiation. Constrains
    what the agent may do across multiple risk dimensions — not
    just transaction value.
  properties:
    allowedActions:
      type: array
      description: >
        Protocol actions this agent is authorized to perform.
        If omitted, the agent is limited to discover only.
      items:
        type: string
        enum:
          - discover
          - select
          - init
          - confirm
          - update
          - cancel
          - status
          - track
          - support
          - rating
    maxTransactionValue:
      type: object
      description: Maximum value for a single transaction.
      required: [amount, currency]
      properties:
        amount:
          type: number
          minimum: 0
        currency:
          type: string
          description: ISO 4217 currency code.
          example: "INR"
    maxCumulativeValue:
      type: object
      description: >
        Maximum aggregate spend across all transactions within this
        mandate's validity window. Prevents an agent from making many
        small transactions that individually pass thresholds but
        collectively exceed the principal's budget.
      required: [amount, currency]
      properties:
        amount:
          type: number
          minimum: 0
        currency:
          type: string
          description: ISO 4217 currency code.
    allowedNetworks:
      type: array
      description: >
        Network IDs the agent is permitted to transact on. Uses the
        same identifiers as the context's networkId field. If omitted,
        no network restriction is applied.
      items:
        type: string
      example: ["beckn.net/mobility", "beckn.net/retail"]
    irreversibleActionPolicy:
      type: string
      enum: [allow, escalate, deny]
      default: escalate
      description: >
        Whether the agent may commit to non-refundable or
        non-cancellable transactions.
        - allow: Agent may commit freely
        - escalate: Triggers human review before commitment
        - deny: Agent must not commit to irreversible actions
    dataSharePolicy:
      type: object
      description: >
        Controls what categories of personal data the agent may
        share with providers during the transaction (e.g., during
        /init when fulfillment details are exchanged).
      properties:
        location:
          type: boolean
          default: true
          description: GPS coordinates, address, geofence data.
        identity:
          type: boolean
          default: false
          description: Government IDs, KYC documents, biometrics.
        health:
          type: boolean
          default: false
          description: Medical records, prescriptions, health conditions.
        financial:
          type: boolean
          default: false
          description: Bank details, income, credit score.
        contact:
          type: boolean
          default: true
          description: Phone number, email address.
    credential:
      type: string
      description: >
        Verifiable credential (SD-JWT+kb, W3C VC, or JWT) proving
        the principal authorized this agent for the declared scope.
        The credential MUST bind to the specific constraints in this
        mandate (allowed actions, value limits, network restrictions,
        data share policy, and expiry).
    expiresAt:
      type: string
      format: date-time
      description: When this mandate expires (RFC 3339).
    delegatable:
      type: boolean
      default: false
      description: Whether this agent can sub-delegate to other agents.
```

**Rationale:** Transaction value alone is insufficient as an authorization boundary. An agent could book 100 hotel rooms at ₹200 each (individually under any value threshold), share health records with an unknown provider, or commit to a non-refundable flight — all without triggering a value-based check. The mandate must constrain across multiple dimensions:

| Risk Dimension | Field | What it prevents |
|---------------|-------|-----------------|
| Single transaction cost | `maxTransactionValue` | Agent overspending on one order |
| Aggregate cost | `maxCumulativeValue` | Many small orders summing to a large exposure |
| Action scope | `allowedActions` | Agent confirming when only authorized to browse/select |
| Network scope | `allowedNetworks` | Agent transacting on unauthorized networks |
| Irreversibility | `irreversibleActionPolicy` | Non-refundable commitments without human review |
| Data exposure | `dataSharePolicy` | Sharing sensitive personal data without consent |
| Time | `expiresAt` | Stale mandates being reused |

### 3.3 Human-in-the-Loop Escalation

```yaml
escalation:
  type: object
  description: >
    Controls for when and how to escalate from agent to human.
    Escalation can be triggered by multiple risk dimensions,
    not just transaction value.
  properties:
    policy:
      type: string
      enum: [never, onTrigger, always]
      description: >
        Overall escalation mode.
        - never: Fully autonomous (triggers are ignored)
        - onTrigger: Escalate when any trigger condition is met
        - always: Every action requires human approval
    triggers:
      type: array
      description: >
        Conditions that trigger escalation when policy is "onTrigger".
        If any trigger fires, escalation is activated. Each trigger
        has a typed condition with a schema-enforced threshold.
      items:
        type: object
        required: [type]
        properties:
          type:
            type: string
            enum:
              - valueExceeded
              - cumulativeValueExceeded
              - irreversibleAction
              - sensitiveDataShare
              - unknownCounterparty
              - networkRestricted
            description: The risk condition to evaluate.
          threshold:
            description: >
              Condition-specific threshold. Schema depends on trigger type.
            oneOf:
              - description: "For valueExceeded / cumulativeValueExceeded"
                type: object
                required: [amount, currency]
                properties:
                  amount:
                    type: number
                    minimum: 0
                  currency:
                    type: string
                    description: ISO 4217 currency code.
              - description: "For sensitiveDataShare"
                type: object
                required: [categories]
                properties:
                  categories:
                    type: array
                    items:
                      type: string
                      enum: [location, identity, health, financial, contact]
              - description: "For unknownCounterparty"
                type: object
                properties:
                  minRatingValue:
                    type: number
                    minimum: 0
                    description: Minimum acceptable rating value for the BPP.
                  minRatingCount:
                    type: integer
                    minimum: 0
                    description: Minimum number of ratings the BPP must have.
              - description: "For networkRestricted"
                type: object
                required: [blockedNetworks]
                properties:
                  blockedNetworks:
                    type: array
                    items:
                      type: string
                    description: Network IDs that should trigger escalation.
              - description: "For irreversibleAction — no threshold needed (binary trigger)"
                type: "null"
    continueUrl:
      type: string
      format: uri
      description: >
        URL where a human can resume/review the transaction
        if escalation is triggered.
    callbackChannel:
      type: string
      enum: [pushNotification, email, sms, inApp, webhook]
      description: How to notify the human when escalation is needed.
```

**Trigger type reference:**

| Trigger Type | Fires When | Threshold Schema |
|-------------|-----------|-----------------|
| `valueExceeded` | Single transaction value exceeds limit | `{amount: number, currency: string}` |
| `cumulativeValueExceeded` | Aggregate spend across mandate window exceeds limit | `{amount: number, currency: string}` |
| `irreversibleAction` | Agent is about to commit to a non-refundable/non-cancellable action | None (binary — always fires for irreversible actions) |
| `sensitiveDataShare` | Transaction requires sharing data in specified categories | `{categories: ["health", "financial", ...]}` |
| `unknownCounterparty` | BPP's rating is below minimum or has insufficient rating history | `{minRatingValue: number, minRatingCount: integer}` |
| `networkRestricted` | Transaction is on a blocked network | `{blockedNetworks: ["networkId", ...]}` |

**Rationale:** This is the safety net. A single value threshold misses entire categories of risk — an agent sharing health records with an unrated provider at ₹0 cost would sail through a value-only check. The typed trigger array lets principals express multi-dimensional escalation rules while keeping every field schema-enforced with no freeform text.

### 3.4 Capability Negotiation (Orthogonal to `schemaContext`)

```yaml
agentCapabilities:
  type: array
  description: >
    Declared capabilities of the requesting agent, enabling the
    responder to tailor its response format and interaction model.
  items:
    type: object
    properties:
      name:
        type: string
        description: >
          Reverse-domain capability identifier
          (e.g., "io.beckn.agent.structuredCheckout",
          "io.beckn.agent.naturalLanguage").
      version:
        type: string
        description: Capability version (semver or date-based).
```

**Rationale:** An AI agent consuming a `/on_select` response has different needs than a mobile app. Capability declaration lets BPPs return richer structured data, tool-use-friendly formats, or conversational responses depending on the consumer.

**`schemaContext` vs `agentCapabilities` — why they are not related:**

| | `schemaContext` | `agentCapabilities` |
|---|---|---|
| **Question it answers** | *"What kind of thing are we transacting on?"* | *"What can this agent do, and how should you talk to it?"* |
| **Layer** | **Data-plane** — describes the domain vocabulary for entities in this transaction | **Control-plane** — describes how the two sides should interact |
| **Example value** | `["https://example.org/schema/EvChargingOffer/v1/context.jsonld"]` — we're dealing with EV charging items | `[{name: "io.beckn.agent.structuredCheckout", version: "1.0"}]` — this agent handles structured checkout flows |
| **Affects** | Schema validation, BPP routing, catalog filtering, `@context` resolution for JSON-LD | Response format, interaction complexity, feature negotiation |
| **Who consumes it** | Schema validators, BPP routers, CDS catalog matchers | The responding platform's adaptation layer |

A human using a mobile app and an AI agent can both transact on the **same** `schemaContext` (e.g., EV charging), but they need very different `agentCapabilities` (one needs rendered UI, the other needs structured JSON with tool-call semantics). Conversely, the same agent capability (e.g., `structuredCheckout`) works across any domain — retail, mobility, logistics — regardless of `schemaContext`.

Modeling domain support as a capability (e.g., `"io.beckn.domain.evCharging": "v1"`) would conflate these two concerns and break Beckn's existing JSON-LD architecture where `schemaContext` drives `@context` resolution.

### 3.5 Conversational Context

```yaml
conversationContext:
  type: object
  description: >
    Multi-turn conversational threading for agent-to-agent dialogues
    that span beyond a single transaction.
  properties:
    conversationId:
      type: string
      description: >
        Persistent conversation thread ID across multiple
        discover/transact cycles. Enables multi-turn agent dialogues
        that span beyond a single transactionId. Generated by the
        initiating agent; passed back on every subsequent message
        in the same dialogue.
    parentMessageId:
      type: string
      description: >
        Links this message to a prior messageId for threading
        within the conversation.
```

**Rationale:** Beckn's `transactionId` scopes a single transaction lifecycle. But agentic interactions are often multi-turn and may span multiple transactions — an agent might discover, ask clarifying questions, refine, then transact. `conversationId` provides a higher-order correlation above `transactionId`.

**Why just two IDs — no shared memory URI?** Industry protocols consistently use **opaque IDs as the sole threading mechanism**. The server (provider) owns all session state; the client (agent) passes back IDs to resume context. No major agent commerce protocol carries shared memory URIs or external state pointers. State reconstruction from IDs is simpler, more secure (no cross-agent state leakage), and transport-agnostic. If an agent needs richer context, it maintains that internally and correlates via `conversationId`.

**How this maps to industry patterns:**

| Protocol Layer | Threading Mechanism | Beckn Equivalent |
|---------------|---------------------|------------------|
| Single request/response | Checkout `id` or resource ID | `messageId` |
| Single transaction lifecycle | Session ID (server-generated) | `transactionId` |
| Multi-turn dialogue spanning transactions | Conversation context ID (e.g., A2A `contextId`) | `conversationContext.conversationId` |
| Task within a conversation | Task ID (reset on completion, context survives) | `transactionId` (resets per transaction, `conversationId` survives) |

The A2A protocol's pattern is instructive: `contextId` persists across multiple tasks (analogous to multiple Beckn transactions), while `taskId` scopes a single task lifecycle (analogous to a single `transactionId`). Beckn's existing `transactionId` already fills the task-scoped role; `conversationId` adds the missing higher-order layer.

**Why no natural language intent field?** Beckn's APIs (`/discover`, `/select`, `/init`, `/confirm`, etc.) already have well-defined structured request bodies — `DiscoverRequest` has `text_search`, `filters`, and `spatial`; transaction endpoints carry the `Order` object. A freeform `intent.text` field would be redundant: the agent's job is to *translate* user intent into these structured payloads before calling the API. Placing raw natural language alongside structured fields creates ambiguity — which takes precedence when they conflict? The structured body *is* the intent, machine-expressed. If an agent cannot construct the structured payload, that's a problem for the agent's own reasoning, not for the protocol wire format.

### 3.6 Observability & Audit

```yaml
trace:
  type: object
  description: >
    Distributed tracing and audit metadata for agent interactions.
  properties:
    traceId:
      type: string
      description: >
        End-to-end trace ID spanning multiple agents and services.
        Complements transactionId (which is Beckn-scoped) with
        a cross-system correlation identifier.
    spanId:
      type: string
      description: Current span within the trace.
    parentSpanId:
      type: string
      description: Parent span for nested agent calls.
    decisionLogUri:
      type: string
      format: uri
      description: >
        Optional URI to an immutable log of agent decisions
        for this transaction (for audit/compliance).
```

**Rationale:** When agents autonomously transact, auditability becomes critical. Distributed tracing is standard in microservices; agent-to-agent commerce needs the same, plus decision audit trails for regulatory compliance.

---

## 4. Interaction Model: How These Fields Work Together

### Scenario: AI Agent Books a Ride

```
1. User tells their AI assistant: "Book me a ride to the airport under ₹500"

2. The agent translates this into a structured /discover request:
   context:
     bapId: "assistant.example.com"
     agent:
       type: aiAssisted
       onBehalfOf: "https://registry.becknprotocol.io/participants/user-12345"
       profileUri: "https://assistant.example.com/.well-known/beckn-agent"
     agentMandate:
       allowedActions: [discover, select, init, confirm]
       maxTransactionValue: { amount: 500, currency: "INR" }
       maxCumulativeValue: { amount: 2000, currency: "INR" }
       allowedNetworks: ["beckn.net/mobility"]
       irreversibleActionPolicy: escalate
       dataSharePolicy:
         location: true
         identity: false
         health: false
         financial: false
         contact: true
       expiresAt: "2026-03-12T23:59:59+05:30"
     escalation:
       policy: onTrigger
       triggers:
         - type: valueExceeded
           threshold: { amount: 500, currency: "INR" }
         - type: unknownCounterparty
           threshold: { minRatingValue: 3.5, minRatingCount: 50 }
         - type: irreversibleAction
       continueUrl: "https://assistant.example.com/review/txn-abc"
       callbackChannel: pushNotification
     conversationContext:
       conversationId: "conv-xyz-789"
   message:
     textSearch: "ride to airport"
     filters:
       type: jsonpath
       expression: "$[?(@.price <= 500)]"

3. BPP responds with rides. Agent evaluates:
   a. Ride A: ₹450, provider rated 4.2 (320 ratings) → all triggers pass → selects
   b. Ride B: ₹380, provider rated 2.8 (12 ratings) → unknownCounterparty fires
      (below minRatingValue 3.5 and minRatingCount 50) → skipped

4. Agent sends /select → /init → /confirm for Ride A.
   All within mandate: value ≤ 500, network is beckn.net/mobility,
   only location + contact shared, action is in allowedActions.

5. Alternative scenario — all rides are ₹550+:
   → valueExceeded trigger fires
   → Agent sends push notification to user
   → User opens continueUrl, reviews options, approves or rejects
   → On approval, a new mandate is issued with higher ceiling

6. Alternative scenario — provider requires identity verification:
   → dataSharePolicy.identity is false
   → Agent cannot share identity data → escalates to human
   → User opens continueUrl, decides whether to share ID
```

---

## 5. Comparison Matrix

| Concern | Beckn v2 Today | Proposed Extension |
|---------|---------------|--------------------|
| Platform identity | `bapId`/`bppId` | Keep BAP/BPP + add `agent.profileUri` |
| Actor type | Implicit (human) | Explicit `agent.type` enum |
| Delegation chain | Not expressed | `agent.onBehalfOf` (DeDi Registry URI) |
| Action scope | Unrestricted | `agentMandate.allowedActions` (enum array) |
| Value limits | None | `agentMandate.maxTransactionValue` + `maxCumulativeValue` |
| Network restrictions | None | `agentMandate.allowedNetworks` (network ID array) |
| Irreversibility control | None | `agentMandate.irreversibleActionPolicy` (enum) |
| Data exposure control | None | `agentMandate.dataSharePolicy` (boolean flags per category) |
| Authorization proof | Out-of-band | `agentMandate.credential` (verifiable credential) |
| Human escalation | Not supported | `escalation` with typed `triggers` array + `continueUrl` |
| Capability negotiation | Not supported (`schemaContext` is data-plane, not control-plane) | `agentCapabilities` array with versioning |
| Multi-turn context | `transactionId` only | `conversationContext.conversationId` |
| Distributed tracing | `messageId` (single hop) | `trace` object with `traceId`/`spanId` |
| Decision audit | None | `trace.decisionLogUri` |

---

## 6. Design Principles

1. **Additive, not breaking.** All new fields are optional. Existing BAP/BPP implementations ignore them. Agentic features activate only when both sides declare support.

2. **Agent ≠ Platform.** An agent operates *within* or *on behalf of* a BAP/BPP. The `agent` object nests inside context alongside (not replacing) `bapId`/`bppId`.

3. **Default to human oversight.** Without an `agentMandate`, the system assumes human-driven interaction. Autonomous operation requires explicit opt-in with cryptographic proof.

4. **Structured payloads are the intent.** The protocol's existing structured request bodies are the canonical expression of intent. Agents translate user goals into structured API calls; the protocol does not carry raw natural language alongside structured fields.

5. **Registry-anchored trust.** The `onBehalfOf` URI must resolve in the DeDi Registry, tying agent authority to a verifiable participant entry rather than self-asserted identity.

6. **Progressive trust.** Browse freely, escalate for commitment. An agent can discover and select without a mandate, but confirm/payment requires authorization proof.

---

## 7. Open Questions

1. **Agent profile format:** Should Beckn define its own agent profile schema, or adopt an existing format for cross-protocol interoperability?

2. **Credential format:** SD-JWT+kb vs. W3C Verifiable Credentials vs. simple JWTs — what's the right balance of security and adoption friction?

3. **Registry integration:** Should agent profiles be registered in the DeDi Registry alongside BAP/BPP entries, or remain self-hosted with registry-verified `onBehalfOf` linkage?

4. **Multi-agent orchestration:** When an agent delegates to sub-agents (e.g., payment agent, logistics agent), should the delegation chain be a flat `onBehalfOf` or a recursive chain with intermediate agent URIs?

5. **Liability:** When an autonomous agent confirms an order, who bears liability — the agent provider, the BAP, or the end user? The protocol should support but not prescribe the answer.
