"""Filesystem verification helper; separate from the one-shot extraction entry point."""
import stat


def no_reparse(path):
    for part in [path, *path.parents]:
        if part.exists():
            info=part.lstat()
            assert not part.is_symlink(), str(part)
            assert not getattr(info,'st_file_attributes',0) & stat.FILE_ATTRIBUTE_REPARSE_POINT, str(part)
