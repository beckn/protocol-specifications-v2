#!/usr/bin/env python3
"""
import_schemas.py — Import and rename schemas in beckn-proposed.yaml:

1. Rename Abhishek-prefixed schemas → suffixed (AbhishekFoo → FooAbhishek)
2. Add Ravi schemas suffixed with Ravi  
3. Add Main schemas (from main branch attributes.yaml) suffixed with Main
4. Update all internal $refs to use new names
"""

import re
import sys
from pathlib import Path

PROPOSED = Path(__file__).parent.parent / "api/v2.0.0/beckn-proposed.yaml"

# ─── 1. Abhishek rename map ─────────────────────────────────────────────────
ABHISHEK_RENAME = {
    "AbhishekCatalog": "CatalogAbhishek",
    "AbhishekCatalogProcessingResult": "CatalogProcessingResultAbhishek",
    "AbhishekCatalogPublishRequest": "CatalogPublishRequestAbhishek",
    "AbhishekCatalogPublishResponse": "CatalogPublishResponseAbhishek",
    "AbhishekCommitment": "CommitmentAbhishek",
    "AbhishekConsideration": "ConsiderationAbhishek",
    "AbhishekContract": "ContractAbhishek",
    "AbhishekDiscoverRequest": "DiscoverRequestAbhishek",
    "AbhishekDiscoverResponse": "DiscoverResponseAbhishek",
    "AbhishekDiscoveryContext": "DiscoveryContextAbhishek",
    "AbhishekMediaInput": "MediaInputAbhishek",
    "AbhishekMediaSearch": "MediaSearchAbhishek",
    "AbhishekMediaSearchOptions": "MediaSearchOptionsAbhishek",
    "AbhishekOffer": "OfferAbhishek",
    "AbhishekPerformance": "PerformanceAbhishek",  # already renamed to Performance - handle carefully
    "AbhishekProcessingNotice": "ProcessingNoticeAbhishek",
    "AbhishekResource": "ResourceAbhishek",  # already renamed to Resource - handle carefully
    "AbhishekSettlement": "SettlementAbhishek",
    "AbhishekSpatialConstraint": "SpatialConstraintAbhishek",
    "AbhishekTransactionContext": "TransactionContextAbhishek",  # already removed
}

