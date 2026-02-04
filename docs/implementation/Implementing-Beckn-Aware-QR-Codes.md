# Beckn Enabled Deep Links

## Objective

To facilitate seamless and standardized user interactions across digital ecosystems, it is crucial to create a universally recognized and standardized "beckn" URI scheme, similar to what Unified Payments Interface (UPI) and WhatsApp has achieved for major platforms like Web, Android and iOS, thus enhancing deep linking capabilities for entities using the Beckn protocol. Furthermore, the scheme should have easy integration and accessibility through software languages like Java, Python, etc.

## Problem Statement

Currently, beckn interactions primarily rely on URL-based RESTFul interfaces that are generic and require additional information carried on wire. Moreover, in an unbundled and interoperable framework, there is a need for a standard whereby creation of information datum needs to be standardized creating the possibility of invoking boilerplate codes for specific actions. To enable widespread adoption and interoperability within the ecosystem, there is a need to establish a universally recognized beckn anchor tag that seamlessly integrates with major platforms, similar to UPI, WhatsApp, messaging interfaces (such as XMPP) etc.

For the current use case of enabling QR codes for merchant shops, merchants lack a unified method to generate QR codes, irrespective of the interfaces where the QR will be consumed, which may direct customers to their specific offerings and catalog within the Beckn ecosystem. Even with the QR codes created, the consumers scanning the QR codes might encounter varied landing experiences due to the absence of a standardized deep linking mechanism via anchor tags.

Hence, in order to increase the accessibility and adoption, embedded QR code is required to direct the consumers to apps compliant with beckn. There is a need for unbundling consumer experience, primarily integrated through buyer apps, at the merchant stores. This will also help the merchants to broaden their reach on any network complying to beckn protocol enabling buyers to buy from identified stores of their choice.

## Proposed Solution
The solution proposed here is to introduce beckn as an identified anchor tag and established protocol within developer community and platforms such as openJDK, Android, iOS etc. As the first use case, it is proposed to enable QR code features for merchants facilitated by their respective BPPs (Seller Apps in this context).

Creating a QR code with data drafted in a deep link enabled through anchor tags of beckn in line of what UPI/ WhatsApp/XMPP have enabled, will enable the discovery of stores and their catalog on the buyer app of their choice. Consumers shall scan such QR codes visibly available on stores onboarded on any network (like ONDC) through a seller app and will be offered for downloading and displaying in the store. Each BAP shall need to respect a standard anchor tag identified through a beckn complaint application and make the store catalog visible on device. The QR code shall make information available in format below. There are two suggestive modes of operation for this anchor tag, however, buyer Apps are free to innovate and create more handles to provide experience to their buyers.

the default scanner apps will point to all beckn enabled apps installed on the phone offering buyer a choice to pick one of them.
The same QR code shall become scannable as an input within App to fetch and render catalog of a specific provider ID as extracted from the URI string mentioned below.

As the primary goal specifically for generating and interpreting QR codes for onboarded merchants, defining the well-defined schema and structure for the beckn anchor tag. This QR code will be available at a seller place like in-store displays, physical advertisements etc. which can be scanned by any buyer willing to engage with a particular seller and their catalog while visiting the store. While a QR code is scanned, it will identify the apps that support the URI or are beckn enabled and will return an on_search response with the catalog.

The deep link for QR code in store is mentioned below:

```beckn://<api-verb>?<param1>=<value1>```

## Data Fields:
The fields provided here are only for reference and serve as a guidance. As use cases evolve and expand, the input fields in the deep link may also grow or change to cater to the specific needs and scenarios. The field structure refers to the beckn protocol specifications. Below fields are populated based on the use cases defined in below sections.

| Fields | Description | Example | Default | Mandatory |
|--------|-------------|---------|---------|-----------|
| context.bpp_id | Subscriber ID of the BPP | seller-np.com | - | No |
| message.intent.provider.id | Id of the provider | P1 | - | No |

