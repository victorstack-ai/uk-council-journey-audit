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
    ),
    "pay-council-tax": Journey(
        name="Pay Council Tax",
        description="Navigate to the council tax online payment page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="council tax payment"),
            JourneyStep(name="Result", action="click_link", target="Council Tax"),
            JourneyStep(name="Payment Page", action="click_link", target="Pay"),
        ]
    ),
    "report-pothole": Journey(
        name="Report a Pothole",
        description="Navigate to the pothole or road defect reporting page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="report pothole"),
            JourneyStep(name="Result", action="click_link", target="Report a pothole"),
        ]
    ),
    "parking-permit": Journey(
        name="Apply for Parking Permit",
        description="Navigate to the residential parking permit application page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="parking permit"),
            JourneyStep(name="Result", action="click_link", target="Parking permits"),
            JourneyStep(name="Apply Page", action="click_link", target="Apply"),
        ]
    ),
    "planning-applications": Journey(
        name="Find Planning Applications",
        description="Navigate to the planning applications search page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="planning applications"),
            JourneyStep(name="Result", action="click_link", target="Planning"),
            JourneyStep(name="Search Page", action="click_link", target="Search"),
        ]
    ),
    "register-to-vote": Journey(
        name="Register to Vote",
        description="Navigate to the electoral registration or voter registration page.",
        steps=[
            JourneyStep(name="Home Page", action="navigate"),
            JourneyStep(name="Search", action="search", target="register to vote"),
            JourneyStep(name="Result", action="click_link", target="Register to vote"),
        ]
    ),
}
