# Payment Settlement Definition Bundle (v1)
---
<p align="center">
  <img
    alt="Migration Notice"
    src="https://capsule-render.vercel.app/api?type=soft&color=0:b42318,100:7a271a&height=100&section=header&text=MIGRATION%20NOTICE&fontSize=54&fontColor=ffffff&animation=fadeIn"
  />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Effective-2026--02--06-fde2e0?style=for-the-badge&labelColor=b42318" alt="Effective: 2026-02-06" />
  <img src="https://img.shields.io/badge/Removal-2026--02--20-dbeafe?style=for-the-badge&labelColor=075985" alt="Removal: 2026-02-20" />
</p>

## This schema is being moved. **Migrate now.**


**What’s changing:** This schema is being merged with the **Core Schema**.  
**Impact:** Run-time references to files in this folder may continue to work until the removal date, after which they will fail.

### Recommended action
1. Change your schema context to **[Core](../../core/v2.1/)**.
2. Update your integrations before **2026-02-20**.
3. If blocked, open an issue with logs and request context.

<p>
  <!-- Replace MIGRATION_GUIDE_LINK with the real URL (your HTML had REPLACEMENT_LINK placeholder) -->
  <a href="https://github.com/beckn/protocol-specifications-v2/issues/new">
    <img src="https://img.shields.io/badge/Report%20an%20issue-b42318?style=for-the-badge" alt="Report an issue" />
  </a>
  <a href="https://github.com/beckn/protocol-specifications-v2/discussions/categories/announcements">
    <img src="https://img.shields.io/badge/Announcements-111827?style=for-the-badge" alt="Announcements" />
  </a>
</p>

<table width="100%" cellpadding="12" cellspacing="0" border="0" bgcolor="#ffe4e6">
  <tr>
    <td>
      <strong>Heads-up:</strong> If you maintain downstream specs or SDKs, pin versions and communicate timelines clearly.
    </td>
  </tr>
</table>

<p align="center">
  <img
    alt="Migration Notice End"
    src="https://capsule-render.vercel.app/api?type=soft&color=0:b42318,100:7a271a&height=25&section=header&text=End%20of%20notice&fontSize=15&fontColor=ffffff&animation=fadeIn"
  />
</p>

---

# Overview

This bundle defines **payment settlement attribute extensions** for Provider and Payment objects. It provides settlement account details required for inter-party fund transfers in Beckn payment transactions.

## **💡 Rationale**

In a Beckn payment transaction, users interact with **Beckn Application Platform (BAP)** to transact with **Beckn Provider Platform (BPP)**. The core Payment object schema captures the primary payment flow, but additional settlement account information is required for secondary fund transfers between parties.

The PaymentSettlement schema extends the Payment object with an array of settlement accounts, where each account specifies:
- **Beneficiary type** (BAP or BPP) - identifies which party the account belongs to
- **Bank account details** - account number, IFSC code, account holder name, bank name
- **Virtual Payment Address (VPA)** - UPI ID for digital payments
- **Payment URL** - URL for payment processing/redirection

### **Use Cases**

1. **Buyer Finder Fee Transfer**: When a BPP accepts payment from a buyer, a buyer finder fee may need to be transferred from BPP to BAP as commission. The settlement accounts enable the BPP to identify the BAP's account details for this transfer.

2. **Overcharge Refund**: When a BAP accepts payment and an overcharged amount needs to be refunded, the settlement accounts enable the BAP to identify the BPP's account details for transferring the excess amount back.

3. **Multi-party Settlements**: In complex scenarios involving multiple parties, settlement accounts allow each party to maintain their account information for various settlement scenarios.

Attach these schemas as follows:

| **Attribute Schema** | **Attach To** | **Purpose** |
| --- | --- | --- |
| PaymentSettlement | Provider.attributes or Payment.attributes | Settlement account details (bank accounts, IFSC codes, UPI addresses) for different beneficiary types (BPP, BAP) to enable inter-party fund transfers. |
| --- | --- | --- |

## **🧭 Role and Design**

- **Aligned with Beckn Core**
  Uses canonical Beckn schemas for common objects and reuses canonical components from:
  - [core.yaml](../../core/v2/attributes.yaml) - Catalog, Item, Offer, Provider, Attributes, Location, Address, GeoJSONGeometry, Payment
  - [api/beckn.yaml](../../../api/beckn.yaml) - Unified API specification for discovery and transaction endpoints
- **Adds settlement semantics only**
  Introduces domain-specific elements for settlement account management including beneficiary types, bank account details, IFSC codes, and UPI addresses.
- **Designed for interoperability**
  Enables BAPs, BPPs, and payment processors to exchange structured settlement account data across Beckn networks for seamless fund transfers.

## **🗺️ Local Namespace Mapping**

The beckn namespace is mapped **locally**:

{ "beckn": "./vocab.jsonld#" }

Vocabulary files live in ./vocab.jsonld and use this same local mapping.

When publishing, replace ./vocab.jsonld# with an absolute URL, e.g.:

<https://schemas.example.org/payment-settlement/v1/vocab.jsonld#>

This supports both local development and public hosting.

## **📂 Files and Folders**

| **File / Folder** | **Purpose** |
| --- | --- |
| **attributes.yaml** | OpenAPI 3.1.1 attribute schema for PaymentSettlement (Provider.attributes or Payment.attributes), annotated with x-jsonld. |
| **context.jsonld** | Maps properties to schema.org and local beckn: IRIs for PaymentSettlement. |
| **vocab.jsonld** | Local vocabulary for PaymentSettlement domain terms (settlementAccounts, beneficiaryType, accountNumber, ifscCode, bankName, vpa, paymentURL, etc.). |
| --- | --- |

## 🏷️ Tags
`payment-settlement, payment, settlement, bank-account, ifsc, vpa, upi, beneficiary, bap, bpp, fund-transfer, buyer-finder-fee, refund, beckn, json-ld, schema.org, openapi`

These tags help implementers and schema registries discover and classify this attribute bundle quickly.