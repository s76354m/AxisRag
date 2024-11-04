import click
import asyncio
from pathlib import Path
import logging
from rich.console import Console
from rich.progress import Progress
from rich.logging import RichHandler

from .AxisRAG import AxisRAG

console = Console()

@click.group()
def cli():
    """AxisRAG - PowerApps Analysis Tool"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console)]
    )

@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='reports', help='Output directory for reports')
@click.option('--model', '-m', default='both', type=click.Choice(['openai', 'anthropic', 'both']))
def analyze(pdf_path: str, output: str, model: str):
    """Analyze a PowerApps PDF document"""
    try:
        console.print(f"[bold green]Starting analysis of[/] {pdf_path}")
        
        # Initialize RAG system
        rag = AxisRAG({
            'output_dir': Path(output),
            'models': model
        })
        
        # Run analysis
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing document...", total=100)
            
            # Run async processing
            result = asyncio.run(rag.process_document(pdf_path))
            
            progress.update(task, completed=100)
            
        if result['status'] == 'success':
            console.print("[bold green]Analysis completed successfully![/]")
            console.print("\nReport locations:")
            for path_type, path in result['report_paths'].items():
                console.print(f"- {path_type}: {path}")
        else:
            console.print(f"[bold red]Error during analysis:[/] {result['error']}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

@cli.command()
@click.option('--query', '-q', required=True, help='Query to process')
def query(query: str):
    """Query the processed documents"""
    try:
        console.print(f"[bold green]Processing query:[/] {query}")
        
        rag = AxisRAG()
        result = asyncio.run(rag.query_system(query))
        
        if result['status'] == 'success':
            console.print("\n[bold]Responses:[/]")
            for model, response in result['responses'].items():
                console.print(f"\n[cyan]{model.upper()}:[/]")
                console.print(response)
                
            console.print("\n[bold]Evaluation:[/]")
            for model, scores in result['evaluation'].items():
                console.print(f"\n{model.upper()} Scores:")
                for metric, score in scores.items():
                    console.print(f"- {metric}: {score:.2f}")
        else:
            console.print(f"[bold red]Error processing query:[/] {result['error']}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    cli() 