import gradio as gr
import requests

API_URL = "http://localhost:8000/solve"

def solve_problem(problem, max_iterations, use_param_plus):
    try:
        response = requests.post(
            API_URL, 
            json={"problem": problem, "max_iterations": max_iterations, "use_param_plus": use_param_plus}
        )
        if response.status_code == 200:
            data = response.json()
            history = ""
            if "history" in data:
                for idx, mem in enumerate(data["history"]):
                    history += f"### Iteration {idx + 1}\n"
                    history += f"**Attempt:** {mem['attempt']}\n\n"
                    history += f"**Error:** {mem['error']}\n\n"
                    history += f"**Reflection:** {mem['reflection']}\n\n"
                    history += "---\n"
                    
            output_text = f"**Success:** {data['success']}\n\n"
            output_text += f"**Final Solution:**\n```python\n{data['solution']}\n```\n\n"
            
            return output_text, history
        else:
            return f"Error: {response.status_code} - {response.text}", ""
    except Exception as e:
        return f"Connection Error: {str(e)}", ""

demo = gr.Interface(
    fn=solve_problem,
    inputs=[
        gr.Textbox(lines=5, label="Problem Description", placeholder="e.g. Write a Python function to check if a number is prime."),
        gr.Slider(minimum=1, maximum=5, value=3, step=1, label="Max Iterations"),
        gr.Checkbox(value=True, label="Use ParamAgent-plus (Cross-Sample Memory)")
    ],
    outputs=[
        gr.Markdown(label="Final Result"),
        gr.Markdown(label="Reflection History")
    ],
    title="ParamMem Agent",
    description="A deployable interface for the Parametric Reflective Memory Agent. The agent dynamically corrects its own errors without reflection collapse.",
    theme=gr.themes.Glass()
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
