class NewsItem:
    def __init__(self, link):
        self.link = link

    def format_news(self):
        return f"{self.link}"

    def __eq__(self, other):
        if isinstance(other, NewsItem):
            return self.link == other.link
        return False