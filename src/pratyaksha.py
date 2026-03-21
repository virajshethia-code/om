"""
pratyaksha.py -- The Perception Layer of the Darshana Architecture
===================================================================

Pratyaksha (direct perception) is the highest-confidence pramana in Nyaya
epistemology. This module implements multi-source perception for the Darshana
system, giving it actual sense organs (indriyas) instead of relying solely
on user text.

In Samkhya philosophy, there are:
  - 5 Jnanendriyas (knowledge senses) -- input channels
  - 5 Karmendriyas (action organs) -- output channels
  - Manas (mind) -- the router that coordinates them

This module maps those concepts to real software:

    Jnanendriyas (input):
        Chakshu  (eye)   -> FileReader          -- read files, parse code
        Shrotra  (ear)   -> WebListener         -- fetch URLs
        Tvak     (skin)  -> ShellSensor         -- execute safe shell commands
        Rasana   (tongue)-> APITaster           -- make HTTP API calls
        Ghrana   (nose)  -> EnvironmentSniffer  -- detect project structure

    Karmendriyas (output, stubs):
        Vak      (speech)    -> send messages
        Pani     (hands)     -> write files
        Pada     (feet)      -> navigate filesystem
        Payu     (elimination) -> delete/clean
        Upastha  (creation)  -> scaffold projects

    Manas (mind):
        PerceptionRouter -- decides which senses to activate for a query

Every piece of perceived data is tagged with:
    pramana   = pratyaksha (direct perception, highest confidence)
    indriya   = which sense organ gathered it
    timestamp = when it was perceived
    confidence = 1.0 for direct perception

Pure Python + stdlib only. No third-party dependencies.

Author: Harsh (with Claude as co-thinker)
License: MIT
"""

from __future__ import annotations

import datetime
import json
import mimetypes
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class IndriyaType(Enum):
    """The five Jnanendriyas (knowledge senses)."""
    CHAKSHU = "chakshu"     # eye -- file reading
    SHROTRA = "shrotra"     # ear -- web listening
    TVAK    = "tvak"        # skin -- shell/system touch
    RASANA  = "rasana"      # tongue -- API tasting
    GHRANA  = "ghrana"      # nose -- environment sniffing


class KarmendriyaType(Enum):
    """The five Karmendriyas (action organs) -- stubs for future."""
    VAK     = "vak"         # speech -- send messages
    PANI    = "pani"        # hands -- write files
    PADA    = "pada"        # feet -- navigate filesystem
    PAYU    = "payu"        # elimination -- delete/clean
    UPASTHA = "upastha"     # creation -- scaffold projects


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Perception:
    """
    A single unit of perceived data from an indriya.

    Every Perception is tagged as pramana=pratyaksha because it comes from
    direct observation, not inference (anumana) or testimony (shabda).

    Attributes:
        content: The perceived data (string, dict, or structured content).
        source: Which indriya gathered this data.
        pramana: Always 'pratyaksha' for direct perception.
        timestamp: ISO 8601 timestamp of when the data was perceived.
        confidence: 1.0 for direct perception (highest in Nyaya hierarchy).
        freshness_seconds: How many seconds ago this data was gathered.
        query: The original query/path/command that triggered perception.
        metadata: Additional context about the perception.
        error: If perception failed, the error message.
    """
    content: Any
    source: IndriyaType
    pramana: str = "pratyaksha"
    timestamp: str = ""
    confidence: float = 1.0
    freshness_seconds: float = 0.0
    query: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()

    @property
    def success(self) -> bool:
        """Whether this perception succeeded without error."""
        return self.error is None

    def to_dict(self) -> dict:
        """Serialize to a plain dict for JSON or logging."""
        return {
            "content": self.content if isinstance(self.content, (str, dict, list))
                       else str(self.content),
            "source": self.source.value,
            "pramana": self.pramana,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "freshness_seconds": round(self.freshness_seconds, 3),
            "query": self.query,
            "metadata": self.metadata,
            "error": self.error,
        }


@dataclass
class PerceptionBundle:
    """
    Combined perceptions from multiple indriyas for a single query.

    This is what Manas (the mind/router) produces after activating
    the relevant sense organs and gathering their results.

    Attributes:
        query: The original query that triggered perception.
        perceptions: List of individual Perception objects.
        timestamp: When the bundle was assembled.
        indriyas_activated: Which sense organs contributed.
        total_time_ms: Total time for all perceptions.
    """
    query: str
    perceptions: List[Perception] = field(default_factory=list)
    timestamp: str = ""
    indriyas_activated: List[str] = field(default_factory=list)
    total_time_ms: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()

    @property
    def successful(self) -> List[Perception]:
        """Return only successful perceptions."""
        return [p for p in self.perceptions if p.success]

    @property
    def failed(self) -> List[Perception]:
        """Return only failed perceptions."""
        return [p for p in self.perceptions if not p.success]

    def as_context(self) -> str:
        """
        Format the bundle as a context string suitable for feeding
        into the Darshana LLM pipeline.

        This bridges Pratyaksha (perception) to the reasoning layers.
        """
        sections = []
        for p in self.successful:
            indriya = p.source.value.upper()
            content = p.content if isinstance(p.content, str) else json.dumps(
                p.content, indent=2, default=str
            )
            sections.append(
                f"[{indriya} | {p.pramana} | {p.timestamp}]\n"
                f"Query: {p.query}\n"
                f"{content}"
            )
        if not sections:
            return "(No successful perceptions gathered.)"
        return "\n\n---\n\n".join(sections)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "perceptions": [p.to_dict() for p in self.perceptions],
            "timestamp": self.timestamp,
            "indriyas_activated": self.indriyas_activated,
            "total_time_ms": round(self.total_time_ms, 1),
            "success_count": len(self.successful),
            "failure_count": len(self.failed),
        }


