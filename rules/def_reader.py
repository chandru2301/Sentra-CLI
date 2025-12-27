result = subprocess.run(
    ["git", "diff", f"{self.base_branch}..HEAD"],
    capture_output=True,
    text=True,
    check=True
)
