#!/usr/bin/env python3
"""
batch_schema_updates.py
Performs 5 batch schema updates to beckn-proposed.yaml:
1. Port Abhishek's schemas with Abhishek prefix
2. Add status enums to Contract
3. Add AckNeedConfirm schema
4. Update Catalog.providerId to oneOf [string, Provider]
5. Update all array Item $refs to oneOf [Item, Resource]
"""

import re
import sys
import os

PROPOSED_PATH = os.path.join(os.path.dirname(__file__), '..', 'api', 'v2.0.0', 'beckn-proposed.yaml')

# ─── The Abhishek schemas to port (with $refs rewritten to AbhishekFoo) ───
# Common transport schemas to SKIP (already present in beckn-proposed.yaml effectively)
SKIP_SCHEMAS = {
    'AckResponse', 'ErrorResponse', 'Descriptor', 'Provider', 'Attributes',
    'TimePeriod', 'Item', 'Order', 'Fulfillment', 'Payment', 'Tracking',
    'TrackAction', 'SupportInfo', 'Rating', 'RatingInput', 'Form',
    'GeoJSONGeometry', 'LegacyOffer',
}

# Schemas from Abhishek's file that we will port (names as they appear in his file)
ABHISHEK_SCHEMA_NAMES = [
    'DiscoveryContext',
    'TransactionContext',
    'DiscoverRequest',
    'DiscoverResponse',
    'Catalog',
    'Resource',
    'Offer',
    'Contract',
    'Commitment',
    'Consideration',
    'Performance',
    'Settlement',
    'SpatialConstraint',
    'MediaSearch',
    'MediaInput',
    'MediaSearchOptions',
    'CatalogPublishRequest',
    'CatalogPublishResponse',
    'CatalogProcessingResult',
    'ProcessingNotice',
]

