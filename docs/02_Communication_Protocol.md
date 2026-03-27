# Communication Protocol (v2.0.0)

## 1. Transport model

Beckn v2.0.0 communication in this repository is:
- HTTPS-based,
- signature-authenticated,
- asynchronous by design,
- action-specific by endpoint.

## 2. Endpoint style

The v2.0.0 API profile uses explicit POST endpoints per action, for example:
- /discover → /on_discover
- /select → /on_select
- /init → /on_init
- /confirm → /on_confirm
- /status → /on_status
- /track → /on_track
- /update → /on_update
- /cancel → /on_cancel
- /rate → /on_rate
- /support → /on_support

Catalog APIs are also explicit:
- /catalog/publish, /catalog/on_publish
- /catalog/subscription and related subscription endpoints
- /catalog/pull and pull-result download endpoint
- /catalog/master/* endpoints

## 3. Request-response lifecycle

1. Sender posts a signed request.
2. Receiver validates signature and structure.
3. Receiver returns immediate Ack/Nack transport response.
4. Business payload callback follows on corresponding on_* endpoint where applicable.

## 4. Authentication and non-repudiation

- Authorization header carries Beckn HTTP Signature.
- Ack carries CounterSignature proving receipt by receiver.
- Callback correlation uses context and action coupling, plus in-reply semantics where applicable.

## 5. Context and execution semantics

- context.action must match invoked endpoint action.
- context.try allows sandbox execution where supported (update/cancel/rate/support).
- Implementations should treat callbacks as primary business delivery mechanism.

## 6. Error semantics

- 200 Ack
- 409 AckNoCallback
- 400 NackBadRequest
- 401 NackUnauthorized
- 500 ServerError

See:
- ./03_Core_API_Envelope.md
- ./05_Signing_Beckn_APIs_in_HTTP.md
- ../api/v2.0.0/beckn.yaml
