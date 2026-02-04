# **1. Attribution Playbook for NFOs [DRAFT]**

## *Publishing network architecture, IG overlays, schema extensions, and examples **without** forking/copy-pasting—while giving implementers **a single front door***

---

## **1.1 About this Document**

### **1.1.1 Latest published version**

To be added.

### **1.1.2 Latest editor’s draft**

To be added.

> Note: Contributors are expected to request commenter access prior to proposing changes. Before requesting access, contributors are expected to review the Community Guidelines for Contributing.

### **1.1.3 Implementation report**

To be added.

### **1.1.4 Editors**

* Ravi Prakash (Beckn Labs)
* Pramod Varma (Networks for Humanity)

### **1.1.5 Authors**

* Ravi Prakash (Beckn Labs)

### **1.1.6 Feedback**

#### **1.1.6.1 Issues**

No issues have been raised.

#### **1.1.6.2 Discussions**

No discussions are currently open.

#### **1.1.6.3 Pull Requests**

No pull requests are currently open on this topic.

#### **1.1.6.4 GitHub Labels**

The following labels are expected to be used when raising Issues, initiating Discussions, and submitting Pull Requests regarding this document:

* `governance`
* `attribution`
* `core-v2`

### **1.1.7 Errata**

No errata exist as of this version.

---

## **1.2 Acknowledgements**

The author acknowledges the following individuals for their valuable contributions:

1. Pramod Varma
2. Sujith Nair
3. Tanmoy Adhikary

---

## **1.3 Notice**

This document is **within the scope of the Governance Model of the Beckn Protocol** (“Governance Model”).

The Governance Model is the **authoritative source** for Beckn’s governing intent—its **philosophies**, **design principles**, and **policies**. Documents such as this one are **derived instruments** that translate that intent into operational recommendations (analogous to how *regulations* are derived from *policies*).

Accordingly:

* This document **does not redefine** Beckn’s core philosophies, design principles, or policies.
* Where interpretation is required, the **Governance Model prevails**.
* Conflicts, ambiguity, or gaps are to be treated as **input for improving the Governance Model**, rather than as justification for divergence from governing intent.

**1.3.1 Lineage (recommended):**

* **Governing Source:** Governance Model of the Beckn Protocol
* **Derived From:** Applicable policies / principles defined therein
* **This Document:** Attribution Playbook for NFOs — operational recommendations and processes derived from the above

---

# **2. Status and Applicability**

This playbook constitutes a **strong recommendation** for Network Facilitator Organizations (NFOs) publishing network-specific repositories for Beckn-based open networks. While not framed as a strictly mandatory requirement, it is intended to be treated as the **default expected approach** for responsible publication, attribution, and long-term maintainability.

Deviation from the guidance in this playbook is expected to be **exceptional**, **justified**, and **explicitly documented**, including the rationale and the compensating measures used to mitigate drift, attribution risk, and implementer confusion.

---

# **3. Context**

Beckn Protocol v2 is designed as a **three-layer ecosystem** intended to scale across domains, regions, and networks without repeated reinvention:

1. **Core layer (Beckn Protocol v2):** Domain-agnostic actions (“verbs”) and a standard vocabulary for the order lifecycle (Discovery → Ordering → Fulfillment → Post-fulfillment), accompanied by broadly semantically aligned schemas (e.g., via JSON-LD).
2. **Domain layer (Layer-2 specifications):** Domain communities—often in collaboration with Networks for Humanity Foundation (NFH) and contributors—publish **domain-specific bindings**, including schemas, vocabulary, and Implementation Guides (IGs), to adapt the core specification to specific industries (e.g., energy, mobility).
3. **Network layer (Layer-3 specifications):** Individual networks (led by NFOs) introduce **region- and network-specific requirements**, including policy constraints, regulatory identifiers, payment mechanisms, operational rules, and network governance, while aiming to remain compatible with core and domain foundations.

This layering is intentional: the **core** is expected to remain stable, **domains** are expected to evolve as practice matures, and **networks** frequently move the fastest due to launch timelines and compliance imperatives.

In practice, network-level requirements often emerge **before** they can be normalized into the domain layer (and certainly before they can be incorporated into the core). At the same time, implementers building for a specific network generally require **a single authoritative entry point**—a coherent “home” where the network’s rules and examples can be found without repeated navigation across repositories and versions.