ABHISHEK_SCHEMAS_YAML = '''
    AbhishekDiscoveryContext:
      $id: https://schema.beckn.io/AbhishekDiscoveryContext/v2.0
      allOf:
        - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications/refs/heads/master/api/transaction/build/transaction.yaml#/components/schemas/Context'
        - type: object
          description: Beckn Context extended for Discovery.
          properties:
            schema_context:
              type: array
              items: { type: string, format: uri }
              description: Optional JSON-LD context URLs indicating entity types to search across

    AbhishekTransactionContext:
      $id: https://schema.beckn.io/AbhishekTransactionContext/v2.0
      allOf:
        - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications/refs/heads/master/api/transaction/build/transaction.yaml#/components/schemas/Context'
        - type: object
          description: Beckn Context extended for Transaction flows.
          properties:
            network_id:
              type: array
              items: { type: string }
              description: Optional list of addressed networks (routing/allowlisting)
            schema_context:
              type: array
              items: { type: string, format: uri }
              description: Optional JSON-LD context URLs relevant to entities in this transaction

    AbhishekDiscoverRequest:
      $id: https://schema.beckn.io/AbhishekDiscoverRequest/v2.0
      type: object
      required: [context]
      properties:
        context:
          allOf:
            - $ref: '#/components/schemas/AbhishekDiscoveryContext'
            - type: object
              properties:
                action:
                  type: string
                  enum: [discover]
        message:
          type: object
          description: Discover payload containing search criteria
          properties:
            text_search: { type: string }
            filters:
              type: object
              properties:
                type: { type: string, enum: [jsonpath], default: jsonpath }
                expression: { type: string }
              required: [type, expression]
            spatial:
              type: array
              items: { $ref: '#/components/schemas/AbhishekSpatialConstraint' }
            media_search:
              $ref: '#/components/schemas/AbhishekMediaSearch'
          anyOf:
            - required: [text_search]
            - required: [filters]
            - required: [spatial]
            - required: [filters, spatial]

    AbhishekDiscoverResponse:
      $id: https://schema.beckn.io/AbhishekDiscoverResponse/v2.0
      type: object
      required: [context, message]
      properties:
        context:
          allOf:
            - $ref: '#/components/schemas/AbhishekDiscoveryContext'
            - type: object
              properties:
                action:
                  type: string
                  enum: [on_discover]
        message:
          type: object
          properties:
            catalogs:
              type: array
              items: { $ref: '#/components/schemas/AbhishekCatalog' }

    AbhishekCatalog:
      $id: https://schema.beckn.io/AbhishekCatalog/v2.0
      type: object
      description: |
        Discovery container returned in /on_discover.
        Backward compatible:
        - legacy: `beckn:items[]` and legacy `beckn:offers[]`
        - new: `beckn:resources[]` and new `beckn:offers[]` (generalized)
      required: ["@context", "@type", "beckn:id", "beckn:descriptor", "beckn:bppId", "beckn:bppUri"]
      anyOf:
        - required: ["beckn:resources"]
        - required: ["beckn:items"]
        - required: ["beckn:offers"]
      additionalProperties: false
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Catalog"]
        beckn:id:
          type: string
        beckn:descriptor:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Descriptor'
        beckn:bppId:
          type: string
        beckn:bppUri:
          type: string
          format: uri
        beckn:validity:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/TimePeriod'
        beckn:isActive:
          type: boolean
          default: true
          description: Whether the catalog is active.
        beckn:resources:
          type: array
          items: { $ref: '#/components/schemas/AbhishekResource' }
        beckn:items:
          type: array
          description: Legacy items (backward compatibility)
          items: { $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Item' }
        beckn:offers:
          type: array
          description: Mixed array of legacy Offer and new generalized Offer.
          items:
            oneOf:
              - $ref: '#/components/schemas/AbhishekOffer'
              - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Offer'
        beckn:availableTo:
          type: array
          description: >
            Optional visibility constraint indicating which network participants
            (by participantId / networkId / role) are allowed to discover or
            transact on this entity.

            If omitted, the entity is assumed to be visible to all participants
            in the addressed network(s).
          items:
            type: object
            required: [type, id]
            properties:
              type:
                type: string
                enum: [NETWORK, PARTICIPANT, ROLE]
                description: Scope of visibility constraint.
              id:
                type: string
                description: Identifier of the network, participant, or role.

    AbhishekResource:
      $id: https://schema.beckn.io/AbhishekResource/v2.0
      type: object
      description: >
        A minimal, domain-neutral abstraction representing any discoverable,
        referenceable, or committable unit of value, capability, service,
        entitlement, or asset within the network.

        Examples:
        - A retail product SKU, a mobility ride, a job role, a carbon credit unit,
          a dataset/API entitlement, a training course, a clinic service slot.

        Designed for composability through `beckn:resourceAttributes` where
        domain packs can plug in their specific fields without changing the core.
      required: ["@context", "@type", "beckn:id", "beckn:descriptor"]
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Resource schema
        "@type":
          type: string
          description: Type of the core Resource
          enum: ["beckn:Resource"]
        beckn:id:
          type: string
          description: Globally unique identifier of the resource.
        beckn:descriptor:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Descriptor'
        beckn:provider:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Provider'
        beckn:isAvailable:
          type: boolean
          default: true
          description: |
            Whether the resource is currently available for discovery/commitment.
            This allows temporary suspension without deleting the resource.
        beckn:availableTo:
          type: array
          description: >
            Optional visibility constraint indicating which network participants
            (by participantId / networkId / role) are allowed to discover or
            transact on this entity.

            If omitted, the entity is assumed to be visible to all participants
            in the addressed network(s).
          items:
            type: object
            required: [type, id]
            properties:
              type:
                type: string
                enum: [NETWORK, PARTICIPANT, ROLE]
                description: Scope of visibility constraint.
              id:
                type: string
                description: Identifier of the network, participant, or role.
        beckn:resourceAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'

    AbhishekOffer:
      $id: https://schema.beckn.io/AbhishekOffer/v2.0
      type: object
      description: >
        A generalized, cross-domain Offer that captures the terms under which
        one or more Resources may be committed.

        Core intent:
        - Support multiple terms/eligibility/constraints/price points for the same Resource(s)
        - Support dynamic / on-the-fly offers (e.g., bundling, combinational discounts,
          eligibility changes, capacity-aware pricing)

        This mirrors the role of Offer in current Beckn (and schema.org patterns),
        but keeps the shape minimal and composable via `beckn:offerAttributes`.
      required: ["@context", "@type", "beckn:id", "beckn:proposer", "beckn:status"]
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Offer schema
        "@type":
          type: string
          description: Type of the core Offer
          enum: ["beckn:Offer"]
        beckn:id:
          type: string
          description: Unique identifier of the offer.
        beckn:status:
          type: string
          description: Current lifecycle state of the offer.
          enum: [ACTIVE, EXPIRED, WITHDRAWN]
        beckn:proposer:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Provider'
        beckn:resourceRefs:
          type: array
          description: References (IDs) to resources covered by this offer.
          items: { type: string }
        beckn:addOnRefs:
          type: array
          description: IDs of optional extra Offers or Resources that can be attached.
          items: { type: string }
        beckn:proposedConsideration:
          type: object
          description: Optional proposed exchange value (monetary or otherwise).
          additionalProperties: true
        beckn:validity:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/TimePeriod'
        beckn:availableTo:
          type: array
          description: >
            Optional visibility constraint indicating which network participants
            (by participantId / networkId / role) are allowed to discover or
            transact on this entity.

            If omitted, the entity is assumed to be visible to all participants
            in the addressed network(s).
          items:
            type: object
            required: [type, id]
            properties:
              type:
                type: string
                enum: [NETWORK, PARTICIPANT, ROLE]
                description: Scope of visibility constraint.
              id:
                type: string
                description: Identifier of the network, participant, or role.
        beckn:offerAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'

    AbhishekContract:
      $id: https://schema.beckn.io/AbhishekContract/v2.0
      type: object
      description: >
        A digitally agreed commitment between two or more participants
        governing the exchange of economic or non-economic value.

        Contract is the canonical post-confirmation object in the generalized
        Beckn v2.1 protocol. It replaces the commerce-specific Order construct
        while preserving backward compatibility at the API layer.

        A Contract binds:
          - Commitments (what is agreed)
          - Consideration (value promised)
          - Performance (how execution occurs)
          - Settlements (how consideration is discharged)

        The model is domain-neutral and supports commerce, hiring,
        energy markets, carbon exchanges, data access, mobility,
        subscriptions, and other use cases.
      required:
        - "@context"
        - "@type"
        - beckn:id
        - beckn:status
        - beckn:parties
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the generalized Contract schema.
        "@type":
          type: string
          description: JSON-LD type of the object.
          enum: ["beckn:Contract"]
        beckn:id:
          type: string
          description: >
            Globally unique identifier for this Contract instance.
        beckn:status:
          type: string
          description: >
            Current lifecycle state of the contract reflecting
            overall progression and execution state.
          enum: [DRAFT, PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, FAILED, TERMINATED]
        beckn:parties:
          type: array
          description: >
            Participants bound by this Contract along with their roles.
            A Contract must have at least two parties.
          minItems: 2
          items:
            type: object
            required:
              - beckn:participantId
              - beckn:role
            properties:
              beckn:participantId:
                type: string
                description: Unique identifier of the participant.
              beckn:role:
                type: string
                description: >
                  Role played by this participant within the contract
                  (e.g., BUYER, SELLER, PROVIDER, CONSUMER, EMPLOYER,
                  EMPLOYEE, PRODUCER, GRID_OPERATOR, etc.)
        beckn:commitments:
          type: array
          description: >
            Structured commitments governed by this contract.
          minItems: 1
          items:
            type: object
            required:
              - beckn:ref
              - beckn:refType
            properties:
              beckn:ref:
                type: string
                description: Identifier of the committed entity.
              beckn:refType:
                type: string
                enum: [RESOURCE, OFFER, OTHER]
                description: Type of entity being committed.
              beckn:quantity:
                type: number
                description: Quantity or extent of the commitment, if applicable.
              beckn:commitmentAttributes:
                $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'
        beckn:consideration:
          type: array
          description: >
            Value agreed to be exchanged under this contract.
          items:
            $ref: '#/components/schemas/AbhishekConsideration'
        beckn:performance:
          type: array
          description: >
            Execution units of the contract.
          items:
            $ref: '#/components/schemas/AbhishekPerformance'
        beckn:settlements:
          type: array
          description: >
            Records representing discharge of agreed consideration.
          items:
            $ref: '#/components/schemas/AbhishekSettlement'
        beckn:contractAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'
          description: >
            Domain-specific extension attributes associated with this contract.

    AbhishekCommitment:
      $id: https://schema.beckn.io/AbhishekCommitment/v2.0
      type: object
      description: |
        A single committed entity in the contract.
        Typically references either:
        - a Resource (what is being committed)
        - an Offer (under which terms)
      required: ["@context", "@type", beckn:ref, beckn:refType]
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Resource schema
        "@type":
          type: string
          description: Type of the core Resource
          enum: ["beckn:Commitment"]
        beckn:ref:
          type: string
          description: Identifier of the committed entity.
        beckn:refType:
          type: string
          enum: [RESOURCE, OFFER, OTHER]
        beckn:quantity:
          type: number
          description: Quantity/extent, if applicable.

    AbhishekConsideration:
      $id: https://schema.beckn.io/AbhishekConsideration/v2.0
      type: object
      description: >
        Generalized representation of value exchanged under a Contract.

        Consideration is domain-neutral and may represent:
        - Monetary value
        - Credits / tokens
        - Asset transfer
        - Service exchange
        - Compliance artifact
      required: ["@context", "@type", beckn:type, beckn:status]
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Resource schema
        "@type":
          type: string
          description: Type of the core Resource
          enum: ["beckn:Consideration"]
        beckn:type:
          type: string
          enum: [MONETARY, TOKEN, CREDIT, ASSET, SERVICE, OTHER]
        beckn:status:
          type: string
          enum: [PROPOSED, AGREED, PENDING, SETTLED, FAILED, CANCELLED]
        beckn:amount:
          type: object
          description: Optional amount/value structure
          additionalProperties: true
        beckn:considerationAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'

    AbhishekPerformance:
      $id: https://schema.beckn.io/AbhishekPerformance/v2.0
      type: object
      description: |
        Generalized execution/performance unit. This is where downstream objects bind:
        - Fulfillment-like details (where/when/how)
        - Tracking handles
        - Support touchpoints
        - Status updates

        Domain packs can attach rich fields via `beckn:performanceAttributes`.
      required: ["@context", "@type", beckn:id, beckn:status]
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Resource schema
        "@type":
          type: string
          description: Type of the core Resource
          enum: ["beckn:Performance"]
        beckn:id:
          type: string
        beckn:status:
          type: string
          description: Execution state of this performance unit.
          enum: [PLANNED, IN_PROGRESS, COMPLETED, FAILED, CANCELLED]
        beckn:mode:
          type: string
          enum: [DELIVERY, SERVICE, ACCESS, TRANSFER, EXECUTION, OTHER]
        beckn:commitmentRefs:
          type: array
          description: Commitments fulfilled by this performance.
          items:
            type: string
        beckn:performanceAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'

    AbhishekSettlement:
      $id: https://schema.beckn.io/AbhishekSettlement/v2.0
      type: object
      description: >
        Represents the discharge of agreed consideration under a Contract.

        Settlement may occur via:
          - Monetary payment
          - Token or credit transfer
          - Asset movement
          - Capacity allocation
          - Service exchange
          - Other domain-specific mechanisms.
      required:
        - "@context"
        - "@type"
        - beckn:type
        - beckn:status
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the core Resource schema
        "@type":
          type: string
          description: Type of the core Resource
          enum: ["beckn:Settlement"]
        beckn:type:
          type: string
          enum: [MONETARY, TOKEN, CREDIT, ASSET, SERVICE, OTHER]
        beckn:status:
          type: string
          enum: [INITIATED, PENDING, COMPLETED, FAILED, CANCELLED]
        beckn:amount:
          type: object
          description: >
            Applicable for monetary or token settlements.
          additionalProperties: true
        beckn:considerationRefs:
          type: array
          description: Consideration obligations discharged by this settlement.
          items:
            type: string
        beckn:settlementRef:
          type: string
          description: >
            External transaction reference (e.g., payment gateway ID,
            blockchain tx hash, clearing reference).
        beckn:settlementAttributes:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Attributes'

    AbhishekSpatialConstraint:
      $id: https://schema.beckn.io/AbhishekSpatialConstraint/v2.0
      type: object
      required: [op, targets]
      properties:
        op:
          type: string
          enum: [s_within, s_contains, s_intersects, s_disjoint, s_overlaps, s_crosses, s_touches, s_equals, s_dwithin]
        targets:
          oneOf:
            - type: string
            - type: array
              items: { type: string }
        geometry: { $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/GeoJSONGeometry' }
        distanceMeters: { type: number, minimum: 0 }
        quantifier:
          type: string
          enum: [any, all, none]
          default: any
      additionalProperties: false

    AbhishekMediaSearch:
      $id: https://schema.beckn.io/AbhishekMediaSearch/v2.0
      type: object
      properties:
        media:
          type: array
          items: { $ref: '#/components/schemas/AbhishekMediaInput' }
        options: { $ref: '#/components/schemas/AbhishekMediaSearchOptions' }
      additionalProperties: false

    AbhishekMediaInput:
      $id: https://schema.beckn.io/AbhishekMediaInput/v2.0
      type: object
      required: [type, url]
      properties:
        id: { type: string }
        type: { type: string, enum: [image, audio, video] }
        url: { type: string, format: uri }
        contentType: { type: string }
        textHint: { type: string }
        language: { type: string }
        startMs: { type: integer }
        endMs: { type: integer }
      additionalProperties: false

    AbhishekMediaSearchOptions:
      $id: https://schema.beckn.io/AbhishekMediaSearchOptions/v2.0
      type: object
      properties:
        goals:
          type: array
          items:
            type: string
            enum: [visual-similarity, visual-object-detect, text-from-image, text-from-audio, semantic-audio-match, semantic-video-match]
        augment_text_search: { type: boolean, default: true }
        restrict_results_to_media_proximity: { type: boolean, default: false }
      additionalProperties: false

    AbhishekCatalogPublishRequest:
      $id: https://schema.beckn.io/AbhishekCatalogPublishRequest/v2.0
      type: object
      required: [context, message]
      properties:
        context:
          allOf:
            - $ref: '#/components/schemas/AbhishekDiscoveryContext'
            - type: object
              properties:
                action:
                  type: string
                  enum: [catalog_publish]
        message:
          type: object
          required: [catalogs]
          properties:
            catalogs:
              type: array
              minItems: 1
              items: { $ref: '#/components/schemas/AbhishekCatalog' }

    AbhishekCatalogPublishResponse:
      $id: https://schema.beckn.io/AbhishekCatalogPublishResponse/v2.0
      type: object
      required: [context, message]
      properties:
        context:
          allOf:
            - $ref: '#/components/schemas/AbhishekDiscoveryContext'
            - type: object
              properties:
                action:
                  type: string
                  enum: [on_catalog_publish]
        message:
          type: object
          properties:
            results:
              type: array
              items: { $ref: '#/components/schemas/AbhishekCatalogProcessingResult' }

    AbhishekCatalogProcessingResult:
      $id: https://schema.beckn.io/AbhishekCatalogProcessingResult/v2.0
      type: object
      required: [catalog_id, status]
      properties:
        catalog_id: { type: string }
        status: { type: string, enum: [ACCEPTED, REJECTED, PARTIAL] }
        item_count: { type: integer, minimum: 0 }
        warnings:
          type: array
          items: { $ref: '#/components/schemas/AbhishekProcessingNotice' }
        error:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Error'

    AbhishekProcessingNotice:
      $id: https://schema.beckn.io/AbhishekProcessingNotice/v2.0
      type: object
      required: [code, message]
      properties:
        code: { type: string }
        message: { type: string }
        details:
          type: object
          additionalProperties: true
'''

