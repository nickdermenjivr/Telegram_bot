class NewsItem:
    def __init__(self, prelink, link):
        self.prelink = prelink
        self.link = link

    def format_news(self):
        return f"🔹{self.prelink}{self.link}"