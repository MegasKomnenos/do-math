"""AFP's official Heptapod API, with every file pinned to a Mercurial revision."""
import io
import json
import re
import tarfile
import tomllib
from datetime import date, datetime
from urllib.parse import quote, urlsplit

from api_adapters import APIAdapter
from scholarly import ServiceError, encoded


def json_values(value):
    if isinstance(value, dict):
        return {k: json_values(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_values(v) for v in value]
    return value.isoformat() if isinstance(value, (date, datetime)) else value


class AFP(APIAdapter):
    source = "afp"
    hosts = ("foss.heptapod.net",)
    options = ("project", "revision", "fields", "topic", "author")
    max_limit = 1000

    def __init__(self, store, client=None):
        super().__init__(store, client)
        self.archives = {}

    def revision(self, project, ref=None):
        if not re.fullmatch(r"afp-(?:devel|20\d{2}(?:-\d+)?)", project):
            raise ServiceError("source_boundary", "Choose an AFP release or afp-devel repository")
        base = "https://foss.heptapod.net/api/v4/projects/" + quote("isa-afp/" + project, safe="")
        metadata, evidence = self.request(base)
        if metadata.get("path_with_namespace") != "isa-afp/" + project:
            raise ServiceError("identity_mismatch", "Heptapod returned another project", evidence=evidence)
        commits, commit_ref = self.request(base + "/repository/commits", params={"ref_name": ref or metadata["default_branch"], "per_page": 1})
        if not isinstance(commits, list) or len(commits) != 1 or not re.fullmatch(r"[a-f0-9]{40}", commits[0].get("id", "")):
            raise ServiceError("invalid_response", "AFP did not resolve a unique revision", evidence=commit_ref)
        commit = commits[0]["id"]
        return base, commit, {"project": metadata, "revision": commits[0]}, [evidence, commit_ref]

    def archive(self, base, commit, path=""):
        key = (base, commit, path)
        if key not in self.archives:
            data, evidence = self.request(base + "/repository/archive.tar.gz", params={"sha": commit, **({"path": path} if path else {})}, accept="binary")
            try:
                with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz"):
                    pass
            except tarfile.TarError:
                raise ServiceError("unexpected_content", "AFP archive endpoint returned no tar archive", evidence=evidence) from None
            evidence = self.store.put(data, "application/gzip", self.source, evidence["url"], preserve_bytes=True,
                role="source_archive", commit=commit, path=path, provider_response_ref=evidence["ref"])
            self.archives[key] = evidence
        evidence = self.archives[key]
        return self.store.read(evidence["ref"])[1], evidence

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        self.validate(options, start, limit)
        if cursor or export not in (None, "json", "native"):
            raise ServiceError("invalid_options", "AFP uses start/limit; export is json or native metadata archive")
        fields = options.get("fields", ["title", "abstract"])
        if not isinstance(fields, list) or not fields or set(fields) - {"id", "title", "abstract", "topics", "authors"}:
            raise ServiceError("invalid_options", "AFP fields are id/title/abstract/topics/authors")
        project = options.get("project", "afp-devel")
        base, commit, version, provenance = self.revision(project, options.get("revision"))
        data, archive = self.archive(base, commit, "metadata/entries")
        records = []
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as bundle:
            for member in bundle:
                if not member.isfile() or not member.name.endswith(".toml"):
                    continue
                if member.size > 8 * 1024 * 1024:
                    raise ServiceError("invalid_response", "AFP entry metadata exceeds the supported entry size", evidence=archive)
                metadata = json_values(tomllib.loads(bundle.extractfile(member).read().decode("utf-8")))
                entry = member.name.rsplit("/", 1)[-1].removesuffix(".toml")
                row = {"id": entry, **metadata, "project": project, "commit": commit, "member_path": member.name,
                    "target": project + "@" + commit + ":thys/" + entry + "/"}
                values = "\n".join(row.get(field, "") if isinstance(row.get(field, ""), str) else json.dumps(row.get(field, ""), ensure_ascii=False) for field in fields)
                if query.casefold() not in values.casefold():
                    continue
                if "topic" in options and options["topic"] not in metadata.get("topics", []):
                    continue
                if "author" in options and options["author"] not in metadata.get("authors", {}):
                    continue
                records.append(row)
        records.sort(key=lambda row: row["id"])
        result = self.page(records[start:start + limit], len(records), archive, query, options, start, limit)
        result.update(project=project, commit=commit, revision_evidence=provenance,
            search_semantics="Case-insensitive literal match in the selected AFP metadata fields; exact topic/author filters; ordered by entry ID")
        return self.export_page(result, export)

    def fetch(self, target, *, parts):
        project, revision, path, entry = "afp-devel", None, None, None
        if target.startswith(("https://", "http://")):
            parsed = urlsplit(target)
            found = re.fullmatch(r"/entries/([A-Za-z0-9_-]+)(?:\.html|/)?", parsed.path)
            if parsed.hostname not in ("isa-afp.org", "www.isa-afp.org") or not found:
                raise ServiceError("source_boundary", "Use an AFP entry URL or project@revision:path target")
            entry = found[1]
        elif ":" in target:
            version, path = target.split(":", 1)
            project, separator, revision = version.partition("@")
            revision = revision if separator else None
            if not path or path.startswith("/") or ".." in path.split("/"):
                raise ServiceError("invalid_target", "Use an exact repository-relative file path")
            directory = re.fullmatch(r"thys/([A-Za-z0-9_-]+)/", path)
            if directory:
                entry = directory[1]
        elif target.startswith("afp-"):
            project, separator, revision = target.partition("@")
            revision = revision if separator else None
        elif re.fullmatch(r"[A-Za-z0-9_-]+", target):
            entry = target
        else:
            result = self.search(target, options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        base, commit, version, provenance = self.revision(project, revision)
        row = {"project": project, "commit": commit, "path": path, "entry": entry, "version": version}
        raw_file = None
        if entry:
            path = "metadata/entries/" + entry + ".toml"
        if path:
            data, raw_file = self.request(base + "/repository/files/" + quote(path, safe="") + "/raw", params={"ref": commit}, accept="binary")
            if path.endswith(".toml"):
                row["entry_metadata"] = json_values(tomllib.loads(data.decode("utf-8")))
        metadata = self.store.put(encoded([row]), "application/json", self.source, base, role="records", commit=commit, project=project, target=target)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": metadata}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": metadata} if row.get("entry_metadata", {}).get("abstract") else {"status": "not_offered", "reason": "This AFP target is a repository file or project without an entry abstract"}
            elif part in ("fulltext", "supplementary"):
                if entry or not path:
                    _, artifact = self.archive(base, commit, "thys/" + entry if entry else "")
                else:
                    artifact = raw_file
                components[part] = {"status": "available", "artifact": artifact, "content_kind": "formalization_source"}
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(c["status"] == "available" for c in components.values()) else "partial", "source": self.source,
            "target": target, "project": project, "commit": commit, "records": metadata, "components": components,
            "revision_evidence": provenance, "raw_metadata": raw_file}
