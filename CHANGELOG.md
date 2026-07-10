# Changelog

## 0.4.1

### Refactor

- Engine split further: `LetterMap` (digraph/single lookup) and
  `SkipPolicy` (foreign-inclusion and Roman-numeral checks) extracted
  from `Rule`, each in its own module. `Rule.apply` is now a short
  pipeline; the class no longer carries the raw lookup tables.
- Table loader and the four pre-built rule instances moved into
  `table.py`, so `rule.py` is only the `Rule` class and its input
  shape.
- Private module filenames lost their leading underscore
  (`_case.py` → `case.py`, etc.). Privacy is expressed by not being
  re-exported from `__init__.py`.

### CI and packaging

- CI steps delegate to `make` targets; the local `make lint` and CI
  `ruff check` no longer disagree on which paths are linted.
- `make wheel-smoke` carries the full assert set the CI job used to
  duplicate inline.
- `S101` (assert usage) tightened to `tests/**` via `per-file-ignores`
  instead of a repo-wide off switch.
- `PLR2004` (magic value) re-enabled; the widths that used to trip it
  are now named constants (`_DIGRAPH_WIDTH`, `_SINGLE_WIDTH`,
  `_MIN_NUMERAL_LEN`, `_MIXED_CASE_CUTOFF`).

### Docs

- README install snippet no longer pins `@v0.4.0`; points at the
  releases page for a specific version and shows `@main` for the
  moving default.
- Test section titles no longer carry internal audit codes.
- CHANGELOG entries rewritten in human language; historical mention
  of the removed `_engine.py` file dropped.

## 0.4.0

### Packaging

- `pyproject.toml` gained `url`, `long_description`, `license`, `keywords`,
  and Trove `classifiers` for Python 3.10 through 3.14.
- Version is now a single line to bump: `[project]` uses `dynamic =
  ["version"]` reading `serbian_translit.__version__`. `ruff.target-version`
  aligned with `requires-python` at `py310`. `setup.py` removed.
- Dev dependencies consolidated into `[project.optional-dependencies].dev`.
  Makefile and CI both call `pip install -e ".[dev]"`. `requirements.txt`
  removed.
- Tests moved out of the installable package. The wheel no longer ships
  `test_transliterate.py` or the QA fixture file to end users.

### CI

- Strict `lint` job: `ruff check`, `ruff format --check`, `mypy --strict`.
- Coverage tracked with `pytest-cov` at `fail_under = 95` (currently 100%).
- Wheel-smoke job builds the wheel and imports it in a clean venv, catching
  `package-data` regressions the source tree misses.
- Test matrix expanded to Python 3.10 through 3.14 across `ubuntu-latest`
  and `macos-latest`.
- `.github/dependabot.yml` added for pip and github-actions ecosystems.
- Pushing a tag `v*` triggers `.github/workflows/release.yml`, which
  extracts the matching CHANGELOG section and publishes it as a GitHub
  Release. Prior tags (v0.1.0, v0.2.0, v0.3.0) backfilled by hand.

### Refactor

- Engine split into single-responsibility modules: case detection,
  Roman-numeral filter, protected-region stashing, rule application.
  `Rule.apply` reads as three named steps (stash, convert, restore);
  `Rule._convert_word` is a short pipeline of named checks.
- Quote-region sentinel is now a per-instance UUID prefix rather than a
  global counter. A user substring shaped like `\x00Q0\x00` no longer
  collides with an internal slot key. Pinned by `tests/tests.yaml`.

### Tests

- The two entry-point smoke tests (empty input, unknown rule pair) split
  into `parametrize` rows, so a break in one call site no longer masks
  the other three.

## 0.3.0

### Fixed

- NFC-normalise input in the rule engine. NFD-decomposed sources
  (macOS clipboard, iOS filenames) used to leak combining marks
  through; `čovek` (NFD) produced `ц̌овек`. Now round-trips to `човек`.
- Roman-numeral filter tightened to the canonical shape plus a
  `never_roman` blacklist in `rules.yaml` for the Serbian and Montenegrin
  particles (`MI`, `LI`, `VI`, `CI`) that happen to be valid Roman
  numerals. Fixes `DA LI voliš?` (was `ДА LI ВОЛИШ?`) and every all-caps
  card using those pronouns. `CIVIL`, `MILD`, and similar non-canonical
  shapes stopped getting mistakenly skipped.
- Pre-stash pass protects URLs, emails, hashtags, and @-mentions before
  word-splitting. `#Beograd`, `https://beograd.rs`, `info@beograd.rs`
  used to be transliterated character-by-character.
- MIXED-case words longer than 2 characters (`iPhone`, `iOS`, `mRNA`,
  `YouTube`) are left untouched. The old lowercased conversion produced
  `ипхоне` etc. The 2-char irregular digraph edge cases (`lJ`, `nJ`,
  `dŽ`) still convert as before.
- Words starting with a digit (`2brzo`, `100dinara`) now transliterate
  their letter part instead of being skipped whole.
- YAML test fixtures keyed by portable `source` and `target` script
  codes instead of Python-only `lang` and `direction`. Swift and Kotlin
  ports will read the same YAML with their own resolvers.

### Documented

- Legacy typewriter `dj` for `đ` is NOT auto-mapped (ambiguity with
  native compounds like `odjek`, `podjednako`). Behaviour pinned by tests.

## 0.2.0

### Changed API

- Replaced `Transliterator(source, target)` with flat submodules:
  `serbian_translit.srp.to_cyr` / `.to_lat` and
  `serbian_translit.cnr.to_cyr` / `.to_lat`. Four fixed pairs did not need a
  runtime string-parameter dispatch; the module form makes wrong pairs
  impossible at import time.
- `data/tests.yaml` sections now identify the transform as
  `lang: srp|cnr` plus `direction: to_cyr|to_lat`, portable to the Swift
  and Kotlin ports.

## 0.1.0

### Added

- Deterministic Serbian and Montenegrin script conversion in both directions:
  `srp-latn ↔ srp-cyrl` and `cnr-latn ↔ cnr-cyrl`.
- Rule table in `data/rules.yaml`; test corpus (131 cases) in
  `data/tests.yaml`. Both files are the source of truth for the Swift and
  Kotlin ports (yet to be released).
- Case preservation for digraphs (`Nj` in title, `NJ` in caps).
- Quoted-region protection with explicit paired alternation
  (German and Serbian `„…"`, French `«…»`, English `“…”`, ASCII `"…"`).
  The symmetric character class the flowbot original used would happily
  mis-pair `»…«` and similar.
- Roman numeral skip (`II`, `XIV`, `XX`).
- Non-native-letter skip on the Latin side (`w`, `x`, `y`, `q`).
- Đ/Ð/đ/ð pre-char normalisation.
- CI on GitHub Actions across Python 3.10, 3.11, 3.12.
