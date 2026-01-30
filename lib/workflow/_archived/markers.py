"""
Marker Parsing for MH1

Parses [[MARKER:data]] patterns from Claude's responses to trigger automations.
"""

import re
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class MarkerType(Enum):
    """Types of markers Claude can output."""
    INPUT = "INPUT"           # [[INPUT:schema_name]] - Collect structured input
    CONFIRM = "CONFIRM"       # [[CONFIRM]] - Require user confirmation
    COUNCIL = "COUNCIL"       # [[COUNCIL]] - Run agent council (internal)
    SKILL = "SKILL"           # [[SKILL:skill_name]] - Execute a skill
    PROGRESS = "PROGRESS"     # [[PROGRESS:percent]] - Update progress
    CHECKPOINT = "CHECKPOINT" # [[CHECKPOINT]] - Save state
    MODULE = "MODULE"         # [[MODULE:action]] - Module operations
    CONFIG = "CONFIG"         # [[CONFIG:platform]] - Configuration


@dataclass
class Marker:
    """Represents a parsed marker."""
    type: MarkerType
    data: Optional[str]
    raw: str
    start: int
    end: int


# Regex pattern for markers
MARKER_PATTERN = re.compile(r'\[\[(INPUT|CONFIRM|COUNCIL|SKILL|PROGRESS|CHECKPOINT|MODULE|CONFIG)(?::([^\]]+))?\]\]')


def parse_markers(text: str) -> list[Marker]:
    """
    Parse all markers from Claude's response.

    Args:
        text: The response text to parse

    Returns:
        List of Marker objects found
    """
    markers = []

    for match in MARKER_PATTERN.finditer(text):
        marker_type_str = match.group(1)
        marker_data = match.group(2)

        try:
            marker_type = MarkerType(marker_type_str)
        except ValueError:
            continue

        markers.append(Marker(
            type=marker_type,
            data=marker_data,
            raw=match.group(0),
            start=match.start(),
            end=match.end()
        ))

    return markers


def strip_markers(text: str) -> str:
    """
    Remove all markers from text for display.

    Args:
        text: Text containing markers

    Returns:
        Text with markers removed
    """
    return MARKER_PATTERN.sub('', text)


def has_marker(text: str, marker_type: MarkerType) -> bool:
    """Check if text contains a specific marker type."""
    markers = parse_markers(text)
    return any(m.type == marker_type for m in markers)


def get_marker_data(text: str, marker_type: MarkerType) -> Optional[str]:
    """Get the data for a specific marker type."""
    markers = parse_markers(text)
    for m in markers:
        if m.type == marker_type:
            return m.data
    return None


def split_by_markers(text: str) -> list[tuple[str, Optional[Marker]]]:
    """
    Split text into segments, each followed by a marker (or None for final segment).

    This allows processing text and handling markers in sequence.

    Returns:
        List of (text_segment, marker_or_none) tuples
    """
    markers = parse_markers(text)
    if not markers:
        return [(text, None)]

    segments = []
    last_end = 0

    for marker in markers:
        # Text before this marker
        segment_text = text[last_end:marker.start]
        segments.append((segment_text, marker))
        last_end = marker.end

    # Remaining text after last marker
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining.strip():
            segments.append((remaining, None))

    return segments


class MarkerHandler:
    """
    Handles marker processing during response streaming.

    Usage:
        handler = MarkerHandler()
        for chunk in response_stream:
            text, markers = handler.process(chunk)
            # Display text
            for marker in markers:
                # Handle marker
    """

    def __init__(self):
        self.buffer = ""
        self.processed_markers = []

    def process(self, chunk: str) -> tuple[str, list[Marker]]:
        """
        Process a chunk of streamed response.

        Args:
            chunk: New text chunk from stream

        Returns:
            Tuple of (safe_text_to_display, new_markers_found)
        """
        self.buffer += chunk

        # Check for complete markers
        new_markers = []
        safe_text = ""

        # Find markers in buffer
        markers = parse_markers(self.buffer)

        if not markers:
            # No markers, but might have partial marker at end
            # Check for potential incomplete marker
            if "[[" in self.buffer and "]]" not in self.buffer.split("[[")[-1]:
                # Potential incomplete marker, hold back
                safe_idx = self.buffer.rfind("[[")
                safe_text = self.buffer[:safe_idx]
                self.buffer = self.buffer[safe_idx:]
            else:
                safe_text = self.buffer
                self.buffer = ""
        else:
            # Process complete markers
            last_end = 0
            for marker in markers:
                # Text before marker is safe
                safe_text += self.buffer[last_end:marker.start]
                new_markers.append(marker)
                self.processed_markers.append(marker)
                last_end = marker.end

            # Keep any remaining text that might contain incomplete marker
            remaining = self.buffer[last_end:]
            if "[[" in remaining and "]]" not in remaining.split("[[")[-1]:
                safe_idx = remaining.rfind("[[")
                safe_text += remaining[:safe_idx]
                self.buffer = remaining[safe_idx:]
            else:
                safe_text += remaining
                self.buffer = ""

        return safe_text, new_markers

    def flush(self) -> tuple[str, list[Marker]]:
        """
        Flush remaining buffer (call at end of stream).

        Returns:
            Tuple of (remaining_text, any_final_markers)
        """
        markers = parse_markers(self.buffer)
        text = strip_markers(self.buffer)
        self.buffer = ""
        return text, markers

    def reset(self):
        """Reset handler state."""
        self.buffer = ""
        self.processed_markers = []
