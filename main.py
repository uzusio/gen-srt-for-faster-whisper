import sys
import os
from dotenv import load_dotenv
from genSrt import transcribe_video, download_video
from translator import Translator

def setup(translate_to_lang: str = 'none'):
    load_dotenv() # 環境変数を読み込む
    api_key = os.getenv("OPENAI_API_KEY")
    translator = Translator(api_key, translate_to_lang)
    return translator

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py [video_url | video_path] [(option)translate_to_lang]')
        sys.exit(1)

    input_arg = sys.argv[1]  # URL or local path
    
    tranlator = None
    translate_to_lang = 'none'
    if len(sys.argv) > 2:
        translate_to_lang = sys.argv[2]
        tranlator = setup(translate_to_lang)

    # URLで始まる場合
    if input_arg.startswith("https://"):
        output_path = 'output'
        original_title, video_extension, timestamp = download_video(input_arg, output_path)
        downloaded_file_path = os.path.join(output_path, f"{timestamp}.{video_extension}")

    # ローカルファイルの場合
    else:
        downloaded_file_path = os.path.abspath(input_arg)
        output_path = os.path.dirname(downloaded_file_path)
        original_title = os.path.splitext(os.path.basename(downloaded_file_path))[0]
        video_extension = os.path.splitext(downloaded_file_path)[1][1:]

    print(f"output_path: {output_path}")
    transcribe_video(downloaded_file_path, output_path, tranlator, translate_to_lang)

if __name__ == "__main__":
    main()