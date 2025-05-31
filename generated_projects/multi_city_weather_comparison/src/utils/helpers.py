from typing import Dict, Any, List
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_api_request(url: str, headers: Dict[str, str], params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an API request with retry logic.
    
    Args:
        url (str): API endpoint URL
        headers (Dict[str, str]): Request headers
        params (Dict[str, Any], optional): Query parameters
    
    Returns:
        Dict[str, Any]: API response
    
    Raises:
        Exception: If the request fails after retries
    """
    import requests
    try:
        logger.info(f'Making API request to {url}')
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info('API request successful')
        return response.json()
    except Exception as e:
        logger.error(f'API request failed: {e}')
        raise