Under these conditions, it is a predictable operational outcome that some networks **republish** domain IG material (and sometimes example payloads) inside network repositories and then extend it with network-specific details. This pattern is commonly driven by:

* **Asynchronous evolution** across core, domain, and network layers
* **Go-to-market pressures** (launch commitments, regulatory timelines, ecosystem deadlines)
* **Developer experience (DX) pragmatism** (reducing “repo-hopping” for implementers)
* **Lack of a default pattern** for overlaying network rules on top of pinned upstream specifications

Over time, however, republishing increases ecosystem friction by introducing **drift** between upstream and network material, blurring boundaries between core/domain/network responsibilities, and increasing maintenance burden—especially when upstream continues to evolve.

This playbook provides a structured approach for NFOs to publish **network-specific architecture documentation, IG overlays, schema extensions, and examples** while treating **Core + Domain** as pinned upstream dependencies and providing implementers a single coherent entry point.

---

# **4. The North Star: One Front Door, Many Rooms**

The implementer experience is strongly recommended to follow these expectations:

1. Implementers should be directed to **one URL** (a documentation portal) presenting a clear navigation structure, typically including:

   * Architecture
   * Implementation Guides
   * Schemas & Contexts
   * Examples
   * Conformance & Policies
   * Release notes / compatibility matrix

2. The documentation portal should be composed from:

   * **Pinned upstream sources** (Core + Domain)
   * **Network-authored overlays** (addenda describing deltas)
   * **Machine-readable extensions** (JSON Schemas, JSON-LD contexts)
   * **Generated examples** (reproducible from patches)

The central principle is that **a single “home” does not require a single repository**.

---

# **5. Organization-Level Principles**

## **5.1 Core and Domain Specifications as Dependencies**

**Strong recommendation (expected practice):**

* Upstream references (tags/commits) should be pinned per network release.
* Upstream IG markdown should not be copied and rebranded within network repositories.

**Rationale:**
Copying upstream content creates drift; drift accumulates into long-term maintenance costs and attribution risk.

## **5.2 Network IGs as Overlays (Not Duplicates)**

**Strong recommendation (expected practice):**
Network-authored IG content should primarily articulate:

* What differs within the network context
* What is stricter
* What is added (extensions, regulatory fields)
* What is forbidden or optional within the network

## **5.3 Extensions as Machine-Readable and Semantically Bindable**

**Strong recommendation (expected practice):**

* Network attribute packs should be published as JSON Schema **and** JSON-LD contexts (`@context`, `@type`).
* These packs should be versioned, and their URLs should remain stable.

## **5.4 Examples as Patches and Generated Outputs**

**Strong recommendation (expected practice):**

* Network repositories should store deltas (e.g., JSON Patch / overlays) and generate full payloads via CI.
* Rebranded upstream examples should not be distributed as hand-edited copies.

---

# **6. Recommended GitHub Organization Blueprint**

## **6.1 Repository Taxonomy**

A well-structured GitHub Organization is expected to use approximately **7–10 repositories**, each with a specific responsibility.

### **6.1.1 Front Door and Navigation**

1. **`<network>-docs`**
   **Purpose:** Documentation portal source (e.g., mkdocs/docusaurus), published via GitHub Pages or equivalent.
   **Contains:** Network-authored docs and integration hooks to render pinned upstream content.

2. **`.github`** (org-wide)
   **Purpose:** Community and governance scaffolding (issue templates, PR templates, CODEOWNERS defaults, security policy, contributing).
   **Contains:** Organization-level norms and guardrails.

### **6.1.2 Network Specification Layer**

3. **`<network>-profile`**
   **Purpose:** Network manifest for compatibility and conformance.
   **Contains:** pinned dependencies, conformance rules, supported use cases, release metadata.

4. **`<network>-schemas`**
   **Purpose:** Source of truth for network attribute packs.
   **Contains:** schemas, JSON-LD contexts, mapping tables (network → beckn → schema.org).

5. **`<network>-examples`**
   **Purpose:** Patch-first examples with generated outputs.
   **Contains:** patches, generated outputs, pinned upstream anchors.

### **6.1.3 Tooling and Automation**

6. **`<network>-tooling`**
   **Purpose:** Tooling required to implement the no-copy pattern (patch applicator, validators, doc composition tools).

7. **`<network>-ci`** (optional)
   **Purpose:** Centralized reusable workflows.

