# Exemplar papers

This folder holds published research papers in mathematics, each as one LaTeX file `<key>.tex`. They are read for how a paper is built and worded, and their mathematics is not used.

`manifest.json` lists the papers: the key that names the paper's file, arXiv identifier with version, title, authors, journal reference, year, arXiv category, field, pages, licence, abstract, the SHA-256 of the `.tex` file, and one sentence on what in the writing makes the paper a good model.

Each `.tex` file is the authors' LaTeX source as fetched from arXiv, joined into one file, with what the authors commented out left out: the lines that begin with `%` and the `comment` environments. The files stay on this machine and are not committed (`.gitignore` excludes them). To fetch them on another machine, run

```
python fetch.py
```

The script downloads the source of every paper that is missing or differs from the manifest, joins it into a single file and checks its SHA-256. `python fetch.py --only <key>` does one paper, and `--to <folder>` writes the files into another folder. It waits three and a half seconds between requests to arXiv and needs only the Python standard library.
