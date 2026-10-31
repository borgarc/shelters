# Anonymise Caretakers instead of deleting them

When a Caretaker leaves the organisation, asks for erasure (GDPR art. 17), or has had no active Assignment for 12 months (and an Administrator confirms), we anonymise them instead of deleting the row: name, email and phone are wiped, login is disabled, tokens are revoked, and active Assignments are closed with today's date. Past Assignments are kept without personal data, so a Colony's caretaking history stays countable without identifying anyone. Erasure is never self-service: an Administrator first reassigns the Caretaker's Colonies, especially when they are the Lead Caretaker.

## Considered Options

- **Hard delete with cascade**: loses the Colony's caretaking history.
- **Hard delete keeping Assignments with a null Caretaker**: same result as anonymising, but every query must handle a missing Caretaker.