# ─── AckNeedConfirm schema ───
ACK_NEED_CONFIRM_YAML = '''
    AckNeedConfirm:
      $id: https://schema.beckn.io/AckNeedConfirm/v2.0
      title: Acknowledgement — Needs Confirmation
      description: |
        Used in two-stage negotiation (context.try: true) where the BPP responds to a
        cancel or update request with the consequences/terms of the requested action.
        The BAP must then submit a second request (context.try: false) to commit.

        This response carries a 200 HTTP status but signals that no state change occurred —
        only the consequences/terms are returned for the BAP's consideration.

        The `consequences` object contains domain-specific details about what will happen
        if the BAP proceeds to commit (e.g. refund amount, penalty, updated pricing).
      allOf:
        - $ref: '#/components/schemas/Ack'
        - type: object
          properties:
            consequences:
              type: object
              description: |
                Domain-specific consequences of committing the requested action.
                May include cancellation policy, refund terms, updated quote, penalties, etc.
              additionalProperties: true
'''


def load_file(path):
    with open(path, 'r') as f:
        return f.read()


def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def get_existing_schema_names(content):
    """Extract all top-level schema names from the components/schemas section."""
    # Find the schemas: section
    schema_pattern = re.compile(r'^    ([A-Za-z][A-Za-z0-9_]+)\s*:', re.MULTILINE)
    return set(schema_pattern.findall(content))


