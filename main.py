"""Main entry point for the RAG Ecosystem."""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional

from rag_ecosystem.agents.agentic_rag import AgenticRAG
from rag_ecosystem.components.indexing import DocumentIndexer
from rag_ecosystem.utils.logger import setup_logger

app = typer.Typer(help="RAG Ecosystem - Production-ready RAG system")
console = Console()
logger = setup_logger("main")


@app.command()
def index(
    path: str = typer.Argument(..., help="Path to file or directory to index"),
    pattern: str = typer.Option("*.txt", help="File pattern for directory indexing"),
    clear: bool = typer.Option(False, help="Clear existing collection before indexing"),
):
    """Index documents into the vector store."""
    console.print(f"[bold blue]Indexing documents from: {path}[/bold blue]")

    indexer = DocumentIndexer()

    if clear:
        console.print("[yellow]Clearing existing collection...[/yellow]")
        indexer.clear_collection()

    file_path = Path(path)

    try:
        if file_path.is_file():
            chunks = indexer.index_from_file(str(file_path))
            console.print(f"[green]✓ Indexed {chunks} chunks from file[/green]")
        elif file_path.is_dir():
            chunks = indexer.index_from_directory(str(file_path), pattern)
            console.print(f"[green]✓ Indexed {chunks} chunks from directory[/green]")
        else:
            console.print(f"[red]✗ Path not found: {path}[/red]")
            raise typer.Exit(1)

        stats = indexer.get_collection_stats()
        console.print(f"\n[bold]Collection Stats:[/bold]")
        console.print(f"  Total documents: {stats['total_documents']}")
        console.print(f"  Collection: {stats['collection_name']}")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def query(
    question: str = typer.Argument(..., help="Question to ask"),
    self_correct: bool = typer.Option(True, help="Enable self-correction"),
    show_docs: bool = typer.Option(False, help="Show retrieved documents"),
):
    """Query the RAG system."""
    console.print(f"[bold blue]Query:[/bold blue] {question}\n")

    rag = AgenticRAG()

    try:
        result = rag.query(question, enable_self_correction=self_correct)

        # Display answer
        console.print(f"[bold green]Answer:[/bold green]")
        console.print(result.get("answer", "No answer generated"))

        # Display metadata
        console.print(f"\n[bold]Metadata:[/bold]")
        console.print(f"  Status: {result.get('status')}")
        console.print(f"  Attempts: {result.get('attempts', 1)}")
        console.print(f"  Documents retrieved: {len(result.get('documents', []))}")

        # Display evaluation if available
        if result.get("evaluation"):
            eval_data = result["evaluation"]
            console.print(f"\n[bold]Evaluation:[/bold]")
            console.print(f"  Overall verdict: {eval_data['overall_verdict']}")

            if 'quality' in eval_data and 'scores' in eval_data['quality']:
                scores = eval_data['quality']['scores']
                console.print(f"  Quality scores:")
                console.print(f"    Relevance: {scores.get('relevance', 0):.1f}/10")
                console.print(f"    Faithfulness: {scores.get('faithfulness', 0):.1f}/10")
                console.print(f"    Completeness: {scores.get('completeness', 0):.1f}/10")

        # Display documents if requested
        if show_docs and result.get("documents"):
            console.print(f"\n[bold]Retrieved Documents:[/bold]")
            for i, doc in enumerate(result["documents"], 1):
                score = doc.metadata.get('reranking_score') or doc.metadata.get('retrieval_score', 0)
                console.print(f"\n  [{i}] Score: {score:.3f}")
                console.print(f"  {doc.page_content[:200]}...")

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        logger.exception("Error during query")
        raise typer.Exit(1)


@app.command()
def stats():
    """Show collection statistics."""
    indexer = DocumentIndexer()
    stats = indexer.get_collection_stats()

    table = Table(title="Vector Store Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Documents", str(stats['total_documents']))
    table.add_row("Collection Name", stats['collection_name'])
    table.add_row("Embedding Model", stats['embedding_model'])
    table.add_row("Vector Store Type", stats['vector_store_type'])

    console.print(table)


@app.command()
def clear():
    """Clear all documents from the vector store."""
    confirm = typer.confirm("Are you sure you want to clear all documents?")

    if confirm:
        indexer = DocumentIndexer()
        indexer.clear_collection()
        console.print("[green]✓ Collection cleared[/green]")
    else:
        console.print("[yellow]Operation cancelled[/yellow]")


@app.command()
def interactive():
    """Start an interactive query session."""
    console.print("[bold blue]RAG Ecosystem - Interactive Mode[/bold blue]")
    console.print("Type 'exit' or 'quit' to stop\n")

    rag = AgenticRAG()

    while True:
        try:
            question = typer.prompt("Your question")

            if question.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            result = rag.query(question)

            console.print(f"\n[bold green]Answer:[/bold green]")
            console.print(result.get("answer", "No answer generated"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]\n")


if __name__ == "__main__":
    app()
