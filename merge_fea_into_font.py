"""
Requires:
    pip install fonttools

What it does:
    - Adds the OpenType features from the .fea file into the provided TTF.
    - Renames the font family, fullname, postscript names, so OS sees it as a different font.
    - Prints a short report of glyph names referenced in the .fea that are missing from the font (you may need to import those glyphs from a math font).
"""
import re
from fontTools import ttLib
from fontTools.feaLib.builder import addOpenTypeFeatures

FEA_GLYPH_RE = re.compile(r"by\s+([A-Za-z0-9_]+)\s*;")


def extract_target_glyphs_from_fea(fea_text):
    """Return a sorted set of glyph names referenced by 'by <glyph>' in the .fea"""
    return sorted(set(FEA_GLYPH_RE.findall(fea_text)))


def rename_font_name_table(font, new_family, new_subfamily, new_fullname, new_psname):
    """
    Update the font's 'name' table to set Family (1), Subfamily (2), Unique ID (3),
    Full name (4), and PostScript name (6) for common platforms.
    """
    name_table = font["name"]

    # Helper to set for Windows (platformID=3) and Mac (platformID=1)
    targets = [
        # (platformID, platEncID, langID)
        (3, 1, 0x409),   # Windows, Unicode BMP, English (U.S.)
        (1, 0, 0),       # Mac, Roman, language 0 (English)
    ]

    # Set Family (1), Subfamily (2), Fullname (4), PostScript (6), and UniqueID (3)
    for platformID, platEncID, langID in targets:
        try:
            name_table.setName(new_family, 1, platformID, platEncID, langID)
            name_table.setName(new_subfamily, 2, platformID, platEncID, langID)
            name_table.setName(new_fullname, 4, platformID, platEncID, langID)
            name_table.setName(new_psname, 6, platformID, platEncID, langID)
            # Unique font identifier (nameID 3) — put something informative
            unique_id = f"{new_psname};{new_family}-{new_subfamily}"
            name_table.setName(unique_id, 3, platformID, platEncID, langID)
        except Exception:
            # Some name records may not accept certain encodings; ignore failures
            pass


def main():
    in_name = "JetBrainsMono"
    out_name = "LigCZY"
    subfamily = "Regular"

    in_path = f"./{in_name}-{subfamily}.ttf"
    fea_path = f"./{out_name}-{in_name}.v2.fea"
    out_path = f"./{out_name}-{in_name}.ttf"

    with open(fea_path, "r", encoding="utf-8") as fh:
        fea_text = fh.read()

    target_glyphs = extract_target_glyphs_from_fea(fea_text)
    print("Glyphs referenced in .fea:")
    print(" ", ", ".join(target_glyphs))

    font = ttLib.TTFont(in_path)

    # build a set of glyphs present in the font
    glyphset = set(font.getGlyphOrder())
    missing = [g for g in target_glyphs if g not in glyphset]
    if missing:
        print("\nWARNING: The following glyphs referenced by the .fea are missing from the font:")
        for g in missing:
            print("  -", g)

    # add the OpenType features
    try:
        addOpenTypeFeatures(font, fea_path)
    except Exception as e:
        print(f"\nERROR: failed to add OpenType features: {e}")
        exit()

    # set new internal names
    try:
        # build new full and postscript names (NO spaces)
        fullname = f"{out_name}-{in_name}"

        print(f"Internal name table renamed to: out_name='{out_name}', full='{fullname}', ps='{fullname}'")
        rename_font_name_table(font, out_name, subfamily, fullname, fullname)
    except Exception as e:
        print(f"Warning: failed to rename name table: {e}")

    # save output
    try:
        font.save(out_path)
        print(f"\nSUCCESS: Merged font saved to: {out_path}")
    except Exception as e:
        print(f"ERROR: Failed to save font: {e}")
        exit()


if __name__ == '__main__':
    main()