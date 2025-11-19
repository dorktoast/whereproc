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

----------

## Why?

Because sometimes you just want a dead-simple way to answer: **“What executable is actually backing this process?”**

Useful for:

-   debugging PATH issues    
-   finding the real location of app bundles / snap packages    
-   scripting around PID or exe discovery    
-   process verification and automation

----------

## Installation

### pipx (recommended)
```
pipx install whereproc
```

### From source

```
git clone https://github.com/dorktoast/whereproc.git
cd whereproc
pipx install .
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