def change1_add_abhishek_schemas(content):
    """Add Abhishek-prefixed schemas (skip existing ones)."""
    existing = get_existing_schema_names(content)
    
    # Parse the ABHISHEK_SCHEMAS_YAML to find schema names
    schema_name_pattern = re.compile(r'^    (Abhishek[A-Za-z0-9_]+)\s*:', re.MULTILINE)
    names_in_block = schema_name_pattern.findall(ABHISHEK_SCHEMAS_YAML)
    
    # Filter out already-existing ones
    schemas_to_add = []
    skipped = []
    seen = set()
    
    # We need to split ABHISHEK_SCHEMAS_YAML into individual schema blocks
    # Split on lines that match "    AbhishekXxx:" at the start
    lines = ABHISHEK_SCHEMAS_YAML.split('\n')
    
    current_name = None
    current_lines = []
    schema_blocks = {}  # name -> yaml block
    
    for line in lines:
        m = re.match(r'^    (Abhishek[A-Za-z0-9_]+)\s*:', line)
        if m:
            if current_name:
                schema_blocks[current_name] = '\n'.join(current_lines)
            current_name = m.group(1)
            current_lines = [line]
        elif current_name:
            current_lines.append(line)
    
    if current_name:
        schema_blocks[current_name] = '\n'.join(current_lines)
    
    to_add_yaml = []
    added_names = []
    for name, block in schema_blocks.items():
        if name in existing:
            skipped.append(name)
        else:
            to_add_yaml.append(block)
            added_names.append(name)
    
    if not to_add_yaml:
        print("No new Abhishek schemas to add (all already exist)")
        return content, added_names, skipped
    
    # Insert before the closing of components/schemas (before the responses: section)
    # Find the last schema in the schemas section - insert before "  # ─── Responses"
    insert_marker = '  # ─── Responses ────────────────────────────────────────────────────'
    if insert_marker not in content:
        # Try another marker
        insert_marker = '  responses:'
    
    insertion_block = '\n'.join(to_add_yaml)
    
    content = content.replace(
        insert_marker,
        insertion_block + '\n\n    # ─── End of Abhishek schemas ───\n\n' + insert_marker
    )
    
    print(f"Added {len(added_names)} Abhishek schemas: {added_names}")
    print(f"Skipped {len(skipped)} schemas: {skipped}")
    return content, added_names, skipped


