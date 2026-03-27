# JSON-LD Context Design and schema.org Alignment

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Minor (informative for transport layer; normative for core_schema and domain schema packs)  
**Security/privacy implications:** JSON-LD context URIs are resolved at runtime. Implementations MUST use controlled document loaders to prevent context injection attacks.  
**Replaces / Relates to:** New in v2. Establishes rules for authoring Beckn JSON-LD contexts.

---

## Abstract

This RFC defines the rules for designing Beckn Protocol v2 JSON-LD contexts and aligning Beckn entity types and properties with schema.org. It specifies naming conventions, context URI governance, mandatory schema.org mappings, and extension patterns for domain-specific vocabularies.

---

## 1. Context

Beckn v2 represents all core entities as JSON-LD graphs. For these graphs to be globally interoperable — usable by external systems without custom adapters — Beckn entity definitions must be anchored to a globally recognized vocabulary. schema.org is the primary target, supplemented by the `beckn:` namespace for protocol-specific semantics.

---

## 2. JSON-LD Basics in Beckn

Every Beckn `Message` payload MUST include a JSON-LD `@context` declaration:

```json
{
  "@context": [
    "https://schema.org/",
    "https://schema.beckn.io/core/v2/context.jsonld",
    "https://schema.beckn.io/retail/v1/context.jsonld"
  ],
  "@type": "SearchAction",
  "object": {
    "@type": "ItemList",
    ...
  }
}
```

The `@context` array is processed in order. Later contexts override earlier ones for the same term.

---

## 3. Beckn Namespace

The Beckn protocol namespace is `beckn:`, with the base URI `https://schema.beckn.io/vocab#`. Terms that have no schema.org equivalent, or that carry Beckn-specific semantics, are defined under this namespace.

```json
{
  "@context": {
    "beckn": "https://schema.beckn.io/vocab#",
    "transactionId": "beckn:transactionId",
    "messageId": "beckn:messageId"
  }
}
```

---

## 4. schema.org Alignment Rules

### 4.1 Mandatory Mapping

Every Beckn core entity MUST be mapped to a schema.org type wherever a reasonable mapping exists:

| Beckn Entity | schema.org Type | Notes |
|---|---|---|
| `Item` | `schema:Product` or `schema:Service` | Use `Product` for physical goods, `Service` for services |
| `Offer` | `schema:Offer` | Direct mapping |
| `Provider` | `schema:Organization` or `schema:LocalBusiness` | |
| `Order` | `schema:Order` | |
| `Fulfillment` | `schema:DeliveryEvent` or `schema:Service` | |
| `Location` | `schema:Place` | |
| `Person` | `schema:Person` | |
| `Price` | `schema:PriceSpecification` | |
| `Category` | `schema:Category` | |
| `Intent` | `schema:SearchAction` | |

### 4.2 Property Mapping

Individual properties MUST be mapped to schema.org properties wherever available:

```json
{
  "@context": {
    "name": "schema:name",
    "description": "schema:description",
    "price": "schema:price",
    "currency": "schema:priceCurrency",
    "url": "schema:url",
    "image": "schema:image"
  }
}
```

### 4.3 Beckn-Specific Terms

When a property has no schema.org equivalent, use the `beckn:` namespace:

```json
{
  "@context": {
    "fulfillmentId": "beckn:fulfillmentId",
    "ttl": "beckn:ttl",
    "bapId": "beckn:bapId"
  }
}
```

---

## 5. Context URI Governance

### 5.1 Core Context

The canonical Beckn core context is published at:

```
https://schema.beckn.io/core/v2/context.jsonld
```

This context is maintained by the Core Working Group (CWG) and versioned with the `core_schema` repository.

### 5.2 Domain Contexts

Domain-specific contexts are published at versioned URIs:

```
https://schema.beckn.io/{domain}/v{N}/context.jsonld
```

Examples:
- `https://schema.beckn.io/retail/v1/context.jsonld`
- `https://schema.beckn.io/mobility/v1/context.jsonld`

### 5.3 Controlled Document Loaders

Implementations MUST NOT resolve JSON-LD context URIs from arbitrary remote sources at runtime without validation. Implementations MUST use a **controlled document loader** that:
- Maintains an allowlist of permitted context URIs.
- Caches resolved context documents.
- Rejects context URIs not on the allowlist.

This prevents context injection attacks where a malicious payload substitutes field definitions via a crafted `@context`.

---

## 6. Extension Patterns

### 6.1 Domain Schema Pack Extension

Domain schema packs extend core entities by adding a domain-specific context layer:

```json
{
  "@context": [
    "https://schema.org/",
    "https://schema.beckn.io/core/v2/context.jsonld",
    "https://schema.beckn.io/mobility/v1/context.jsonld"
  ],
  "@type": ["Item", "TaxiService"],
  "name": "Sedan",
  "vehicleType": "sedan",
  "routeId": "route-123"
}
```

### 6.2 Network-Specific Terms

Networks MAY define network-specific terms using their own namespace:

```json
{
  "@context": {
    "mynetwork": "https://mynetwork.example.org/vocab#",
    "certificationCode": "mynetwork:certificationCode"
  }
}
```

---

## 7. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-022-01 | Every `Message` payload MUST include a `@context` declaration | MUST |
| CON-022-02 | `@context` MUST include the Beckn core context URI | MUST |
| CON-022-03 | Core entities MUST be mapped to schema.org types | MUST |
| CON-022-04 | Properties with schema.org equivalents MUST use schema.org terms | MUST |
| CON-022-05 | Implementations MUST use controlled document loaders | MUST |
| CON-022-06 | Context URIs for core and domain contexts MUST be versioned | MUST |

---

## 8. Security Considerations

- Context injection: without a controlled document loader, a malicious `@context` can redefine field semantics. Controlled document loaders are mandatory.
- Context URI spoofing: context URIs SHOULD use HTTPS and SHOULD be integrity-checked (e.g., with SRI hashes for cached contexts).

---

## 9. References

- [JSON-LD 1.1 Specification](https://www.w3.org/TR/json-ld11/)
- [schema.org](https://schema.org)
- [schema.beckn.io](https://schema.beckn.io)
- [6_Schema_Distribution_Model.md](./6_Schema_Distribution_Model.md)
- [21_Schema_Pack_Contract.md](./21_Schema_Pack_Contract.md)

---

## 10. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
