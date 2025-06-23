import gradio as gr
import requests
import json
import os

OPENFABRIC_API = "http://localhost:8888/execution"

def generate_assets(prompt: str):
    try:
        response = requests.post(
            OPENFABRIC_API,
            json={"prompt": prompt},
            timeout=300  
        )
        response.raise_for_status()
        
        result = json.loads(response.json().get("message", "{}"))
        
        if result.get("status") == "success":
            return (
                result["expanded_prompt"],
                result["image"],
                result["model_3d"]
            )
        else:
            return f"Error: {result.get('message', 'Unknown error')}", None, None
            
    except Exception as e:
        return f"Pipeline error: {str(e)}", None, None


with gr.Blocks(title="Openfabric Creative Partner") as demo:
    gr.Markdown("""
    # 🐉 Creative Partner
    *Describe your vision, and watch it come to life!*
    """)
    
    with gr.Row():
        prompt_input = gr.Textbox(
            label="Describe your creation",
            placeholder="A glowing dragon standing on a cliff at sunset...",
            lines=3
        )
    
    submit_btn = gr.Button("Generate", variant="primary")
    
    with gr.Column():
        expanded_prompt = gr.Textbox(label="Expanded Description", interactive=False)
        
        with gr.Row():
            image_output = gr.Image(label="Generated Image", type="filepath")
            model_output = gr.File(label="3D Model", type="filepath")
    
    submit_btn.click(
        fn=generate_assets,
        inputs=prompt_input,
        outputs=[expanded_prompt, image_output, model_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
