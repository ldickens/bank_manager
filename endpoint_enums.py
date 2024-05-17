from enum import Enum, unique


@unique
class Endpoints(Enum):
    GET_MEDIA_MAP = "/media/map"
    GET_MEDIA = "/media"
    GET_MEDIA_DATA = "/media/"
    POST_MEDIA = "/media/upload"
    GET_THUMB = "/media/thumb/"
    PUT_ENTRY = "/media/addmapentry/"
