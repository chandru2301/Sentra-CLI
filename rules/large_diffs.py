"""Rule 4: Detect large AI-style diffs."""
from typing import Dict, List


def check_large_diffs(changed_files: List[str], diff_data: Dict) -> Dict:
    """Detect large diffs that might indicate AI-generated changes.
    
    Heuristics:
    - Many files touched
    - Large blocks added
    - Repeated patterns
    
    Risk: MEDIUM
    """
    total_added = 0
    total_removed = 0
    large_files = []
    
    for filepath, file_data in diff_data.items():
        added = file_data.get("added_lines", 0)
        removed = file_data.get("removed_lines", 0)
        total_added += added
        total_removed += removed
        
        # File with > 200 lines changed
        if added + removed > 200:
            large_files.append((filepath, added + removed))
    
    reasons = []
    
    # Many files touched (> 10)
    if len(changed_files) > 10:
        reasons.append(f"Large number of files changed ({len(changed_files)} files)")
    
    # Large total diff (> 500 lines)
    if total_added + total_removed > 500:
        reasons.append(f"Large diff: {total_added} added, {total_removed} removed lines")
    
    # Many large files
    if len(large_files) > 3:
        reasons.append(f"Multiple large files modified ({len(large_files)} files > 200 lines)")
    
    # Check for repeated patterns (simple heuristic: many similar chunk sizes)
    chunk_sizes = []
    for file_data in diff_data.values():
        for chunk in file_data.get("chunks", []):
            chunk_size = chunk.get("new_count", 0) + chunk.get("old_count", 0)
            if chunk_size > 20:  # Only count substantial chunks
                chunk_sizes.append(chunk_size)
    
    # If many similar-sized large chunks, detect AI-style patterns
    if len(chunk_sizes) > 5:
        avg_chunk = sum(chunk_sizes) / len(chunk_sizes)
        # Check if chunks are similar in size (within 20% of average)
        similar_chunks = sum(1 for size in chunk_sizes if abs(size - avg_chunk) / avg_chunk < 0.2)
        if similar_chunks > 5:
            reasons.append("Repeated patterns detected (AI-style diff pattern)")
    
    if reasons:
        return {
            "triggered": True,
            "rule_id": "LARGE_DIFF",
            "severity": "MEDIUM",
            "message": "; ".join(reasons),
            "files": changed_files,
            "risk": "MEDIUM",
            "reason": "; ".join(reasons)
        }
    
    return {
        "triggered": False,
        "rule_id": "LARGE_DIFF",
        "severity": "LOW",
        "message": None,
        "files": [],
        "risk": "LOW",
        "reason": None
    }

