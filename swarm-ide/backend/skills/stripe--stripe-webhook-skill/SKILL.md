---
name: Stripe Webhook Handler
description: Handles Stripe webhooks securely.
---

## Instructions
Always use `stripe.Webhook.construct_event` to verify the payload signature.
Always wrap the handler in a try/except stripe.error.SignatureVerificationError.
