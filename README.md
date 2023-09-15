# twtdl

twtdl is a bare-bones wrapper used to trivialize VOD + chat rendering for offline viewing.

Currently the chat is burned-in to the top-right of the VOD. It is underlaid with a transparent black rectangle.

The program has a few customizable options. Check them by passing `--help`.

## Usage

Download the twtdl repository to your computer, and then open a PowerShell window / terminal with the working directory being the repository folder.

To download a VOD with default parameters:
`python ./start.py "VOD ID here"`

To download a VOD with custom parameter(s):
`python ./start.py --chat_opacity 0.4 --gamma 1.6 "VOD ID here"`

To display parameter documentation:
`python ./start.py --help`

## Requirements

* The latest version of Python must be installed / in your PATH.
* `TwitchDownloaderCLI`  is required. You can place it in the repository folder, add it to your PATH, or pass `--twitch-dl`.
	* TwitchDownloader available here: https://github.com/lay295/TwitchDownloader
* `ffmpeg` and `ffprobe` are required. You can place them in the repository folder, add them to your PATH, or pass `--ffmpeg` & `--ffprobe` respectively.

## Attributions

TwitchDownloader - https://github.com/lay295/TwitchDownloader
ffmpeg / ffprobe - https://ffmpeg.org/
Python - https://www.python.org/
