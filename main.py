import os
import sys
import argparse
import time
import json
import csv
import subprocess
import statistics
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Output will be plain text. Install it with: pip install rich")

# --- Configuration & Constants ---

# Extensive Language Map
LANGUAGE_MAP = {
    # Code
    ".py": "Python", ".pyw": "Python", ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++", ".cc": "C++",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".rb": "Ruby", ".go": "Go", ".rs": "Rust", ".php": "PHP", ".cs": "C#",
    ".swift": "Swift", ".kt": "Kotlin", ".kts": "Kotlin", ".scala": "Scala", ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "Sass", ".sass": "Sass", ".less": "Less", ".sql": "SQL", ".sh": "Shell",
    ".bash": "Shell", ".zsh": "Shell", ".ps1": "PowerShell", ".bat": "Batch", ".cmd": "Batch",
    ".lua": "Lua", ".pl": "Perl", ".r": "R", ".dart": "Dart", ".elm": "Elm", ".clj": "Clojure",
    ".ex": "Elixir", ".exs": "Elixir", ".erl": "Erlang", ".hs": "Haskell", ".v": "Verilog/V",
    ".zig": "Zig", ".nim": "Nim", ".jl": "Julia", ".m": "Objective-C", ".mm": "Objective-C++",
    ".vue": "Vue", ".svelte": "Svelte", ".jsx": "JavaScript (React)", ".asm": "Assembly",
    ".dockerfile": "Dockerfile", "dockerfile": "Dockerfile", ".mk": "Makefile",
    
    # Config / Data
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML", ".xml": "XML",
    ".ini": "INI", ".csv": "CSV", ".md": "Markdown", ".txt": "Text", ".rst": "reStructuredText",
    ".gitignore": "Git Config", ".env": "Env Config"
}

# Binary Signatures
BINARY_SIGNATURES = [
    b"\x89PNG", b"GIF8", b"BM", b"\xFF\xD8\xFF", b"PK\x03\x04", b"%PDF",
    b"\x7FELF", b"MZ", b"\xCF\xFA\xED\xFE", b"\xCA\xFE\xBA\xBE",
]

# Excluded Directories (Default)
DEFAULT_EXCLUDES = {
    ".git", "node_modules", "build", "dist", "__pycache__", ".idea", ".vscode",
    "vendor", "bin", "obj", ".venv", "env", "venv", "target", ".mypy_cache"
}

# TODO Indicators
TODO_PATTERNS = ["TODO", "FIXME", "BUG", "HACK", "XXX", "NOTE"]

# --- Helper Functions ---

def is_binary(file_path: Path, sample_size=8192) -> bool:
    try:
        with file_path.open("rb") as f:
            header = f.read(sample_size)
            if not header: return False
            for signature in BINARY_SIGNATURES:
                if header.startswith(signature): return True
            if b"\x00" in header: return True
            
            text_chars = bytes(range(32, 127)) + b"\r\n\t\b"
            binary_chars = sum(1 for byte in header if byte not in text_chars)
            return binary_chars / len(header) > 0.3
    except (IOError, OSError):
        return True
    return False

def count_tokens_heuristic(text: str) -> int:
    """Approximate token count (1 token ~= 4 chars). Good enough for estimates."""
    return len(text) // 4

