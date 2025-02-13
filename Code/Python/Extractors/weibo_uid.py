import re


class WeiboUIDExtractor:
    """
    A class to extract Weibo user ID from an image URL. The class provides methods
    to extract the user ID, generate the full Weibo URL, and get only the UID.
    """

    def __init__(self, pic_url):
        """
        Initializes the WeiboUIDExtractor with the given picture URL.

        :param pic_url: The URL of the image (string)
        """
        self.pic_url = pic_url

    def from62to10(self, s):
        """
        Converts a string from base 62 to base 10.

        :param s: The base 62 encoded string (string)
        :return: The corresponding base 10 integer (int)
        """
        return sum(
            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".index(c)
            * (62 ** (len(s) - i - 1))
            for i, c in enumerate(s)
        )

    def get_uid(self):
        """
        Extracts the Weibo user ID from the provided image URL. The method checks the
        first 8 characters of the filename and converts the string to a number either
        using base 62 or base 16 based on the pattern.

        :return: The Weibo user ID (int)
        """
        name = self.pic_url.split("/")[-1][:8]
        return (
            int(name, 16)
            if re.match(r"[0-9a-fA-F]{6}", name)
            else self.from62to10(name[2:])
        )

    def get_weibo_url(self):
        """
        Generates the full Weibo URL for the user based on the extracted UID.

        :return: The full Weibo URL (string)
        """
        return f"http://weibo.com/u/{self.get_uid()}"

    def get_uid_only(self):
        """
        Returns only the Weibo user ID.

        :return: The Weibo user ID (int)
        """
        return self.get_uid()


# Example usage:
pic = "https://wx2.sinaimg.cn/large/5f5b23d7gy1hygkp2zpfnj20zk1hj44u.jpg"
weibo = WeiboUIDExtractor(pic)

# Get the full Weibo URL
print(weibo.get_weibo_url())  # Output: http://weibo.com/u/1599808471

# Get only the UID
print(weibo.get_uid_only())  # Output: 1599808471
