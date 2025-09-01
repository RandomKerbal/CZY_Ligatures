"""
Requires:
    pip install fonttools
"""
from fontTools.ttLib import TTFont

font_path = "./JetBrainsMono-Regular.ttf"  # replace with your font file

font = TTFont(font_path)

# get Unicode mappings
cmap = font['cmap'].getBestCmap()  # maps codepoint -> glyph name

print("All glyphs in the font:\n")
for glyph_name in font.getGlyphOrder():
    # find the Unicode character if it exists
    char = None
    for codepoint, _glyph_name in cmap.items():
        if glyph_name == _glyph_name:
            char = chr(codepoint)
            break
    if char:
        print(f"'{char}' -> {_glyph_name}")
    else:
        print(f"(no glyph) -> {_glyph_name}")