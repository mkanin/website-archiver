import waybackpy


class Archiver:

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def archive(self, url):
        wayback = waybackpy.Url(url, self.user_agent)
        archive = wayback.save()
        return archive.archive_url
