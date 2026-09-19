---
title: ParamMem Reasoning Dashboard
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🧠 ParamMem: Augmenting Language Agents with Parametric Reflective Memory

ParamMem is a research-grade architecture designed to overcome **reflection collapse** in LLM agents. By replacing traditional retrieval-heavy memory with a lightweight **parametric encoding module**, the agent internalizes cross-sample reasoning patterns to generate diverse and effective corrective signals.

## 🎬 System Demo & Launch Walkthrough

<p align="center">
  <img src="assets/demo.gif" alt="ParamMem Reasoning Dashboard Demo" width="100%" />
</p>

## 🚀 Key Features
- **Neural Trace Visualization**: A real-time, "cyber-dark" dashboard built with React and Framer Motion.
- **Parametric Reflection**: LoRA-tuned memory module that provides high-diversity feedback without retrieval overhead.
- **Hybrid Architecture**: Combines Episodic, Parametric, and Cross-Sample (ChromaDB) memory systems.
- **Lightning Fast**: Optimized for the **Groq API**, supporting models like GPT-OSS and Llama-3.

## 🛠️ Architecture
- **Agent**: `ParamAgent` manages the iterative reasoning loop.
- **Memory**: `ParametricMemory` (Local LoRA or Remote API) handles the internal "logic of reflection."
- **Retrieval**: `CrossSampleMemory` utilizes ChromaDB for pattern retrieval.
- **Backend**: FastAPI server providing low-latency solve endpoints.
- **Frontend**: Modern React dashboard with interactive iteration depth and memory toggles.

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 20+
- Groq API Key (for high-speed mode)

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ParamMem.git
   cd ParamMem
   ```

2. **Backend Setup**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your GROQ_API_KEY
   python -m uvicorn src.api.server:app --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd src/web
   npm install
   npm run dev
   ```

## 🐳 Deployment (Hugging Face Spaces)
The project is container-ready. Use the provided `Dockerfile` or run the automated script:
```bash
python deploy_to_hf.py
```

## 📖 Research & Citation
This project is part of ongoing research into reflective language agents.

**Title**: ParamMem: Augmenting Language Agents with Parametric Reflective Memory  
**Conference**: ICLR 2025 (Projected)

```bibtex
@article{parammem2025,
  title={ParamMem: Augmenting Language Agents with Parametric Reflective Memory},
  author={ParamMem Research Group},
  year={2025}
}
```

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.