# ─── 2. Ravi schemas to add ──────────────────────────────────────────────────
RAVI_SCHEMAS_YAML = """
    CancelConfirmMessageRavi:
      description: |
        Cancel confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#CancelConfirmMessage
      type: object
      required:
        - cancelAction
      properties:
        cancelAction:
          type: object
          required: [order, reason]
          properties:
            order:
              allOf:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'
                - required: [id, docs]
            reason:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/CancellationReason'

    CancelInitMessageRavi:
      description: |
        Cancel init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#CancelInitMessage
      type: object
      required:
        - order
      properties:
        cancelAction:
          type: object
          properties:
            order:
              type: object
              additionalProperties: false
              required:
                - beckn:id
              properties:
                beckn:id:
                  $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/beckn:id'
            reason:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/CancellationDetails'

    CatalogProcessingResultRavi:
      description: |
        Processing result for a single catalog from Ravi's version.
        Source: beckn-ravis-original-version.yaml#CatalogProcessingResult
      type: object
      required:
        - catalogId
        - status
      properties:
        catalogId:
          type: string
          description: Identifier of the catalog being processed
        status:
          type: string
          enum: [accepted, rejected, processing]
          description: Processing status of the catalog
        errors:
          type: array
          description: List of errors encountered during processing
          items:
            type: object
            properties:
              code:
                type: string
              message:
                type: string
              path:
                type: string
        stats:
          type: object
          description: Derived statistics about the catalog
          properties:
            itemCount:
              type: integer
            providerCount:
              type: integer
            categoryCount:
              type: integer

    CatalogPublishMessageRavi:
      description: |
        Catalog publish request from Ravi's version.
        Source: beckn-ravis-original-version.yaml#CatalogPublishMessage
      type: object
      required:
        - catalogs
      properties:
        catalogs:
          type: array
          description: Array of catalogs containing items
          items:
            $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Catalog'
          minItems: 1

    ConfirmMessageRavi:
      description: |
        Confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#ConfirmMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    DiscoverMessageRavi:
      description: |
        Discover message (DiscoveryIntent) from Ravi's version.
        Source: beckn-ravis-original-version.yaml#DiscoverMessage
      $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/DiscoveryIntent'

    InitMessageRavi:
      description: |
        Init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#InitMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnCancelConfirmMessageRavi:
      description: |
        On cancel confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnCancelConfirmMessage
      type: object
      required:
        - cancelAction
      properties:
        cancelAction:
          type: object
          properties:
            order:
              allOf:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'
                - required: [cancellationPolicy, cancellationOutcome, docs]
            reason:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/CancellationReason'

    OnCancelInitMessageRavi:
      description: |
        On cancel init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnCancelInitMessage
      type: object
      required:
        - cancelAction
      properties:
        cancelAction:
          type: object
          properties:
            order:
              allOf:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'
                - required: [beckn:id, beckn:cancellationPolicy]
            reason:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/CancellationDetails'

    OnCatalogPublishMessageRavi:
      description: |
        On catalog publish callback from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnCatalogPublishMessage
      type: object
      required:
        - results
      properties:
        results:
          type: array
          description: Per-catalog processing results
          items:
            $ref: '#/components/schemas/CatalogProcessingResultRavi'

    OnConfirmMessageRavi:
      description: |
        On confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnConfirmMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnDiscoverMessageRavi:
      description: |
        On discover message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnDiscoverMessage
      type: object
      required:
        - catalogs
      properties:
        catalogs:
          type: array
          items:
            $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Catalog'

    OnInitMessageRavi:
      description: |
        On init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnInitMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnRateConfirmMessageRavi:
      description: |
        On rate confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnRateConfirmMessage
      type: object
      required:
        - rating
      properties:
        order:
          type: object
          properties:
            beckn:id:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
        ratings:
          type: array
          items:
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Rating'
        feedback:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Feedback'

    OnRateInitMessageRavi:
      description: |
        On rate init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnRateInitMessage
      type: object
      required:
        - order
      properties:
        order:
          type: object
          properties:
            beckn:id:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
        ratings:
          type: array
          items:
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Rating'
        feedback:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Feedback'

    OnSelectMessageRavi:
      description: |
        On select message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnSelectMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnStatusMessageRavi:
      description: |
        On status message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnStatusMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnSupportConfirmMessageRavi:
      description: |
        On support confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnSupportConfirmMessage
      type: object
      required:
        - support
      properties:
        support:
          type: object
          properties:
            order:
              type: object
              properties:
                beckn:id:
                  $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
              required:
                - beckn:id
            methods:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/SupportMethods'
            tickets:
              type: array
              items:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Ticket'

    OnSupportInitMessageRavi:
      description: |
        On support init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnSupportInitMessage
      type: object
      required:
        - support
      properties:
        support:
          type: object
          properties:
            order:
              type: object
              properties:
                beckn:id:
                  $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
              required:
                - beckn:id
            methods:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/SupportMethods'
            tickets:
              type: array
              items:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Ticket'

    OnTrackMessageRavi:
      description: |
        On track message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnTrackMessage
      type: object
      required:
        - tracking
      properties:
        tracking:
          allOf:
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/TrackAction'
            - required: [orderId, refId]

    OnUpdateConfirmMessageRavi:
      description: |
        On update confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnUpdateConfirmMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    OnUpdateInitMessageRavi:
      description: |
        On update init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#OnUpdateInitMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    RateConfirmMessageRavi:
      description: |
        Rate confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#RateConfirmMessage
      type: object
      required:
        - order
        - ratings
      properties:
        order:
          type: object
          properties:
            beckn:id:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
        ratings:
          type: array
          items:
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Rating'
        feedback:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Feedback'

    RateInitMessageRavi:
      description: |
        Rate init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#RateInitMessage
      type: object
      required:
        - order
      properties:
        order:
          type: object
          properties:
            beckn:id:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'

    SelectMessageRavi:
      description: |
        Select message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#SelectMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    StatusMessageRavi:
      description: |
        Status message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#StatusMessage
      type: object
      required:
        - order
      properties:
        order:
          type: object
          properties:
            beckn:id:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/beckn:id'

    SupportConfirmMessageRavi:
      description: |
        Support confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#SupportConfirmMessage
      type: object
      required:
        - support
      properties:
        support:
          type: object
          properties:
            order:
              type: object
              properties:
                beckn:id:
                  $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
              required:
                - beckn:id
            methods:
              $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/SupportMethods'
            tickets:
              type: array
              items:
                - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Ticket'

    SupportInitMessageRavi:
      description: |
        Support init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#SupportInitMessage
      type: object
      required:
        - support
      properties:
        support:
          type: object
          properties:
            order:
              type: object
              properties:
                beckn:id:
                  $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order/properties/id'
              required:
                - beckn:id

    TrackMessageRavi:
      description: |
        Track message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#TrackMessage
      type: object
      required:
        - tracking
      properties:
        tracking:
          allOf:
            - $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/TrackAction'
            - required: [orderId, refId]

    UpdateConfirmMessageRavi:
      description: |
        Update confirm message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#UpdateConfirmMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'

    UpdateInitMessageRavi:
      description: |
        Update init message from Ravi's version.
        Source: beckn-ravis-original-version.yaml#UpdateInitMessage
      type: object
      required:
        - order
      properties:
        order:
          $ref: 'https://raw.githubusercontent.com/beckn/protocol-specifications-v2/refs/heads/draft/schema/core/v2.1/attributes.yaml#/components/schemas/Order'
"""