def change2_add_status_enums_to_contract(content):
    """
    In Contract.status, update the string branch oneOf to include additional enums.
    Currently the Contract in beckn-proposed.yaml has:
      status:
        oneOf:
        - type: string
          description: A single code describing the status of the contract.
        - type: object
    We want to add enum: [DRAFT, ACTIVE, CANCELLED, COMPLETE, PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, FAILED, TERMINATED]
    """
    old = '''        status:
          description: The current state of the contract. Depending on the context, it could be just a code
            or a detailed description of state.
          oneOf:
          - type: string
            description: A single code describing the status of the contract.
          - type: object'''
    
    new = '''        status:
          description: The current state of the contract. Depending on the context, it could be just a code
            or a detailed description of state.
          oneOf:
          - type: string
            description: A single code describing the status of the contract.
            enum: [DRAFT, ACTIVE, CANCELLED, COMPLETE, PENDING, CONFIRMED, IN_PROGRESS, COMPLETED, FAILED, TERMINATED]
          - type: object'''
    
    if old in content:
        content = content.replace(old, new)
        print("Change 2: Updated Contract.status string enum")
    else:
        print("Change 2: WARNING — could not find Contract.status oneOf pattern to update")
    
    return content


def change3_add_ack_need_confirm(content):
    """Add AckNeedConfirm schema."""
    existing = get_existing_schema_names(content)
    if 'AckNeedConfirm' in existing:
        print("Change 3: AckNeedConfirm already exists, skipping")
        return content
    
    # Insert after AckNoCallback schema
    # Find "AckNoCallback:" and insert after its block
    insert_after = '    AckNoCallback:'
    
    # Find the position after AckNoCallback block (before the next schema)
    # Look for the next top-level schema after AckNoCallback
    # We'll insert ACK_NEED_CONFIRM_YAML before AsyncError:
    insert_before = '    AsyncError:'
    
    if insert_before in content:
        content = content.replace(
            insert_before,
            ACK_NEED_CONFIRM_YAML.strip() + '\n\n    AsyncError:'
        )
        print("Change 3: Added AckNeedConfirm schema")
    else:
        print("Change 3: WARNING — could not find insertion point for AckNeedConfirm")
    
    return content


