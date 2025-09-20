"""
Requires:
    pip install fonttools
    pip install fontFeatures
"""
import re
from fontTools import ttLib
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontFeatures.ttLib import unparse

family1 = "JetBrainsMono"  # family of original font
family2 = "CZY"  # family of modified font
subfamily = "Regular"
FEA_GLYPH_RE = re.compile(r"by\s+([A-Za-z0-9_]+)\s*;")


def font_to_strFea(font) -> str:
    """Extract OpenType Layout Tables from font, convert into .fea format str."""
    return unparse(font).asFea()


def fea_to_str(fea_path: str) -> str:
    with open(fea_path, 'r') as f:
        return f.read()


def clean_and_relocate(out_fea: str) -> tuple:
    """
    - Remove duplicates of 'languagesystem ...;' (keep first one).
    - Remove ALL 'languagesystem', 'script', and 'language' statement lines from body because feaLib rejects them inside feature/lookup blocks, but only 'languagesystem' are kept in header.
    :return: tuple(cleaned_text, list_of_duplicate_languagesystem_lines)
    """
    languagesystem_regex = re.compile(r'(?im)^[ \t]*(languagesystem\b[^;]*;)[ \t]*\r?\n?')
    script_regex = re.compile(r'(?im)^[ \t]*script\b[^;]*;[ \t]*\r?\n?')
    language_regex = re.compile(r'(?im)^[ \t]*language\b[^;]*;[ \t]*\r?\n?')  # singular "language"

    found_langsys = languagesystem_regex.findall(out_fea)
    seen = set()
    dup_langsys = []
    for s in found_langsys:
        key = s.strip().lower()
        if key not in seen:
            seen.add(key)
            dup_langsys.append(s.strip())

    # remove all occurrences of languagesystem/script/language from the body
    cleaned = languagesystem_regex.sub('', out_fea)
    cleaned = script_regex.sub('', cleaned)
    cleaned = language_regex.sub('', cleaned)

    header_lines = []
    if dup_langsys:
        header_lines.append("# --- relocated languagesystem statements (duplicated) ---")
        header_lines.extend(dup_langsys)
        header_lines.append("")  # blank line

    new_text = "\n".join(header_lines) + cleaned.lstrip()
    return new_text, dup_langsys


def rename_name_table(font, new_family: str, new_subfamily: str):
    """
    Update the font's 'name' table to set Family (1), Subfamily (2), Unique ID (3), Full name (4), and PostScript name (6) for common platforms.
    For consistency, Family name = Full name = PostScript name
    """
    name_table = font["name"]

    # Helper to set for Windows (platformID=3) and Mac (platformID=1)
    targets = [
        # (platformID, platEncID, langID)
        (3, 1, 0x409),  # Windows, Unicode BMP, English (U.S.)
        (1, 0, 0),  # Mac, Roman, language 0 (English)
    ]

    # Set Family (1), Subfamily (2), Fullname (4), PostScript (6), and UniqueID (3)
    for platformID, platEncID, langID in targets:
        try:
            name_table.setName(new_family, 1, platformID, platEncID, langID)
            name_table.setName(new_subfamily, 2, platformID, platEncID, langID)
            name_table.setName(new_family, 4, platformID, platEncID, langID)
            name_table.setName(new_family, 6, platformID, platEncID, langID)
            # Unique font identifier (nameID 3) — put something informative
            unique_id = f"{new_family}-{new_subfamily}"
            name_table.setName(unique_id, 3, platformID, platEncID, langID)
        except Exception:
            # Some name records may not accept certain encodings; ignore failures
            pass


def main():
    in_path = f"./{family2}-{family1}-noSub.ttf"
    add_path = f"./{family2}-{family1}.v2.fea"
    out_path = f"./{family2}-{family1}.ttf"

    print(f"Input path: {in_path}")
    print(f"Features path: {add_path}")
    print(f"Output path: {out_path}", end='\n\n')

    font = ttLib.TTFont(in_path)
    in_fea = font_to_strFea(font)
    add_fea = fea_to_str(add_path)

    missing = set(FEA_GLYPH_RE.findall(add_fea)) - set(font.getGlyphOrder())
    if missing:
        print("\nWARNING: The following glyphs referenced by the .fea are missing from the font:")
        for glyph in missing:
            print("  -", glyph)

    out_fea = add_fea.rstrip() + '\n' + in_fea.rstrip()

    out_fea, langs = clean_and_relocate(out_fea)
    if langs:
        print("Relocated languagesystem statements:")
        for lang in langs:
            print("  ", lang)

    addOpenTypeFeaturesFromString(font, out_fea)

    family = f"{family2}-{family1}"
    print(f"Internal name table renamed to: {family}")
    rename_name_table(font, family, subfamily)

    font.save(out_path)
    print(f"\nSUCCESS: Merged font saved to: {out_path}")


if __name__ == '__main__':
    main()