### **6.1.4 Policies, Legal, Operations**

8. **`<network>-policy`** (recommended in regulated networks)
   **Purpose:** Network policy, security posture, onboarding rules, and associated artifacts.

9. **`<network>-registry`** (optional)
   **Purpose:** Registry data models and fixtures (not the live registry).

The guiding principle is to avoid consolidating unrelated responsibilities into a single repository that becomes difficult to maintain.

---

# **7. Naming Conventions**

Predictable naming is strongly recommended so implementers can quickly locate information:

* Portal: `<network>-docs`
* Compatibility/conformance manifest: `<network>-profile`
* Extensions: `<network>-schemas`
* Examples: `<network>-examples`
* Automation: `<network>-tooling`
* Policies: `<network>-policy`
* Org defaults: `.github`

Repository descriptions are recommended to begin with a verb (e.g., “Builds…”, “Defines…”, “Publishes…”).

---

# **8. Repository-Level Information Architecture**

## **8.1 `<network>-profile` (Contract Repository)**

This repository is expected to serve as the canonical answer to: **what the network supports**.

### **8.1.1 Recommended structure**

```text
<network>-profile/
  README.md
  LICENSE
  NOTICE.md
  CHANGELOG.md

  profile/
    DEPENDENCIES.yaml
    SUPPORT_MATRIX.md
    CONFORMANCE/
      discovery.md
      ordering.md
      fulfillment.md
      post_fulfillment.md
    POLICY_REFERENCES.md

  releases/
    v1.4.0.md
```

### **8.1.2 Strong recommendation (expected practice)**

Each release should tag the repository and update `DEPENDENCIES.yaml`, `CHANGELOG.md`, and the compatibility matrix.

## **8.2 `<network>-schemas` (Attribute Packs and Contexts)**

### **8.2.1 Recommended structure**

```text
<network>-schemas/
  README.md
  LICENSE
  NOTICE.md
  CHANGELOG.md

  context/
    network/
      payment.upi.v1.context.jsonld
      provider.regulatory.v1.context.jsonld

  jsonschema/
    network/
      payment.upi.v1.schema.json
      provider.regulatory.v1.schema.json

  mapping/
    mapping-matrix.csv
    notes.md
```

### **8.2.2 Strong recommendation (expected practice)**

Contexts should be stable and resolvable; every pack should include `@type` version semantics, JSON Schema, and mapping notes.

## **8.3 `<network>-examples` (Patch-First Examples)**

### **8.3.1 Recommended structure**

```text
<network>-examples/
  README.md
  LICENSE
  NOTICE.md
  CHANGELOG.md

  upstream-refs/
    ev-charging.yaml

  patches/
    ev-charging/
      on_search.patch.json
      on_confirm.patch.json

  generated/
    ev-charging/
      on_search.json
      on_confirm.json

  reports/
    latest-validation.json
```

### **8.3.2 Strong recommendation (expected practice)**

Generated outputs should be reproducible from upstream references, patches, and tooling versions.

## **8.4 `<network>-docs` (Portal Repository)**

### **8.4.1 Recommended structure**

```text
<network>-docs/
  README.md
  LICENSE
  NOTICE.md

  docs/
    index.md
    architecture/
      overview.md
      participants.md
      trust-registry.md
      security.md
    ig/
      ev-charging/
        overlay.md
        conformance.md
        workflows/
        faq.md
    schemas/
      packs.md
    examples/
      ev-charging.md
    releases/
      index.md

  mkdocs.yml
  tools/
    fetch-upstreams/
```

### **8.4.2 Strong recommendation (expected practice)**

Upstream content should be rendered without copying it into network-authored documentation. Two accepted patterns are:

* build-time fetch with pinned refs, or
* submodules/subtrees pinned to commits/tags.

## **8.5 `.github` (Organization Guardrails)**

### **8.5.1 Recommended contents**

```text
.github/
  CONTRIBUTING.md
  SECURITY.md
  CODE_OF_CONDUCT.md
  PULL_REQUEST_TEMPLATE.md
  ISSUE_TEMPLATE/
  workflows/
    reusable-validate.yml
    reusable-release.yml
```

### **8.5.2 Strong recommendation (expected practice)**

PR checklists should explicitly evaluate: absence of copied upstream content, pinned dependency updates, patch-based example generation, and NOTICE/attribution compliance.

---

# **9. Single Home Without Copying**

