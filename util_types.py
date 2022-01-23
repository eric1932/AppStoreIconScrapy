from enum import Enum
from typing import List


class Chart(Enum):
    TOP_FREE = "top-free"
    TOP_PAID = "top-paid"


class Region(Enum):
    CN = "cn"
    US = "us"


class Genre(dict):
    genreId: int
    name: str
    url: str

    def __init__(self, *args, **kwargs):
        super(Genre, self).__init__(*args, **kwargs)
        self.__dict__ = self


class RankingResult(dict):
    artistName: str
    id: int
    name: str
    releaseDate: str
    kind: str
    artworkUrl100: str
    genres: List[Genre]

    def __init__(self, *args, **kwargs):
        super(RankingResult, self).__init__(*args, **kwargs)
        self.__dict__ = self
        if self.get('genres', None):
            self.genres = list(map(Genre, self.genres))
