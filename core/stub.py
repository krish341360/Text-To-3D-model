import json
import logging
import time
from typing import Any, Dict, List, Literal, Tuple, Optional

import requests
from requests.exceptions import RequestException

from core.remote import Remote

# Type aliases
Manifests = Dict[str, dict]
Schemas = Dict[str, Tuple[dict, dict]]
Connections = Dict[str, Remote]


class Stub:
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, app_ids: List[str]):
        self._schema: Schemas = {}
        self._manifest: Manifests = {}
        self._connections: Connections = {}
        
        for app_id in app_ids:
            self._init_app(app_id)

    def _init_app(self, app_id: str):
        app_nodes = {
            "f0997a01-d6d3-a5fe-53d8-561300318557": "f0997a01-d6d3-a5fe-53d8-561300318557.node3.openfabric.network",
            "69543f29-4d41-4afc-7f29-3d51591f11eb": "69543f29-4d41-4afc-7f29-3d51591f11eb.node5.openfabric.network"
        }
        base_url = app_nodes.get(app_id)
        if not base_url:
            raise ValueError(f"Unknown app ID: {app_id}")
        logging.info(f"Initializing app: {base_url}")

        for attempt in range(self.MAX_RETRIES):
            try:
                manifest = self._fetch_json(f"https://{base_url}/manifest")
                self._manifest[app_id] = manifest
                logging.info(f"[{base_url}] Manifest loaded")

                input_schema = self._fetch_json(f"https://{base_url}/schema?type=input")
                output_schema = self._fetch_json(f"https://{base_url}/schema?type=output")
                self._schema[app_id] = (input_schema, output_schema)
                logging.info(f"[{base_url}] Schemas loaded")


                self._connections[app_id] = self._create_connection(base_url)
                return  # Success, exit retry loop
                
            except RequestException as e:
                logging.warning(f"[{base_url}] Attempt {attempt+1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    logging.error(f"[{base_url}] Initialization failed after {self.MAX_RETRIES} attempts")
                    raise

    def _fetch_json(self, url: str) -> dict:
        try:
            response = requests.get(url, timeout=10, allow_redirects=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error for {url}: {e.response.status_code}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url}: {str(e)}")
            raise

    def _create_connection(self, base_url: str) -> Remote:
        """Create and connect Remote instance with proper resource URL"""
        ws_url = f"wss://{base_url}/app"
        resource_url = f"https://{base_url}/resource?reid={{reid}}"
        remote = Remote(ws_url, f"{base_url}-proxy", resource_url)
        return remote.connect()

    def _json_schema_to_marshmallow(self, schema: dict):
        """Convert JSON schema to a Marshmallow schema."""
        from marshmallow import Schema, fields

        class DynamicSchema(Schema):
            pass

        for field_name, field_props in schema.get("properties", {}).items():
            field_type = field_props.get("type")
            if field_type == "string":
                setattr(DynamicSchema, field_name, fields.String())
            elif field_type == "integer":
                setattr(DynamicSchema, field_name, fields.Integer())
            elif field_type == "boolean":
                setattr(DynamicSchema, field_name, fields.Boolean())
            elif field_type == "array":
                setattr(DynamicSchema, field_name, fields.List(fields.String()))  # Adjust as needed
            else:
                setattr(DynamicSchema, field_name, fields.Raw())
        return DynamicSchema

    def _resolve_resources(self, base_url: str, data: dict, schema):
        """Resolve resources in the data using the schema."""
        resolved_data = {}
        for key, value in data.items():
            if key in schema.fields and isinstance(value, str) and value.startswith("http"):
                resolved_data[key] = f"{base_url}/{value}"
            else:
                resolved_data[key] = value
        return resolved_data

    # def call(self, app_id: str, data: Any, uid: str = 'super-user') -> dict:
    #     connection = self._connections.get(app_id)
    #     if not connection:
    #         raise ConnectionError(f"No connection for app: {app_id}")
        
    #     try:
    #         # Execute request
    #         handler = connection.execute(data, uid)
    #         result = connection.get_response(handler)
            
    #         # Handle resource resolution
    #         _, output_schema = self._schema[app_id]
    #         marshmallow = self._json_schema_to_marshmallow(output_schema)
            
    #         if any(field in marshmallow().fields for field in ['resource', 'url', 'link']):
    #             result = self._resolve_resources(
    #                 self._manifest[app_id].get('dos', ''),
    #                 result,
    #                 marshmallow()
    #             )
    #         return result
            
    #     except Exception as e:
    #         logging.error(f"[{app_id}] Execution failed: {str(e)}")
    #         raise  # Propagate to caller
    def call(self, app_id: str, data: dict, user: str):
        full_address = self.app_nodes.get(app_id)
        if not full_address:
            raise ValueError(f"Unknown app ID: {app_id}")
        
        
        response = requests.post(
            f"https://{full_address}/execute",
            json=data,
            headers={"Authorization": f"Bearer {user}"},
            timeout=30
        )
        return response.json()

    def manifest(self, app_id: str) -> dict:
        return self._manifest.get(app_id, {})

    def schema(self, app_id: str, schema_type: Literal['input', 'output']) -> dict:
        schemas = self._schema.get(app_id)
        if not schemas:
            raise ValueError(f"No schemas found for app: {app_id}")
            
        if schema_type == 'input':
            return schemas[0]
        elif schema_type == 'output':
            return schemas[1]
        else:
            raise ValueError("schema_type must be 'input' or 'output'")

    def reconnect(self, app_id: str):
        """Reconnect to an application"""
        if app_id in self._connections:
            self._connections[app_id].disconnect()
        self._init_app(app_id)