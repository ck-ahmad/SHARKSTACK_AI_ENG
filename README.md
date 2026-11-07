<div align="center">

<br>

# 🦈 AI Engineer Roadmap

### *From fundamentals to mastery in 13 weeks*

<br>

![Duration](https://img.shields.io/badge/Duration-13_Weeks-0A66C2?style=for-the-badge&labelColor=0b1220)
![Level](https://img.shields.io/badge/Level-Beginner_→_Advanced-8A2BE2?style=for-the-badge&labelColor=0b1220)
![Focus](https://img.shields.io/badge/Focus-AI_Engineering-FF6F61?style=for-the-badge&labelColor=0b1220)
![Outcome](https://img.shields.io/badge/Outcome-Capstone_Project-2ea44f?style=for-the-badge&labelColor=0b1220)

![Week 1](https://img.shields.io/badge/Week_1-Complete-2ea44f?style=flat-square&logo=checkmarx&logoColor=white)
![Projects](https://img.shields.io/badge/Projects_Shipped-5-0A66C2?style=flat-square)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white)

<br>

**A training program by SharkStack**
<br>
<sub>Followed by a potential permanent position, based on your performance and trainer feedback.</sub>

<br>

[🌊 Journey](#-the-journey-at-a-glance) &nbsp;·&nbsp;
[🗺️ Overview](#️-overview) &nbsp;·&nbsp;
[📚 Weekly Plan](#-week-by-week) &nbsp;·&nbsp;
[🧰 Tech Stack](#-tech-stack-at-a-glance) &nbsp;·&nbsp;
[🏆 Capstone](#-week-13--capstone-project) &nbsp;·&nbsp;
[🚀 Projects](#-my-projects) &nbsp;·&nbsp;
[✅ Progress](#-progress-tracker)

</div>

<br>

---

## 🌊 The journey at a glance

```mermaid
flowchart LR
    A["🌱 FOUNDATIONS<br/>W1 · W2 · W3"] --> B["🔬 MACHINE LEARNING<br/>W4 · W5"]
    B --> C["🤖 OPEN SOURCE & AGENTS<br/>W6 · W7"]
    C --> D["⚙️ AUTOMATION<br/>W8 · W9"]
    D --> E["🎙️ MULTIMODAL<br/>W10"]
    E --> F["🚀 PRODUCTION<br/>W11 · W12"]
    F --> G["🏆 CAPSTONE<br/>W13"]

    style A fill:#e8f5e9,stroke:#2ea44f,color:#0b1220
    style B fill:#e3f2fd,stroke:#0A66C2,color:#0b1220
    style C fill:#f3e5f5,stroke:#8A2BE2,color:#0b1220
    style D fill:#fff3e0,stroke:#f59e0b,color:#0b1220
    style E fill:#fce4ec,stroke:#e11d74,color:#0b1220
    style F fill:#e0f7fa,stroke:#0891b2,color:#0b1220
    style G fill:#fff9c4,stroke:#eab308,color:#0b1220
```

<div align="center">

| 🌱 Foundations | 🔬 Machine Learning | 🤖 Open Source & Agents |
|:---:|:---:|:---:|
| **W1** APIs & Chatbots | **W4** ML Fundamentals | **W6** Local LLMs & Deployment |
| **W2** Prompting | **W5** Deep Learning | **W7** Agents & Workflows |
| **W3** Embeddings & RAG | | |

| ⚙️ Automation | 🎙️ Multimodal | 🚀 Production |
|:---:|:---:|:---:|
| **W8** n8n & Zapier | **W10** Speech & Vision | **W11** FastAPI Backend |
| **W9** Custom Tools | | **W12** Docker & Cloud |

### 🏆 **W13** · Capstone

</div>

> [!NOTE]
> Every week follows the same rhythm: **learn the theory → build something real → review and iterate**. By Week 13 you combine every skill into one production-style system.

<br>

---

## 🗺️ Overview

| Week | Phase | Theme | You will build |
|:---:|:---:|:---|:---|
| 1️⃣ | 🌱 | Introduction to AI Engineering | A simple chatbot wrapper |
| 2️⃣ | 🌱 | AI Models & Prompting | A prompt optimizer |
| 3️⃣ | 🌱 | Embeddings & Vector Databases | A RAG pipeline |
| 4️⃣ | 🔬 | Custom ML: Fundamentals | A scikit-learn classifier |
| 5️⃣ | 🔬 | Custom ML: Deep Learning | CNNs, GANs, RNNs, fine-tuned HF models |
| 6️⃣ | 🤖 | Open-Source Models & Deployment | A local LLM with an API wrapper |
| 7️⃣ | 🤖 | Agents & Agentic Workflows | Tool-using agents |
| 8️⃣ | ⚙️ | Modern AI Automation Tools | n8n and Zapier automations |
| 9️⃣ | ⚙️ | Advanced Automation & Custom Tools | Serverless functions, custom n8n nodes |
| 🔟 | 🎙️ | Multimodal Systems & Speech | STT, TTS and vision pipelines |
| 1️⃣1️⃣ | 🚀 | Production Backend Architecture | A FastAPI service with caching and a DB |
| 1️⃣2️⃣ | 🚀 | Deployment & Scaling | A containerized cloud deployment |
| 1️⃣3️⃣ | 🏆 | Capstone Project | An end-to-end AI system |

<br>

---

## 📚 Week by week

> [!TIP]
> Click a week to expand it. Each week lists the theory, the hands-on practical, and the resources to start from.

<br>

### 🌱 Phase 1 · Foundations

<details>
<summary><b>📅 Week 1 &nbsp;·&nbsp; Introduction to AI Engineering</b> &nbsp;✅</summary>

<br>

**🧠 Theory**
- AI engineering basics
- API fundamentals and authentication
- OpenAI API key setup

**🛠️ Practical**
- First API calls: OpenAI chat completions
- Build a simple chatbot wrapper

**🎯 Outcome:** you can call an LLM from code, manage keys safely, and wrap it in a small chatbot.

**📖 Resources** &nbsp;→&nbsp; OpenAI API Documentation · Anthropic Claude API

</details>

<details>
<summary><b>📅 Week 2 &nbsp;·&nbsp; Working with AI Models & Prompting</b></summary>

<br>

**🧠 Theory**
- Tokens, temperature, top-p sampling
- Few-shot prompting and chain-of-thought
- Frequency and presence penalties

**🛠️ Practical**
- Prompt engineering for various tasks
- Build a prompt optimizer

**🎯 Outcome:** you can control model behavior with sampling parameters and structured prompts.

**📖 Resources** &nbsp;→&nbsp; OpenAI Prompt Engineering · Anthropic Prompt Guide

</details>

<details>
<summary><b>📅 Week 3 &nbsp;·&nbsp; Embeddings & Vector Databases</b></summary>

<br>

**🧠 Theory**
- Text embeddings and semantic search
- Vector database fundamentals
- RAG (Retrieval-Augmented Generation) concepts

**🛠️ Practical**
- Generate embeddings with OpenAI/Anthropic
- Build a RAG pipeline with Pinecone/ChromaDB
- Semantic search implementation

**🎯 Outcome:** you can ground an LLM in your own documents with retrieval.

**📖 Resources** &nbsp;→&nbsp; OpenAI Embeddings · Pinecone Docs · ChromaDB Docs

</details>

<br>

### 🔬 Phase 2 · Machine Learning

<details>
<summary><b>📅 Week 4 &nbsp;·&nbsp; Custom ML Models: Fundamentals</b></summary>

<br>

**🧠 Theory**
- Supervised vs unsupervised learning
- Training, validation and test splits
- Loss functions and optimization

**🛠️ Practical**
- Build a classification model with scikit-learn
- Fine-tune embeddings for domain-specific tasks
- Model evaluation and metrics

**🎯 Outcome:** you can train, evaluate and compare classical ML models properly.

**📖 Resources** &nbsp;→&nbsp; Scikit-learn Guide · Fast.ai Practical Deep Learning

</details>

<details>
<summary><b>📅 Week 5 &nbsp;·&nbsp; Custom ML Models: Deep Learning</b></summary>

<br>

**🧠 Theory**
- Neural network basics (PyTorch/TensorFlow)
- Transfer learning fundamentals
- Fine-tuning pre-trained models

**🛠️ Practical**
- Build CNNs, GANs and RNNs with PyTorch
- Fine-tune Hugging Face models for custom tasks
- Model checkpointing and evaluation

**🎯 Outcome:** you can build neural networks and adapt pre-trained models to a custom task.

**📖 Resources** &nbsp;→&nbsp; PyTorch Documentation · Hugging Face Course · Hugging Face Transformers

</details>

<br>

### 🤖 Phase 3 · Open Source & Agents

<details>
<summary><b>📅 Week 6 &nbsp;·&nbsp; Open-Source Models & Deployment</b></summary>

<br>

**🧠 Theory**
- Open-source alternatives (Mistral, Llama, etc.)
- Model quantization and optimization
- Local model serving

**🛠️ Practical**
- Deploy an open-source LLM locally (Ollama/LM Studio)
- Implement inference with Hugging Face
- Build an API wrapper around custom models

**🎯 Outcome:** you can run and serve open models on your own machine behind an API.

**📖 Resources** &nbsp;→&nbsp; Hugging Face Models Hub · Ollama Documentation · vLLM for Fast Inference

</details>

<details>
<summary><b>📅 Week 7 &nbsp;·&nbsp; Agents & Agentic Workflows</b></summary>

<br>

**🧠 Theory**
- Agent architectures (ReAct, tool use)
- Multi-step reasoning and planning
- Tool integration patterns

**🛠️ Practical**
- Build agents with LangChain/LlamaIndex
- Implement function calling (Claude tool use/OpenAI)
- Create multi-step workflows

**🎯 Outcome:** you can build agents that plan, call tools and complete multi-step tasks.

**📖 Resources** &nbsp;→&nbsp; LangChain Documentation · LlamaIndex Docs · Claude Tool Use

</details>

<br>

### ⚙️ Phase 4 · Automation

<details>
<summary><b>📅 Week 8 &nbsp;·&nbsp; Modern AI Automation Tools</b> &nbsp;🟡 <i>early preview done</i></summary>

<br>

**🧠 Theory**
- n8n, Zapier and Make.com for AI-powered workflows
- RPA (Robotic Process Automation) vs AI-driven automation

**🛠️ Practical**
- Set up real-world automations with n8n and Zapier, e.g. automatic email responses with NLP models

**🎯 Outcome:** you can wire AI into everyday business workflows without writing a full backend.

> [!NOTE]
> A first n8n automation (Gmail → LLM → auto-reply, plus a Slack alert) is already built. See [Task 5 · Mail Automation with n8n](#-task-5--mail-automation-with-n8n).

**📖 Resources** &nbsp;→&nbsp; n8n Docs · Zapier Automation Guide

</details>

<details>
<summary><b>📅 Week 9 &nbsp;·&nbsp; Advanced Automation & Custom Tools</b></summary>

<br>

**🧠 Theory**
- Building custom integrations
- Webhook handling and async processing
- Error handling and retry logic

**🛠️ Practical**
- Build serverless functions (AWS Lambda/Google Cloud Functions)
- Create custom n8n nodes
- Implement robust error handling and logging

**🎯 Outcome:** you can extend automation platforms with your own code and make them resilient.

**📖 Resources** &nbsp;→&nbsp; AWS Lambda Python Guide · Google Cloud Functions · n8n Custom Nodes

</details>

<br>

### 🎙️ Phase 5 · Multimodal

<details>
<summary><b>📅 Week 10 &nbsp;·&nbsp; Multimodal Systems & Speech</b></summary>

<br>

**🧠 Theory**
- Multimodal AI concepts (text + image + audio)
- Speech-to-text and text-to-speech
- Vision models and image understanding

**🛠️ Practical**
- Build an STT pipeline with Whisper/AssemblyAI
- Implement TTS with ElevenLabs/Azure
- Vision tasks with Claude vision or open-source models
- Combine modalities in one unified system

**🎯 Outcome:** you can build systems that hear, see and speak.

**📖 Resources** &nbsp;→&nbsp; OpenAI Whisper API · ElevenLabs TTS · Claude Vision

</details>

<br>

### 🚀 Phase 6 · Production

<details>
<summary><b>📅 Week 11 &nbsp;·&nbsp; Production Backend Architecture</b></summary>

<br>

**🧠 Theory**
- API design patterns (FastAPI/Flask)
- Database design for AI systems
- Caching and performance optimization

**🛠️ Practical**
- Build a production API with FastAPI
- Implement caching (Redis)
- Database integration (PostgreSQL/MongoDB)
- Load testing and monitoring

**🎯 Outcome:** you can ship a fast, cached, database-backed AI service.

**📖 Resources** &nbsp;→&nbsp; FastAPI Documentation · Redis Documentation · SQLAlchemy ORM

</details>

<details>
<summary><b>📅 Week 12 &nbsp;·&nbsp; Deployment & Scaling</b></summary>

<br>

**🧠 Theory**
- Containerization (Docker)
- Kubernetes basics
- CI/CD pipelines for ML

**🛠️ Practical**
- Containerize an ML application with Docker
- Deploy to the cloud (AWS/GCP/Azure)
- Implement basic autoscaling
- Monitor model performance in production

**🎯 Outcome:** you can package, deploy, scale and monitor an AI application in the cloud.

**📖 Resources** &nbsp;→&nbsp; Docker Documentation · Kubernetes Basics · GitHub Actions for CI/CD

</details>

<br>

---

## 🧰 Tech stack at a glance

| Area | Tools you'll work with |
|:---|:---|
| 🧠 **LLM APIs** | OpenAI · Anthropic Claude · OpenRouter |
| 🏠 **Local & open models** | Ollama · LM Studio · Hugging Face · vLLM · Mistral · Llama |
| 🔎 **Retrieval** | Pinecone · ChromaDB · embeddings |
| 🔬 **Machine learning** | scikit-learn · PyTorch · TensorFlow · Hugging Face Transformers |
| 🤖 **Agents** | LangChain · LlamaIndex · function / tool calling |
| 🔁 **Automation** | n8n · Zapier · Make.com · AWS Lambda · Google Cloud Functions |
| 🎙️ **Speech & vision** | Whisper · AssemblyAI · ElevenLabs · Azure · Claude vision |
| 🌐 **Backend** | FastAPI · Flask · Redis · PostgreSQL · MongoDB · SQLAlchemy |
| 📦 **Delivery** | Docker · Kubernetes · GitHub Actions · AWS / GCP / Azure |

<br>

---

## 🏆 Week 13 · Capstone Project

> *Everything you learned, in one end-to-end system.*

| Layer | Component |
|:---:|:---|
| 🧬 **Model** | Custom fine-tuned ML model |
| 🤖 **Agent** | LLM agent with tool use |
| 🔎 **Knowledge** | Vector database and RAG |
| 🎧 **Senses** | Multimodal capabilities |
| 🔁 **Automation** | Automated workflows (n8n integration) |
| 🌐 **Backend** | Production FastAPI backend |
| 📦 **Delivery** | Containerized deployment |
| 🎤 **Wrap-up** | Project presentation and code review |

### 💡 Project ideas

| | Idea |
|:---:|:---|
| 📄 | AI-powered document processing pipeline |
| 🎧 | Intelligent customer support agent with custom intent classification |
| 🖼️ | Multimodal content analysis system |
| 🔄 | Automated data pipeline with LLM validation |

<br>

---

## 🚀 My projects

> [!IMPORTANT]
> This section tracks what has actually been built and submitted, task by task.

### 📦 Week 1 submissions

| # | Project | Folder | What it does |
|:---:|:---|:---|:---|
| 1️⃣ | **Memory Chatbot Agent** | [`Week 1/`](Week%201) | Local Ollama agent with memory, tools and model switching |
| 2️⃣ | **Memory Chatbot by LLMS** | [`Memory Chatbot by LLMS T2/`](Memory%20Chatbot%20by%20LLMS%20T2) | Memory chatbot built on LLM APIs |
| 3️⃣ | **Token Optimizer** | [`Token Optimizer T3/`](Token%20Optimizer%20T3) | Token usage optimizer for LLM prompts |
| 4️⃣ | **Enterprise RAG Project** | [`Enterprise RAG Project/`](Enterprise%20RAG%20Project) | EnterpriseIQ, a retrieval-augmented knowledge assistant |
| 5️⃣ | **Mail Automation with n8n** | [`MAIL Automantion N8N/`](MAIL%20Automantion%20N8N) | Gmail → LLM → auto-reply, with Slack alert in V2 |

<br>

### 📧 Task 5 · Mail Automation with n8n

An end-to-end **email automation** built in [n8n](https://n8n.io): every incoming Gmail message is picked up by a trigger, passed through an LLM chain powered by an **OpenRouter chat model**, and answered automatically from Gmail. The workflow is published and runs on its own.

```mermaid
flowchart LR
    T["📥 Gmail Trigger<br/><sub>new email arrives</sub>"] --> L["🧠 Basic LLM Chain<br/><sub>drafts the reply</sub>"]
    M["🔀 OpenRouter<br/>Chat Model"] -. model .-> L
    L --> G["📤 Gmail · Send a message<br/><sub>sends the reply</sub>"]
    G -.-> S["💬 Slack · Send a message1<br/><sub>V2 only · posts a notification</sub>"]

    style T fill:#fde8e8,stroke:#ea4335,color:#0b1220
    style L fill:#e3f2fd,stroke:#0A66C2,color:#0b1220
    style M fill:#f3e5f5,stroke:#8A2BE2,color:#0b1220
    style G fill:#fde8e8,stroke:#ea4335,color:#0b1220
    style S fill:#e8f5e9,stroke:#2ea44f,color:#0b1220
```

#### 🔁 Two iterations, side by side

<table>
<tr>
<td width="50%" align="center">

**V1 · Core auto-reply**

<img src="MAIL%20Automantion%20N8N/V1_Prove.png" alt="n8n workflow V1: Gmail Trigger, Basic LLM Chain with OpenRouter model, Gmail Send a message" width="100%">

<sub>3 nodes + model · every step ran with ✅ and passed 1 item along</sub>

</td>
<td width="50%" align="center">

**V2 · Auto-reply + Slack alert**

<img src="MAIL%20Automantion%20N8N/V2_Prove.png" alt="n8n workflow V2: same pipeline extended with a Slack Send a message node" width="100%">

<sub>Same pipeline, extended with a Slack notification node</sub>

</td>
</tr>
</table>

| | **V1** | **V2** |
|:---|:---:|:---:|
| 📥 Gmail Trigger | ✅ | ✅ |
| 🧠 Basic LLM Chain (OpenRouter model) | ✅ | ✅ |
| 📤 Gmail auto-reply | ✅ | ✅ |
| 💬 Slack message | ➖ | ✅ |
| 🟢 Workflow published and executed successfully | ✅ | ✅ |

#### 🧩 Node breakdown

| Node | Type | Role in the workflow |
|:---|:---|:---|
| **Gmail Trigger** | Trigger | Starts the workflow whenever a new email arrives |
| **Basic LLM Chain** | AI chain | Takes the email content and produces the response text |
| **OpenRouter Chat Model** | Language model | The model plugged into the chain, reached through OpenRouter |
| **Send a message** | Gmail · send message | Sends the generated reply back out through Gmail |
| **Send a message1** | Slack · post message | *(V2)* Posts a message to Slack once the reply is handled |

#### 🎓 What this task practiced

- 🔌 Connecting real services (Gmail, Slack) with OAuth credentials in n8n
- 🧠 Using an LLM inside a no-code workflow through a model provider (OpenRouter)
- 🔗 Passing data between nodes, from trigger to model to action
- 🟢 Publishing a workflow so it runs automatically, then proving it with execution runs

> [!NOTE]
> This is hands-on practice for [Week 8](#-phase-4--automation), done early.

<br>

### 🗂️ Repository layout

```text
SHARKSTACK_AI_ENG/
├── 📁 Week 1/                       # Task 1 · Memory Chatbot Agent (Ollama)
├── 📁 Memory Chatbot by LLMS T2/    # Task 2
├── 📁 Token Optimizer T3/           # Task 3
├── 📁 Enterprise RAG Project/       # Task 4 · EnterpriseIQ
├── 📁 MAIL Automantion N8N/         # Task 5 · n8n mail automation
│   ├── 🖼️ V1_Prove.png
│   └── 🖼️ V2_Prove.png
└── 📄 README.md
```

<br>

---

## ✅ Progress tracker

![Progress](https://img.shields.io/badge/Progress-1_of_13_weeks-2ea44f?style=for-the-badge&labelColor=0b1220)
![Tasks](https://img.shields.io/badge/Tasks_done-5-0A66C2?style=for-the-badge&labelColor=0b1220)

```text
[█░░░░░░░░░░░░]  8%   ·   Week 1 of 13 complete
```

### 🌱 Week 1 &nbsp;·&nbsp; Complete

- [x] **Task 1** · Memory Chatbot Agent *(local Ollama agent with memory, tools and model switching)*
- [x] **Task 2** · Memory Chatbot by LLMS *(`Memory Chatbot by LLMS T2`)*
- [x] **Task 3** · Token Optimizer *(`Token Optimizer T3`)*
- [x] **Task 4** · Enterprise RAG Project *(`Enterprise RAG Project` / EnterpriseIQ)*
- [x] **Task 5** · Mail Automation with n8n *(`MAIL Automantion N8N` · V1 and V2)*

### 🗓️ Up next

- [ ] **Week 2** · Prompting
- [ ] **Week 3** · Embeddings and RAG
- [ ] **Week 4** · ML fundamentals
- [ ] **Week 5** · Deep learning
- [ ] **Week 6** · Open-source models
- [ ] **Week 7** · Agents
- [ ] **Week 8** · Automation tools
- [ ] **Week 9** · Custom automation
- [ ] **Week 10** · Multimodal
- [ ] **Week 11** · Backend
- [ ] **Week 12** · Deployment
- [ ] **Week 13** · Capstone

<br>

---

<div align="center">

<br>

### 🦈 SharkStack AI Engineer Program

*Learn it. &nbsp;Build it. &nbsp;Ship it.*

<br>

</div>
