# Problem Definition

The task is privacy-preserving biometric identification over unit-norm templates.

Given an enrolled gallery of identity templates and a query template, the system must identify the matching enrolled subject when the query is genuine and reject non-enrolled impostor queries. Templates are fixed 512-dimensional real-valued unit vectors, matching quality is judged from gallery-query scores, and the benchmark fixes:

- one enrolled gallery template per identity,
- genuine query templates with identity labels,
- impostor query templates that should be rejected at calibrated thresholds.

The problem is method-agnostic. Any submitted method may use any protected representation or matching procedure, provided it writes gallery-query score matrices in the required artifact format and does not store enrolled gallery templates as raw reusable unit vectors when claiming protected-template performance.

## Portable Dataset

The gym uses a reproducible synthetic unit-vector benchmark in `data/generate_synthetic.py`. The generated data preserves the relevant identification structure: high-dimensional normalized templates, same-identity query variation, many enrolled identities, and impostor queries used to set false-positive identification thresholds.
