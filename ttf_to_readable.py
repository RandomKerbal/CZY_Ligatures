from fontTools.ttLib import TTFont


def ttf_to_readable(ttf_path, output_path=None):
    try:
        font = TTFont(ttf_path)

        # Save in TTX (XML) format for readability
        font.saveXML(output_path)
        print(f"Readable font data saved in: {output_path}")

    except Exception as e:
        print(f"Error reading TTF: {e}")


if __name__ == "__main__":
    ttf_file = "./LigCZY-JetBrainsMono-Regular.ttf"
    output_file = ttf_file.rsplit('.', 1)[0] + '.txt'
    ttf_to_readable(ttf_file, output_file)