## QR code generation
BPPs would facilitate the sellers to generate the QR codes specific to the provider. Networks may offer open-source SDKs designed to produce QR codes embedded with merchant-specific information. However, BPPs may decide to provide their own feature and technology sets to generate standard QR codes with appropriate density for each scanning of the code.

## URI scheme Recognition
Each BAP application that are beckn enabled would need to add beckn as the supported URI scheme. When the QR code with deep link - beckn://<api-verb>?context.bpp_id=.... is scanned, the system checks for installed applications which can handle the beckn:// scheme.

## Platform Integrations
Different platforms have different handling mechanisms, for example, Android uses Intent Filters and iOS uses URL schemes or Universal links to identify which apps can handle which URI schemes or use fallback URLs to redirect the consumer to a fallback web URL, usually prompting them to download the relevant app. If multiple apps have registered the same URI scheme, it will either redirect to the default app or prompt the user to select the app they would like to use.

## Action Identification
The component in the deep link identifies the specific api action. For example,
```beckn://<api-verb>?context.bpp_id=<bpp_id>```

## Network Agnostic
The QR code does not recommend to use network. This is because the items or provider catalogues are meant to operate in different networks. The BAP scanning the QR code maintains the network context for the transaction.

## Interpreting Deep Link
The interpretation of a beckn deep link depends on the specific parameters and values included in the deep link URL. Beckn deep links are designed to convey specific instructions or information to Beckn enabled applications (Buyer Application Platforms or BAPs). Here's a general guide on how a beckn deep link is typically interpreted.

Beckn Deep Link Structure:
```beckn://<api-verb>?context.bpp_id=<BPP_ID>```

### Scheme (beckn://):
The custom URI scheme that indicates the deep link is specifically for beckn enabled apps or services.

### API Action Verb ():
The component in the deep link identifies the specific api action to which the request can be tied. 

### Query Parameters:
The query parameters are key-value pairs included in the deep link, and they convey specific information for BAP to consume and redirect the user accordingly. All the query parameters are optional, but they must be fully qualified beckn protocol identifiers.

Defining deep links can help in
A standardized schema and structure to QR code generation and interpretation.
Consumers are guaranteed a consistent experience regardless of which merchant's QR code they scan.
With a standard protocol in place, developers can build and scale faster.
Merchants can run targeted campaigns, knowing they can direct users to specific actions or pages seamlessly.

## Use Cases:
Deep linking with the beckn URI scheme can open the door to a wide range of use cases, each designed to enhance user interaction, convenience, and efficiency across different domains within the network. While the possibilities are vast, we've cataloged a few illustrative use cases to showcase the potential of this technology.

### Catalog Access through Seller-Generated QR Codes
Imagine a buyer walking into a store and having the power to view the complete merchant's catalog using their smartphone. By scanning a QR code generated by the seller (facilitated by BPP), customers can have instant access to the entire inventory, enhancing the shopping experience while making it more efficient.

Deep Link Structure:
```beckn://discover?context.bpp_id=sellerapp.com&message.catalogs.items.provider.id=P1```

When a buyer scans the QR code, the system (buyer’s mobile device) looks for applications that support beckn URI scheme. Once a buyer chooses one specific buyer application (BAP) from the list of applications supported by beckn, the BAP identifies the action, which is the discovery phase and redirects the buyer to the catalog for sellerapp.com.P1 from cache.

## Considerations
The merchant generated QR code will have specific bpp id and provider id in the deep link. Hence, a BAP can either:

- Show the catalog from cache or
- Send a live search to all BPPs and then show specific merchant’s catalog
- Send live search for specific bpp id in context, however in that case the BAP would need the bpp url (from local lookup).
- All BAPs would need to support beckn anchor tags across different platforms, i.e., web, Android, and iOS.

The BAPs would need to maintain a local lookup for registry endpoints based on the network, in case the BAP is complying to multiple networks within beckn.
