# Offline Piper text-to-speech

The optional Piper adapter synthesizes narration locally from text using a pre-installed Piper executable and an existing local voice model. It does not download models or call a cloud API.

## Use

```sh
btm-synthesize script-narration.txt /path/to/voice.onnx voice-model-asset-id rights-ledger.json narration.wav
```

The voice model must be listed in a structurally valid rights ledger, with license and commercial-use permissions reviewed by a human. This adapter does not determine whether a particular model/voice license is legally sufficient.

After synthesis, add a separate provenance record for the generated narration output before passing it to the renderer. Do not assume the model's license automatically clears the generated audio or the chosen use.

## Install

Install Piper and obtain a compatible model through the appropriate distribution. This repository does not download or install binaries/models. Check the license, attribution requirements, commercial-use terms, and voice-specific restrictions before use. If those terms are unclear, do not use the model.

## Limits

The adapter creates an audio file only. It does not assess pronunciation, pacing, emotion, factual accuracy, consent/voice likeness, or suitability. Listen to the entire narration and human-review it before rendering.
