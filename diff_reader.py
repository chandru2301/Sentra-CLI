"""Read and parse git diffs."""
import subprocess
import re
from typing import List, Dict, Tuple


class DiffReader:
    """Reads git diff and extracts file changes."""
    
    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch
    
    def get_diff(self) -> str:
        """Get git diff between current branch and base branch."""
        try:
            result = subprocess.run(
                ["git", "diff", f"{self.base_branch}..HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Fallback to staged changes if branch comparison fails
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Check if we're in a git repo
                check_repo = subprocess.run(
                    ["git", "rev-parse", "--git-dir"],
                    capture_output=True,
                    text=True
                )
                if check_repo.returncode != 0:
                    raise RuntimeError("Not a git repository. Please run this command from a git repository.")
                raise RuntimeError(f"Failed to get git diff: {e.stderr}")
            return result.stdout
        except FileNotFoundError:
            raise RuntimeError("git command not found. Please ensure git is installed.")
    
    def parse_diff(self, diff_text: str) -> Dict[str, Dict]:
        """Parse diff text into structured format.
        
        Returns:
            Dict mapping file paths to change info:
            {
                "path/to/file.py": {
                    "added_lines": 10,
                    "removed_lines": 5,
                    "chunks": [...]
                }
            }
        """
        files = {}
        current_file = None
        current_chunk = None
        
        lines = diff_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # File header: +++ or ---
            if line.startswith('+++ b/'):
                filepath = line[6:].strip()
                if filepath and filepath != '/dev/null':
                    current_file = filepath
                    files[current_file] = {
                        "added_lines": 0,
                        "removed_lines": 0,
                        "chunks": []
                    }
            
            # Chunk header: @@ -start,count +start,count @@
            elif line.startswith('@@'):
                match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2) or 1)
                    new_start = int(match.group(3))
                    new_count = int(match.group(4) or 1)
                    
                    if current_file:
                        current_chunk = {
                            "old_start": old_start,
                            "old_count": old_count,
                            "new_start": new_start,
                            "new_count": new_count,
                            "lines": []
                        }
                        files[current_file]["chunks"].append(current_chunk)
            
            # Content lines
            elif current_file and current_chunk is not None:
                if line.startswith('+') and not line.startswith('+++'):
                    files[current_file]["added_lines"] += 1
                    current_chunk["lines"].append(("added", line[1:]))
                elif line.startswith('-') and not line.startswith('---'):
                    files[current_file]["removed_lines"] += 1
                    current_chunk["lines"].append(("removed", line[1:]))
                elif line.startswith(' ') or line == '':
                    current_chunk["lines"].append(("context", line[1:] if line.startswith(' ') else line))
            
            i += 1
        
        return files
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed file paths."""
        diff_text = self.get_diff()
        return list(self.parse_diff(diff_text).keys())
    
    def get_file_content(self, filepath: str) -> str:
        """Get current content of a file (read-only)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, UnicodeDecodeError):
            return ""

