class url:
   full_url = ""
   url_location = ""

   def __init__(self, full_url, url_location):
       self.full_url = full_url
       self.region = url_location


def create_url(full_url, region):

   url = create_url(full_url, region)
   return url