def change4_update_catalog_provider_id(content):
    """Update Catalog.providerId to oneOf [string, Provider]."""
    old = '''        providerId:
          description: Reference to the provider that owns this catalog
          type: string
          example: tech-store-001'''
    
    new = '''        providerId:
          description: |
            Identifier or full object of the provider that owns this catalog.
            - String: reference by ID (lightweight, for CDS indexing)
            - Provider object: full provider details (for direct BPP responses)
          oneOf:
            - type: string
              description: Provider ID string reference
              example: tech-store-001
            - $ref: '#/components/schemas/AbhishekResource'
              description: Forward reference to AbhishekProvider (resolves after Abhishek schemas added)'''
    
    # Wait - the task says to use AbhishekProvider if it exists. Since Abhishek's file
    # doesn't have a Provider schema directly (it's a $ref to external), we use 
    # oneOf [string, object with additionalProperties: true] as fallback.
    # But the task says to use AbhishekProvider if it exists. Since we're adding
    # the Abhishek schemas but there's no AbhishekProvider (Provider was in the skip list),
    # let's use the external Provider ref.
    
    new = '''        providerId:
          description: |
            Identifier or full object of the provider that owns this catalog.
            - String: reference by ID (lightweight, for CDS indexing)
            - Provider object: full provider details (for direct BPP responses)
          oneOf:
            - type: string
              description: Provider ID string reference
              example: tech-store-001
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/main/schema/core/v2/attributes.yaml#/components/schemas/Provider'
              description: Full provider object'''
    
    if old in content:
        content = content.replace(old, new)
        print("Change 4: Updated Catalog.providerId to oneOf [string, Provider]")
    else:
        print("Change 4: WARNING — could not find Catalog.providerId pattern to update")
    
    return content


