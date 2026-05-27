from unittest.mock import patch, MagicMock
import src.collectors.github_release as gh_mod
from src.collectors.github_release import GithubReleaseCollector

@patch.object(gh_mod, "REPOS", ["owner/repo"])
@patch("src.collectors.github_release.httpx.get")
def test_fetch_raw_returns_releases(mock_get):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [
        {"html_url": "https://gh/r/1", "name": "v1.0", "tag_name": "v1.0",
         "published_at": "2026-05-26T00:00:00Z", "body": "release notes"},
    ]
    mock_get.return_value = resp
    items = GithubReleaseCollector().fetch_raw()
    assert len(items) == 1
    assert items[0]["title"].startswith("[owner/repo]")

@patch.object(gh_mod, "REPOS", ["owner/repo"])
@patch("src.collectors.github_release.httpx.get")
def test_skip_on_non_200(mock_get):
    resp = MagicMock()
    resp.status_code = 404
    mock_get.return_value = resp
    assert GithubReleaseCollector().fetch_raw() == []
