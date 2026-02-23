# Beckn Protocol v2 — Documentation

This folder contains the reference documentation and RFC series for Beckn Protocol Version 2.

---

## Reference Documents (1–9)

| # | File | Description |
|---|---|---|
| 1 | [1_Introduction.md](./1_Introduction.md) | What Beckn Protocol v2 is, design philosophy, and key differences from v1 |
| 2 | [2_Network_Architecture.md](./2_Network_Architecture.md) | Actor model, Core→Domain→Network layering, and component relationships |
| 3 | [3_Communication_Protocol.md](./3_Communication_Protocol.md) | Async communication model, endpoint modes, ACK/callback lifecycle |
| 4 | [4_Authentication_and_Security.md](./4_Authentication_and_Security.md) | Beckn Signature, Ed25519, signing string construction, key resolution |
| 5 | [5_Discovery_Architecture.md](./5_Discovery_Architecture.md) | CPS and CDS architecture, catalog push/pull flows |
| 6 | [6_Registry_and_Identity.md](./6_Registry_and_Identity.md) | DeDi-compliant registry, participant records, DID, key lifecycle |
| 7 | [7_Schema_Distribution_Model.md](./7_Schema_Distribution_Model.md) | Three-tier schema model: transport envelope / core_schema / domain packs |
| 8 | [8_Versioning_and_Compatibility.md](./8_Versioning_and_Compatibility.md) | SemVer rules, deprecation policy, LTS/EoS designations, migration from v1 |
| 9 | [9_Conformance_and_Testing.md](./9_Conformance_and_Testing.md) | Conformance rules by actor type, mandatory fields, test vector guidance |

---

## RFC Series (10–25)

| # | File | Title | Status |
|---|---|---|---|
| 10 | [10_RFC_Template.md](./10_RFC_Template.md) | RFC Template | — |
| 11 | [11_Keyword_Definitions.md](./11_Keyword_Definitions.md) | Keyword Definitions for Technical Specifications | Draft |
| 12 | [12_Core_API_Envelope.md](./12_Core_API_Envelope.md) | Beckn v2 Core API Envelope | Draft |
| 13 | [13_Signing_Beckn_APIs_in_HTTP.md](./13_Signing_Beckn_APIs_in_HTTP.md) | Signing Beckn APIs in HTTP | Draft |
| 14 | [14_Non_Repudiation_and_Lineage.md](./14_Non_Repudiation_and_Lineage.md) | Non-Repudiation, Counter-Signatures, and Message Lineage | Draft |
| 15 | [15_Communication_Protocol_RFC.md](./15_Communication_Protocol_RFC.md) | Beckn Protocol Communication | Draft |
| 16 | [16_Catalog_Publishing_Service.md](./16_Catalog_Publishing_Service.md) | Catalog Publishing Service (CPS) | Draft |
| 17 | [17_Catalog_Discovery_Service.md](./17_Catalog_Discovery_Service.md) | Catalog Discovery Service (CDS) | Draft |
| 18 | [18_DeDi_Registry_Integration.md](./18_DeDi_Registry_Integration.md) | DeDi-Compliant Network Registry | Draft |
| 19 | [19_Network_Policy_Profiles.md](./19_Network_Policy_Profiles.md) | Network Policy Profiles and Overlays | Draft |
| 20 | [20_Payments_on_Beckn_Networks.md](./20_Payments_on_Beckn_Networks.md) | Payments on Beckn-Enabled Networks | Draft |
| 21 | [21_Error_Codes.md](./21_Error_Codes.md) | Error Codes and Error Handling | Draft |
| 22 | [22_JSONld_Context_and_Schema_Alignment.md](./22_JSONld_Context_and_Schema_Alignment.md) | JSON-LD Context Design and schema.org Alignment | Draft |
| 23 | [23_Schema_Pack_Contract.md](./23_Schema_Pack_Contract.md) | Domain Schema Pack Contract | Draft |
| 24 | [24_Get_Query_Mode.md](./24_Get_Query_Mode.md) | GET Query Mode — Self-Contained URL Protocol | Draft |
| 25 | [25_Conformance_and_Certification.md](./25_Conformance_and_Certification.md) | Conformance Rules and Certification Criteria | Draft |

---

## Governance

All RFCs in this folder follow the lifecycle defined in [GOVERNANCE.md](../GOVERNANCE.md):

```
Proposal → Draft → Candidate → Released → Deprecated → Removed
```

Any normative change MUST include a conformance impact classification (Patch / Minor / Major / Informative) and explicit security/privacy implications as required by the Governance Model.