# ─── 3. Main schemas (inlined from main branch attributes.yaml) ──────────────
MAIN_SCHEMAS_YAML = """
    # ─── Main Branch Schemas (from schema/core/v2/attributes.yaml on main) ───
    # Source: https://github.com/beckn/protocol-specifications-v2/blob/main/schema/core/v2/attributes.yaml

    AcceptedPaymentMethodMain:
      description: |
        Payment methods accepted for an offer.
        Source: main/schema/core/v2/attributes.yaml#AcceptedPaymentMethod
      type: array
      items:
        type: string
        enum: ["UPI", "CREDIT_CARD", "DEBIT_CARD", "WALLET", "BANK_TRANSFER", "CASH", "APPLE_PAY"]
      x-jsonld:
        "@id": beckn:acceptedPaymentMethod

    AckResponseMain:
      description: |
        Acknowledgement response.
        Source: main/schema/core/v2/attributes.yaml#AckResponse
      type: object
      additionalProperties: false
      properties:
        transaction_id:
          type: string
        timestamp:
          type: string
          format: date-time
        ack_status:
          type: string
          enum: [ACK, NACK]
        error:
          $ref: '#/components/schemas/ErrorMain'
      required: [transaction_id, timestamp, ack_status]
      allOf:
        - if:
            properties:
              ack_status:
                const: NACK
            required: [ack_status]
          then:
            required: [error]
        - if:
            properties:
              ack_status:
                const: ACK
            required: [ack_status]
          then:
            not:
              required: [error]

    AddressMain:
      description: |
        Postal address aligned with schema.org PostalAddress.
        Source: main/schema/core/v2/attributes.yaml#Address
      type: object
      properties:
        streetAddress:
          type: string
          description: Street address (building name/number and street).
        extendedAddress:
          type: string
          description: Address extension (apt/suite/floor, C/O).
        addressLocality:
          type: string
          description: City/locality.
        addressRegion:
          type: string
          description: State/region/province.
        postalCode:
          type: string
          description: Postal/ZIP code.
        addressCountry:
          type: string
          description: Country name or ISO-3166-1 alpha-2 code.
      additionalProperties: false

    AttributesMain:
      description: |
        JSON-LD aware bag for domain-specific attributes.
        Source: main/schema/core/v2/attributes.yaml#Attributes
      type: object
      required: ["@context", "@type"]
      minProperties: 2
      additionalProperties: true
      properties:
        "@context":
          type: string
          format: uri
          description: JSON-LD context URI for the specific domain schema
        "@type":
          type: string
          description: JSON-LD type within the domain schema

    BuyerMain:
      description: |
        A minimal entity representing a buyer (Person or Organization).
        Source: main/schema/core/v2/attributes.yaml#Buyer
      type: object
      additionalProperties: false
      required: ["@context", "@type", "beckn:id"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Buyer"]
        beckn:id:
          type: string
          description: Unique identifier for the buyer
        beckn:role:
          type: string
          enum: ["BUYER","SELLER","INTERMEDIARY","PAYER","PAYEE","FULFILLER"]
        beckn:displayName:
          type: string
        beckn:telephone:
          type: string
        beckn:email:
          type: string
          format: email
        beckn:taxID:
          type: string
        beckn:buyerAttributes:
          $ref: '#/components/schemas/AttributesMain'

    CatalogMain:
      description: |
        Core Catalog schema from main branch.
        Source: main/schema/core/v2/attributes.yaml#Catalog
      type: object
      required: ["@context", "@type", "beckn:id", "beckn:descriptor", "beckn:bppId", "beckn:bppUri", "beckn:items"]
      additionalProperties: false
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          example: "beckn:Catalog"
        "beckn:id":
          type: string
          description: Unique identifier for the catalog
        "beckn:descriptor":
          $ref: '#/components/schemas/DescriptorMain'
        "beckn:providerId":
          type: string
          description: Reference to the provider that owns this catalog
        "beckn:bppId":
          type: string
          description: BPP identifier
        "beckn:bppUri":
          type: string
          format: uri
          description: BPP URI endpoint
        "beckn:validity":
          $ref: '#/components/schemas/TimePeriodMain'
        "beckn:isActive":
          type: boolean
          default: true
        beckn:items:
          type: array
          items:
            $ref: '#/components/schemas/ItemMain'
        beckn:offers:
          type: array
          items:
            $ref: '#/components/schemas/OfferMain'

    CategoryCodeMain:
      description: |
        Category code.
        Source: main/schema/core/v2/attributes.yaml#CategoryCode
      type: object
      required: ["@type", "schema:codeValue"]
      properties:
        "@type":
          type: string
          enum: ["schema:CategoryCode"]
        "schema:codeValue":
          type: string
        "schema:name":
          type: string
        "schema:description":
          type: string

    DescriptorMain:
      description: |
        Human-readable descriptor.
        Source: main/schema/core/v2/attributes.yaml#Descriptor
      type: object
      required: ["@type"]
      properties:
        "@type":
          type: string
          enum: ["beckn:Descriptor"]
        "schema:name":
          type: string
        "beckn:shortDesc":
          type: string
        "beckn:longDesc":
          type: string
        "schema:image":
          type: array
          items:
            type: string
            format: uri

    EligibilityMain:
      description: |
        Eligibility constraints.
        Source: main/schema/core/v2/attributes.yaml#Eligibility
      type: object
      properties:
        eligibleRegion:
          type: string
        eligibleQuantity:
          type: object
          properties:
            min:
              type: number
            max:
              type: number

    ErrorMain:
      description: |
        Error response object.
        Source: main/schema/core/v2/attributes.yaml#Error
      type: object
      required: [code, message]
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object

    ErrorResponseMain:
      description: |
        Error response envelope.
        Source: main/schema/core/v2/attributes.yaml#ErrorResponse
      type: object
      required: [error]
      properties:
        error:
          $ref: '#/components/schemas/ErrorMain'

    FormMain:
      description: |
        Describes a form.
        Source: main/schema/core/v2/attributes.yaml#Form
      type: object
      required: ["@context", "@type"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Form"]
        url:
          type: string
          format: uri
          description: URL from where the form can be fetched.
        data:
          type: object
          additionalProperties:
            type: string
        mime_type:
          type: string
          enum:
            - text/html
            - application/xml
        submission_id:
          type: string
          format: uuid

    FulfillmentMain:
      description: |
        Core fulfillment envelope.
        Source: main/schema/core/v2/attributes.yaml#Fulfillment
      type: object
      additionalProperties: false
      required: ["@context", "@type", "beckn:mode"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Fulfillment"]
        beckn:id:
          type: string
        beckn:fulfillmentStatus:
          type: string
        beckn:mode:
          type: string
          enum: ["DELIVERY", "PICKUP", "RESERVATION", "DIGITAL"]
        trackingAction:
          $ref: '#/components/schemas/TrackActionMain'
        beckn:deliveryAttributes:
          $ref: '#/components/schemas/AttributesMain'

    GeoJSONGeometryMain:
      description: |
        GeoJSON geometry per RFC 7946.
        Source: main/schema/core/v2/attributes.yaml#GeoJSONGeometry
      type: object
      required: [type]
      properties:
        type:
          type: string
          enum:
            - Point
            - LineString
            - Polygon
            - MultiPoint
            - MultiLineString
            - MultiPolygon
            - GeometryCollection
        coordinates:
          type: array
        geometries:
          type: array
          items:
            $ref: '#/components/schemas/GeoJSONGeometryMain'
        bbox:
          type: array
          minItems: 4
          maxItems: 4
      additionalProperties: true

    InvoiceMain:
      description: |
        Commercial invoice snapshot.
        Source: main/schema/core/v2/attributes.yaml#Invoice
      type: object
      additionalProperties: false
      required: ["@context", "@type", "beckn:id", "beckn:number", "beckn:issueDate", "beckn:totals", "beckn:payee", "beckn:payer"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Invoice"]
        beckn:id:
          type: string
        beckn:number:
          type: string
        beckn:issueDate:
          type: string
          format: date
        beckn:dueDate:
          type: string
          format: date
          nullable: true
        beckn:payee:
          type: string
          description: Provider ID reference
        beckn:payer:
          type: string
          description: Buyer ID reference
        beckn:totals:
          $ref: '#/components/schemas/PriceSpecificationMain'
        beckn:invoiceAttributes:
          $ref: '#/components/schemas/AttributesMain'

    ItemMain:
      description: |
        Core Item schema from main branch.
        Source: main/schema/core/v2/attributes.yaml#Item
      type: object
      additionalProperties: false
      required: ["@context", "@type", "beckn:id", "beckn:descriptor", "beckn:provider", "beckn:itemAttributes"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Item"]
        "beckn:id":
          type: string
        "beckn:descriptor":
          $ref: '#/components/schemas/DescriptorMain'
        "beckn:category":
          $ref: '#/components/schemas/CategoryCodeMain'
        "beckn:availableAt":
          type: array
          items:
            $ref: '#/components/schemas/LocationMain'
        "beckn:availabilityWindow":
          type: array
          items:
            $ref: '#/components/schemas/TimePeriodMain'
        "beckn:rateable":
          type: boolean
        "beckn:rating":
          $ref: '#/components/schemas/RatingMain'
        "beckn:isActive":
          type: boolean
          default: true
        "beckn:networkId":
          type: array
          items:
            type: string
        "beckn:provider":
          $ref: '#/components/schemas/ProviderMain'
        "beckn:itemAttributes":
          $ref: '#/components/schemas/AttributesMain'

    LocationMain:
      description: |
        A place represented by GeoJSON geometry and optional address.
        Source: main/schema/core/v2/attributes.yaml#Location
      type: object
      required: [geo]
      additionalProperties: false
      properties:
        "@type":
          type: string
          enum: ["beckn:Location"]
        geo:
          $ref: '#/components/schemas/GeoJSONGeometryMain'
        address:
          oneOf:
            - type: string
            - $ref: '#/components/schemas/AddressMain'

    OfferMain:
      description: |
        Core Offer schema from main branch.
        Source: main/schema/core/v2/attributes.yaml#Offer
      type: object
      additionalProperties: false
      required:
        - "@context"
        - "@type"
        - beckn:id
        - beckn:descriptor
        - beckn:provider
        - beckn:items
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Offer"]
        beckn:id:
          type: string
        beckn:descriptor:
          $ref: '#/components/schemas/DescriptorMain'
        beckn:provider:
          type: string
          description: Provider ID reference
        beckn:items:
          type: array
          minItems: 1
          items:
            type: string
            description: Item ID reference
        beckn:addOns:
          type: array
          items:
            type: string
            description: Add-on offer ID reference
        beckn:addOnItems:
          type: array
          items:
            type: string
            description: Add-on item ID reference
        beckn:isActive:
          type: boolean
          default: true
        beckn:validity:
          $ref: '#/components/schemas/TimePeriodMain'
        beckn:price:
          $ref: '#/components/schemas/PriceSpecificationMain'
        beckn:eligibleRegion:
          type: array
          items:
            $ref: '#/components/schemas/LocationMain'
        beckn:acceptedPaymentMethod:
          $ref: '#/components/schemas/AcceptedPaymentMethodMain'
        beckn:offerAttributes:
          $ref: '#/components/schemas/AttributesMain'

    OrderMain:
      description: |
        Core Order schema from main branch.
        Source: main/schema/core/v2/attributes.yaml#Order
      type: object
      additionalProperties: false
      required:
        - "@context"
        - "@type"
        - beckn:orderStatus
        - beckn:seller
        - beckn:buyer
        - beckn:orderItems
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Order"]
        beckn:id:
          type: string
        beckn:orderStatus:
          type: string
          enum: ["CREATED","PENDING","CONFIRMED","INPROGRESS","PARTIALLYFULFILLED","COMPLETED","CANCELLED","REJECTED","FAILED","RETURNED","REFUNDED","ONHOLD"]
        beckn:orderNumber:
          type: string
        beckn:seller:
          type: string
          description: Provider ID reference
        beckn:buyer:
          $ref: '#/components/schemas/BuyerMain'
        beckn:orderItems:
          type: array
          minItems: 1
          items:
            $ref: '#/components/schemas/OrderItemMain'
        beckn:acceptedOffers:
          type: array
          items:
            $ref: '#/components/schemas/OfferMain'
        beckn:orderValue:
          $ref: '#/components/schemas/PriceSpecificationMain'
        beckn:invoice:
          type: string
          description: Invoice ID reference
        beckn:payment:
          $ref: '#/components/schemas/PaymentMain'
        beckn:fulfillment:
          $ref: '#/components/schemas/FulfillmentMain'
        beckn:orderAttributes:
          $ref: '#/components/schemas/AttributesMain'

    OrderItemMain:
      description: |
        A line item within an Order.
        Source: main/schema/core/v2/attributes.yaml#OrderItem
      type: object
      required: ["beckn:orderedItem"]
      properties:
        beckn:lineId:
          type: string
        beckn:orderedItem:
          type: string
          description: Item ID reference
        beckn:acceptedOffer:
          $ref: '#/components/schemas/OfferMain'
        beckn:quantity:
          $ref: '#/components/schemas/QuantityMain'
        beckn:price:
          $ref: '#/components/schemas/PriceSpecificationMain'
        beckn:orderItemAttributes:
          $ref: '#/components/schemas/AttributesMain'

    PaymentMain:
      description: |
        Core payment object.
        Source: main/schema/core/v2/attributes.yaml#Payment
      type: object
      additionalProperties: false
      required: ["@context", "@type", "beckn:paymentStatus"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Payment"]
        beckn:id:
          type: string
        beckn:paymentStatus:
          type: string
          enum: ["INITIATED","PENDING","AUTHORIZED","CAPTURED","COMPLETED","FAILED","CANCELLED","REFUNDED","PARTIALLY_REFUNDED","CHARGEBACK","DISPUTED","EXPIRED","REVERSED","VOIDED","SETTLED","ON_HOLD","ADJUSTED"]
        beckn:amount:
          type: object
          properties:
            currency:
              type: string
            value:
              type: number
        beckn:paymentURL:
          type: string
          format: uri
        beckn:txnRef:
          type: string
        beckn:paidAt:
          type: string
          format: date-time
          nullable: true
        beckn:acceptedPaymentMethod:
          $ref: '#/components/schemas/AcceptedPaymentMethodMain'
        beckn:beneficiary:
          type: string
          enum: ["BPP", "BAP", "BUYER"]
        beckn:paymentAttributes:
          $ref: '#/components/schemas/AttributesMain'

    PriceSpecificationMain:
      description: |
        Price specification.
        Source: main/schema/core/v2/attributes.yaml#PriceSpecification
      type: object
      additionalProperties: true
      properties:
        currency:
          type: string
        value:
          type: number
        applicableQuantity:
          $ref: '#/components/schemas/QuantityMain'
        components:
          type: array
          items:
            type: object
            properties:
              type:
                type: string
                enum: ["UNIT","TAX","DELIVERY","DISCOUNT","FEE","SURCHARGE"]
              value:
                type: number
              currency:
                type: string
              description:
                type: string

    ProviderMain:
      description: |
        Core Provider schema from main branch.
        Source: main/schema/core/v2/attributes.yaml#Provider
      type: object
      required: ["beckn:id", "beckn:descriptor"]
      additionalProperties: false
      properties:
        "beckn:id":
          type: string
        "beckn:descriptor":
          $ref: '#/components/schemas/DescriptorMain'
        "beckn:validity":
          $ref: '#/components/schemas/TimePeriodMain'
        "beckn:locations":
          type: array
          items:
            $ref: '#/components/schemas/LocationMain'
        "beckn:rateable":
          type: boolean
        "beckn:rating":
          $ref: '#/components/schemas/RatingMain'
        "beckn:providerAttributes":
          $ref: '#/components/schemas/AttributesMain'

    QuantityMain:
      description: |
        Quantity specification.
        Source: main/schema/core/v2/attributes.yaml#Quantity
      type: object
      additionalProperties: false
      properties:
        unitText:
          type: string
        unitCode:
          type: string
        unitQuantity:
          type: number
        minQuantity:
          type: number
        maxQuantity:
          type: number

    RatingInputMain:
      description: |
        Rating input form.
        Source: main/schema/core/v2/attributes.yaml#RatingInput
      type: object
      additionalProperties: false
      required: ["@context", "@type", "id", "ratingValue"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:RatingInput"]
        id:
          type: string
        ratingValue:
          type: number
          minimum: 0
        bestRating:
          type: number
        worstRating:
          type: number
        category:
          type: string
          enum: [ORDER, FULFILLMENT, ITEM, PROVIDER, AGENT, OTHER]
        feedback:
          type: object
          additionalProperties: false
          properties:
            comments:
              type: string
            tags:
              type: array
              items:
                type: string

    RatingMain:
      description: |
        Rating.
        Source: main/schema/core/v2/attributes.yaml#Rating
      type: object
      required: ["@type"]
      properties:
        "@type":
          type: string
          enum: ["beckn:Rating"]
        "beckn:ratingValue":
          type: number
          minimum: 0
          maximum: 5
        "beckn:ratingCount":
          type: integer
          minimum: 0

    SupportInfoMain:
      description: |
        Canonical support contact for an entity.
        Source: main/schema/core/v2/attributes.yaml#SupportInfo
      type: object
      additionalProperties: false
      required: ["@context", "@type"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:SupportInfo"]
        name:
          type: string
        phone:
          type: string
        email:
          type: string
          format: email
        url:
          type: string
          format: uri
        hours:
          type: string
        channels:
          type: array
          items:
            type: string
            enum: ["PHONE","EMAIL","WEB","CHAT","WHATSAPP","IN_APP","OTHER"]

    TimePeriodMain:
      description: |
        Time window with date-time precision.
        Source: main/schema/core/v2/attributes.yaml#TimePeriod
      type: object
      required: ["@type"]
      properties:
        "@type":
          type: string
        "schema:startDate":
          type: string
          format: date-time
        "schema:endDate":
          type: string
          format: date-time
        "schema:startTime":
          type: string
          format: time
        "schema:endTime":
          type: string
          format: time
      anyOf:
        - required: ["schema:startDate"]
        - required: ["schema:endDate"]
        - required: ["schema:startTime", "schema:endTime"]

    TrackActionMain:
      description: |
        Minimal schema.org TrackAction for clickable tracking.
        Source: main/schema/core/v2/attributes.yaml#TrackAction
      type: object
      additionalProperties: true
      properties:
        id:
          type: string
        url:
          type: string
          format: uri

    TrackingMain:
      description: |
        Non-streaming tracking handle.
        Source: main/schema/core/v2/attributes.yaml#Tracking
      type: object
      additionalProperties: false
      required: ["@context", "@type", "tl_method", "url", "trackingStatus"]
      properties:
        "@context":
          type: string
          format: uri
        "@type":
          type: string
          enum: ["beckn:Tracking"]
        tl_method:
          type: string
          enum: [http/get, http/post, http/redirect, ws/handle, custom]
        url:
          type: string
          format: uri
        trackingStatus:
          type: string
          enum: [ACTIVE, DISABLED, COMPLETED]
        expires_at:
          type: string
          format: date-time
"""


