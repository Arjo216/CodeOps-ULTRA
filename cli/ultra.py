# cli/ultra.py
import typer
import requests
import os
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.prompt import Confirm

app = typer.Typer()
console = Console()

# Pointing to your local FastAPI server
API_BASE_URL = "http://127.0.0.1:8000"

# Map file extensions to our backend language keys
EXT_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".c": "c",
    ".cpp": "cpp",
    ".rs": "rust",
    ".go": "go",
    ".java": "java"
}

@app.command()
def review(filepath: str):
    """
    Reads a local file and sends it to CodeOps ULTRA for Polyglot Security Review.
    """
    if not os.path.exists(filepath):
        console.print(f"[bold red]❌ Error: File '{filepath}' not found.[/bold red]")
        raise typer.Abort()

    # Auto-detect language based on the file extension
    _, ext = os.path.splitext(filepath)
    language = EXT_MAP.get(ext.lower(), "auto-detect")

    # Read the file
    with open(filepath, "r") as f:
        code_content = f.read()

    console.print(f"\n[bold cyan]🚀 Sending {filepath} ({language.upper()}) to ULTRA Cognitive Core...[/bold cyan]")
    
    # ==========================================
    # 1. THE FAST GEAR (Static Analysis)
    # ==========================================
    try:
        response = requests.post(f"{API_BASE_URL}/api/v2/agent/review", json={"code": code_content, "language": language})
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            console.print(f"[bold red]❌ AI Error:[/bold red] {data['error']}")
            raise typer.Abort()
            
        ai_code = data["ai_analysis"]
        
        # Display the AI response with beautiful VS Code-style syntax highlighting in the terminal!
        console.print("\n[bold green]🛡️ ULTRA Verified Optimization Complete:[/bold green]")
        syntax_lang = language if language != "auto-detect" else "python"
        syntax = Syntax(ai_code, syntax_lang, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, border_style="green"))

    except Exception as e:
        console.print(f"[bold red]❌ Connection Error:[/bold red] Is your backend running? ({e})")
        raise typer.Abort()

    # ==========================================
    # 2. THE HYBRID BRIDGE (Dynamic Execution)
    # ==========================================
    console.print("\n")
    deploy = Confirm.ask(f"[bold yellow]⚠️ Deploy this {language.upper()} code to the Secure Docker Sandbox?[/bold yellow]")
    
    if deploy:
        console.print(f"[bold cyan]🐳 Spinning up Ephemeral {language.upper()} Container...[/bold cyan]")
        try:
            # We send the task AND the language to the LangGraph solver endpoint
            sandbox_res = requests.post(f"{API_BASE_URL}/api/solve", json={
                "task": f"Execute this exact code:\n\n{ai_code}",
                "language": language if language != "auto-detect" else "python"
            })
            sandbox_data = sandbox_res.json()
            
            console.print("\n[bold magenta]--- LIVE CONTAINER LOGS ---[/bold magenta]")
            for log in sandbox_data.get("logs", []):
                if "Error" in log or "Rejected" in log:
                    console.print(f"[red]{log}[/red]")
                else:
                    console.print(f"[dim]{log}[/dim]")
                    
            console.print(f"\n[bold green]✅ Execution Finished. Sandbox Wiped.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Execution Engine Failure:[/bold red] {e}")

if __name__ == "__main__":
    app()