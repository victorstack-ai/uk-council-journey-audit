# UK Council Journey Audit Tool

This tool is inspired by **David Bishop's Council Insight** methodology, which rethinks how UK council websites are evaluated by focusing on **user journeys** and **customer needs** rather than just technical metrics.

## Inspiration
David Bishop, founder of Digital Journey Coach, developed Council Insight to analyze how users interact with local authority websites. This tool aims to provide a lightweight, automated way to audit common user journeys across UK council websites.

## Features
- **Journey-based Auditing**: Define and run automated checks for common council tasks (e.g., reporting a missed bin, finding council tax info).
- **Findability Analysis**: Measures how many clicks/interactions it takes to reach a goal.
- **Rich Reporting**: Generates a summary of the journey's health.

## Installation
```bash
pip install .
playwright install chromium
```

## Usage
```bash
council-audit --url https://www.oxford.gov.uk --journey missed-bin
```

## Disclaimer
This is a demonstration tool and not an official Council Insight product.
