from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

# This tool is given to the agent to look up information about a customer
@tool
def get_customer_info(customer_id: int, first_name: str, last_name: str):
    """
    Retrieves customer information from the database based on Customer ID, First Name, and Last Name.
    If Customer ID, First Name, and Last Name is not supplied, then ask the user to provide them.
    Do not retrive customer information if Customer ID, First Name, and Last Name is not supplied.
    
    Args:
        customer_id (int): The unique ID of the customer.
        first_name (str): The first name of the customer.
        last_name (str): The last name of the customer.

    Returns:
        dict: A dictionary containing customer information, or an error message.
    """
    return {'customer_id': 1, 'first_name': 'Neil', 'last_name': 'Manvar'}
    

tools = [get_customer_info]