def change5_update_item_refs_in_arrays(content):
    """
    Update all array items: $ref: 'https://schema.beckn.io/Item/v2.0' to oneOf.
    Only change occurrences that are inside `items:` context (array items).
    """
    # The pattern in beckn-proposed.yaml is:
    #   items:
    #     $ref: "https://schema.beckn.io/Item/v2.0"
    # We want to change to:
    #   items:
    #     oneOf:
    #       - $ref: '#/components/schemas/Item'
    #       - $ref: '#/components/schemas/AbhishekResource'
    
    # Pattern: items:\n            $ref: "https://schema.beckn.io/Item/v2.0"
    # Or:      items:\n          $ref: "https://schema.beckn.io/Item/v2.0"
    # Need to handle different indentation levels
    
    old_pattern = re.compile(
        r'([ \t]+items:\n)([ \t]+)\$ref: ["\']https://schema\.beckn\.io/Item/v2\.0["\']',
        re.MULTILINE
    )
    
    count = 0
    def replace_item_ref(m):
        nonlocal count
        count += 1
        indent_items = m.group(1)  # "          items:\n"
        indent_ref = m.group(2)    # "            "
        return (indent_items + 
                indent_ref + 'oneOf:\n' +
                indent_ref + '  - $ref: \'https://schema.beckn.io/Item/v2.0\'\n' +
                indent_ref + '  - $ref: \'#/components/schemas/AbhishekResource\'')
    
    content = old_pattern.sub(replace_item_ref, content)
    
    if count > 0:
        print(f"Change 5: Updated {count} array Item $refs to oneOf [Item, AbhishekResource]")
    else:
        print("Change 5: No array Item $refs found with pattern https://schema.beckn.io/Item/v2.0")
        # Try internal ref pattern
        old_internal = re.compile(
            r'([ \t]+items:\n)([ \t]+)\$ref: ["\']#/components/schemas/Item["\']',
            re.MULTILINE
        )
        count2 = 0
        def replace_item_ref_internal(m):
            nonlocal count2
            count2 += 1
            indent_items = m.group(1)
            indent_ref = m.group(2)
            return (indent_items +
                    indent_ref + 'oneOf:\n' +
                    indent_ref + '  - $ref: \'#/components/schemas/Item\'\n' +
                    indent_ref + '  - $ref: \'#/components/schemas/AbhishekResource\'')
        
        content = old_internal.sub(replace_item_ref_internal, content)
        if count2 > 0:
            print(f"Change 5: Updated {count2} internal array Item $refs to oneOf [Item, AbhishekResource]")
        else:
            print("Change 5: WARNING — no array Item refs found to update")
    
    return content


def main():
    path = os.path.abspath(PROPOSED_PATH)
    print(f"Processing: {path}")
    
    content = load_file(path)
    
    # Change 1: Add Abhishek schemas
    content, added, skipped = change1_add_abhishek_schemas(content)
    
    # Change 2: Update Contract.status enum
    content = change2_add_status_enums_to_contract(content)
    
    # Change 3: Add AckNeedConfirm schema
    content = change3_add_ack_need_confirm(content)
    
    # Change 4: Update Catalog.providerId
    content = change4_update_catalog_provider_id(content)
    
    # Change 5: Update Item array refs
    content = change5_update_item_refs_in_arrays(content)
    
    save_file(path, content)
    print(f"\nDone! File saved: {path}")
    print(f"\nSummary:")
    print(f"  Abhishek schemas added: {len(added)}")
    print(f"  Abhishek schemas skipped: {len(skipped)}")
    return added, skipped


if __name__ == '__main__':
    main()