# ===========================================================================
# JNANENDRIYAS (Knowledge Senses) -- Input Channels
# ===========================================================================

class Indriya(ABC):
    """
    Base class for all sense organs (indriyas).

    Each Indriya can:
      - perceive(query) -> Perception -- gather data from its source
      - available() -> bool -- check if this sense organ is operational

    Subclasses implement the five Jnanendriyas from Samkhya philosophy.
    """

    indriya_type: IndriyaType
    name: str
    sanskrit_name: str
    description: str

    @abstractmethod
    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Gather data from this sense organ.

        Args:
            query: What to perceive (file path, URL, command, etc.)
            **kwargs: Sense-specific parameters.

        Returns:
            A Perception object tagged with pramana=pratyaksha.
        """
        ...

    @abstractmethod
    def available(self) -> bool:
        """Check if this sense organ is operational and configured."""
        ...

    def _make_perception(
        self,
        content: Any,
        query: str,
        start_time: float,
        metadata: Optional[Dict] = None,
        error: Optional[str] = None,
    ) -> Perception:
        """Helper to construct a Perception with timing."""
        elapsed = time.monotonic() - start_time
        return Perception(
            content=content,
            source=self.indriya_type,
            pramana="pratyaksha",
            confidence=1.0 if error is None else 0.0,
            freshness_seconds=elapsed,
            query=query,
            metadata=metadata or {},
            error=error,
        )


# ---------------------------------------------------------------------------
# 1. Chakshu (Eye) -- FileReader
# ---------------------------------------------------------------------------

class Chakshu(Indriya):
    """
    The eye of the system -- reads and perceives files.

    Reads local files, parses code structure (functions, classes, imports),
    and extracts metadata. Like the physical eye, it perceives form and
    structure from the written world.

    Supported:
        - Text files (.py, .js, .ts, .json, .yaml, .toml, .md, .txt, etc.)
        - Binary file metadata (size, type, modification time)
        - Directory listings
    """

    indriya_type = IndriyaType.CHAKSHU
    name = "FileReader"
    sanskrit_name = "Chakshu"
    description = "Reads files and perceives code structure"

    # Maximum file size to read in full (1 MB)
    MAX_READ_BYTES = 1_048_576

    # Text file extensions we will read content from
    TEXT_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
        ".toml", ".md", ".txt", ".rst", ".csv", ".html", ".css", ".scss",
        ".sh", ".bash", ".zsh", ".fish", ".cfg", ".ini", ".conf", ".env",
        ".sql", ".r", ".rb", ".go", ".rs", ".java", ".c", ".cpp", ".h",
        ".hpp", ".swift", ".kt", ".xml", ".svg", ".lua", ".pl", ".ex",
        ".exs", ".clj", ".hs", ".ml", ".vim", ".el", ".dockerfile",
        ".gitignore", ".editorconfig",
    }

    def available(self) -> bool:
        return True  # Files are always available on a local system

    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Read a file or directory and return structured content.

        Args:
            query: File or directory path.
            **kwargs:
                max_lines: Maximum lines to read (default: all).
                parse_structure: If True, extract code structure for .py files.
        """
        start = time.monotonic()
        path = Path(query).expanduser().resolve()

        if not path.exists():
            return self._make_perception(
                None, query, start, error=f"Path does not exist: {path}"
            )

        # Directory perception
        if path.is_dir():
            return self._perceive_directory(path, query, start)

        # File perception
        return self._perceive_file(
            path, query, start,
            max_lines=kwargs.get("max_lines"),
            parse_structure=kwargs.get("parse_structure", True),
        )

    def _perceive_file(
        self,
        path: Path,
        query: str,
        start: float,
        max_lines: Optional[int] = None,
        parse_structure: bool = True,
    ) -> Perception:
        """Read and analyze a single file."""
        stat = path.stat()
        metadata = {
            "path": str(path),
            "name": path.name,
            "suffix": path.suffix,
            "size_bytes": stat.st_size,
            "modified": datetime.datetime.fromtimestamp(
                stat.st_mtime, tz=datetime.timezone.utc
            ).isoformat(),
            "is_text": self._is_text_file(path),
        }

        # Check if we should read content
        if not self._is_text_file(path):
            mime, _ = mimetypes.guess_type(str(path))
            metadata["mime_type"] = mime or "unknown"
            return self._make_perception(
                f"[Binary file: {path.name}, {stat.st_size} bytes, type: {mime}]",
                query, start, metadata=metadata,
            )

        if stat.st_size > self.MAX_READ_BYTES:
            return self._make_perception(
                f"[File too large: {path.name}, {stat.st_size} bytes, "
                f"limit: {self.MAX_READ_BYTES}]",
                query, start, metadata=metadata,
                error=f"File exceeds {self.MAX_READ_BYTES} byte limit",
            )

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError) as e:
            return self._make_perception(
                None, query, start, metadata=metadata,
                error=f"Cannot read file: {e}",
            )

        if max_lines is not None:
            lines = text.splitlines(keepends=True)
            text = "".join(lines[:max_lines])
            metadata["truncated_at_line"] = max_lines

        metadata["line_count"] = text.count("\n") + (1 if text and not text.endswith("\n") else 0)

        # Parse structure for Python files
        if parse_structure and path.suffix == ".py":
            structure = self._parse_python_structure(text)
            metadata["structure"] = structure

        return self._make_perception(text, query, start, metadata=metadata)

    def _perceive_directory(
        self, path: Path, query: str, start: float
    ) -> Perception:
        """List directory contents with basic metadata."""
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError as e:
            return self._make_perception(
                None, query, start, error=f"Cannot read directory: {e}"
            )

        listing = []
        for entry in entries[:200]:  # Cap at 200 entries
            kind = "dir" if entry.is_dir() else "file"
            size = ""
            if entry.is_file():
                try:
                    size = f" ({entry.stat().st_size} bytes)"
                except OSError:
                    size = ""
            listing.append(f"  [{kind}] {entry.name}{size}")

        content = f"Directory: {path}\n" + "\n".join(listing)
        metadata = {
            "path": str(path),
            "entry_count": len(entries),
            "shown": min(len(entries), 200),
        }
        return self._make_perception(content, query, start, metadata=metadata)

    def _is_text_file(self, path: Path) -> bool:
        """Check if a file is likely a text file by extension."""
        suffix = path.suffix.lower()
        if suffix in self.TEXT_EXTENSIONS:
            return True
        # Files without extensions that are commonly text
        if path.name.lower() in {
            "makefile", "dockerfile", "procfile", "gemfile",
            "rakefile", "vagrantfile", "license", "readme",
            "changelog", "authors", "contributors",
        }:
            return True
        return False

    @staticmethod
    def _parse_python_structure(source: str) -> Dict[str, Any]:
        """
        Extract structural elements from Python source code.

        Uses regex -- no AST parsing to keep it stdlib-light and robust
        against syntax errors in the target file.
        """
        structure: Dict[str, Any] = {
            "imports": [],
            "classes": [],
            "functions": [],
            "global_vars": [],
        }

        for line in source.splitlines():
            stripped = line.strip()

            # Imports
            if stripped.startswith("import ") or stripped.startswith("from "):
                structure["imports"].append(stripped)

            # Class definitions
            match = re.match(r"^class\s+(\w+)(?:\((.*?)\))?:", stripped)
            if match:
                structure["classes"].append({
                    "name": match.group(1),
                    "bases": match.group(2) or "",
                })

            # Function definitions (top-level and methods)
            match = re.match(r"^(    )?def\s+(\w+)\s*\((.*?)\)", stripped)
            if match:
                indent = match.group(1)
                entry = {
                    "name": match.group(2),
                    "params": match.group(3),
                    "is_method": indent is not None,
                }
                structure["functions"].append(entry)

            # Top-level assignments (potential constants/globals)
            if not stripped.startswith((" ", "\t", "#", "def ", "class ", "import ", "from ")):
                match = re.match(r"^([A-Z_][A-Z_0-9]*)\s*=", stripped)
                if match:
                    structure["global_vars"].append(match.group(1))

        return structure


