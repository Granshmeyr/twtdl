import datetime
import json
import os
import subprocess
import argparse
import textwrap
from typing import Optional
from pathvalidate import sanitize_filename


class CommandLine:
    def __init__(self):
        parser = argparse.ArgumentParser(formatter_class=CustomHelpFormatter)

        parser.add_argument(
            "vod-id",
            type=int,
            help=textwrap.dedent(
                """\
                ID of the Twitch VOD
                """
            ),
        )

        parser.add_argument(
            "-q",
            "--quality",
            type=str,
            required=False,
            help=textwrap.dedent(
                """\
                Desired video quality settings.
                Example: 1080p60, 720p, 480p30

                Default: source

                """
            ),
        )

        parser.add_argument(
            "-n",
            "--chat-width",
            type=float,
            required=False,
            default="0.40",
            help=textwrap.dedent(
                """\
                Scale chat width relative to video width.
                A value of 0.33 means chat spans 33%% of video width.

                Default: "0.40"

                """
            ),
        )

        parser.add_argument(
            "-m",
            "--chat-height",
            type=float,
            required=False,
            default="0.40",
            help=textwrap.dedent(
                """\
                Scale chat height relative to video height.
                A value of 0.25 means chat spans 25%% of video height.

                Default: "0.40"

                """
            ),
        )

        parser.add_argument(
            "-o",
            "--chat-opacity",
            type=float,
            required=False,
            default="0.6",
            help=textwrap.dedent(
                """\
                Opacity of chat background.
                A value of 0.6 means 60%% opacity.

                Default: "0.6"

                """
            ),
        )

        parser.add_argument(
            "-s",
            "--font-size",
            type=int,
            required=False,
            help=textwrap.dedent(
                """\
                Font size of chat, scaling with video resolution.
                Example starting from "30":
                1080p: 30 | 720p: 20 | 480p: 13 | 360p: 10
                Formula is {font_size} * {video_height} / 1080

                Default: "30"

                """
            ),
        )

        parser.add_argument(
            "-g",
            "--gamma",
            type=float,
            required=False,
            help=textwrap.dedent(
                """\
                Gamma adjustment applied to video.

                """
            ),
        )

        parser.add_argument(
            "-t",
            "--twitch-dl",
            type=str,
            required=False,
            help=textwrap.dedent(
                """\
                Path to TwitchDownloaderCLI binary.

                Default: PATH, env

                """
            ),
        )

        parser.add_argument(
            "-f",
            "--ffmpeg",
            type=str,
            required=False,
            help=textwrap.dedent(
                """\
                Path to FFmpeg binary.

                Default: PATH, env

                """
            ),
        )

        parser.add_argument(
            "-p",
            "--ffprobe",
            type=str,
            required=False,
            help=textwrap.dedent(
                """\
                Path to FFprobe binary.

                Default: PATH, env

                """
            ),
        )

        parser.add_argument(
            "-l",
            "--temp",
            type=str,
            required=False,
            default="./vods/temp",
            help=textwrap.dedent(
                """\
            Path to use for cache.
            Contains very large temporary video files.

            Default: working_directory/vods/temp

            """
            ),
        )

        args = parser.parse_args()

        dataPath = f"./vods/data/{str(getattr(args, 'vod-id'))}"
        outputPath = f"./vods/rendered"

        DownloadVODAndChat(
            dataPath=dataPath,
            vodId=getattr(args, "vod-id"),
            quality=args.quality,
            twitchDlPath=args.twitch_dl,
            tmpPath=args.temp,
            ffmpegPath=args.ffmpeg,
        )

        metadata = Metadata(filePath=f"{dataPath}/vod.mp4", ffprobePath=args.ffprobe)

        outputName = f"[{metadata.hour}h{metadata.minute}m{metadata.second}s] {sanitize_filename(metadata.artist)} - {sanitize_filename(metadata.title)}"

        RenderAndBurnChat(
            chatScaleW=args.chat_width,
            chatScaleH=args.chat_height,
            chatOpacity=args.chat_opacity,
            gamma=args.gamma,
            fontSize=args.font_size,
            videoW=metadata.width,
            videoH=metadata.height,
            dataPath=dataPath,
            outputPath=outputPath,
            outputName=outputName,
            tmpPath=args.temp,
            twitchDlPath=args.twitch_dl,
            ffmpegPath=args.ffmpeg,
        )


class Metadata:
    def __init__(self, filePath: str, ffprobePath: str):
        self.artist: str
        self.title: str
        self.second: str
        self.minute: str
        self.hour: str
        self.width: int
        self.height: int

        ffprobe = [
            ffprobePath
            if isinstance(ffprobePath, str)
            else "ffprobe.exe"
            if os.name == "nt"
            else "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            filePath,
        ]

        process = subprocess.run(
            ffprobe,
            stdout=subprocess.PIPE,
        )
        output = json.loads(process.stdout.decode("utf-8"))

        seconds, milliseconds = map(int, output["format"]["duration"].split("."))
        duration = str(
            datetime.timedelta(seconds=seconds + (milliseconds / 1000))
        ).split(":")

        self.artist = output["format"]["tags"]["artist"]
        self.title = output["format"]["tags"]["title"]
        self.second = "{:02d}".format(int(duration[2]))
        self.minute = "{:02d}".format(int(duration[1]))
        self.hour = "{:02d}".format(int(duration[0]))
        self.width = int(output["streams"][0]["coded_width"])
        self.height = int(output["streams"][0]["coded_height"])


