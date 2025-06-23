import logging
from typing import Dict
import ollama
import sqlite3
import os
import uuid
import time
import json
from openfabric_pysdk.context import Ray, State 
from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from core.stub import Stub


configurations: Dict[str, ConfigClass] = dict()


TEXT_TO_IMAGE_APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
IMAGE_TO_3D_APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"

############################################################
# Config callback function - OVERRIDE INCORRECT APP IDs
############################################################
def config(configuration: Dict[str, ConfigClass]) -> None:
    for uid, conf in configuration.items():
        conf.app_ids = [TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID]
        logging.info(f"Corrected config for user '{uid}': {conf.app_ids}")
        configurations[uid] = conf

############################################################
# Execution callback function
############################################################
def execute(request: InputClass, ray: Ray, state: State) -> OutputClass:
    response = OutputClass()
    
    conn = sqlite3.connect('memory.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS memories
                    (id TEXT PRIMARY KEY,
                     user_id TEXT,
                     prompt TEXT,
                     expanded_prompt TEXT,
                     image_path TEXT,
                     model3d_path TEXT,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    try:
        logging.info(f"Processing prompt: {request.prompt}")
        
        llm_response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': request.prompt}],
            options={'temperature': 0.7}
        )
        expanded_prompt = llm_response['message']['content']
        logging.info(f"Expanded prompt: {expanded_prompt}")
        
        stub = Stub([TEXT_TO_IMAGE_APP_ID, IMAGE_TO_3D_APP_ID])
        
       
        image_obj = stub.call(
            TEXT_TO_IMAGE_APP_ID, 
            {'prompt': expanded_prompt}, 
            'super-user'
        )
        image_bytes = image_obj.get('result')
        
        image_filename = f"output_{int(time.time())}.png"
        with open(image_filename, 'wb') as f:
            f.write(image_bytes)
        logging.info(f"Image saved: {image_filename}")
        
        model_obj = stub.call(
            IMAGE_TO_3D_APP_ID, 
            {'image': image_bytes}, 
            'super-user'
        )
        model_bytes = model_obj.get('result')
        
        model_filename = f"model_{int(time.time())}.glb"
        with open(model_filename, 'wb') as f:
            f.write(model_bytes)
        logging.info(f"3D model saved: {model_filename}")
        
        conn.execute(
            "INSERT INTO memories (id, user_id, prompt, expanded_prompt, image_path, model3d_path) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), 'super-user', request.prompt, expanded_prompt, image_filename, model_filename)
        )
        conn.commit()
        
        response.message = json.dumps({
            "status": "success",
            "image": image_filename,
            "model_3d": model_filename,
            "expanded_prompt": expanded_prompt
        }, indent=2)
        
    except Exception as e:
        logging.error(f"Pipeline error: {str(e)}", exc_info=True)
        response.message = json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2)
        
    finally:
        conn.close()
    
    return response