[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub followers](https://img.shields.io/github/followers/dorktoast?label=dorktoast)![Bluesky followers](https://img.shields.io/bluesky/followers/dorktoast.gib.games?label=dorktoast.gib.games)![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UCKzyNJr9-1p55WJiYycgBjQ?label=@dorktoast)

# `whereproc`

A small, cross-platform command-line tool to locate the executable path of a running process.

It gives you:

-   PID lookup
-   Process-name matching (substring / exact / regex)    
-   Command-line matching    
-   JSON output
-   A quiet mode for scripting (`--quiet` → just print the process path)    

## Why?

The reason I made this is because I work on multiple platforms (Linux, macOS, Windows), and the question **“what executable is this process actually running?”** isn’t consistently answered across them. For example:

- Windows’ built-in tools don’t reliably show the resolved binary path.
- macOS hides app bundle paths behind layers of symlinks.
- On Linux, depending on the distribution or container environment, /proc/<pid>/exe may be masked or point to a launcher script instead of the binary.

`psutil` gives a single cross-platform API for exactly this one piece of information, which is why the tool uses it.

So the goal isn’t to replace ps, but to have a tiny, uniform CLI that works the same way on every OS and always returns the actual executable path, with optional matching modes and script-friendly output.

Useful for:

-   debugging PATH issues    
-   finding the real location of app bundles / snap packages    
-   scripting around PID or exe discovery    
-   process verification and automation

## Installation

### Linux and MacOS (Intel or Apple Silicon)

#### [pipx](https://github.com/pypa/pipx) (recommended)
```
pipx install whereproc
```

#### From source

```bash
git clone https://github.com/dorktoast/whereproc.git
cd whereproc
pipx install .
```
### Windows via PowerShell
**Via pipx:**
```powershell
# Install pipx if you don't already have it
python -m pip install --user pipx
python -m pipx ensurepath

# Close and reopen PowerShell, then:
pipx install whereproc
```

**If you prefer not to use pipx:**

```powershell
python -m pip install --user whereproc
```
Then make sure Python’s Scripts directory is on PATH:
```powershell
$env:PATH += ";$($env:USERPROFILE)\AppData\Roaming\Python\Python311\Scripts"
```

## Usage
### Basic substring match
```
whereproc firefox
```
```
PID    NAME     EXE
----------------------------------------------------------
75032  firefox  /snap/firefox/7355/usr/lib/firefox/firefox
```

### Quiet Mode (print only path)
Useful for scripts!
```
whereproc --quiet firefox
```
```
/snap/firefox/7355/usr/lib/firefox/firefox
```

### Exact Name match
```
whereproc --exact python3.12
```
### Regex name match
```
whereproc --regex "python(3\.\d+)?"
```
### Match against command line instead of process name
```
whereproc --cmd /snap/firefox
```
### Regex on command line
```
whereproc --cmd --regex "snap.*firefox"
```
### First-match output
When you don’t care about multiple processes.
```
whereproc --first firefox
```
### Full command line
```
whereproc --cmdline firefox
```
### JSON output
```
whereproc --json firefox
```
```json
[
  {
    "pid": 75032,
    "name": "firefox",
    "exe": "/snap/firefox/7355/usr/lib/firefox/firefox",
    "cmdline": [
      "/snap/firefox/7355/usr/lib/firefox/firefox",
      "--some-arg"
    ]
  }
]
```
### PID Search
If the query is an integer, it is treated as a PID.
```
whereproc 75032
```

### Return Codes
-   `0` → at least 1 match found
-   `1` → no match

## Requirements

-   Python ≥ 3.8
-   `psutil`
