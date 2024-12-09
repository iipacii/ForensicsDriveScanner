import os
from dotenv import load_dotenv
import requests
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Optional, Dict, Any


# Load environment variables
load_dotenv()

class VirusScanner:
    def __init__(self):
        self.logger = logging.getLogger("virus_scanner")
        self.logger.info("Initializing VirusScanner")
        
        self.api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.base_url = os.getenv('VIRUSTOTAL_API_URL')
        
        if not self.api_key:
            self.logger.error("VIRUSTOTAL_API_KEY not found")
            raise ValueError("VIRUSTOTAL_API_KEY not found")
            
        self.cache_file = Path("hash_cache.json")
        self.cache = self._load_cache()
        self.logger.info("VirusScanner initialized successfully")

    def _convert_timestamp(self, timestamp):
        if not timestamp:
            return None
        try:
            return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            self.logger.error(f"Error converting timestamp: {e}")
            return None  
        
    def _load_cache(self):
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.logger.info(f"Cache loaded successfully with {len(cache_data)} entries")
                    return cache_data
            self.logger.info("No cache file found, creating new cache")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
            return {}

    def _save_cache(self):
        """Save virus scan results to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
        except Exception as e:
            print(f"Error saving cache: {e}")

    # virus_scanner.py
    def check_hash(self, file_hash: str) -> Dict[str, Any]:
        self.logger.info(f"Checking hash: {file_hash}")
        
        try:
            if file_hash in self.cache:
                cache_data = self.cache[file_hash]
                self.logger.info(f"Cache hit for hash: {file_hash}")
                
                # Validate cached data structure
                if not isinstance(cache_data, dict) or "message" not in cache_data:
                    self.logger.warning(f"Invalid cache data for hash {file_hash}, fetching fresh data")
                    del self.cache[file_hash]
                else:
                    return cache_data
            
            headers = {
                "accept": "application/json",
                "x-apikey": self.api_key
            }

            self.logger.debug(f"Making API request to VirusTotal for hash: {file_hash}")
            response = requests.get(
                f"{self.base_url}/files/{file_hash}",
                headers=headers,
                timeout=10  # Add timeout
            )
            
            self.logger.info(f"API Response received - Status: {response.status_code}")
            
            result = {
                "status_code": response.status_code,
                "data": None,
                "message": "Unknown error",  # Default message
                "error_details": None,
                "timestamp": datetime.utcnow().isoformat()
            }

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    
                    # Validate response structure
                    if not isinstance(json_response, dict) or "data" not in json_response:
                        raise ValueError("Invalid response format from VirusTotal API")
                        
                    data = json_response.get("data", {})
                    attrs = data.get("attributes", {})
                    
                    filtered_data = {
                        "last_analysis_stats": attrs.get("last_analysis_stats", {}),
                        "signature_verified": attrs.get("signature_info", {}).get("verified", False),
                        "total_votes": attrs.get("total_votes", {}),
                        "last_analysis_date": self._convert_timestamp(attrs.get("last_analysis_date"))
                    }
                    
                    result.update({
                        "data": filtered_data,
                        "message": "File analysis complete",
                        "error_details": None
                    })
                    self.logger.info(f"Successfully parsed data for hash: {file_hash}")
                    
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    self.logger.error(f"Failed to parse API response for hash {file_hash}: {str(e)}")
                    result.update({
                        "message": "Error parsing API response",
                        "error_details": str(e)
                    })
                    
            elif response.status_code == 404:
                result["message"] = "File not found in VirusTotal database"
            elif response.status_code == 401:
                result["message"] = "Invalid API key"
                self.logger.error("API authentication failed")
            else:
                result.update({
                    "message": f"Unexpected API response: {response.status_code}",
                    "error_details": response.text[:200]  # Limit error text length
                })

            # Cache only valid responses
            if response.status_code in (200, 404) and result["message"] != "Error parsing API response":
                self.cache[file_hash] = result
                self._save_cache()
                self.logger.debug(f"Cached result for hash: {file_hash}")

            return result

        except requests.RequestException as e:
            error_msg = f"API request failed for hash {file_hash}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "status_code": 500,
                "data": None,
                "message": "API request failed",
                "error_details": str(e)
            }
        except Exception as e:
            error_msg = f"Unexpected error checking hash {file_hash}: {str(e)}"
            self.logger.exception(error_msg)
            return {
                "status_code": 500,
                "data": None, 
                "message": "Internal error",
                "error_details": str(e)
            }