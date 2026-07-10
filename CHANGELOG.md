# Changelog

## 0.4.0

### Packaging and CI (audit follow-up)

- **N1**. `pyproject.toml` metadata expanded with `url`, `long_description`,
  `license`, `keywords`, and Trove `classifiers` for Python 3.10 through
  3.14.
- **N2, N3**. Single source of truth for the version. `[project]` uses
  `dynamic = ["version"]` reading `serbian_translit.__version__`; bump one
  line on release. `ruff.target-version` aligned with `requires-python` at
  `py310`. `setup.py` deleted.
- **N4**. Strict CI: `ruff check`, `ruff format --check`, and `mypy --strict`
  run in a dedicated `lint` job. Coverage tracked with `pytest-cov` at
  `fail_under = 95` (currently 100%). Wheel-smoke job builds the wheel and
  imports it in a clean venv, catching `package-data` regressions the
  source tree misses.
- **N5**. Test matrix expanded to Python 3.10, 3.11, 3.12, 3.13, 3.14 across
  `ubuntu-latest` and `macos-latest`.
- **N6**. GitHub Releases automated: pushing a tag `v*` triggers
  `.github/workflows/release.yml`, which extracts the matching CHANGELOG
  section and publishes it. Prior tags (v0.1.0, v0.2.0, v0.3.0) backfilled
  by hand.

### Refactor

- Split the 240-line `_engine.py` into one-concept-per-file modules:
  `_case.py`, `_roman.py`, `_protection.py`, `_rule.py`. `Rule.apply` reads
  as three named steps (`stash_all`, `_convert_part`, `restore`);
  `Rule._convert_word` is a short pipeline of named checks.
- Sentinel is now a per-instance UUID prefix, not a global counter.
  A user substring shaped like `\x00Q0\x00` no longer collides with a slot
  key. Pinned by `tests/tests.yaml`.

### Post-audit fixes

- **B-2**. `.github/dependabot.yml` added for pip and github-actions
  ecosystems.
- **M-1**. Tests moved out of the installable package. Wheel no longer
  ships `test_transliterate.py` or the QA fixture file to end users.
- **M-2**. Dev dependencies consolidated into
  `[project.optional-dependencies].dev`. Makefile and both CI jobs call
  `pip install -e ".[dev]"`. `requirements.txt` removed.
- **M-3**. `test_empty_input_returns_empty_string` and
  `test_unknown_rule_pair_raises_value_error` split into
  `parametrize` rows, so a break in one entry point no longer masks
  the other three.
- **N-1**. Unused `Stash` alias removed.
- **N-5**. Redundant `if not text: return ""` removed from `Rule.apply`;
  the empty string round-trips through the pipeline unchanged.
- **N-6**. One-line docstrings on the four public functions so
  `help(srp.to_cyr)` returns something.

### Not shipped this cycle

- **M-3 quotes** (nested and mixed-style paired regions) and **M-4**
  (single-style curly and guillemet quotes). Flagged by the earlier
  correctness audit, still open. Tracked; will land alongside a proper
  quote tokenizer rather than another regex tweak.

## 0.3.0

### Fixed

- **B1**. NFC-normalise input in `_Rule.apply`. NFD-decomposed sources
  (macOS clipboard, iOS filenames) used to leak combining marks
  through; `čovek` (NFD) produced `ц̌овек`. Now round-trips to `човек`.
- **B2**. Roman-numeral filter tightened to the canonical shape plus
  a `never_roman` blacklist in `rules.yaml` for the Serbian and
  Montenegrin particles (`MI`, `LI`, `VI`, `CI`) that happen to be valid
  Roman numerals. Fixes `DA LI voliš?` (was `ДА LI ВОЛИШ?`) and every
  all-caps card using those pronouns. `CIVIL`, `MILD`, and similar
  non-canonical shapes stopped getting mistakenly skipped.
- **B3**. Pre-stash pass protects URLs, emails, hashtags, and
  @-mentions before word-splitting. `#Beograd`, `https://beograd.rs`,
  `info@beograd.rs` used to be transliterated character-by-character.
- **M1**. MIXED-case words longer than 2 characters (`iPhone`, `iOS`,
  `mRNA`, `YouTube`) are left untouched. The old lowercased conversion
  produced `ипхоне` etc. The 2-char irregular digraph edge cases
  (`lJ`, `nJ`, `dŽ`) still convert as before.
- **M2**. Words starting with a digit (`2brzo`, `100dinara`) now
  transliterate their letter part instead of being skipped whole.
- **M6**. YAML test fixtures keyed by portable `source` and `target`
  script codes instead of Python-only `lang` and `direction`. Swift and
  Kotlin ports will read the same YAML with their own resolvers.

### Documented

- **M5**. Legacy typewriter `dj` for `đ` is NOT auto-mapped
  (ambiguity with native compounds like `odjek`, `podjednako`).
  Behaviour pinned by tests.

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
