# Spine JSON Converter

A small Python utility for a specific Spine JSON compatibility issue.

## Purpose

This script is intended for JSON files exported by **bone3 in Spine 4.2 format** when those files are imported into projects using an **older Unity engine / Spine runtime**.

In some cases, the older runtime may fail to read or recognize the exported JSON correctly. This converter applies two small compatibility adjustments that may help with that situation:

- Adds an empty `hash` field at the beginning of the top-level `skeleton` object, if the field is missing.
- Renames `color` timelines to `rgba` under each animation's `slots` section.

**This is a targeted workaround, not a general Spine version converter.** It does not guarantee compatibility with every older Unity engine or Spine runtime version. The result should be tested in your own project.

## Requirements

- Python 3.8 or later
- A JSON file exported by bone3 using Spine 4.2 format

No third-party Python packages are required.

## Usage

Run the script from a terminal:

```bash
python spine_json_converter.py path/to/your_skeleton.json
```

For example:

```bash
python spine_json_converter.py wqs1.1.json
```

## Backup

Before modifying the input file, the script creates a backup next to it:

```text
wqs1.1.json.bak
```

If a backup with that name already exists, the script stops without overwriting it. Keep the backup until you have confirmed that the converted file works in your Unity project.

## Scope and Limitations

- Only the top-level `skeleton` object and `animations -> slots` color timelines are modified.
- Existing `hash` values are left unchanged.
- Each converted color keyframe is expected to contain an 8-character hexadecimal color value.
- The script does not modify atlas files, images, meshes, constraints, or other Spine data.
- It cannot resolve every possible JSON parsing error or runtime/export-version mismatch.

## Disclaimer

This utility is provided as-is for troubleshooting the specific bone3 + Spine 4.2 JSON import scenario described above. Always keep a copy of your original exported files and verify the result with the exact Unity and Spine runtime versions used by your project.
