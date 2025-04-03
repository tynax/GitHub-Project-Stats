<div align="center">

# Github Project Stats

A lightweight Python script to analyze and count files, lines, and characters in your GitHub projects.

</div>

## Features

- Quick statistics about your project's codebase
- Categorizes files by type (Code, Markup, Documentation, Scripts, Config)
- Works with just a drag-and-drop into your repo root
- Fast binary file detection to skip non-text files
- Excludes common directories like `.git`, `node_modules`, etc.
- Generates timestamped report files
- Can be run via command line or interactively

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## How to Use

### Simple Method (Drag & Drop)
1. Download the `project_stats_counter.py` script
2. Place it in the root directory of your project
3. Double-click to run (or run via command line)

### Command Line Method
```bash
python project_stats_counter.py [-dir PATH_TO_DIRECTORY]
```

If no directory is specified, it will analyze the current directory.

### Interactive Mode
When run without command line arguments, you'll get an interactive menu with options to:
1. Save statistics to a text file
2. Quit
3. Run the analysis again

## Example Output

```text
================================================================================
PROJECT STATISTICS SUMMARY
================================================================================

Markup Files:
  Files:      7
  Lines:      575
  Characters: 20,696

Other Text Files:
  Files:      3
  Lines:      184
  Characters: 4,213

================================================================================
TOTAL: 10 files, 759 lines, 24,909 characters
================================================================================
```

## Requirements

- Python 3.x
- No external dependencies

<div align="center">

## [Join my Discord server](https://discord.gg/2nHHHBWNDw)

</div>

## Supported File Types

<details>
<summary><b>📁 Code Files (100+ languages)</b></summary>

- Python (.py)
- JavaScript (.js) 
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- PHP (.php)
- Ruby (.rb)
- Go (.go)
- Rust (.rs)
- Swift (.swift)
- Kotlin (.kt, .kts)
- Scala (.scala)
- TypeScript (.ts, .tsx)
- JSX (.jsx)
- HTML (.html, .htm)
- CSS/Sass/Less (.css, .scss, .sass, .less)
- SQL (.sql)
- Shell scripts (.sh, .bash)
- Batch files (.bat, .cmd)
- PowerShell (.ps1)
- Lua (.lua)
- R (.r)
- Perl (.pl, .pm)
- Tcl (.tcl)
- AWK (.awk)
- sed (.sed)
- Dart (.dart)
- Groovy (.groovy)
- Visual Basic (.vb, .vbs)
- Assembly (.asm)
- Fortran (.f, .f90, .f95)
- MATLAB (.m)
- OCaml (.ml, .mli)
- Vue (.vue)
- Elm (.elm)
- Clojure (.clj, .cljs, .cljc)
- Elixir (.ex, .exs)
- Erlang (.erl, .hrl)
- Lisp (.lisp, .lsp)
- Haskell (.hs)
- PureScript (.purs)
- Ada (.ada)
- D (.d)
- Nim (.nim)
- Zig (.zig)
- Julia (.jl)
- Crystal (.cr)
- JSON5 (.json5)
- Haxe (.hx)
- Wren (.wren)
- P4 (.p4)
- Racket (.rkt)
- Idris (.idris)
- Pike (.pike)
- Lean (.lean)
- Verilog (.v)
- Agda (.agda)
- COBOL (.cob, .cpy)
- ABAP (.abap)
- RPG (.rpg)
- 4GL (.4gl)
- Chapel (.chpl)
- REXX (.rex)
- Omgrofl (.omgrofl)
</details>

<details>
<summary><b>📄 Markup & Data Files</b></summary>

- Markdown (.md)
- reStructuredText (.rst)
- Plain text (.txt)
- LaTeX (.tex, .latex, .bib)
- JSON (.json)
- YAML (.yaml, .yml)
- TOML (.toml)
- INI (.ini, .cfg, .conf)
- Properties (.properties)
- CSV/TSV (.csv, .tsv)
- XML (.xml, .xsl, .xsd, .xslt)
- XHTML (.xhtml)
- SVG (.svg)
- RSS (.rss)
- Atom (.atom)
</details>

<details>
<summary><b>📝 Documentation Files</b></summary>

- Word (.doc, .docx)
- PDF (.pdf)
- Rich Text (.rtf)
- OpenDocument (.odt, .fodt)
- StarOffice (.sxw)
- WordPerfect (.wpd)
- Texinfo (.texi)
- Manual pages (.me, .ms)
</details>

<details>
<summary><b>🛠️ Scripts & Build Files</b></summary>

- PowerShell (.ps1)
- CMD (.cmd)
- Batch (.bat)
- VBScript (.vbs)
- AppleScript (.applescript)
- AutoHotkey (.ahk)
- Korn Shell (.ksh)
- Zsh (.zsh)
- Fish (.fish)
- C Shell (.csh, .tcsh)
- Makefiles (.mak, .mk)
- Ninja (.ninja)
- Gentoo (.ebuild, .eclass)
- Arch Linux (.pkgbuild)
</details>

<details>
<summary><b>⚙️ Configuration Files</b></summary>

- Environment (.env, .venv)
- EditorConfig (.editorconfig)
- Git (.gitattributes, .gitignore, .gitmodules)
- Docker (.dockerfile)
- npm/yarn (.npmrc, .yarnrc)
- Babel (.babelrc)
- ESLint (.eslint)
- Prettier (.prettierrc)
- Stylelint (.stylelintrc)
- Conda (.condarc)
- Flake8 (.flake8)
- Pylint (.pylintrc)
- mypy (.mypy.ini)
- pydocstyle (.pydocstyle)
- PHP CS (.phpcs)
- PHPMD (.phpmd)
</details>

<details>
<summary><b>🚫 Excluded Directories</b></summary>

- .git
- node_modules
- build
- dist
- __pycache__
- .idea
- .vscode
- vendor
- bin
- obj
</details>

<details>
<summary><b>🔍 Binary File Detection</b></summary>

The script automatically skips files with these signatures:

- PNG
- GIF
- BMP
- JPEG
- ZIP
- PDF
- ELF
- Windows PE
- Mach-O
- Java class files

</details>

## Customization

You can modify these variables in the script:
- `TEXT_EXTENSIONS` - Add/remove file extensions
- `EXCLUDE_DIRS` - Add directories to exclude from analysis
- `BINARY_SIGNATURES` - Add binary file signatures to skip

## Contributing

Contributions are welcome! Please open an issue or pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.