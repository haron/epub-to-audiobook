#!/usr/bin/env -S uv run modal run
import modal
import subprocess
import tempfile
from pathlib import Path
from natsort import natsorted


gpu = "T4"
convert_timeout = 3600  # seconds
compress_timeout = convert_timeout // 2
image = (
    modal.Image.from_registry("python:3.10-slim-bookworm")
    .apt_install("ffmpeg", "curl")
    .uv_sync(groups=["remote"])
)
volume = modal.Volume.from_name("epub_to_audiobook", create_if_missing=True)
app = modal.App("epub_to_audiobook")
result_path = Path("/result")
audiblez_opts = ""  # see https://github.com/santinic/audiblez?tab=readme-ov-file#help-page


def cmd(command):
    print(f"Running command: {command}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True, bufsize=1)
    for line in process.stdout:
        print(line.rstrip())
    process.wait()


@app.function(gpu=gpu, image=image, volumes={"/result": volume}, timeout=convert_timeout)
def epub_to_audiobook(epub_path: Path):
    print("Converting epub to wav")
    cmd(f"/.uv/.venv/bin/audiblez '{result_path}/{epub_path.name}' {audiblez_opts} --cuda -o {result_path}")
    volume.commit()
    print("Done")


@app.function(cpu=8.0, image=image, volumes={"/result": volume}, timeout=compress_timeout)
def compress():
    print("Converting wav to m4b")
    audio_files = natsorted(result_path.glob("*.wav"))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete_on_close=False) as file_list:
        content = "\n".join([f"file '{audio_file}'" for audio_file in audio_files])
        file_list.write(content)
        file_list.close()
        cmd(f"ffmpeg -f concat -safe 0 -i {file_list.name} -vn -c:a aac -b:a 64k -movflags +faststart {result_path}/audiobook.m4b")
    volume.commit()
    print("Done")


def download():
    print("Downloading m4b")
    # downloading via command line tool due to 16Mb limit: https://modal.com/docs/guide/volumes#downloading-a-file-from-a-volume
    cmd(f"uvx modal volume get {volume.name} /audiobook.m4b audiobook.m4b")
    print("Revoming volume")
    volume.delete(volume.name)


@app.local_entrypoint()
def main(epub: str):
    epub_path = Path(epub)
    print(f"Uploading {epub_path} to volume {volume.name}")
    with volume.batch_upload(force=True) as batch:
        batch.put_file(epub_path, epub_path.name)
    print(f"Processing {epub_path}")
    epub_to_audiobook.remote(epub_path)
    compress.remote()
    download()
    print("Done")
