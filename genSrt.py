import os
import sys
import re
import subprocess
import json
from datetime import datetime
from datetime import timedelta
import srt
from srt import Subtitle
from faster_whisper import WhisperModel

def download_video(url: str, output_dir: str = 'output') -> (str, str, str):
    """
    指定されたURLから動画をダウンロードし、タイトル、拡張子、タイムスタンプを返します。

    Args:
    url (str): ダウンロードする動画のURL。
    output_dir (str): ダウンロードした動画を保存するディレクトリ。

    Returns:
    tuple: ダウンロードされた動画のタイトル、拡張子、タイムスタンプを含むタプル。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file_template = os.path.join(output_dir, f'{timestamp}.%(ext)s')
  
    command = [
        'yt-dlp',
        '--print-json',
        '-o', output_file_template,
        url
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    video_info = json.loads(result.stdout)
    print(video_info)

    return  video_info['title'],  video_info['ext'], timestamp

def result2subs(segments):
    """
    セグメントをSRT形式の字幕データに変換します。

    Args:
    segments: Whisperモデルから取得したセグメントのリスト。

    Returns:
    list: SRT形式の字幕データリスト。
    """
    subs = []

    for index, segment in enumerate(segments):
        start = segment.start
        end = segment.end
        text = segment.text
        sub = Subtitle(index=index + 1,
                       start=timedelta(seconds=start),
                       end=timedelta(seconds=end),
                       content=text)

        subs.append(sub)
    return subs

def transcribe_video(file_path: str, output_path: str = 'output'):
    """
    指定された動画ファイルをトランスクリプトし、結果をSRTファイルとして保存します。

    Args:
    file_path (str): トランスクリプトする動画ファイルのパス。
    output_path (str): SRTファイルを保存するディレクトリ。

    """
    print(file_path)
    model_size = "large-v3"

    # Run on GPU with FP16
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    segments, info = model.transcribe(file_path, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    # SRTファイルを保存するディレクトリ
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    srt_file_path = os.path.join(output_path, f"{os.path.basename(file_path)}.srt")

    # SRTファイルを生成して保存
    with open(srt_file_path, 'w', encoding='utf-8') as f:
        f.write(srt.compose(result2subs(segments)))

def rename_files(old_path: str, new_name: str, extension: str, output_dir: str = 'output'):
    """
    ファイル名を新しい名前に変更します。

    Args:
    old_path (str): 元のファイルパス。
    new_name (str): 新しいファイル名。
    extension (str): ファイルの拡張子。
    output_dir (str): ファイルを保存するディレクトリ。
    """
    counter = 1
    new_file_name = clean_filename(new_name)

    while os.path.exists(os.path.join(output_dir, f"{new_file_name}.{extension}")):
        new_file_name = f"{new_name}_{counter}"
        counter += 1
    os.rename(old_path, os.path.join(output_dir, f"{new_file_name}.{extension}"))

def clean_filename(filename: str) -> str:
    return re.sub(r'[/*?:"<>|]', '', filename)    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python genSrt.py [video_url | video_path]')
        sys.exit(1)

    input_arg = sys.argv[1]  # URL or local path

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
    transcribe_video(downloaded_file_path, output_path)
    # rename_files(downloaded_file_path, original_title, video_extension, output_path)
    # rename_files(f"{downloaded_file_path}.srt", original_title, 'srt', output_path)


