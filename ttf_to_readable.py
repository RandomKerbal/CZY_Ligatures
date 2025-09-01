from fontTools.ttLib import TTFont
from merge_fea_into_font import family1, family2


def ttf_to_readable(ttf_path, output_path=None):
    try:
        font = TTFont(ttf_path)

        # save in TTX (XML) format for readability
        font.saveXML(output_path)
        print(f"Readable font data saved in: {output_path}")

    except Exception as e:
        print(f"Error reading TTF: {e}")


if __name__ == "__main__":
    in_path = f"./{family2}-{family1}.ttf"
    out_path = in_path.rsplit('.', 1)[0] + '.txt'
    ttf_to_readable(in_path, out_path)
