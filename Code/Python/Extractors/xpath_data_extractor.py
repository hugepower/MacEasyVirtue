from lxml import etree


def extract_with_xpath(html, xpath_expressions):
    """
    Extracts data from an HTML string using XPath expressions.

    Parameters:
    - html: str, the HTML string to be parsed
    - xpath_expressions: dict, a dictionary containing field names as keys
      and corresponding XPath expressions as values

    Returns:
    - result: dict, extracted data where keys are field names and values are the extracted content
    """
    tree = etree.HTML(html, parser=etree.HTMLParser())
    result = {}

    for key, xpath in xpath_expressions.items():
        # Use XPath to extract data and store it in the result dictionary
        elements = tree.xpath(xpath)
        if elements:
            result[key] = elements[0]  # Retrieve the first matching element's content
        else:
            result[key] = None  # If no match is found, store None

    return result


# Sample HTML string
html = """
<html>
  <head>
    <title>Example Page Title</title>
  </head>
  <body>
    <div class="article">
      <h1 class="title">Example Article Title</h1>
      <p class="content">This is the content of the article.</p>
    </div>
  </body>
</html>
"""

# XPath expressions defined in the configuration
xpath_expressions = {
    "title_tag": "//title/text()",  # Extract content from the <title> tag
    "article_title": "//div[@class='article']/h1[@class='title']/text()",  # Extract article title
    "content": "//div[@class='article']/p[@class='content']/text()",  # Extract article content
}

# Extract data using the function
extracted_data = extract_with_xpath(html, xpath_expressions)

# Print the extracted data
print("Page Title:", extracted_data["title_tag"])
print("Article Title:", extracted_data["article_title"])
print("Content:", extracted_data["content"])
