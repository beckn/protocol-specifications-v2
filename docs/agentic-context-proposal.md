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

## 2. Why Agent Context in the Protocol Layer?

The BAP-side agent generates the entire Beckn request payload — so why carry agent metadata in the context rather than handling it internally?

**The context travels to the counterparty.** The BAP-side agent enforces its own constraints internally (it won't call `/confirm` if its mandate says `browseOnly`). But the context makes those constraints **verifiable by the BPP**. Without it, the BPP blindly trusts that the calling agent had authority.

The context fields serve two consumers:

1. **BPP-side enforcement** — The BPP (or its agent) validates the mandate: "This agent claims it's authorized for `confirm` up to ₹500 on `beckn.net/mobility` — let me verify the credential before processing." This is especially critical for high-value or irreversible actions.

2. **Agent-to-agent adaptation** — When both sides have agents, the BPP-side agent uses these fields to adapt behavior (e.g., return structured vs. conversational responses based on `agentCapabilities`, or refuse to proceed if the mandate doesn't cover the requested action).

---

## 3. Industry Patterns for Agent-Native Commerce

Research across emerging agent commerce protocols surfaces several recurring patterns:

### 3.1 Agent Identity as a Discoverable Profile
Agent-native protocols move beyond static platform IDs toward **discoverable profile documents** hosted at well-known URLs. The profile declares the agent's capabilities, supported services, and signing keys.

### 3.2 Capability Negotiation
Rather than implicit assumptions about what each side supports, agent protocols use **declared capability sets** with version negotiation. On first contact, both sides compute the intersection and select the highest mutually supported version.

### 3.3 Human-in-the-Loop as a First-Class State
Agent commerce protocols define explicit escalation states with handoff URLs for human review. Messages carry severity levels:
- `recoverable` — agent can auto-fix
- `requiresBuyerInput` — needs human data entry
- `requiresBuyerReview` — needs human authorization (e.g., high-value order)
- `unrecoverable` — session cannot proceed

This is the single most important pattern missing from Beckn for agentic flows.

### 3.4 Autonomous Authorization via Verifiable Credentials
For agents to transact without human-in-the-loop at every step, protocols use **Verifiable Digital Credentials** (SD-JWT+kb, W3C VCs) so an agent can cryptographically prove it has user consent for a specific scope. This creates a non-repudiable audit trail.

### 3.5 Conversation Threading via IDs, Not Shared State
Agent commerce protocols rely on **opaque IDs** for conversation continuity — not shared memory stores or state URIs. The server (provider) owns all session state; the client (agent) passes back IDs to resume context.

### 3.6 Transport Agnosticism
Agent protocols increasingly support multiple transport bindings — REST, MCP (for LLM tool use), A2A (agent-to-agent) — with identical semantics across all transports. Beckn's callback-based async model maps naturally to this, but the context needs to carry enough metadata for any transport.

---

## 4. Proposed Context Extensions for Beckn

Grouped by concern, from highest to lowest priority.

### 4.1 Agent Identity

**Rationale:** Beckn currently identifies *platforms* (BAP/BPP) but not *agents*. A BPP needs to know whether it's dealing with a human or an autonomous agent to adjust its response strategy (e.g., requiring explicit consent for high-value transactions). The `onBehalfOf` URI ties the agent back to a verifiable registry entry, preventing impersonation.

```yaml
agent:
  type: object
  description: Identity of the AI agent acting in this interaction.
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
        URL to a discoverable agent profile document
        (capabilities, signing keys, supported schemas).
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
        Web-based distributed identifier (DID) URI of the principal
        this agent acts for — a BAP, BPP, or individual user.
        Any W3C DID method is supported; the first version targets
        DeDi Registry URIs as the primary resolution mechanism.
      example: "did:dedi:registry.becknprotocol.io:participants:user-12345"
```

### 4.2 Agent Authorization & Delegation

**Rationale:** Transaction value alone is insufficient as an authorization boundary. An agent could book 100 hotel rooms at ₹200 each (individually under any value threshold), share health records with an unknown provider, or commit to a non-refundable flight — all without triggering a value-based check. The mandate constrains across multiple risk dimensions:

| Risk Dimension | Field | What it prevents |
|---------------|-------|-----------------|
| Authorization proof | `credential` | Unverified agents acting without consent |
| Sub-delegation | `delegatable` | Unauthorized agent-to-agent delegation chains |
| Action scope | `allowedActions` | Agent confirming when only authorized to browse/select |
| Single transaction cost | `maxTransactionValue` | Agent overspending on one order |
| Aggregate cost | `maxCumulativeValue` | Many small orders summing to a large exposure |
| Network scope | `allowedNetworks` | Agent transacting on unauthorized networks |
| Irreversibility | `irreversibleActionPolicy` | Non-refundable commitments without human review |
| Data exposure | `dataSharePolicy` | Sharing sensitive personal data without consent |
| Time | `expiresAt` | Stale mandates being reused |

```yaml
agentMandate:
  type: object
  description: >
    Proof of authority for the agent to act. Constrains what the
    agent may do across multiple risk dimensions.
  properties:
    credential:
      type: string
      description: >
        Verifiable credential (SD-JWT+kb, W3C VC, or JWT) proving
        the principal authorized this agent for the declared scope.
        The credential MUST bind to the specific constraints in this
        mandate (allowed actions, value limits, network restrictions,
        data share policy, and expiry).
    delegatable:
      type: boolean
      default: false
      description: Whether this agent can sub-delegate to other agents.
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
        mandate's validity window.
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
    expiresAt:
      type: string
      format: date-time
      description: When this mandate expires (RFC 3339).
```

### 4.3 Human-in-the-Loop Escalation

**Rationale:** A single value threshold misses entire categories of risk — an agent sharing health records with an unrated provider at ₹0 cost would sail through a value-only check. The typed trigger array lets principals express multi-dimensional escalation rules while keeping every field schema-enforced with no freeform text.

**Who escalates?** The **BAP-side agent** is the entity that evaluates triggers and initiates escalation. It does so in two situations:

1. **Before sending a request** — The agent evaluates its mandate and escalation triggers against the action it's about to take. For example, before calling `/confirm`, the agent checks whether the transaction value exceeds the `valueExceeded` trigger threshold. If so, it halts and escalates to the human *before* the request reaches the BPP.

2. **After receiving a BPP response** — The agent evaluates the BPP's response against triggers. For example, after `/on_select` returns a quote, the agent discovers the BPP requires identity verification (`dataSharePolicy.identity` is false) or the BPP's rating is below `minRatingValue`. The agent escalates based on what the BPP response reveals.

**Who provides `continueUrl` and `callbackChannel`?** The **BAP** (or the application layer above it) provisions these when creating the agent's mandate. The `continueUrl` points to a BAP-hosted UI where the human can review and resume the transaction. The `callbackChannel` is the notification mechanism the BAP uses to alert the human. These are set at mandate creation time, not by the BPP.

```yaml
escalation:
  type: object
  description: >
    Controls for when and how to escalate from agent to human.
    Evaluated by the BAP-side agent against its mandate and
    BPP responses.
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
        BAP-hosted URL where a human can resume/review the
        transaction if escalation is triggered. Provisioned by
        the BAP at mandate creation time.
    callbackChannel:
      type: string
      enum: [pushNotification, email, sms, inApp, webhook]
      description: >
        How the BAP notifies the human when escalation is needed.
        Provisioned by the BAP at mandate creation time.
```

**Trigger type reference:**

| Trigger Type | Fires When | Threshold Schema |
|-------------|-----------|-----------------|
| `valueExceeded` | Single transaction value exceeds limit | `{amount: number, currency: string}` |
| `cumulativeValueExceeded` | Aggregate spend across mandate window exceeds limit | `{amount: number, currency: string}` |
| `irreversibleAction` | Agent is about to commit to a non-refundable/non-cancellable action | None (binary) |
| `sensitiveDataShare` | Transaction requires sharing data in specified categories | `{categories: ["health", "financial", ...]}` |
| `unknownCounterparty` | BPP's rating is below minimum or has insufficient rating history | `{minRatingValue: number, minRatingCount: integer}` |
| `networkRestricted` | Transaction is on a blocked network | `{blockedNetworks: ["networkId", ...]}` |

### 4.4 Capability Negotiation

**Rationale:** An AI agent consuming a `/on_select` response has different needs than a mobile app. Capability declaration lets BPPs return richer structured data, tool-use-friendly formats, or conversational responses depending on the consumer. This is orthogonal to `schemaContext`, which describes the domain vocabulary (data-plane), not how the two sides should interact (control-plane).

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

### 4.5 Conversational Context

**Rationale:** Beckn's `transactionId` scopes a single transaction lifecycle. But agentic interactions are often multi-turn and may span multiple transactions — an agent might discover, ask clarifying questions, refine, then transact. `conversationId` provides a higher-order correlation above `transactionId`.

Industry protocols consistently use **opaque IDs as the sole threading mechanism**. The server (provider) owns all session state; the client (agent) passes back IDs to resume context. State reconstruction from IDs is simpler, more secure (no cross-agent state leakage), and transport-agnostic.

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
        discover/transact cycles. Generated by the initiating
        agent; passed back on every subsequent message
        in the same dialogue.
    parentMessageId:
      type: string
      description: >
        Links this message to a prior messageId for threading
        within the conversation.
```

**How this maps to industry patterns:**

| Protocol Layer | Threading Mechanism | Beckn Equivalent |
|---------------|---------------------|------------------|
| Single request/response | Resource ID | `messageId` |
| Single transaction lifecycle | Session ID (server-generated) | `transactionId` |
| Multi-turn dialogue spanning transactions | Conversation context ID | `conversationContext.conversationId` |
| Task within a conversation | Task ID (reset on completion, context survives) | `transactionId` (resets per transaction, `conversationId` survives) |

**Why no natural language intent field?** Beckn's APIs already have well-defined structured request bodies — `DiscoverRequest` has `text_search`, `filters`, and `spatial`; transaction endpoints carry the `Order` object. The structured body *is* the intent, machine-expressed. If an agent cannot construct the structured payload, that's a problem for the agent's own reasoning, not for the protocol wire format.

---

## 5. Interaction Model: How These Fields Work Together

### Scenario: AI Agent Books a Ride

```
1. User tells their AI assistant: "Book me a ride to the airport under ₹500"

2. The BAP provisions a mandate and escalation config for the agent.
   The agent translates the user's request into a structured /discover:
   context:
     bapId: "assistant.example.com"
     agent:
       type: aiAssisted
       onBehalfOf: "did:dedi:registry.becknprotocol.io:participants:user-12345"
       profileUri: "https://assistant.example.com/.well-known/beckn-agent"
     agentMandate:
       credential: "eyJhbGciOiJFZERTQSIs..."   # signed by the user's DID
       delegatable: false
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

3. BPP receives the request. BPP-side agent verifies the credential
   in agentMandate, confirms allowedActions includes "discover",
   and returns matching rides.

4. BAP-side agent evaluates BPP response:
   a. Ride A: ₹450, provider rated 4.2 (320 ratings) → all triggers pass → selects
   b. Ride B: ₹380, provider rated 2.8 (12 ratings) → unknownCounterparty fires
      (below minRatingValue 3.5 and minRatingCount 50) → skipped

5. Agent sends /select → /init → /confirm for Ride A.
   BPP verifies credential on each action, checks allowedActions.
   All within mandate: value ≤ 500, network is beckn.net/mobility,
   only location + contact shared.

6. Alternative scenario — all rides are ₹550+:
   → BAP-side agent detects valueExceeded trigger before calling /confirm
   → Sends push notification to user via callbackChannel
   → User opens continueUrl (BAP-hosted review page), approves or rejects
   → On approval, BAP issues a new mandate with higher ceiling

7. Alternative scenario — provider requires identity verification:
   → BPP response to /init indicates identity data is needed
   → BAP-side agent checks dataSharePolicy.identity → false
   → Agent escalates to human via callbackChannel
   → User opens continueUrl, decides whether to share ID
```

---

## 6. Comparison Matrix

| Concern | Beckn v2 Today | Proposed Extension |
|---------|---------------|--------------------|
| Platform identity | `bapId`/`bppId` | Keep BAP/BPP + add `agent.profileUri` |
| Actor type | Implicit (human) | Explicit `agent.type` enum |
| Delegation chain | Not expressed | `agent.onBehalfOf` (DID URI, DeDi Registry in v1) |
| Authorization proof | Out-of-band | `agentMandate.credential` (verifiable credential) |
| Sub-delegation | Not expressed | `agentMandate.delegatable` (boolean) |
| Action scope | Unrestricted | `agentMandate.allowedActions` (enum array) |
| Value limits | None | `agentMandate.maxTransactionValue` + `maxCumulativeValue` |
| Network restrictions | None | `agentMandate.allowedNetworks` (network ID array) |
| Irreversibility control | None | `agentMandate.irreversibleActionPolicy` (enum) |
| Data exposure control | None | `agentMandate.dataSharePolicy` (boolean flags per category) |
| Human escalation | Not supported | `escalation` with typed `triggers` array + `continueUrl` |
| Capability negotiation | Not supported (`schemaContext` is data-plane) | `agentCapabilities` array with versioning |
| Multi-turn context | `transactionId` only | `conversationContext.conversationId` |

---

## 7. Design Principles

1. **Additive, not breaking.** All new fields are optional. Existing BAP/BPP implementations ignore them. Agentic features activate only when both sides declare support.

2. **Agent ≠ Platform.** An agent operates *within* or *on behalf of* a BAP/BPP. The `agent` object nests inside context alongside (not replacing) `bapId`/`bppId`.

3. **Context is for the counterparty.** The BAP-side agent enforces its own constraints internally. The context makes those constraints verifiable by the BPP — the BPP doesn't have to take the agent's word for it.

4. **Default to human oversight.** Without an `agentMandate`, the system assumes human-driven interaction. Autonomous operation requires explicit opt-in with cryptographic proof.

5. **Structured payloads are the intent.** The protocol's existing structured request bodies are the canonical expression of intent. Agents translate user goals into structured API calls.

6. **Progressive trust.** Browse freely, escalate for commitment. An agent can discover and select without a mandate, but confirm/payment requires authorization proof.

---

## 8. Open Questions

1. **Agent profile format:** Should Beckn define its own agent profile schema, or adopt an existing format for cross-protocol interoperability?

2. **Credential format:** SD-JWT+kb vs. W3C Verifiable Credentials vs. simple JWTs — what's the right balance of security and adoption friction?

3. **Registry integration:** Should agent profiles be registered in the DeDi Registry alongside BAP/BPP entries, or remain self-hosted with registry-verified `onBehalfOf` linkage?

4. **Multi-agent orchestration:** When an agent delegates to sub-agents (e.g., payment agent, logistics agent), should the delegation chain be a flat `onBehalfOf` or a recursive chain with intermediate agent URIs?

5. **Liability:** When an autonomous agent confirms an order, who bears liability — the agent provider, the BAP, or the end user? The protocol should support but not prescribe the answer.