## **9.1 Option A (Preferred)**

The documentation portal composes upstream content and network overlays. Every upstream-derived page is expected to display the upstream source, pinned reference, and license/notice pointer.

## **9.2 Option B**

The portal provides curated indexes and deep-links to upstream content at pinned references. This approach is lower-effort but less cohesive.

---

# **10. Release Mechanics Across Multiple Repositories**

## **10.1 Profile as Release Coordinator**

`<network>-profile` is strongly recommended to serve as the canonical release coordinator.

A network release (e.g., `v1.4.0`) is expected to align with corresponding tags for:

* `<network>-profile`
* `<network>-schemas` (or a compatible `v1.4.x`)
* `<network>-examples`
* `<network>-docs` (optional but recommended)

## **10.2 Single Source of Compatibility**

`DEPENDENCIES.yaml` in `<network>-profile` is expected to serve as the canonical compatibility declaration.

---

# **11. Attribution Controls**

## **11.1 Repository-Level NOTICE**

Each repository is expected to include a `NOTICE.md` listing:

* upstream repositories used
* exact references
* relevant licenses and notice requirements
* a statement that upstream specifications remain authoritative

## **11.2 File-Level Attribution for Overlays**

Each overlay IG page is expected to declare:

* pinned base reference
* what is authored within the overlay
* copyright attribution boundaries

---

# **12. CI Controls (Recommended Enforcement)**

Minimum CI expectations include:

* **Schemas repository:** JSON Schema validation and JSON-LD context sanity checks
* **Examples repository:** patch application checks and validation against core/domain/network schemas
* **Docs repository:** build integrity against pinned upstream refs and optional link checking

---

# **13. Anti-Patterns**

The following patterns are strongly discouraged:

* A repository that is effectively a fork of an upstream domain repository with only branding changes
* Multiple repositories carrying duplicated copies of IG content
* Hand-edited “generated” examples without a reproducible build pipeline
* Compatibility claims such as “compatible with main” without pinned references

---

# **14. Minimal Starter Kit for Rapid Launch**

For networks under urgent timelines, the minimum recommended set of repositories is:

1. `.github`
2. `<network>-profile`
3. `<network>-schemas`
4. `<network>-examples`
5. `<network>-docs`

This set is typically sufficient to support rapid launch while avoiding the long-term costs of copy-paste drift.

---

# **16. Scaffolding Script Reference**

To promote consistent repository structure and reduce inadvertent divergence across network repositories, NFOs are **strongly recommended** to use the official scaffolding scripts referenced below to generate the GitHub Organization layout locally.

These scripts generate only the **folder structure and placeholder file names**, initialize each folder as an independent Git repository, and (where applicable) add **upstream repositories as submodule references** in the documentation portal repository.

## **16.1 Full-Fledged Organization Scaffold**

[Click here to view the script](../scripts/network-scaffold/forge-the-network.sh)

## **16.2 Minimal Starter Organization Scaffold**

[Click here to view the script](../scripts/network-scaffold/spark-the-network.sh)

## **16.3 Expected Capabilities**

The referenced scripts are expected to support, at minimum:

* creation of the recommended repository folders for the selected scaffold profile (full or minimal),
* `git init` for each repository folder,
* insertion of upstream dependencies as submodules under `<network>-docs/upstream/` (e.g., `core`, `domain`),
* generation of only file/folder names (no authored content).

## **16.4 Org Folder Structure Description**
The recommended GitHub organization structure for an NFO and its details can be found [here](./NFO_ORG_STRUCTURE.md)

---

# **17. Conclusion**

This playbook establishes a strongly recommended operating model for NFOs to publish network-specific documentation, overlays, extensions, and examples **without** forking or duplicating upstream content, while still delivering a coherent “single front door” experience for implementers.

By treating **Core** and **Domain** specifications as pinned upstream dependencies, expressing network requirements through a **profile**, **overlays**, and **machine-readable extension packs**, and generating examples through reproducible pipelines rather than manual copying, networks can:

* reduce long-term drift and maintenance burden,
* preserve clear responsibility boundaries across Core → Domain → Network layers,
* strengthen attribution fidelity and ecosystem trust, and
* accelerate iteration without sacrificing interoperability.

The recommended organization-level structure is intended to remain lightweight in day-to-day use while being robust enough to withstand fast network evolution, regulatory change, and multi-stakeholder implementation realities.