def main():
    text = PROPOSED.read_text()

    # ── Step 1: Rename Abhishek-prefix schemas in the file ──────────────────
    # Sort by length (longest first) to avoid partial replacement
    for old, new in sorted(ABHISHEK_RENAME.items(), key=lambda x: -len(x[0])):
        # Replace schema key definitions: "    AbhishekFoo:"
        text = re.sub(r'(?m)^(    )' + re.escape(old) + r'(:)', r'\1' + new + r'\2', text)
        # Replace $ref: '#/components/schemas/AbhishekFoo'
        text = text.replace(
            f"'#/components/schemas/{old}'",
            f"'#/components/schemas/{new}'"
        )
        text = text.replace(
            f'"#/components/schemas/{old}"',
            f'"#/components/schemas/{new}"'
        )
        # Replace $ref: '#/components/schemas/AbhishekFoo/...'
        text = re.sub(
            r"'#/components/schemas/" + re.escape(old) + r"(/[^']*)'",
            f"'#/components/schemas/{new}" + r"\1'",
            text
        )

    # ── Step 2: Insert Ravi schemas before the responses: section ────────────
    # Find "  # ─── Responses" or "  responses:" to insert before
    responses_marker = '\n  # ─── Responses'
    if responses_marker not in text:
        responses_marker = '\n  responses:'
    
    insert_pos = text.find(responses_marker)
    if insert_pos == -1:
        print("ERROR: Could not find responses: section", file=sys.stderr)
        sys.exit(1)

    text = text[:insert_pos] + '\n' + RAVI_SCHEMAS_YAML + text[insert_pos:]

    # ── Step 3: Insert Main schemas (after Ravi, before responses) ───────────
    insert_pos = text.find(responses_marker)
    text = text[:insert_pos] + '\n' + MAIN_SCHEMAS_YAML + text[insert_pos:]

    PROPOSED.write_text(text)
    print(f"Done. Updated: {PROPOSED}")
    print(f"  Renamed {len(ABHISHEK_RENAME)} Abhishek-prefixed schemas → suffixed")
    print(f"  Added {len(RAVI_SCHEMAS_YAML.split('Ravi:'))-1} Ravi schemas")
    print(f"  Added {len(MAIN_SCHEMAS_YAML.split('Main:'))-1} Main schemas")


if __name__ == "__main__":
    main()
