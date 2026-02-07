from .models import Journey, JourneyStep

DEFAULT_JOURNEYS = {
    "missed-bin": Journey(
        name="Report a Missed Bin",
        description="Navigate to the missed bin reporting page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="missed bin"),
            JourneyStep(name="Result", action="click_link", target="Report a missed bin"),
        ]
    ),
    "council-tax": Journey(
        name="Council Tax Payment",
        description="Find where to pay council tax.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="pay council tax"),
            JourneyStep(name="Result", action="click_link", target="Pay your Council Tax"),
        ]
    )
}