# ---------------------------------------------------------------------------
# 2. Shrotra (Ear) -- WebListener
# ---------------------------------------------------------------------------

class Shrotra(Indriya):
    """
    The ear of the system -- listens to the web.

    Fetches URLs and reads web content. Like the physical ear, it receives
    information broadcast from distant sources.

    Uses urllib from stdlib only -- no requests, no httpx.
    """

    indriya_type = IndriyaType.SHROTRA
    name = "WebListener"
    sanskrit_name = "Shrotra"
    description = "Fetches URLs and reads web content"

    # Maximum response size (2 MB)
    MAX_RESPONSE_BYTES = 2_097_152
    # Timeout in seconds
    DEFAULT_TIMEOUT = 15

    def available(self) -> bool:
        """Web is available if we can resolve a basic DNS lookup."""
        try:
            urllib.request.urlopen(
                "https://httpbin.org/status/200", timeout=5
            )
            return True
        except Exception:
            return False

    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Fetch a URL and return its content.

        Args:
            query: The URL to fetch.
            **kwargs:
                timeout: Request timeout in seconds.
                headers: Additional headers dict.
                strip_html: If True, attempt to strip HTML tags (default True).
        """
        start = time.monotonic()
        timeout = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        strip_html = kwargs.get("strip_html", True)

        # Basic URL validation
        if not query.startswith(("http://", "https://")):
            return self._make_perception(
                None, query, start,
                error="URL must start with http:// or https://",
            )

        try:
            req = urllib.request.Request(
                query,
                headers={
                    "User-Agent": "Darshana-Pratyaksha/0.1 (perception layer)",
                    **(kwargs.get("headers") or {}),
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                raw = response.read(self.MAX_RESPONSE_BYTES)

                # Determine encoding
                charset = "utf-8"
                if "charset=" in content_type:
                    charset = content_type.split("charset=")[-1].split(";")[0].strip()

                text = raw.decode(charset, errors="replace")

                metadata = {
                    "url": query,
                    "status": response.status,
                    "content_type": content_type,
                    "content_length": len(raw),
                    "headers": dict(response.headers),
                }

                # Strip HTML if requested and content is HTML
                if strip_html and "html" in content_type.lower():
                    text = self._strip_html(text)
                    metadata["html_stripped"] = True

                return self._make_perception(
                    text, query, start, metadata=metadata
                )

        except urllib.error.HTTPError as e:
            return self._make_perception(
                None, query, start,
                metadata={"status": e.code, "url": query},
                error=f"HTTP {e.code}: {e.reason}",
            )
        except urllib.error.URLError as e:
            return self._make_perception(
                None, query, start,
                error=f"URL error: {e.reason}",
            )
        except Exception as e:
            return self._make_perception(
                None, query, start,
                error=f"Fetch failed: {type(e).__name__}: {e}",
            )

    @staticmethod
    def _strip_html(html: str) -> str:
        """
        Rough HTML stripping -- extract readable text from HTML.
        Not a full parser, but sufficient for perception purposes.
        """
        # Remove script and style blocks
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode common entities
        for entity, char in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                             ("&nbsp;", " "), ("&quot;", '"'), ("&#39;", "'")]:
            text = text.replace(entity, char)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Restore some structure with line breaks at sentence boundaries
        text = re.sub(r"([.!?])\s+", r"\1\n", text)
        return text


# ---------------------------------------------------------------------------
# 3. Tvak (Skin/Touch) -- ShellSensor
# ---------------------------------------------------------------------------

class Tvak(Indriya):
    """
    The skin of the system -- touches the OS through shell commands.

    Executes safe shell commands and returns their output. Like touch,
    this sense interacts directly with the environment.

    SAFETY: Maintains an allowlist of safe command prefixes. Refuses
    anything that could modify the system (rm, sudo, kill, etc.).
    """

    indriya_type = IndriyaType.TVAK
    name = "ShellSensor"
    sanskrit_name = "Tvak"
    description = "Executes safe shell commands and reads system state"

    # Commands that are SAFE to execute (read-only / informational)
    SAFE_PREFIXES = {
        "ls", "cat", "head", "tail", "wc", "file", "stat",
        "find", "which", "where", "type", "echo",
        "pwd", "whoami", "hostname", "uname", "date",
        "git status", "git log", "git branch", "git diff", "git show",
        "git remote", "git tag", "git rev-parse", "git describe",
        "python --version", "python3 --version", "pip list", "pip3 list",
        "pip show", "pip3 show",
        "node --version", "npm --version", "npm list", "npm ls",
        "env", "printenv",
        "df", "du", "free", "uptime", "top -l 1", "ps aux",
        "sw_vers", "system_profiler",  # macOS
        "grep", "rg", "ag",  # search tools
        "tree",
        "curl --head", "curl -I",  # HEAD requests only
    }

    # Commands that are NEVER allowed
    BLOCKED_PATTERNS = {
        "rm ", "rm\t", "rmdir", "sudo", "su ",
        "chmod", "chown", "chgrp",
        "kill", "killall", "pkill",
        "mkfs", "dd ", "format",
        "shutdown", "reboot", "halt",
        "> ", ">> ",  # output redirection (could overwrite files)
        "mv ", "cp ",  # file operations
        "pip install", "pip3 install", "npm install",  # package installs
        "curl -X POST", "curl -X PUT", "curl -X DELETE",  # mutating HTTP
        "wget ",
        "eval ", "exec ",
        "&&", "||", ";",  # command chaining (could bypass allowlist)
        "|",  # pipes (could chain to dangerous commands)
        "`",  # command substitution
        "$(",  # command substitution
    }

    # Timeout for shell commands (seconds)
    DEFAULT_TIMEOUT = 10

    def available(self) -> bool:
        return True  # Shell is always available

    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Execute a safe shell command and return its output.

        Args:
            query: The shell command to execute.
            **kwargs:
                cwd: Working directory for the command.
                timeout: Command timeout in seconds.
        """
        start = time.monotonic()
        timeout = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        cwd = kwargs.get("cwd")

        # Safety check
        safety_result = self._check_safety(query)
        if safety_result is not None:
            return self._make_perception(
                None, query, start,
                error=f"BLOCKED: {safety_result}",
                metadata={"blocked": True, "reason": safety_result},
            )

        try:
            result = subprocess.run(
                query,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            content = result.stdout
            metadata = {
                "command": query,
                "return_code": result.returncode,
                "cwd": cwd or os.getcwd(),
            }

            if result.stderr:
                metadata["stderr"] = result.stderr

            if result.returncode != 0:
                content = content or result.stderr
                metadata["success"] = False
            else:
                metadata["success"] = True

            return self._make_perception(
                content, query, start, metadata=metadata,
            )

        except subprocess.TimeoutExpired:
            return self._make_perception(
                None, query, start,
                error=f"Command timed out after {timeout}s",
            )
        except Exception as e:
            return self._make_perception(
                None, query, start,
                error=f"Shell error: {type(e).__name__}: {e}",
            )

    def _check_safety(self, command: str) -> Optional[str]:
        """
        Check if a command is safe to execute.

        Returns None if safe, or a string explaining why it was blocked.
        """
        cmd = command.strip()

        # Check blocked patterns first (higher priority)
        for blocked in self.BLOCKED_PATTERNS:
            if blocked in cmd:
                return (
                    f"Command contains blocked pattern '{blocked.strip()}'. "
                    f"Tvak (ShellSensor) only executes read-only commands."
                )

        # Check if the command starts with an allowed prefix
        cmd_lower = cmd.lower()
        for safe in self.SAFE_PREFIXES:
            if cmd_lower.startswith(safe):
                return None  # Safe

        return (
            f"Command '{cmd.split()[0]}' is not in the safe command allowlist. "
            f"Tvak (ShellSensor) only executes read-only informational commands. "
            f"Allowed: {', '.join(sorted(self.SAFE_PREFIXES)[:15])}..."
        )


# ---------------------------------------------------------------------------
# 4. Rasana (Tongue/Taste) -- APITaster
# ---------------------------------------------------------------------------

class Rasana(Indriya):
    """
    The tongue of the system -- tastes API responses.

    Makes HTTP API calls and returns structured JSON data. Like the tongue
    distinguishes flavors, this sense parses structured data from APIs.

    Supports configurable base URLs and authentication headers.
    """

    indriya_type = IndriyaType.RASANA
    name = "APITaster"
    sanskrit_name = "Rasana"
    description = "Makes HTTP API calls and parses JSON responses"

    DEFAULT_TIMEOUT = 15

    def __init__(
        self,
        base_urls: Optional[Dict[str, str]] = None,
        auth_headers: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            base_urls: Named base URLs, e.g. {"github": "https://api.github.com"}.
            auth_headers: Default auth headers applied to all requests.
        """
        self.base_urls = base_urls or {}
        self.auth_headers = auth_headers or {}

    def available(self) -> bool:
        return True  # API access is always technically available

    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Make an HTTP API call and return the parsed response.

        Args:
            query: The URL or endpoint to call.
                   If it starts with a name in base_urls (e.g., "github:/repos/..."),
                   the base URL is prepended.
            **kwargs:
                method: HTTP method (default GET). Only GET and HEAD are allowed.
                headers: Additional request headers.
                timeout: Request timeout in seconds.
        """
        start = time.monotonic()
        method = kwargs.get("method", "GET").upper()
        extra_headers = kwargs.get("headers") or {}
        timeout = kwargs.get("timeout", self.DEFAULT_TIMEOUT)

        # Safety: only allow safe HTTP methods
        if method not in ("GET", "HEAD", "OPTIONS"):
            return self._make_perception(
                None, query, start,
                error=f"Method {method} not allowed. Rasana only tastes "
                      f"(GET/HEAD/OPTIONS), it does not write.",
            )

        # Resolve base URL aliases
        url = self._resolve_url(query)
        if url is None:
            return self._make_perception(
                None, query, start,
                error=f"Could not resolve URL from: {query}",
            )

        # Merge headers
        headers = {
            "User-Agent": "Darshana-Pratyaksha/0.1",
            "Accept": "application/json",
        }
        headers.update(self.auth_headers)
        headers.update(extra_headers)

        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read(2_097_152)  # 2 MB limit
                content_type = response.headers.get("Content-Type", "")

                metadata = {
                    "url": url,
                    "method": method,
                    "status": response.status,
                    "content_type": content_type,
                    "content_length": len(raw),
                }

                # Try to parse as JSON
                text = raw.decode("utf-8", errors="replace")
                if "json" in content_type.lower():
                    try:
                        parsed = json.loads(text)
                        metadata["parsed_as"] = "json"
                        return self._make_perception(
                            parsed, query, start, metadata=metadata
                        )
                    except json.JSONDecodeError:
                        metadata["parsed_as"] = "text (json decode failed)"

                return self._make_perception(
                    text, query, start, metadata=metadata
                )

        except urllib.error.HTTPError as e:
            return self._make_perception(
                None, query, start,
                metadata={"status": e.code, "url": url},
                error=f"HTTP {e.code}: {e.reason}",
            )
        except urllib.error.URLError as e:
            return self._make_perception(
                None, query, start,
                error=f"URL error: {e.reason}",
            )
        except Exception as e:
            return self._make_perception(
                None, query, start,
                error=f"API call failed: {type(e).__name__}: {e}",
            )

    def _resolve_url(self, query: str) -> Optional[str]:
        """Resolve a query to a full URL, using base_urls if applicable."""
        # Already a full URL
        if query.startswith(("http://", "https://")):
            return query

        # Check for alias:path pattern
        if ":" in query:
            alias, path = query.split(":", 1)
            if alias in self.base_urls:
                base = self.base_urls[alias].rstrip("/")
                return f"{base}/{path.lstrip('/')}"

        return None

    def register_api(self, name: str, base_url: str, auth: Optional[str] = None):
        """Register a named API base URL with optional auth token."""
        self.base_urls[name] = base_url
        if auth:
            self.auth_headers[f"Authorization-{name}"] = auth


# ---------------------------------------------------------------------------
# 5. Ghrana (Nose/Smell) -- EnvironmentSniffer
# ---------------------------------------------------------------------------

class Ghrana(Indriya):
    """
    The nose of the system -- smells the environment.

    Detects project type, language, framework, and structure by sniffing
    for marker files. Like the nose detects subtle chemical signatures,
    this sense reads the fingerprints of a codebase.

    Detects:
        - Programming languages (by file extensions)
        - Frameworks (by config files: package.json, pyproject.toml, etc.)
        - Version control (git status)
        - Container/deployment (Dockerfile, docker-compose.yml)
        - Documentation patterns
        - Dependency information
    """

    indriya_type = IndriyaType.GHRANA
    name = "EnvironmentSniffer"
    sanskrit_name = "Ghrana"
    description = "Detects project type, language, and structure"

    # Marker files and what they indicate
    MARKERS = {
        # Python
        "pyproject.toml":       {"language": "python", "tool": "pyproject"},
        "setup.py":             {"language": "python", "tool": "setuptools"},
        "setup.cfg":            {"language": "python", "tool": "setuptools"},
        "requirements.txt":     {"language": "python", "tool": "pip"},
        "Pipfile":              {"language": "python", "tool": "pipenv"},
        "poetry.lock":          {"language": "python", "tool": "poetry"},
        "tox.ini":              {"language": "python", "tool": "tox"},
        "pytest.ini":           {"language": "python", "framework": "pytest"},
        ".flake8":              {"language": "python", "tool": "flake8"},
        "mypy.ini":             {"language": "python", "tool": "mypy"},

        # JavaScript / TypeScript
        "package.json":         {"language": "javascript", "tool": "npm"},
        "package-lock.json":    {"language": "javascript", "tool": "npm"},
        "yarn.lock":            {"language": "javascript", "tool": "yarn"},
        "pnpm-lock.yaml":      {"language": "javascript", "tool": "pnpm"},
        "bun.lockb":            {"language": "javascript", "tool": "bun"},
        "tsconfig.json":        {"language": "typescript"},
        "next.config.js":       {"language": "javascript", "framework": "nextjs"},
        "next.config.mjs":      {"language": "javascript", "framework": "nextjs"},
        "next.config.ts":       {"language": "typescript", "framework": "nextjs"},
        "nuxt.config.ts":       {"language": "typescript", "framework": "nuxt"},
        "vite.config.ts":       {"language": "typescript", "tool": "vite"},
        "vite.config.js":       {"language": "javascript", "tool": "vite"},
        "webpack.config.js":    {"language": "javascript", "tool": "webpack"},
        "tailwind.config.js":   {"language": "javascript", "tool": "tailwind"},
        "tailwind.config.ts":   {"language": "typescript", "tool": "tailwind"},
        "components.json":      {"tool": "shadcn-ui"},

        # Rust
        "Cargo.toml":           {"language": "rust", "tool": "cargo"},
        "Cargo.lock":           {"language": "rust", "tool": "cargo"},

        # Go
        "go.mod":               {"language": "go", "tool": "go-modules"},
        "go.sum":               {"language": "go", "tool": "go-modules"},

        # Ruby
        "Gemfile":              {"language": "ruby", "tool": "bundler"},
        "Gemfile.lock":         {"language": "ruby", "tool": "bundler"},
        "Rakefile":             {"language": "ruby"},

        # Java / JVM
        "pom.xml":              {"language": "java", "tool": "maven"},
        "build.gradle":         {"language": "java", "tool": "gradle"},
        "build.gradle.kts":     {"language": "kotlin", "tool": "gradle"},

        # Infrastructure
        "Dockerfile":           {"infra": "docker"},
        "docker-compose.yml":   {"infra": "docker-compose"},
        "docker-compose.yaml":  {"infra": "docker-compose"},
        ".dockerignore":        {"infra": "docker"},
        "Makefile":             {"tool": "make"},
        "Procfile":             {"infra": "heroku"},
        "fly.toml":             {"infra": "fly.io"},
        "vercel.json":          {"infra": "vercel"},
        "netlify.toml":         {"infra": "netlify"},
        "render.yaml":          {"infra": "render"},

        # Documentation
        "README.md":            {"docs": "readme"},
        "CHANGELOG.md":         {"docs": "changelog"},
        "LICENSE":              {"docs": "license"},
        "CLAUDE.md":            {"tool": "claude-code"},
        "THESIS.md":            {"docs": "thesis"},

        # Config
        ".env":                 {"config": "env-vars"},
        ".env.example":         {"config": "env-vars"},
        ".gitignore":           {"vcs": "git"},
        ".git":                 {"vcs": "git"},
        ".editorconfig":        {"tool": "editorconfig"},

        # Frappe / ERPNext
        "hooks.py":             {"framework": "frappe"},
    }

    def available(self) -> bool:
        return True

    def perceive(self, query: str, **kwargs) -> Perception:
        """
        Sniff a directory and detect its project structure.

        Args:
            query: Directory path to analyze.
            **kwargs:
                depth: How deep to scan for files (default 2).
                include_git: Whether to include git status (default True).
        """
        start = time.monotonic()
        path = Path(query).expanduser().resolve()

        if not path.exists():
            return self._make_perception(
                None, query, start,
                error=f"Directory does not exist: {path}",
            )

        if not path.is_dir():
            return self._make_perception(
                None, query, start,
                error=f"Not a directory: {path}",
            )

        depth = kwargs.get("depth", 2)
        include_git = kwargs.get("include_git", True)

        scent: Dict[str, Any] = {
            "path": str(path),
            "name": path.name,
            "markers_found": {},
            "languages": set(),
            "frameworks": set(),
            "tools": set(),
            "infra": set(),
            "vcs": set(),
        }

        # Sniff marker files
        for marker, signals in self.MARKERS.items():
            marker_path = path / marker
            if marker_path.exists():
                scent["markers_found"][marker] = signals
                for key, value in signals.items():
                    if key in scent and isinstance(scent[key], set):
                        scent[key].add(value)

        # Count files by extension
        extension_counts = self._count_extensions(path, depth)
        scent["file_extensions"] = extension_counts

        # Detect primary language from file extensions
        lang_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".rs": "rust", ".go": "go", ".rb": "ruby", ".java": "java",
            ".c": "c", ".cpp": "c++", ".swift": "swift", ".kt": "kotlin",
        }
        for ext, lang in lang_map.items():
            if ext in extension_counts and extension_counts[ext] > 0:
                scent["languages"].add(lang)

        # Git status if available
        if include_git and (path / ".git").exists():
            git_info = self._sniff_git(path)
            scent["git"] = git_info

        # Read key config files for more detail
        scent["configs"] = self._sniff_configs(path)

        # Convert sets to sorted lists for serialization
        for key in ("languages", "frameworks", "tools", "infra", "vcs"):
            scent[key] = sorted(scent[key])

        # Generate a summary
        summary = self._summarize(scent)
        scent["summary"] = summary

        return self._make_perception(
            scent, query, start,
            metadata={"path": str(path), "marker_count": len(scent["markers_found"])},
        )

    def _count_extensions(self, path: Path, max_depth: int) -> Dict[str, int]:
        """Count file extensions up to max_depth levels deep."""
        counts: Dict[str, int] = {}

        def _walk(p: Path, depth: int):
            if depth > max_depth:
                return
            try:
                for entry in p.iterdir():
                    if entry.name.startswith(".") and entry.is_dir():
                        continue  # Skip hidden directories
                    if entry.is_file():
                        ext = entry.suffix.lower()
                        if ext:
                            counts[ext] = counts.get(ext, 0) + 1
                    elif entry.is_dir():
                        _walk(entry, depth + 1)
            except PermissionError:
                pass

        _walk(path, 0)
        # Return top 20 by count
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_counts[:20])

    def _sniff_git(self, path: Path) -> Dict[str, Any]:
        """Sniff git information from a repository."""
        info: Dict[str, Any] = {}
        try:
            # Current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=str(path), timeout=5,
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()

            # Status summary
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=str(path), timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().splitlines()
                info["dirty_files"] = len(lines)
                info["clean"] = len(lines) == 0

            # Last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%h %s"],
                capture_output=True, text=True, cwd=str(path), timeout=5,
            )
            if result.returncode == 0:
                info["last_commit"] = result.stdout.strip()

            # Remote
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True, text=True, cwd=str(path), timeout=5,
            )
            if result.returncode == 0:
                info["remotes"] = result.stdout.strip()

        except (subprocess.TimeoutExpired, Exception):
            info["error"] = "Could not read git info"

        return info

    def _sniff_configs(self, path: Path) -> Dict[str, Any]:
        """Read key configuration files for additional signals."""
        configs: Dict[str, Any] = {}

        # package.json
        pkg_json = path / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                configs["package_json"] = {
                    "name": data.get("name"),
                    "version": data.get("version"),
                    "scripts": list(data.get("scripts", {}).keys()),
                    "dependencies": list(data.get("dependencies", {}).keys())[:20],
                    "devDependencies": list(data.get("devDependencies", {}).keys())[:20],
                }
            except (json.JSONDecodeError, OSError):
                pass

        # pyproject.toml (basic parsing without toml library)
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            try:
                text = pyproject.read_text(encoding="utf-8")
                configs["pyproject_toml"] = {
                    "exists": True,
                    "has_poetry": "[tool.poetry]" in text,
                    "has_setuptools": "[build-system]" in text,
                    "has_pytest": "[tool.pytest" in text,
                    "has_ruff": "[tool.ruff" in text,
                    "has_mypy": "[tool.mypy" in text,
                }
            except OSError:
                pass

        # requirements.txt
        req_txt = path / "requirements.txt"
        if req_txt.exists():
            try:
                lines = req_txt.read_text(encoding="utf-8").strip().splitlines()
                deps = [
                    l.strip().split("==")[0].split(">=")[0].split("<=")[0]
                    for l in lines
                    if l.strip() and not l.strip().startswith("#")
                ]
                configs["requirements_txt"] = deps[:30]
            except OSError:
                pass

        return configs

    @staticmethod
    def _summarize(scent: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the project."""
        parts = []
        name = scent.get("name", "unknown")
        parts.append(f"Project: {name}")

        langs = scent.get("languages", [])
        if langs:
            parts.append(f"Languages: {', '.join(langs)}")

        frameworks = scent.get("frameworks", [])
        if frameworks:
            parts.append(f"Frameworks: {', '.join(frameworks)}")

        tools = scent.get("tools", [])
        if tools:
            parts.append(f"Tools: {', '.join(tools)}")

        infra = scent.get("infra", [])
        if infra:
            parts.append(f"Infrastructure: {', '.join(infra)}")

        git = scent.get("git", {})
        if git:
            branch = git.get("branch", "?")
            dirty = git.get("dirty_files", 0)
            state = "clean" if git.get("clean") else f"{dirty} dirty files"
            parts.append(f"Git: branch={branch}, {state}")

        return " | ".join(parts)


# ===========================================================================
# KARMENDRIYAS (Action Organs) -- Output Channels (Stubs)
# ===========================================================================

class Karmendriya(ABC):
    """
    Base class for action organs (karmendriyas).

    These are the system's means of acting on the world. In Samkhya,
    the five karmendriyas complement the five jnanendriyas -- perception
    without action is incomplete.

    These are stubs for future implementation.
    """

    karmendriya_type: KarmendriyaType
    name: str
    sanskrit_name: str
    description: str

    @abstractmethod
    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        """Execute an action in the world."""
        ...

    @abstractmethod
    def available(self) -> bool:
        """Check if this action organ is operational."""
        ...


class Vak(Karmendriya):
    """Speech -- send messages (Telegram, email, notifications)."""
    karmendriya_type = KarmendriyaType.VAK
    name = "Speaker"
    sanskrit_name = "Vak"
    description = "Sends messages and communications"

    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        return {"status": "stub", "action": "speak", "message": instruction}

    def available(self) -> bool:
        return False  # Not yet implemented


class Pani(Karmendriya):
    """Hands -- write files, edit code."""
    karmendriya_type = KarmendriyaType.PANI
    name = "Writer"
    sanskrit_name = "Pani"
    description = "Writes files and edits code"

    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        return {"status": "stub", "action": "write", "target": instruction}

    def available(self) -> bool:
        return False


class Pada(Karmendriya):
    """Feet -- navigate filesystem, change context."""
    karmendriya_type = KarmendriyaType.PADA
    name = "Navigator"
    sanskrit_name = "Pada"
    description = "Navigates filesystem and changes context"

    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        return {"status": "stub", "action": "navigate", "destination": instruction}

    def available(self) -> bool:
        return False


class Payu(Karmendriya):
    """Elimination -- delete files, clean up, garbage collection."""
    karmendriya_type = KarmendriyaType.PAYU
    name = "Cleaner"
    sanskrit_name = "Payu"
    description = "Deletes files and cleans up resources"

    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        return {"status": "stub", "action": "clean", "target": instruction}

    def available(self) -> bool:
        return False


class Upastha(Karmendriya):
    """Creation -- create new projects, scaffold structures."""
    karmendriya_type = KarmendriyaType.UPASTHA
    name = "Creator"
    sanskrit_name = "Upastha"
    description = "Creates new projects and scaffolds structures"

    def act(self, instruction: str, **kwargs) -> Dict[str, Any]:
        return {"status": "stub", "action": "create", "target": instruction}

    def available(self) -> bool:
        return False


# ===========================================================================
# MANAS (Mind) -- The Perception Router
# ===========================================================================

class Manas:
    """
    The mind -- coordinates all sense organs (indriyas).

    In Samkhya, Manas is the internal organ that receives data from the
    jnanendriyas and routes it to Buddhi for discrimination. Here, Manas
    decides WHICH sense organs to activate for a given query, coordinates
    their execution, and assembles the results into a PerceptionBundle.

    This is meta-attention over the senses: not what to perceive, but
    HOW to perceive.
    """

    def __init__(self):
        """Initialize Manas with all five jnanendriyas."""
        self.chakshu = Chakshu()
        self.shrotra = Shrotra()
        self.tvak = Tvak()
        self.rasana = Rasana()
        self.ghrana = Ghrana()

        self._indriyas: Dict[IndriyaType, Indriya] = {
            IndriyaType.CHAKSHU: self.chakshu,
            IndriyaType.SHROTRA: self.shrotra,
            IndriyaType.TVAK: self.tvak,
            IndriyaType.RASANA: self.rasana,
            IndriyaType.GHRANA: self.ghrana,
        }

    def get_indriya(self, indriya_type: IndriyaType) -> Indriya:
        """Get a specific sense organ by type."""
        return self._indriyas[indriya_type]

    def perceive_with(
        self, indriya_type: IndriyaType, query: str, **kwargs
    ) -> Perception:
        """Perceive using a specific sense organ."""
        return self._indriyas[indriya_type].perceive(query, **kwargs)

    def perceive_all(self, query: str, **kwargs) -> PerceptionBundle:
        """
        Analyze a query and activate the relevant sense organs.

        Manas examines the query to determine which indriyas are relevant,
        then activates them and collects results into a PerceptionBundle.

        The routing logic:
            - File paths -> Chakshu (eye)
            - URLs (http/https) -> Shrotra (ear)
            - Shell commands (explicit prefix) -> Tvak (skin)
            - API endpoints (json/api patterns) -> Rasana (tongue)
            - Directory paths / project queries -> Ghrana (nose)
            - Ambiguous -> activate multiple senses

        Args:
            query: The perception query (may contain multiple sub-queries).
            **kwargs: Passed through to individual indriyas.

        Returns:
            A PerceptionBundle with all gathered perceptions.
        """
        start = time.monotonic()
        bundle = PerceptionBundle(query=query)
        activated = []

        # Determine which indriyas to activate
        plans = self._route_query(query)

        for indriya_type, sub_query, extra_kwargs in plans:
            indriya = self._indriyas[indriya_type]
            merged_kwargs = {**kwargs, **extra_kwargs}

            perception = indriya.perceive(sub_query, **merged_kwargs)
            bundle.perceptions.append(perception)
            activated.append(indriya_type.value)

        bundle.indriyas_activated = activated
        bundle.total_time_ms = (time.monotonic() - start) * 1000
        return bundle

    def _route_query(
        self, query: str
    ) -> List[Tuple[IndriyaType, str, Dict[str, Any]]]:
        """
        Determine which indriyas to activate for a query.

        Returns a list of (indriya_type, sub_query, kwargs) tuples.
        """
        plans: List[Tuple[IndriyaType, str, Dict[str, Any]]] = []
        query_lower = query.lower().strip()

        # URL detection
        url_pattern = re.compile(r'https?://\S+')
        urls = url_pattern.findall(query)
        for url in urls:
            plans.append((IndriyaType.SHROTRA, url, {}))

        # File path detection (absolute paths or relative with extensions)
        file_pattern = re.compile(
            r'(?:^|[\s,])(/[\w./\-]+(?:\.\w+)?|~/[\w./\-]+(?:\.\w+)?)'
        )
        file_paths = file_pattern.findall(query)
        for fp in file_paths:
            fp = fp.strip()
            path = Path(fp).expanduser()
            if path.exists():
                if path.is_dir():
                    plans.append((IndriyaType.GHRANA, fp, {}))
                else:
                    plans.append((IndriyaType.CHAKSHU, fp, {}))

        # Shell command detection (explicit markers)
        shell_markers = [
            "git status", "git log", "git branch", "git diff",
            "ls ", "pwd", "whoami", "uname", "uptime",
            "python --version", "python3 --version",
        ]
        for marker in shell_markers:
            if marker in query_lower:
                plans.append((IndriyaType.TVAK, marker.strip(), {}))
                break  # Only one shell command per query

        # API detection
        api_patterns = [
            r'api\.\w+\.\w+',         # api.github.com
            r'/api/v\d+/',              # /api/v1/
            r'application/json',
        ]
        for pattern in api_patterns:
            if re.search(pattern, query_lower):
                # Extract the URL-like part
                api_url = re.search(r'https?://\S+', query)
                if api_url and api_url.group() not in urls:
                    plans.append((
                        IndriyaType.RASANA, api_url.group(), {}
                    ))
                break

        # Directory / project detection
        dir_keywords = [
            "project", "codebase", "repository", "repo",
            "directory", "folder", "structure", "detect",
            "sniff", "analyze", "environment",
        ]
        if any(kw in query_lower for kw in dir_keywords):
            # Try to extract a directory path, or use cwd
            dir_paths = [
                fp for fp in file_paths
                if Path(fp).expanduser().is_dir()
            ]
            if dir_paths:
                for dp in dir_paths:
                    # Avoid duplicate if already added
                    if not any(
                        t == IndriyaType.GHRANA and q == dp
                        for t, q, _ in plans
                    ):
                        plans.append((IndriyaType.GHRANA, dp, {}))
            elif not any(t == IndriyaType.GHRANA for t, _, _ in plans):
                plans.append((IndriyaType.GHRANA, os.getcwd(), {}))

        # If nothing matched, try to be smart about it
        if not plans:
            # Default: sniff current directory for context
            plans.append((IndriyaType.GHRANA, os.getcwd(), {}))

        return plans


# ===========================================================================
# Module-level convenience functions
# ===========================================================================

def create_manas(
    api_base_urls: Optional[Dict[str, str]] = None,
    api_auth_headers: Optional[Dict[str, str]] = None,
) -> Manas:
    """
    Factory function to create a configured Manas (perception router).

    Args:
        api_base_urls: Named API base URLs for the Rasana (APITaster).
        api_auth_headers: Default auth headers for API calls.

    Returns:
        A configured Manas instance with all five jnanendriyas.
    """
    manas = Manas()
    if api_base_urls:
        manas.rasana.base_urls.update(api_base_urls)
    if api_auth_headers:
        manas.rasana.auth_headers.update(api_auth_headers)
    return manas
