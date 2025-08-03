# EPUB to Audiobook Converter

Convert EPUB files to audiobooks using [audiblez](https://github.com/santinic/audiblez) and
[Modal's](https://modal.com/) cloud GPU.

## Prerequisites

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Set up Modal authentication:
   ```
   uvx modal setup
   ```

## Usage

Run the conversion script with your EPUB file:

    ./audiobook.py path/to/your/book.epub

The script will:
1. Upload your EPUB to Modal's cloud storage
2. Convert it to audio using `audiblez`
3. Compress the audio files into a single M4B audiobook
4. Download the generated book as `audiobook.m4b`
5. Clean up the cloud storage

## Example

It should take less than 15 minutes and about $0.15 in Modal fees (see "Usage and billing" in [Modal settings](https://modal.com/settings)):

    # Download "Hamlet":
    wget https://www.gutenberg.org/cache/epub/27761/pg27761.epub

    time ./audiobook.py --epub ./pg27761.epub
    # lots of output skipped...
    real	14m33.014s

    ls -lh audiobook.m4b
    -rw-r--r-- 1 *** staff 119M Aug  4 14:17 audiobook.m4b

## Cleanup

**IMPORTANT**: when the script exits due to an error, dangling data may be left in the
`epub_to_audiobook` volume. Go to [Modal storage](https://modal.com/storage/) to delete it.

## Tuning

You can:

* change GPU type from `T4` to [another available GPU](https://modal.com/pricing)
* increase the timeouts to process a longer book
* change narrating voice, language and speed - see [audiblez help](https://github.com/santinic/audiblez?tab=readme-ov-file#help-page)
