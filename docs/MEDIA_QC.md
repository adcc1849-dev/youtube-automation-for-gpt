# Local media technical inspection

The `btm-inspect-media` command invokes a locally installed `ffprobe` executable. It does not make network requests or upload the file.

## Install FFmpeg

Install FFmpeg/ffprobe using the package manager appropriate to your environment. Android/Termux users should use Termux packages, not assume Ubuntu's package manager. This repository does not install system packages automatically.

## Run

```sh
btm-inspect-media output.mp4
```

The default channel format requires an 8–12 minute media file with both audio and video streams. The command returns JSON containing duration, stream checks, and blockers. Exit status is zero only when the checks pass.

## Limits

A passing result confirms only that ffprobe found a readable file with expected duration and audio/video streams. It does not establish visual quality, audible narration, synchronization, factual accuracy, copyright, rights clearance, or YouTube policy compliance. A human review and the remaining release gates are still required.
