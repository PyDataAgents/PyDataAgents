from bs4 import BeautifulSoup

from pydag.utils.StringUtils import StringUtils


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
            
    def dict_to_htmltable(data: dict) -> str:
        DEFAULT_CELL_STYLE : str = """
        <style>
            .bordered-table {
                border-collapse: collapse; /* make borders appear as single lines */
                width: 100%;
            }

            .bordered-table th,
            .bordered-table td {
                border: 1px solid #000; /* black border for each cell */
                padding: 8px;
                text-align: left;
            }

            .bordered-table th {
                background-color: #f0f0f0; /* optional: header background */
            }
        </style>\n
        """
        if not data:
            return "<table></table>"
        display_cols = list(data.keys())
        html = DEFAULT_CELL_STYLE + "<table class='bordered-table'>\n"
        html += "  <tr>" + "".join(f"<th>{col}</th>" for col in display_cols) + "</tr>\n"        
        if isinstance(data[display_cols[0]], list):
            rows = zip(*[data[c] for c in display_cols])
            for row in rows:
                html += "  <tr>"
                for val in row:
                    if isinstance(val, str) and (StringUtils.is_valid_url(val) or StringUtils.is_valid_file_link(val)):
                        html += f"<td><a href='{val}' target='_blank'>{val}</a></td>"
                    else:
                        html += f"<td>{val}</td>"
                html += "  </tr>\n"
        else:
            html += "  <tr>"
            for key, val in data.items():
                if StringUtils.is_valid_url(val) or StringUtils.is_valid_file_link(val):
                    html += f"<td><a href='{val}' target='_blank'>{val}</a></td>"
                else:
                    html += f"<td>{val}</td>"
            html += "  </tr>\n"       
        html += "</table>"        
        return html