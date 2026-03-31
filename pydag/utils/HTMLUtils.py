from bs4 import BeautifulSoup


class HTMLUtils:
    
    @staticmethod
    def open_html_doc(html_file : str) -> BeautifulSoup:
        """Load an HTML file and return a BeautifulSoup object."""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return BeautifulSoup(content, 'html.parser')
    
    @staticmethod
    def save_html_doc(soup : BeautifulSoup, output_file : str):
        """Save a BeautifulSoup object to an HTML file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    
    @staticmethod
    def replace_value_by_id(soup : BeautifulSoup, element_id : str, new_value : str):
        """Find an element by ID and replace its value."""
        element = soup.find(id=element_id)
        if element:
            element['value'] = new_value
    
    @staticmethod
    def replace_values_by_tag(soup : BeautifulSoup, tag : str, new_text : str):
        """Find an element by ID and replace its text."""
        for element in soup.find_all(tag):
            element.string = new_text