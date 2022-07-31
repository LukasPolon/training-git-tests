from pathlib import Path


class GitDirectoryStructure:
    """Helper class for GIT directory structure representation."""

    @classmethod
    def get_initial_dirs(cls, base_dir: Path) -> list[Path]:
        """Directory structure of fresh .git.

        Args:
            base_dir: path to .git directory or equivalent
        """
        initial_dirs = [
            Path(base_dir, "branches"),
            Path(base_dir, "hooks"),
            Path(base_dir, "info"),
            Path(base_dir, "objects"),
            Path(base_dir, "objects", "info"),
            Path(base_dir, "objects", "pack"),
            Path(base_dir, "refs"),
            Path(base_dir, "refs", "heads"),
            Path(base_dir, "refs", "tags"),
        ]
        return initial_dirs

    @classmethod
    def get_initial_files(cls, base_dir: Path) -> list[Path]:
        """Files structure of fresh .git.

        Args:
            base_dir: path to .git directory or equivalent
        """
        initial_files = [
            Path(base_dir, "HEAD"),
            Path(base_dir, "config"),
            Path(base_dir, "description"),
            Path(base_dir, "info", "exclude"),
            Path(base_dir, "hooks", "applypatch-msg.sample"),
            Path(base_dir, "hooks", "commit-msg.sample"),
            Path(base_dir, "hooks", "fsmonitor-watchman.sample"),
            Path(base_dir, "hooks", "post-update.sample"),
            Path(base_dir, "hooks", "pre-applypatch.sample"),
            Path(base_dir, "hooks", "pre-commit.sample"),
            Path(base_dir, "hooks", "pre-merge-commit.sample"),
            Path(base_dir, "hooks", "pre-push.sample"),
            Path(base_dir, "hooks", "pre-rebase.sample"),
            Path(base_dir, "hooks", "pre-receive.sample"),
            Path(base_dir, "hooks", "prepare-commit-msg.sample"),
            Path(base_dir, "hooks", "push-to-checkout.sample"),
            Path(base_dir, "hooks", "update.sample"),
        ]
        return initial_files