def get_git_info(target_dir: Path):
    """
    Retrieve basic git stats using subprocess.
    Returns: (is_git_repo, details_dict)
    """
    if not (target_dir / ".git").exists():
        return False, {}

    try:
        # Check if git is installed
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        info = {}
        
        # Total Commits
        result = subprocess.run(["git", "-C", str(target_dir), "rev-list", "--count", "HEAD"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            info["total_commits"] = int(result.stdout.strip())
            
        # Unique Contributors
        result = subprocess.run(["git", "-C", str(target_dir), "shortlog", "-s", "-n", "HEAD"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            contributors = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            info["contributors_count"] = len(contributors)
            info["top_contributors"] = contributors[:5] # Top 5
            
        return True, info
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, {}

# --- Analysis Logic ---

class ProjectAnalyzer:
    def __init__(self, root_dir: Path, exclude_dirs=None):
        self.root_dir = root_dir
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDES
        
        # Stats Storage
        self.stats_by_lang = defaultdict(lambda: {"files": 0, "lines": 0, "chars": 0, "tokens": 0})
        self.total_stats = {"files": 0, "lines": 0, "chars": 0, "tokens": 0, "binary_files": 0}
        self.todo_counts = Counter()
        self.files_list = [] # List of (path, lines, tokens, type) for ranking
        
    def analyze(self):
        start_time = time.time()
        
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip self
                if file_path.resolve() == Path(__file__).resolve():
                    continue
                    
                self._process_file(file_path)
                
        self.execution_time = time.time() - start_time
        
    def _process_file(self, file_path: Path):
        # 1. Determine Type
        ext = file_path.suffix.lower()
        lang = LANGUAGE_MAP.get(ext)
        
        if not lang:
            # Check if binary
            if is_binary(file_path):
                self.total_stats["binary_files"] += 1
                return 
            lang = "Other Text"
            
        # 2. Read & Count
        try:
            with file_path.open("r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            lines = content.count('\n') + (1 if content else 0)
            chars = len(content)
            tokens = count_tokens_heuristic(content)
            
            # 3. Scan TODOs
            for pattern in TODO_PATTERNS:
                self.todo_counts[pattern] += content.count(pattern)
                
            # 4. Update Stats
            self.stats_by_lang[lang]["files"] += 1
            self.stats_by_lang[lang]["lines"] += lines
            self.stats_by_lang[lang]["chars"] += chars
            self.stats_by_lang[lang]["tokens"] += tokens
            
            self.total_stats["files"] += 1
            self.total_stats["lines"] += lines
            self.total_stats["chars"] += chars
            self.total_stats["tokens"] += tokens
            
            self.files_list.append({
                "path": str(file_path.relative_to(self.root_dir)),
                "lines": lines,
                "tokens": tokens,
                "lang": lang
            })
            
        except Exception as e:
            # print(f"Error reading {file_path}: {e}")
            pass

    def get_top_files(self, key="lines", limit=5):
        return sorted(self.files_list, key=lambda x: x[key], reverse=True)[:limit]
    
    def export_json(self, output_path: Path):
        data = {
            "meta": {
                "analyzed_at": datetime.now().isoformat(),
                "root_dir": str(self.root_dir),
                "execution_time": self.execution_time
            },
            "totals": self.total_stats,
            "languages": self.stats_by_lang,
            "top_files": self.get_top_files(limit=10),
            "todos": self.todo_counts
        }
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
    def export_csv(self, output_path: Path):
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Language", "Files", "Lines", "Tokens", "Chars"])
            for lang, stats in self.stats_by_lang.items():
                writer.writerow([lang, stats["files"], stats["lines"], stats["tokens"], stats["chars"]])


# --- UI & Reporting ---

def print_rich_report(analyzer: ProjectAnalyzer, git_info: tuple):
    console = Console()
    
    # 1. Header
    title = f"Project Stats for: [bold cyan]{analyzer.root_dir.name}[/]"
    console.print(Panel(title, expand=False))
    
    # 2. Git Pulse
    is_git, git_data = git_info
    if is_git:
        git_table = Table(show_header=False, box=None)
        git_table.add_column("Key", style="yellow")
        git_table.add_column("Value", style="white")
        git_table.add_row("Total Commits", f"{git_data.get('total_commits', 'Unknown'):,}")
        git_table.add_row("Contributors", str(git_data.get('contributors_count', 0)))
        console.print(Panel(git_table, title="Git Pulse", border_style="green"))
    
    # 3. Overview Table
    ov_table = Table(title="Overview")
    ov_table.add_column("Metric", style="magenta")
    ov_table.add_column("Count", justify="right", style="cyan")
    
    ov_table.add_row("Total Files", f"{analyzer.total_stats['files']:,}")
    ov_table.add_row("Total Lines", f"{analyzer.total_stats['lines']:,}")
    ov_table.add_row("Estimated Tokens", f"{analyzer.total_stats['tokens']:,}")
    ov_table.add_row("Binary Files (Skipped)", str(analyzer.total_stats['binary_files']))
    console.print(ov_table)
    
    # 4. Language Breakdown
    lang_table = Table(title="Language Composition")
    lang_table.add_column("Language", style="green")
    lang_table.add_column("Files", justify="right")
    lang_table.add_column("Lines", justify="right")
    lang_table.add_column("Tokens (Est.)", justify="right")
    lang_table.add_column("% Lines", justify="right")
    
    total_lines = analyzer.total_stats['lines'] or 1
    
    sorted_langs = sorted(analyzer.stats_by_lang.items(), key=lambda x: x[1]['lines'], reverse=True)
    
    for lang, stats in sorted_langs:
        percentage = (stats['lines'] / total_lines) * 100
        lang_table.add_row(
            lang,
            f"{stats['files']:,}",
            f"{stats['lines']:,}",
            f"{stats['tokens']:,}",
            f"{percentage:.1f}%"
        )
    console.print(lang_table)
    
    # 5. Top Files & TODOs
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column()
    
    # Largest Files
    top_files_table = Table(title="Top 5 Largest Files", box=None)
    top_files_table.add_column("File", style="yellow", no_wrap=True)
    top_files_table.add_column("Lines", style="cyan", justify="right")
    for file in analyzer.get_top_files("lines"):
        top_files_table.add_row(file['path'], f"{file['lines']:,}")
        
    # TODOs
    todo_table = Table(title="Technical Debt Indicators", box=None)
    todo_table.add_column("Tag", style="red")
    todo_table.add_column("Count", style="white", justify="right")
    for tag, count in analyzer.todo_counts.most_common():
        todo_table.add_row(tag, str(count))
        
    grid.add_row(top_files_table, todo_table)
    console.print(Panel(grid, title="Deep Dive", border_style="blue"))


def print_plain_report(analyzer: ProjectAnalyzer, git_info: tuple):
    print(f"\n{'='*40}")
    print(f"Project Stats: {analyzer.root_dir.name}")
    print(f"{'='*40}")
    
    print(f"\nTotal Files: {analyzer.total_stats['files']:,}")
    print(f"Total Lines: {analyzer.total_stats['lines']:,}")
    print(f"Total Tokens: {analyzer.total_stats['tokens']:,}")
    
    print(f"\n--- Language Breakdown ---")
    sorted_langs = sorted(analyzer.stats_by_lang.items(), key=lambda x: x[1]['lines'], reverse=True)
    for lang, stats in sorted_langs:
        print(f"{lang:<20} | Files: {stats['files']:<5} | Lines: {stats['lines']:<8}")

    print(f"\n--- Top 5 Largest Files ---")
    for file in analyzer.get_top_files("lines"):
        print(f"{file['lines']:<6} : {file['path']}")
        
    print(f"\n--- TODOs ---")
    for tag, count in analyzer.todo_counts.most_common():
        print(f"{tag}: {count}")

# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Advanced Project Statistics & Health Analyzer")
    parser.add_argument("-d", "--directory", default=".", help="Target directory (default: current)")
    parser.add_argument("--json", help="Export to JSON file")
    parser.add_argument("--csv", help="Export to CSV file")
    parser.add_argument("--no-git", action="store_true", help="Skip Git analysis")
    
    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()
    
    if not target_dir.exists():
        print(f"Error: Directory {target_dir} not found.")
        sys.exit(1)
        
    # Run Analysis
    analyzer = ProjectAnalyzer(target_dir)
    
    if RICH_AVAILABLE:
        with Console().status(f"[bold green]Scanning {target_dir.name}...[/]") as status:
            analyzer.analyze()
            # Git Scan
            git_info = (False, {})
            if not args.no_git:
                status.update("[bold yellow]Fetching Git Info...[/]")
                git_info = get_git_info(target_dir)
    else:
        print(f"Scanning {target_dir.name}...")
        analyzer.analyze()
        git_info = get_git_info(target_dir) if not args.no_git else (False, {})

    # Display
    if RICH_AVAILABLE:
        print_rich_report(analyzer, git_info)
    else:
        print_plain_report(analyzer, git_info)
        
    # Export
    if args.json:
        analyzer.export_json(Path(args.json))
        print(f"\nJSON report saved to {args.json}")
        
    if args.csv:
        analyzer.export_csv(Path(args.csv))
        print(f"\nCSV report saved to {args.csv}")

if __name__ == "__main__":
    main()