def DownloadVODAndChat(
    dataPath: str,
    vodId: int,
    quality: Optional[str],
    tmpPath: Optional[str],
    twitchDlPath: Optional[str],
    ffmpegPath: Optional[str],
) -> None:
    videodownloadProc = [
        twitchDlPath
        if isinstance(twitchDlPath, str)
        else "TwitchDownloaderCLI.exe"
        if os.name == "nt"
        else "TwitchDownloaderCLI",
        "videodownload",
        "--id",
        str(vodId),
        "--temp-path",
        tmpPath,
        "--output",
        f"{dataPath}/vod.mp4",
    ]

    match (isinstance(ffmpegPath, str), isinstance(quality, str)):
        case (True, False):
            videodownloadProc.extend(["--ffmpeg-path", ffmpegPath])
        case (False, True):
            videodownloadProc.extend(["--quality", quality])
        case (True, True):
            videodownloadProc.extend(
                ["--ffmpeg-path", ffmpegPath] + ["--quality", quality]
            )

    chatdownloadProc = [
        twitchDlPath
        if isinstance(twitchDlPath, str)
        else "TwitchDownloaderCLI.exe"
        if os.name == "nt"
        else "TwitchDownloaderCLI",
        "chatdownload",
        "--id",
        str(vodId),
        "--temp-path",
        tmpPath,
        "--output",
        f"{dataPath}/chat.json",
    ]

    subprocess.run(videodownloadProc)
    subprocess.run(chatdownloadProc)


def RenderAndBurnChat(
    chatScaleW: float,
    chatScaleH: float,
    chatOpacity: float,
    gamma: Optional[float],
    fontSize: Optional[float],
    dataPath: str,
    videoW: int,
    videoH: int,
    outputPath: str,
    outputName: str,
    tmpPath: Optional[str],
    twitchDlPath: Optional[str],
    ffmpegPath: Optional[str],
) -> None:
    chatrenderProc = [
        twitchDlPath
        if isinstance(twitchDlPath, str)
        else "TwitchDownloaderCLI.exe"
        if os.name == "nt"
        else "TwitchDownloaderCLI",
        "chatrender",
        "--input",
        f"{dataPath}/chat.json",
        "--chat-width",
        str(int(chatScaleW * videoW)),
        "--chat-height",
        str(int(chatScaleH * videoH)),
        "--framerate",
        "30",
        "--font-size",
        f"{fontSize * (videoH / 1080)}"
        if isinstance(fontSize, int)
        else f"{30 * (videoH / 1080)}",
        "--temp-path",
        tmpPath,
        "--output",
        f"{dataPath}/chat.mp4",
        "--verbose-ffmpeg",
        "--generate-mask",
        "--background-color",
        "#00000000",
    ]

    if isinstance(ffmpegPath, str):
        chatrenderProc.extend(["--ffmpeg-path", ffmpegPath])

    boxX = videoW - int(chatScaleW * videoW)
    boxY = 0

    gammaCheck = isinstance(gamma, float)

    filterComplex = (
        "[1:v][2:v]alphamerge[chat];"
        + f"color=c=black@{chatOpacity}:size={int(chatScaleW * videoW)}x{int(chatScaleH * videoH)}[box];"
        + f"{'[gamma]' if gammaCheck else '[0:v]'}[box]overlay=x={boxX}:y={boxY}[video];"
        + "[video][chat]overlay=main_w-overlay_w-0:0:shortest=1"
    )

    if gammaCheck:
        filterComplex = f"[0:v]eq=gamma={gamma}[gamma];" + filterComplex

    ffmpegProc = [
        ffmpegPath
        if isinstance(ffmpegPath, str)
        else "ffmpeg.exe"
        if os.name == "nt"
        else "ffmpeg",
        "-i",
        f"{dataPath}/vod.mp4",
        "-i",
        f"{dataPath}/chat.mp4",
        "-i",
        f"{dataPath}/chat_mask.mp4",
        "-filter_complex",
        filterComplex,
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        f"{outputPath}/{outputName}.mp4",
        "-y",
    ]

    os.makedirs(outputPath, exist_ok=True)

    subprocess.run(chatrenderProc)
    subprocess.run(ffmpegProc)


class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def _get_help_string(self, action):
        if isinstance(action, argparse._HelpAction):
            return textwrap.dedent(
                """\
                Show this help message and exit.

                """
            )
        return super()._get_help_string(action)


if __name__ == "__main__":
    app = CommandLine()
