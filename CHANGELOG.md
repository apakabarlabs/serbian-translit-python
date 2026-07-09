# Changelog

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
