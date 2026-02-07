import click
from rich.console import Console
from rich.table import Table
from .auditor import CouncilAuditor
from .journeys import DEFAULT_JOURNEYS

console = Console()

@click.command()
@click.option("--url", required=True, help="Base URL of the UK Council website.")
@click.option("--journey", type=click.Choice(list(DEFAULT_JOURNEYS.keys())), default="missed-bin", help="The journey to audit.")
def main(url: str, journey: str):
    """UK Council Website Journey Auditor."""
    journey_obj = DEFAULT_JOURNEYS[journey]
    
    console.print(f"[bold blue]Auditing journey:[/bold blue] {journey_obj.name} on {url}")
    
    auditor = CouncilAuditor(url)
    result = auditor.run_journey(journey_obj)
    
    table = Table(title="Audit Result")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Success", "[green]Yes[/green]" if result.success else "[red]No[/red]")
    table.add_row("Steps Taken", str(result.steps_taken))
    table.add_row("Duration", f"{result.duration:.2f}s")
    
    if result.error_message:
        table.add_row("Error", result.error_message)
        
    console.print(table)
    
    if result.log:
        console.print("
[bold]Journey Log:[/bold]")
        for entry in result.log:
            console.print(f"  - {entry}")

if __name__ == "__main__":
    main()
