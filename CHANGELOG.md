# Changelog

## 0.3.0

### Fixed
- **B1** — NFC-normalise input in `_Rule.apply`. NFD-decomposed sources
  (macOS clipboard, iOS filenames) used to leak combining marks
  through; `čovek` (NFD) → `ц̌овек`. Now round-trips to `човек`.
- **B2** — Roman-numeral filter tightened to the canonical shape plus
  a `never_roman` blacklist in `rules.yaml` for the Serbian/Montenegrin
  particles (`MI`, `LI`, `VI`, `CI`) that happen to be valid Roman
  numerals. Fixes `DA LI voliš?` → `ДА ЛИ волиш?` (was `ДА LI ВОЛИШ?`)
  and every all-caps card using those pronouns. `CIVIL`, `MILD`, and
  similar non-canonical shapes stopped getting mistakenly skipped.
- **B3** — Pre-stash pass protects URLs, emails, hashtags, and
  @-mentions before word-splitting. `#Beograd`, `https://beograd.rs`,
  `info@beograd.rs` used to be transliterated character-by-character.
- **M1** — MIXED-case words longer than 2 characters (`iPhone`, `iOS`,
  `mRNA`, `YouTube`) are left untouched. The old lowercased conversion
  produced `ипхоне` etc. The 2-char irregular digraph edge cases
  (`lJ`, `nJ`, `dŽ`) still convert as before.
- **M2** — Words starting with a digit (`2brzo`, `100dinara`) now
  transliterate their letter part instead of being skipped whole.
- **M6** — YAML test fixtures keyed by portable `source`/`target`
  script codes instead of Python-only `lang`/`direction`. Swift and
  Kotlin ports will read the same YAML with their own resolvers.

### Documented
- **M5** — Legacy typewriter `dj` for `đ` is NOT auto-mapped
  (ambiguity with native compounds like `odjek`, `podjednako`).
  Behaviour pinned by tests.

## 0.2.0

### Changed — API
- Replaced `Transliterator(source, target)` with flat submodules:
  `serbian_translit.srp.to_cyr` / `.to_lat` and
  `serbian_translit.cnr.to_cyr` / `.to_lat`. Four fixed pairs did not need a
  runtime string-parameter dispatch; the module form makes wrong pairs
  impossible at import time.
- `data/tests.yaml` sections now identify the transform as
  `lang: srp|cnr` + `direction: to_cyr|to_lat`, portable to the Swift
  and Kotlin ports.

## 0.1.0

### Added
- Deterministic Serbian/Montenegrin script conversion in both directions:
  `srp-latn ↔ srp-cyrl` and `cnr-latn ↔ cnr-cyrl`.
- Rule table in `data/rules.yaml`; test corpus (131 cases) in
  `data/tests.yaml` — both the source of truth for the Swift and Kotlin
  ports (yet to be released).
- Case-preservation for digraphs (`Nj` in title, `NJ` in caps).
- Quoted-region protection with explicit paired alternation
  (German/Serbian `„…"`, French `«…»`, English `“…”`, ASCII `"…"`) —
  the symmetric character class the flowbot original used would happily
  mis-pair `»…«` and similar.
- Roman numeral skip (`II`, `XIV`, `XX`).
- Non-native-letter skip on the Latin side (`w`, `x`, `y`, `q`).
- Đ/Ð/đ/ð pre-char normalisation.
- CI on GitHub Actions across Python 3.10 / 3.11 / 3.12.
