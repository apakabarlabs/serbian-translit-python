# Changelog

## 0.4.1

Internal refactor only. Public API and behaviour unchanged; drop-in
upgrade from 0.4.0.

## 0.4.0

### Added

- Python 3.13 and 3.14 supported. Matrix now covers 3.10 – 3.14 on
  Linux and macOS.

## 0.3.0

### Fixed

- NFD input now transliterates correctly. Text from macOS clipboard or
  iOS filenames used to leak combining marks through (`čovek` produced
  `ц̌овек`); the engine now normalises to NFC first.
- All-caps Serbian and Montenegrin particles (`MI`, `LI`, `VI`, `CI`)
  stopped being mis-detected as Roman numerals. `DA LI voliš?` used to
  transliterate as `ДА LI ВОЛИШ?`; now it comes out as `ДА ЛИ ВОЛИШ?`.
- URLs, emails, hashtags and @-mentions are preserved verbatim.
  `#Beograd`, `https://beograd.rs`, `info@beograd.rs` used to get
  transliterated character-by-character.
- Brand names in MIXED case (`iPhone`, `iOS`, `mRNA`, `YouTube`) are
  now left untouched. The old lowercased conversion produced `ипхоне`,
  `иос` and similar.
- Words starting with a digit (`2brzo`, `100dinara`) now transliterate
  their letter part instead of being skipped whole.

### Documented

- Typewriter `dj` for `đ` is NOT auto-mapped (ambiguous with native
  compounds like `odjek`, `podjednako`). Behaviour pinned by tests.

## 0.2.0

### Changed

- **Breaking**. `Transliterator(source, target)` replaced with flat
  submodules. Migration:

  ```python
  # before
  from serbian_translit import Transliterator
  t = Transliterator("srp-latn", "srp-cyrl")
  t("Beograd")

  # after
  from serbian_translit import srp
  srp.to_cyr("Beograd")
  ```

  Four functions, one per direction: `srp.to_cyr`, `srp.to_lat`,
  `cnr.to_cyr`, `cnr.to_lat`. Wrong pairs are now impossible at
  import time.

## 0.1.0

First release.

### Added

- Serbian and Montenegrin script conversion in both directions:
  `srp-latn ↔ srp-cyrl` and `cnr-latn ↔ cnr-cyrl`.
- Case preservation for digraphs (`Nj` in title case, `NJ` in caps).
- Quoted regions (`"…"`, `„…"`, `“…”`, `«…»`) preserved verbatim.
- Roman numerals (`II`, `XIV`, `XX`) left in Latin regardless of
  direction.
- Words containing non-native Latin letters (`w`, `x`, `y`, `q`)
  skipped as foreign inclusions.
- Đ variants (`Đ`, `đ`, `Ð`, `ð`) all map to `Ђ`/`ђ`.
- Supported Python versions: 3.10, 3.11, 3.12.
