# UK Council Journey Audit Tool

A Python-based browser automation tool that audits UK council websites for user task completion. Inspired by **David Bishop's Council Insight** methodology, this tool evaluates council websites by focusing on **user journeys** and **customer needs** rather than just technical metrics.

The tool uses Playwright to simulate real user interactions, navigating council websites and measuring how easy it is to complete common tasks such as reporting a missed bin, paying council tax, or finding planning applications.

## What It Measures

- **Findability (clicks to goal)**: Counts the number of clicks and interactions required to reach a specific service or information page from the council homepage.
- **Journey success/failure**: Determines whether a user can successfully complete a common task end-to-end.
- **Time to completion**: Measures how long each journey takes, including page load times.
- **Error detection**: Identifies broken links, missing search results, and inaccessible pages that block user journeys.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from source

```bash
git clone https://github.com/your-username/uk-council-journey-audit.git
cd uk-council-journey-audit
pip install .
playwright install chromium
```

### Install dependencies only (for development)

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Run a predefined journey

```bash
council-audit --url https://www.oxford.gov.uk --journey missed-bin
```

### Available options

```bash
council-audit --help
```

| Option      | Description                              | Required |
|-------------|------------------------------------------|----------|
| `--url`     | Base URL of the UK council website       | Yes      |
| `--journey` | Name of the journey to audit             | No (default: `missed-bin`) |

### Examples

Audit the missed bin journey on Oxford City Council:

```bash
council-audit --url https://www.oxford.gov.uk --journey missed-bin
```

Audit council tax payment on Birmingham City Council:

```bash
council-audit --url https://www.birmingham.gov.uk --journey pay-council-tax
```

Report a pothole on Manchester City Council:

```bash
council-audit --url https://www.manchester.gov.uk --journey report-pothole
```

Find planning applications on Leeds City Council:

```bash
council-audit --url https://www.leeds.gov.uk --journey planning-applications
```

## Available Journeys

| Journey Key             | Description                                         |
|-------------------------|-----------------------------------------------------|
| `missed-bin`            | Report a missed bin collection                      |
| `council-tax`           | Find council tax payment information                |
| `pay-council-tax`       | Navigate to the council tax payment page            |
| `report-pothole`        | Report a pothole or road defect                     |
| `parking-permit`        | Apply for a residential parking permit              |
| `planning-applications` | Find and search planning applications               |
| `register-to-vote`      | Register to vote or find electoral registration     |

## Adding Custom Journeys

You can define custom journeys by creating `Journey` objects with a sequence of steps. Each step has a `name`, an `action` type, and an optional `target`.

### Supported actions

- `navigate` -- Opens the council homepage (base URL).
- `search` -- Fills in a search box with the `target` text and submits.
- `click_link` -- Clicks a link matching the `target` text.

### Example: define a custom journey in Python

```python
from uk_council_journey_audit.models import Journey, JourneyStep
from uk_council_journey_audit.auditor import CouncilAuditor

custom_journey = Journey(
    name="Find Recycling Info",
    description="Navigate to the recycling information page.",
    steps=[
        JourneyStep(name="Home Page", action="navigate"),
        JourneyStep(name="Search", action="search", target="recycling"),
        JourneyStep(name="Result", action="click_link", target="Recycling and waste"),
    ]
)

auditor = CouncilAuditor("https://www.oxford.gov.uk")
result = auditor.run_journey(custom_journey)

print(f"Success: {result.success}")
print(f"Steps taken: {result.steps_taken}")
print(f"Duration: {result.duration:.2f}s")
```

## Sample Output

```
Auditing journey: Report a Missed Bin on https://www.oxford.gov.uk

              Audit Result
┌──────────────┬──────────────────┐
│ Metric       │ Value            │
├──────────────┼──────────────────┤
│ Success      │ Yes              │
│ Steps Taken  │ 3                │
│ Duration     │ 4.23s            │
└──────────────┴──────────────────┘

Journey Log:
  - Step 1: Home Page (navigate)
  - Step 2: Search (search)
  - Step 3: Result (click_link)
```

## Development

### Running tests

```bash
pytest
```

### Project structure

```
uk-council-journey-audit/
├── src/uk_council_journey_audit/
│   ├── auditor.py     # Core browser automation and auditing logic
│   ├── cli.py         # Command-line interface (Click)
│   ├── journeys.py    # Predefined journey definitions
│   └── models.py      # Pydantic data models
├── tests/
│   └── test_auditor.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This is a demonstration tool and not an official Council Insight product.
