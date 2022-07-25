from __future__ import annotations
import pathlib
import requests
from bs4 import BeautifulSoup
import json


class DivarParser:
    def __init__(
        self,
        region: str = "/s/tehran",
        paths: list[str] | None = None,
        n_results: int = 20,
    ):
        self.base_url = "https://www.divar.ir"
        self.region = region
        self.paths = paths or self.get_paths()

    def get_paths(self) -> list[str]:
        res = requests.get(self.base_url + self.region)
        parsed = BeautifulSoup(res.content, "html.parser")

        paths = []
        filter_box = parsed.find("div", class_="filter-box")
        sections = filter_box.find_all("a", "kt-accordion-item__header")  # type: ignore
        for section in sections:
            paths.append(section["href"])
        return paths

    def get_section_titles(self) -> dict[str, list[str]]:
        data = {}
        for path in self.paths:
            res = requests.get(f"{self.base_url}{path}")
            parsed = BeautifulSoup(res.content, "html.parser")
            results = parsed.find_all("div", class_="post-card-item")
            titles = []
            for i, item in enumerate(results[:20]):
                header = item.find("h2", class_="kt-post-card__title")
                titles.append(header.text.strip())
            data[path] = titles
            print(f"Processed {self.base_url}{path}.")
        return data

    def dump_section_titles(
        self, file_path: str | pathlib.Path, data: dict[str, list[str]] | None = None
    ) -> None:
        if data is None:
            data = self.get_section_titles()
        with open(file_path, "w") as f:
            json.dump(data, f)


divar_parser = DivarParser()
data = divar_parser.get_section_titles()
with open("data.txt", "w") as f:
    f.write(str(data))
divar_parser.dump_section_titles("divar-data.json", data)
