import json
from typing import Dict, List
from urllib.request import urlopen

from types import Chart, Region, RankingResult


def get_top_ranking_apps(region: Region = Region.CN,
                         chart: Chart = Chart.TOP_FREE,
                         result_limit: int = 10) -> List[RankingResult]:
    api_url = f"https://rss.applemarketingtools.com/api/v2" \
              f"/{region.value}/apps/{chart.value}/{result_limit}/apps.json"
    j: Dict = json.loads(urlopen(api_url).read().decode())
    return list(map(RankingResult, j.get("feed", {}).get("results", None)))


if __name__ == '__main__':
    t = get_top_ranking_apps()
    print(t[0].genres[0].genreId)
