# type definitions
MEDIA_DATA = dict[str, int | bool | str | list[int]]
"""
{
  "aspectRatio": 0,
  "audioChannels": 0,
  "audioSampleRate": 0,
  "canBeDeleted": true,
  "duration": 0,
  "durationFrames": 0,
  "fileName": "string",
  "fileSize": 0,
  "fileType": "string",
  "fps": 0,
  "hasAlpha": true,
  "height": 0,
  "iD": "string",
  "mapIndexes": [
    0
  ],
  "timeUploaded": "string",
  "width": 0
}
"""

MEDIA_MAP = dict[str, list[dict[str, str | int]]]
"""
{
  "entries": [
    {
      "index": 0,
      "mediaID": "string",
      "name": "string"
    }
  ]
}
"""

MEDIA_FILE = list[str]
"""
{
  "mediaFiles": [
    {
      "folderPath": "string",
      "mediaID": "string",
      "name": "string"
    }
  ]
}
"""

MEDIA_MAP_ENTRY = list[str | int]
"""
[
"index": 0,
"mediaID": "string",
"name": "string"
]
"""
