# Beckn Network Observability Specification

## Overview

This document details the telemetry specification to be implemented by the Beckn network participants to enable Network Observability.

This specification employs Open Telemetry principles and adopts the [Open Network Telemetry Specification](https://github.com/Sunbird-Obsrv/network-telemetry-spec). The document contains the following sections:

**Collection and Export of Network events** \- The section aims to capture the ideal quantity and level of detail from the Beckn network.

- **Telemetry Structure** \- List of all telemetry events and their corresponding OpenTelemetry signals that are part of the spec  
- **Event Definitions** \- Detailed definition of every event along with Beckn examples  
- **Key Otel attributes** and their mapping with corresponding Beckn schema.

**Receiving Network events** \- The section aims to capture the details of the Receiver API.

- **Receiver API** \- Details such as endpoint, payload, auth and more. 

A complete list of all additional Beckn specific telemetry attributes are defined as per the OTel Semantic Convention specification in an addendum document, [here](?tab=t.tg46xoryddin).

## Open Network Telemetry Specification

We will be adopting the [Open Network Telemetry Specification](https://github.com/Sunbird-Obsrv/network-telemetry-spec) defined by [Sunbird](https://sunbird.org) for all decentralized networks like Beckn, Sahamti etc. This specification is based on the OpenTelemetry protocol. While the envelope structure is going to be the same, there are some changes (additional attributes) to the structure that are documented as part of the [telemetry structure](#telemetry-structure).

## Telemetry Structure

As described in the [Open Network Telemetry Specification](https://github.com/Sunbird-Obsrv/network-telemetry-spec), Following is the overall structure of the telemetry event:

```javascript
{
  "resource": { // Required. Entity level context
    "attributes": [
       {
            "key": "String",
            "value": {}
        }
      ]
  },
  "scopeSpans/scopeMetrics/scopeLogs": [ // Required. Capture one or more event types
    {
      "scope": { // Optional. Event level transport context corresponding to the actual events sent in the "<type>" array.
        "name": "String",
        "version": "String",
        "attributes": [
          {
            "key": "String",
            "value": {}
          }
        ]
      },
      "spans/metrics/logRecords": [{}] // Required. Events of the same type or for a particular flow
    }
  ]
}
```

Adopting OpenTelemetry protocol enables us to batch multiple events either of the same type of within a same flow (like discover & order confirm)

Every event has 3 parts to it:

1. `resource` \- Capture the required entity level global contextual attributes as explained in the next [section](#entity-context)  
2. `scope` \- Capture the optional transport contextual attributes of the succeeding events explained in next [section](#transport-context)  
3. `spans/metrics/logRecords` \- Capture the actual data about the event explained in next [section](#event-data)

### Entity Context {#entity-context}

Following is the required entity level contextual attributes to be sent for all events:

```javascript
"resource": {
  "attributes": [
    {
      "key": "eid", // Required. Type of the event produced. One of API/METRIC/AUDIT
      "value": {"stringValue": String}
    },
    {
      "key": "producer", // Required. Which network participant has produced the event (Beckn Subscriber_id)
      "value": {"stringValue": String}
    },
    {
      "key": "producerType", // Required. Type of the network participant - One of BAP/BPP (Beckn)
      "value": {"stringValue": String}
    }
  ]
}
```

Detailed example would be described as part of [event types](#event-types)

### Transport Context {#transport-context}

Following are the optional transport contextual attributes that can be sent for every event:

```javascript
"scope": { // Optional
  "name": String, // Required. An identifier/name for the signals in this scope. For ex: subscriber_id
  "version": String, // Required. A version number of the  telemetry specification
  "attributes": [ // Optional. Attributes that are common for all the signals in this envelope
    {
      "key": "scope_uuid", // Optional. Generate a unique id for the batch for idempotency
      "value": {"stringValue": String}
    },
    {
      "key": "checksum", // Optional. Generate a checksum to enable checks for tampering
      "value": {"stringValue": String}
    },
    {
      "key": "count", // Optional. Total count of api, metric or audit events in the succeeding events section
      "value": {"intValue": Int} etc 
    }
  ]
} 
```

### Benefits of Sending Transport-Level Information within Telemetry Events

1. **scope\_uuid** \- *Idempotency*: Using a UUID allows for the unique identification of each event or batch of events. This is crucial for ensuring idempotency, meaning that duplicate events can be easily identified and discarded. It helps prevent unintended duplication of data, ensuring data integrity and accuracy.  
     
2. **checksum** \- *Data Integrity*: Including a checksum in the telemetry events enables recipients to verify that the data has not been tampered with during transmission. By calculating the checksum at the sender's end and verifying it at the receiver's end, any unauthorized modifications or tampering with the data can be detected, ensuring data integrity and security.  
     
3. **count** \- *Completeness Check*: Including a count within the telemetry events provides a quick and simple way to verify whether all the events in a batch have been successfully received. By comparing the count of events sent with the count of events received, recipients can quickly identify any discrepancies or missing data. This helps ensure data completeness and reliability, allowing for effective monitoring and troubleshooting of data transmission issues.

### Event Data {#event-data}

Contains the actual data about the event for the defined [event types](#event-types). The structure will be specific for every event type.

## Event Types

As explained in the [Open Network Telemetry Specification](https://github.com/Sunbird-Obsrv/network-telemetry-spec/blob/main/docs/otel-specification.md#telemetry-events), there are 3 types of events required:

1. **API Spans** \- Event to capture information from API payload   
2. **METRIC** \- Event to capture Business & Operational Metrics   
3. **AUDIT** \- Event to capture logs Information

### API (Spans)

API telemetry event is used by network participants to share API data with the network observability infrastructure. API telemetry event contains API transport data, including the API URL, correlation identifiers for mapping multiple interconnected API calls, and response metadata like status codes and error details.

For a Beckn network, each Span represents a single API event carried out by the Network Participant. The context propagation is achieved by mapping standard OpenTelemetry attributes with Beckn Context attributes, as per below

* `Trace_id` \- mapped to Beckn `Context.transaction_id` that holds the complete transaction context  
* `Span_id` \- mapped to Beckn `Context.message_id` that holds the round trip context for every Beckn action (e.g. select, confirm, status etc.)


  
Following is the event data spec which adopts the structure defined in the Open Network Telemetry Spec:

```javascript
{
  "spans": [{ // Required. One or more API events in detail
    "name": String, // Required. API Name
    "traceId": String, // Required. Unique ID to trace/track the entire transaction or flow (context.transaction_id)
    "spanId": String, // Required. Unique ID of the API event call (context.message_id)
    "parentSpanId": String, // Optional. Parent API id for correlation (ex. message_id of parent transaction_id for cascaded transaction.)
    "startTimeUnixNano": String, // Required. Start time of the API call in nano-seconds
    "endTimeUnixNano": String, // Required. End time of the API call in nano-seconds
    "status": String, // Required. one of Error, Ok
    "attributes": [ // Required. List of attributes providing additional details about the span
      {
        "key": "span_uuid", // Required. Unique identifier for this span record
        "value": {"stringValue": String}
      },
      {
        "key": "observedTimeUnixNano", // Optional. Event generated time as ISO datetime if different than endTimeUnixNano
        "value": {"stringValue": String}
      },
      {
        "key": "sender.id", // Required. Identifier of the networ node that initiated the API call (bap_id for forward Beckn action calls or bpp_id for callback action calls.)
        "value": {"stringValue": String}
      },
      {
        "key": "recipient.id", // Required. Identifier of the network node that is expected to be the recipient of the API call (bpp_id for forward Beckn action calls or bap_id for callback action calls.)
        "value": {"stringValue": String}
      },
      {
        "key": "http.request.method", // Required. Http method one of GET/POST/PATCH/DELETE etc
        "value": {"stringValue": String}
      },
      {
        "key": "server.address", // Optional. Server name if any
        "value": {"stringValue": String}
      },
      {
        "key": "http.route", // Required. URL of the request
        "value": {"stringValue": String}
      },
      {
        "key": "http.response.status_code", // Required. Status code of the API call
        "value": {"intValue": Int}
      },
      {
        "key": "user_agent.original", // Optional. Service emitting the network logs.
        "value": {"stringValue": String}
      }

    ],
    "events": [{ // Optional. Capture additional API specific data like errors and optional attributes
      "name": String, // Required. Name of the additional data
      "time": String, // Required. Event time as ISO datetime
      "attributes": [] // Optional. List of attributes 
    }]
  }]
}
```

**Note**: There can be additional attributes to be sent for various APIs that will be defined under the [Semantic Convention section](?tab=t.tg46xoryddin). 

#### Example API Event

The following event (A discover API call for example) contains an example complete event as per open network telemetry specification and all the required sections and attributes described in this document.

```json
{
  "resourceSpans": [{
    "resource": {
      "attributes": [
        {"key": "eid", "value": {"stringValue": "API"}},
        {"key": "producer", "value": {"stringValue": "BAP1`"}},
        {"key": "producerType", "value": {"stringValue": "BAP"}},
        {"key": "purposeCode", "value": {"stringValue": "105"}}
      ]
    }, 
    "scopeSpans": [{
      "scope": {
        "name": "Discovery", 
        "version": "1.0", 
        "attributes": [
          {"key": "scope_uuid", "value": {"stringValue": "9db4-325096b39f47"}},
          {"key": "checksum", "value": {"stringValue": "120EA8A25E5D487BF68B5F7096440019"}},
          {"key": "count", "value": {"intValue": 1}}
        ]
      },
     "spans": [{ 
       "name": "Discover",
       "traceId": "f35761ac-4a18-11e8-96ff-0277a9fbfedc",
       "spanId": "f35761ac-4a18-11e8-96ff-0277a9fbfedc",
       "startTimeUnixNano": "1544712660000000000",
       "endTimeUnixNano": "1544712661000000000",
       "status": "Ok",
       "attributes": [
        {"key":"span_uuid","value": {"stringValue": "3fae2d5f-3cfb-4e6e-b6a2-0ee5d6579832"}},
        {"key":"observedTimeUnixNano","value": {"stringValue": "1581452772000000321"}},
        {"key":"sender.id","value": {"stringValue": "BAP`"}},
        {"key":"recipient.id","value": {"stringValue": "BPP1"}},
        {"key":"http.request.method","value": {"stringValue": "POST"}},
        {"key":"http.route","value": {"stringValue": "/discover"}},
        {"key":"server.address","value": {"stringValue": "bap.np1.com"}},
        {"key":"http.response.status_code","value": {"stringValue": "200"}},
        {"key":"user_agent.original","value": {"stringValue": "Beckn_ONIX/1.3.1"}}
       ]
     }]
   }]
 }]
}
```

### METRIC

Metric event is used by Network Participants to share business metrics data with the network observability infrastructure.

Following is the metric data spec as per the Open Network Telemetry Spec:

```javascript
{
  "metrics": [{ // Required. One or more METRIC events in detail
    "name": String, // Required. Metric name
    "unit": String, // Required. Type of metrics stream unit. Common unit types are:
            // Count: Represents a simple count of events or entities. The unit for count is "1"
            // Seconds: Represents a duration or time interval. The unit is "s" or "seconds"
            // Bytes: Represents data size. The unit is typically "B" or "bytes."
            // Percent: Represents a ratio multiplied by 100. The unit is "%"
            // Milliseconds: Represents a duration in milliseconds. The unit is "ms" or "milliseconds"
    "description": String, // Optional. The metric streams description
    "sum": { // Required. The metric data type
      "aggregationTemporality": Int, // Required. One of 1 or 2. 1 - delta and 2 is cumulative
      "isMonotonic": Boolean, // Optional. Defaults to false
      "dataPoints": [{
        "asDouble": Double, // Required. The metric value in double
        "startTimeUnixNano": String, // Required. Start time of the sum time window
        "endTimeUnixNano": String, // Required. End time of the the sum time window
        "attributes": [ // Required. Attributes providing additional details about the metric
          {
            "key": "metric_uuid", // Required. Unique identifier for this metric record
            "value": {"stringValue": String}
          },
          {
            "key": "observedTimeUnixNano", // Optional. Event generated time as ISO datetime
            "value": {"stringValue": String}
          },
          {
            "key": "metric.code", // Required. Code of the metric as defined in the metrics registry
            "value": {"stringValue": String}
          },
          {
            "key": "metric.category", // Optional. metric category or type.
            "value": {"stringValue": String}
          },
          {
            "key": "metric.granularity", // Required. Metric granularity - Hour/Week/Day etc
            "value": {"stringValue": String}
          },
          {
            "key": "metric.frequency", // Required.Metric computation frequency-hr/day/week etc
            "value": {"stringValue": String}
          }
        ]
      }]
    }
  }]
}
```

#### Example Metric Event

The following metric event (A BAP usage metric) contains an example complete event as per open network telemetry specification including all the required sections and attributes described in this document.

```json
{
 "resourceMetrics": [{
   "resource": { 
     "attributes": [
       {"key": "eid", "value": {"stringValue": "METRIC"}},
       {"key": "producer", "value": {"stringValue": "bap-1234"}},
       {"key": "domain", "value": {"stringValue": "Retail"}}
     ]
   }, 
   "scopeMetrics": [{
     "scope": {
       "name": "Beckn_ONIX",
       "version": "1.3.1",
       "attributes": [
         {"key":"scope_uuid","value": {"stringValue": "9db4-325096b39f47"}},
         {"key":"checksum","value": {"stringValue": "120EA8A25E5D487BF68B5F7096440019"}},
         {"key":"count","value": {"intValue": 3}}
       ] 
     },
     "metrics": [
     { // 1. Number of on_discover API calls in a day
      "name": "search_api_total_count",
      "unit": "1",
      "sum": {
        "aggregationTemporality": 1,
        "isMonotonic": false,
        "dataPoints": [{
          "asDouble": 15699,
          "startTimeUnixNano": "1544712660000000000",
          "endTimeUnixNano": "1544712661590000000",
          "attributes": [
            {"key":"metric_uuid","value": {"stringValue": "43kr3d5f-3cfb-4e6e-b6a2-0ee5d6508923"}},
            {"key":"observedTimeUnixNano","value": {"stringValue": "1581452772000000321"}},
            {"key":"metric.code","value": {"stringValue": "search_api_total_count"}},
            {"key":"metric.category","value": {"stringValue": "Discovery"}},
            {"key":"metric.granularity","value": {"stringValue": "day"}},
            {"key":"metric.frequency","value": {"stringValue": "day"}},
            {"key":"addlData.apiid","value": {"stringValue": "search"}} // Custom attribute
          ]
        }]
      }
     },
     { // 2. Average response time for all API calls in an hour
      "name": "avg_api_response_time",
      "unit": "1",
      "sum": {
        "aggregationTemporality": 1,
        "isMonotonic": false,
        "dataPoints": [{
          "asDouble": 1211,
          "startTimeUnixNano": "1544712660000000000",
          "endTimeUnixNano": "1544712661590000000",
          "attributes": [
            {"key":"metric_uuid","value": {"stringValue": "9rie3d5f-3cfb-4e6e-b6a2-0ee5d639822"}},
            {"key":"observedTimeUnixNano","value": {"stringValue": "1581452772000000321"}},
            {"key":"metric.code","value": {"stringValue": "avg_api_response_time"}},
            {"key":"metric.category","value": {"stringValue": "NetworkHealth"}},
            {"key":"metric.granularity","value": {"stringValue": "hour"}},
            {"key":"metric.frequency","value": {"stringValue": "day"}}
          ]
        }]
      }
     },
     { // 3. Average response time for on_search API calls in a day
      "name": "search_api_failure_percent",
      "unit": "%",
      "sum": {
        "aggregationTemporality": 2,
        "isMonotonic": false,
        "dataPoints": [{
          "asDouble": 2.3,
          "startTimeUnixNano": "1544712660000000000",
          "endTimeUnixNano": "1544712661590000000",
          "attributes": [
            {"key":"metric_uuid","value": {"stringValue": "93j3jd5f-3cfb-4e6e-b6a2-0ee5d6391221"}},
            {"key":"observedTimeUnixNano","value": {"stringValue": "1581452772000000321"}},
            {"key":"metric.code","value": {"stringValue": "search_api_failure_percent"}},
            {"key":"metric.category","value": {"stringValue": "NetworkHealth"}},
            {"key":"metric.granularity","value": {"stringValue": "day"}},
            {"key":"metric.frequency","value": {"stringValue": "day"}}
          ]
        }]
      }
     }]
   }]
 }]
}
```

### AUDIT Logs

Audit events are used by participants to communicate about updates and state changes of entities within the network. The entities include objects like transactions, as well as the participants themselves.   
In addition audit events can also be used to store all transaction logs to the `Transaction Ledger`.

Following is the overall structure for Log events as per the open telemetry spec:

```javascript
{
  "logRecords": [{ // Required. One or more LOG events in detail
    "timeUnixNano": String, // Required. Time when the event occurred
    "observedTimeUnixNano": String, // Optional.Time when the event was observed if different from occurred
    "severityNumber": String, // Optional. Default to 12
    "traceId": String, // Optional. Correlate to any API event context transaction id
    "spanId": String, // Optional. Correlate to any API event context message id
    "body": { // Required. Body of the log record as per OTEL protocol
        "stringValue": String, // Required. Capture the description here
    }
    "attributes": [] // Required. Attributes providing additional details about the audit record
  }]
}
```

**Note**: The attributes to be sent for various APIs will be defined under the [Semantic Convention section](?tab=t.tg46xoryddin). 

### Support for **Two** Receivers

- Exporters can send envelopes to `two` independent Receiver APIs.   
  - One Receiver is operated by the Network Operator for Governance  
  - Another Receiver is an optional receiver that may offer comprehensive Network aware analytics capability or a NP hosted analytics service for better debugging and observability.  
- Network Operators may mandate sharing network events with the Receiver hosted by them. Sharing network events with the second Receiver is optional and configurable.  
- Support separate Configuration with the Exporter for each Receiver.  
- Execution: When a Beckn request is processed, the observability exporter pushes the data to all active Receivers concurrently.  
- Failure Handling: A failure to push to one Receiver should not interrupt the flow to another Receiver, ensuring that separate configurations provide operational redundancy.

## Key Attributes of Telemetry Event

In this section, we list OTel Keys and their mapping with Beckn schema fields. This section ensures that the semantic conventions of OTel are mapped to corresponding fields from the Beckn schema, enabling all downstream Observability applications to maintain the same semantics for every Beckn network seamlessly.

| Key | Description | What value to send? |
| :---- | :---- | :---- |
| spanId | An unique id to identify a specific API round trip of Beckn action or Audit event | Use the `context.message_id` being passed in the request/response structures. |
| traceId | An unique id to trace or track an entire end to end transaction or flow. For ex: Account discovery to linking flow | Use the `context.transaction_id` being passed in the request/response structures. |
| sender.id | An unique id to identify the originator of the API transaction | Use the `context.bap_id` if you are initiating beckn action calls (e.g. select) Use the `context.bpp_id` if you are initiating beckn callback action calls (e.g. on\_select) |
| recipient.id | An unique id to identify the recipient of the API transaction | Use the `context.bpp_id` if you are initiating beckn action calls (e.g. select) Use the `context.bap_id` if you are initiating beckn callback action calls (e.g. on\_select) |
| producer | An unique id to identify the owner of the telemetry event | Use `context.bap_id` or  `context.bpp_id` depending on your role (BAP/BPP) |
| producerType | Type of network node | If you are an BAP, add `BAP` If you are an BPP, add `BPP` |
| observedTimeUnixNano | Timestamp at which the event was observed | For API event add the timestamp when you have received the response back For a METRIC event add the timestamp of when the metric event is generated For the AUDIT event add the timestamp of when the event was observed |

## ---

## Receiver API

The section covers details on how the API is structured and some recommendations on how it can be implemented.

### API to Receive events 

```
POST /v1/telemetry
```

### Log Receiver API Requirements:

The Receiver API implementation should support following:

1. **Protocols:**  
   - Support OTLP, HTTP, Protobuf  
   - Accept compressed payloads (gzip)

   

2. **Signature Validation:**  
   - Use Beckn signature header in the request to validate both sender and payload as per Beckn specification.  
   - Implement Rate limiting per client to protect from surge of incoming calls

   

3. **Data Validation:**  
   - Validate OTLP schema conformance  
   - Check for Required fields  
   - Reject logs with unmasked PII patterns  
   - Size limits per log record (configurable max 256KB)

   

4. **Storage & Retention:**  
   - Support High-throughput log ingestion (\>10K logs/sec)  
   - Indexing on: transaction\_id, timestamp, action, status  
   - Retention policy: TTL configurable by the Network operator

### Log shipping cadence

Network Operators can define configuration of cadence that the exporter will use to ship the envelopes to the Receiver API. Supported configuration attributes with sample values are listed below-

**Batch Processing:**

- **Default batch size**: 100 log entries  
- **Default flush interval**: 60 seconds  
- **Configurable max wait time**: 5 minutes (safety flush)  
- **Retry on failure**: Exponential backoff (100ms → 500ms → 2s → 10s)  
- **Maximum retry attempts**: 3

**Real-time Triggers:**

- Critical errors (HTTP 5xx, validation failures, specific Beckn Error codes)  
- High-value transactions (configurable threshold)  
- Fraud detection triggers (configurable rules)

**Performance Considerations:**

- Asynchronous processing (non-blocking)  
- In-memory buffer with overflow to disk (configurable)  
- Circuit breaker pattern for API failures  
- Compression of payloads before transmission (gzip)

### Sampling for network events

**Filter Configuration:**

- Allow filtering by action, network, status  
- Support sampling rates (e.g., log 10% of search APIs, 100% of confirm APIs)
