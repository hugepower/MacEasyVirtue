import json
import re


class StringTransformer:
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")
        self.text = text.strip()
        if not self.text:
            raise ValueError("Input string cannot be empty.")

    def _convert_case(
        self, separator: str, capitalize_first: bool = False, title_case: bool = False
    ):
        """
        Converts the string `self.text` to different formats, adjusting the case and separator based on the specified conditions.

        Parameters:
        separator (str): The separator used to join the words. For example, `'-'` or `'_'`.
        capitalize_first (bool, optional): If True, the function converts the first word to lowercase and capitalizes the first letter of subsequent words (camelCase). Default is False.
        title_case (bool, optional): If True, the function capitalizes the first letter of each word (Title Case). Default is False.

        Returns:
        str: The converted string, with words joined by `separator`.

        Examples:
        - If `self.text = "hello world_example"` and `separator = "_"`:
            - When `capitalize_first=True`, returns `"helloWorld_example"`
            - When `title_case=True`, returns `"Hello_World_Example"`
            - By default, returns `"hello_world_example"`
        """
        # Use regular expression to split `self.text` into words, using spaces or underscores as separators
        words = re.split(r"\s+|_", self.text)

        # If title_case is True, capitalize the first letter of each word
        if title_case:
            return separator.join(word.capitalize() for word in words)

        # If capitalize_first is True, lowercase the first word and capitalize the first letter of subsequent words
        if capitalize_first:
            return words[0].lower() + "".join(word.capitalize() for word in words[1:])

        # By default, convert all words to lowercase and join them with the separator
        return separator.join(word.lower() for word in words)

    def to_lower(self):
        """Converts text to lowercase."""
        return self.text.lower()

    def to_upper(self):
        """Converts text to uppercase."""
        return self.text.upper()

    def to_title_case(self):
        """Converts text to title case (first letter of each word capitalized)."""
        return self.text.title()

    def to_camel_case(self):
        """Converts text to camel case (first word lowercase, others capitalized)."""
        return self._convert_case("", capitalize_first=True)

    def to_pascal_case(self):
        """Converts text to Pascal case (capitalizes first letter of every word)."""
        return self._convert_case("", capitalize_first=False, title_case=True)

    def to_snake_case(self):
        """Converts text to snake case (words joined with underscores, all lowercase)."""
        return self._convert_case("_", capitalize_first=False)

    def to_upper_snake_case(self):
        """Converts text to upper snake case (words joined with underscores, all uppercase)."""
        return self.to_snake_case().upper()

    def to_kebab_case(self):
        """Converts text to kebab case (words joined with hyphens, all lowercase)."""
        return self._convert_case("-", capitalize_first=False)

    def to_upper_kebab_case(self):
        """Converts text to upper kebab case (words joined with hyphens, all uppercase)."""
        return self.to_kebab_case().upper()

    def to_title_kebab_case(self):
        """Converts text to title kebab case (words joined with hyphens, first letter of each word capitalized)."""
        return self._convert_case("-", capitalize_first=False, title_case=True)

    def to_title_snake_case(self):
        """Converts text to title snake case (words joined with underscores, first letter of each word capitalized)."""
        return self._convert_case("_", capitalize_first=False, title_case=True)

    def to_json(self):
        """
        Returns a JSON string containing all converted variations of the original text.
        """
        data = {
            "original": self.text,
            "lower": self.to_lower(),
            "upper": self.to_upper(),
            "title_case": self.to_title_case(),
            "title_snake_case": self.to_title_snake_case(),
            "camel_case": self.to_camel_case(),
            "pascal_case": self.to_pascal_case(),
            "snake_case": self.to_snake_case(),
            "upper_snake_case": self.to_upper_snake_case(),
            "kebab_case": self.to_kebab_case(),
            "upper_kebab_case": self.to_upper_kebab_case(),
            "title_kebab_case": self.to_title_kebab_case(),
        }
        return json.dumps(data, indent=4)


try:
    text = "this should be a simple example for you"
    transformer = StringTransformer(text)
    print(transformer.to_json())
except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"Unexpected error: {e}")

"""
output:

{
    "original": "this should be a simple example for you",
    "lower": "this should be a simple example for you",
    "upper": "THIS SHOULD BE A SIMPLE EXAMPLE FOR YOU",
    "title_case": "This Should Be A Simple Example For You",
    "title_snake_case": "This_Should_Be_A_Simple_Example_For_You",
    "camel_case": "thisShouldBeASimpleExampleForYou",
    "pascal_case": "ThisShouldBeASimpleExampleForYou",
    "snake_case": "this_should_be_a_simple_example_for_you",
    "upper_snake_case": "THIS_SHOULD_BE_A_SIMPLE_EXAMPLE_FOR_YOU",
    "kebab_case": "this-should-be-a-simple-example-for-you",
    "upper_kebab_case": "THIS-SHOULD-BE-A-SIMPLE-EXAMPLE-FOR-YOU",
    "title_kebab_case": "This-Should-Be-A-Simple-Example-For-You"
}
"""
