# 📚 Contributing Domain-specific Schemas

> This document is maintained in `docs/governance/CONTRIBUTING_SCHEMAS.md`. For contributing to the core protocol schemas in `beckn/schemas`, follow the guidelines below.

---

## 🚀 Adding a New Schema Bundle

### 📁 Folder Structure

```bash
schema/
└── YourUseCase/
    └── v1/
        ├── 📄 attributes.yaml      # OpenAPI attribute schemas
        ├── 🗺️ context.jsonld       # JSON-LD context mapping
        ├── 📋 profile.json         # Schema profile & operational hints
        ├── 🎨 renderer.json        # UI rendering templates
        ├── 📚 vocab.jsonld         # Use-case vocabulary
        ├── 📖 README.md            # Documentation
        ├── 📁 examples/
        │   └── 📁 schema/
        │       ├── 📄 item-example.json
        │       ├── 📄 offer-example.json
        │       └── 📄 provider-attributes-example.json
        ├── 📁 migrations/          # Scripts to migrate from existing schema to new schema
        ├── 📁 validations/         # Scripts to validate the schema with actual data
        └── 📁 tests/               # Scripts to test the schema changes
```

### 📋 File Descriptions

| 📄 **File / Folder** | 🎯 **Purpose** |
| --- | --- |
| 🗺️ **context.jsonld** | Maps all properties to schema.org and local beckn: IRIs. Defines semantic equivalences (e.g., serviceLocation ≡ beckn:availableAt). |
| | |
| 🔧 **attributes.yaml** | OpenAPI 3.1.1 attribute schemas for use-case specific entities, each annotated with x-jsonld. Reuses schema.org entities where possible. |
| | |
| 📋 **profile.json** | Lists included schemas, operational/index hints, minimal attributes for discovery, and privacy guidance for implementers. |
| | |
| 🎨 **renderer.json** | Defines rendering templates (HTML + JSON data paths) for discovery cards, offer chips, and status views used in UI implementations. |
| | |
| 📚 **vocab.jsonld** | Local vocabulary for use-case specific terms in JSON-LD format with RDFS definitions and semantic relationships. |
| | |
| 📁 **examples/** | Contains working examples showing each attribute type in the context of Beckn discover and transaction flows. |
| | |
| 📁 **migrations/** | Scripts to migrate from existing schema to new schema versions, including data transformation utilities. |
| | |
| 📁 **validations/** | Scripts to validate the schema with actual data, including compliance checks and data integrity tests. |
| | |
| 📁 **tests/** | Scripts to test schema changes, including unit tests, integration tests, and regression tests. |

### 🗺️ Local Namespace Mapping

The beckn namespace is mapped **locally**:

```json
{ "beckn": "./vocab.jsonld#" }
```

> 💡 **Vocabulary files** live in `v1/vocab.jsonld` and use this same local mapping.

When publishing, replace `./vocab.jsonld#` with an absolute URL, e.g.:

```
https://schemas.example.org/your-use-case/v1/vocab.jsonld#
```

> ✅ **This supports both local development and public hosting.**

### 📝 Conventions

| Convention | Description |
| --- | --- |
| **Naming** | Use `YourUseCase` format for bundle names |
| **Versioning** | Version folders use semantic versioning (v1, v2, etc.) |
| **Schema Reuse** | Reuse or repurpose schema.org entities and definitions where possible |
| **Custom Properties** | Define individual properties only when not available in schema.org |
| **Namespace** | Use `beckn:` namespace for use-case specific terms |
| **Examples** | Include working examples for all attribute types |

---

## ❓ When to Add a New Schema Bundle

Create a new schema bundle when:

| # | Criteria | Description |
|---|----------|-------------|
| 1️⃣ | **New Use Case** | Introducing a completely new business use case (e.g., healthcare, education, logistics) |
| 2️⃣ | **Independent Attributes** | Use case has unique attributes that don't overlap with existing bundles |
| 3️⃣ | **Different Business Processes** | Serving distinct user scenarios or workflows |
| 4️⃣ | **Regulatory Separation** | Different compliance or regulatory requirements |
| 5️⃣ | **Technology Stack** | Different underlying technologies or standards |

---

## 🔗 Schema Extension Guidelines

### 🎯 When to Extend

Extend an existing schema bundle when:

| # | Scenario | Description |
|---|----------|-------------|
| 1️⃣ | **Regional Variations** | Same use case but different regional requirements (e.g., `EvChargingService_EU`) |
| 2️⃣ | **Regulatory Compliance** | Additional fields for specific jurisdictions |
| 3️⃣ | **Feature Additions** | Adding optional features to existing use case |
| 4️⃣ | **Backward Compatibility** | Maintaining existing implementations while adding new capabilities |

### 🏗️ Extension Pattern

```bash
schema/
├── EvChargingService/
│   └── v1/                    # 📦 Base schema
└── EvChargingService_EU/      # 🔗 Extension
    └── v1/
        ├── 📄 attributes.yaml    # Extends base attributes
        ├── 🗺️ context.jsonld     # Additional mappings
        └── 📖 README.md          # Extension documentation
```

### ✅ Extension Requirements

| Requirement | Description |
|-------------|-------------|
| **Inheritance** | Inherit from base schema via `allOf` or `$ref` |
| **Additive Only** | Add only new fields, don't modify existing ones |
| **Compatibility** | Maintain backward compatibility |
| **Documentation** | Document differences clearly |
| **Examples** | Include examples showing extended functionality |
