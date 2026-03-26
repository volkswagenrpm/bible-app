# Bible Text Sources

This app uses real text sources (no machine translation) and keeps source IDs visible in the UI.

## GUI Sources

1. English Orthodox (default)
- Source: `wldeh/bible-api` dataset
- Version ID: `en-kjv`
- Scope: Includes deuterocanonical books in this dataset (80-book canon)
- URL: https://github.com/wldeh/bible-api

2. Portuguese
- Source: `bible-api.com`
- Version ID: `almeida`
- Translation: João Ferreira de Almeida
- License (from endpoint metadata): Public Domain
- URL: https://bible-api.com/data/almeida

3. Arabic
- Source: `wldeh/bible-api` dataset
- Version ID: `arb-kehm`
- Translation label in source: Biblica Open New Arabic Version 2012
- URL: https://github.com/wldeh/bible-api

## Notes

- Availability of deuterocanonical books depends on the source and translation.
- When a source does not include a requested book/chapter, the app shows a clear unavailable/error message.
