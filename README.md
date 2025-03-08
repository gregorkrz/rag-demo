[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Flare](https://img.shields.io/badge/flare-network-e62058.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzNCIgaGVpZ2h0PSIzNCI+PHBhdGggZD0iTTkuNC0uMWEzMjAuMzUgMzIwLjM1IDAgMCAwIDIuOTkuMDJoMi4yOGExMTA2LjAxIDExMDYuMDEgMCAwIDEgOS4yMy4wNGMzLjM3IDAgNi43My4wMiAxMC4xLjA0di44N2wuMDEuNDljLS4wNSAyLTEuNDMgMy45LTIuOCA1LjI1YTkuNDMgOS40MyAwIDAgMS02IDIuMDdIMjAuOTJsLTIuMjItLjAxYTQxNjEuNTcgNDE2MS41NyAwIDAgMS04LjkyIDBMMCA4LjY0YTIzNy4zIDIzNy4zIDAgMCAxLS4wMS0xLjUxQy4wMyA1LjI2IDEuMTkgMy41NiAyLjQgMi4yIDQuNDcuMzcgNi43LS4xMiA5LjQxLS4wOXoiIGZpbGw9IiNFNTIwNTgiLz48cGF0aCBkPSJNNy42NSAxMi42NUg5LjJhNzU5LjQ4IDc1OS40OCAwIDAgMSA2LjM3LjAxaDMuMzdsNi42MS4wMWE4LjU0IDguNTQgMCAwIDEtMi40MSA2LjI0Yy0yLjY5IDIuNDktNS42NCAyLjUzLTkuMSAyLjVhNzA3LjQyIDcwNy40MiAwIDAgMC00LjQtLjAzbC0zLjI2LS4wMmMtMi4xMyAwLTQuMjUtLjAyLTYuMzgtLjAzdi0uOTdsLS4wMS0uNTVjLjA1LTIuMSAxLjQyLTMuNzcgMi44Ni01LjE2YTcuNTYgNy41NiAwIDAgMSA0LjgtMnoiIGZpbGw9IiNFNjIwNTciLz48cGF0aCBkPSJNNi4zMSAyNS42OGE0Ljk1IDQuOTUgMCAwIDEgMi4yNSAyLjgzYy4yNiAxLjMuMDcgMi41MS0uNiAzLjY1YTQuODQgNC44NCAwIDAgMS0zLjIgMS45MiA0Ljk4IDQuOTggMCAwIDEtMi45NS0uNjhjLS45NC0uODgtMS43Ni0xLjY3LTEuODUtMy0uMDItMS41OS4wNS0yLjUzIDEuMDgtMy43NyAxLjU1LTEuMyAzLjM0LTEuODIgNS4yNy0uOTV6IiBmaWxsPSIjRTUyMDU3Ii8+PC9zdmc+&colorA=FFFFFF)](https://dev.flare.network/)

# Flare AI RAG

Flare AI Kit template for Retrieval-Augmented Generation (RAG) Knowledge.

## 🚀 Key Features

- **Modular Architecture:** Designed with independent components that can be easily extended.
- **Qdrant-Powered Retrieval:** Leverages Qdrant for fast, semantic document retrieval, but can easily be adapted to other vector databases.
- **Highly Configurable & Extensible:** Uses a straightforward configuration system, enabling effortless integration of new features and services.
- **Unified LLM Integration:** Leverages Gemini as a unified provider while maintaining compatibility with OpenRouter for a broader range of models.

## 🎯 Getting Started

### Prerequisites

Before getting started, ensure you have:

- A **Python 3.12** environment.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed for dependency management.
- [Docker](https://www.docker.com/)
- A [Gemini API key](https://aistudio.google.com/app/apikey).
- Access to one of the Flare databases. (The [Flare Developer Hub](https://dev.flare.network/) is included in CSV format for local testing.)

### Build & Run Instructions

You can deploy Flare AI RAG using Docker or set up the backend and frontend manually.

#### Environment Setup

1. **Prepare the Environment File:**
   Rename `.env.example` to `.env` and update the variables accordingly. (e.g. your [Gemini API key](https://aistudio.google.com/app/apikey))

### Build using Docker (Recommended)

1. **Build the Docker Image:**

   ```bash
   docker build -t flare-ai-rag .
   ```

2. **Run the Docker Container:**

   ```bash
   docker run -p 80:80 -it --env-file .env flare-ai-rag
   ```

3. **Access the Frontend:**
   Open your browser and navigate to [http://localhost:80](http://localhost:80) to interact with the Chat UI.

### 🛠 Build Manually

Flare AI RAG is composed of a Python-based backend and a JavaScript frontend. Follow these steps for manual setup:

#### Backend Setup

1. **Install Dependencies:**
   Use [uv](https://docs.astral.sh/uv/getting-started/installation/) to install backend dependencies:

   ```bash
   uv sync --all-extras
   ```

2. **Setup a Qdrant Service:**
   Make sure that Qdrant is up an running before running your script.
   You can quickly start a Qdrant instance using Docker:

   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

3. **Start the Backend:**
   The backend runs by default on `0.0.0.0:8080`:

   ```bash
   uv run start-backend
   ```

#### Frontend Setup

1. **Install Dependencies:**
   In the `chat-ui/` directory, install the required packages using [npm](https://nodejs.org/en/download):

   ```bash
   cd chat-ui/
   npm install
   ```

2. **Configure the Frontend:**
   Update the backend URL in `chat-ui/src/App.js` for testing:

   ```js
   const BACKEND_ROUTE = "http://localhost:8080/api/routes/chat/";
   ```

   > **Note:** Remember to change `BACKEND_ROUTE` back to `'api/routes/chat/'` after testing.

3. **Start the Frontend:**

   ```bash
   npm start
   ```

## 📁 Repo Structure

```
src/flare_ai_rag/
├── ai/                     # AI Provider implementations
│   ├── base.py            # Abstract base classes
│   ├── gemini.py          # Google Gemini integration
│   ├── model.py           # Model definitions
│   └── openrouter.py      # OpenRouter integration
├── api/                    # API layer
│   ├── middleware/        # Request/response middleware
│   └── routes/           # API endpoint definitions
├── attestation/           # TEE security layer
│   ├── simulated_token.txt
│   ├── vtpm_attestation.py  # vTPM client
│   └── vtpm_validation.py   # Token validation
├── prompts/              # AI system prompts & templates
│   ├── library.py        # Prompt module library
│   ├── schemas.py        # Schema definitions
│   ├── service.py        # Prompt service module
│   └── templates.py       # Prompt templates
├── responder/            # Response generation
│   ├── base.py           # Base responder interface
│   ├── config.py         # Response configuration
│   ├── prompts.py        # System prompts
│   └── responder.py      # Main responder logic
├── retriever/            # Document retrieval
│   ├── base.py          # Base retriever interface
│   ├── config.py        # Retriever configuration
│   ├── qdrant_collection.py  # Qdrant collection management
│   └── qdrant_retriever.py   # Qdrant implementation
├── router/               # API routing
│   ├── base.py          # Base router interface
│   ├── config.py        # Router configuration
│   ├── prompts.py       # Router prompts
│   └── router.py        # Main routing logic
├── utils/               # Utility functions
│   ├── file_utils.py    # File operations
│   └── parser_utils.py  # Input parsing
├── input_parameters.json # Configuration parameters
├── main.py              # Application entry point
├── query.txt           # Sample queries
└── settings.py         # Environment settings
```

## 🚀 Deploy on TEE

Deploy on a [Confidential Space](https://cloud.google.com/confidential-computing/confidential-space/docs/confidential-space-overview) using AMD SEV.

### Prerequisites

- **Google Cloud Platform Account:**
  Access to the [`verifiable-ai-hackathon`](https://console.cloud.google.com/welcome?project=verifiable-ai-hackathon) project is required.

- **Gemini API Key:**
  Ensure your [Gemini API key](https://aistudio.google.com/app/apikey) is linked to the project.

- **gcloud CLI:**
  Install and authenticate the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

### Environment Configuration

1. **Set Environment Variables:**
   Update your `.env` file with:

   ```bash
   TEE_IMAGE_REFERENCE=ghcr.io/flare-foundation/flare-ai-rag:main  # Replace with your repo build image
   INSTANCE_NAME=<PROJECT_NAME-TEAM_NAME>
   ```

2. **Load Environment Variables:**

   ```bash
   source .env
   ```

   > **Reminder:** Run the above command in every new shell session or after modifying `.env`. On Windows, we recommend using [git BASH](https://gitforwindows.org) to access commands like `source`.

3. **Verify the Setup:**

   ```bash
   echo $TEE_IMAGE_REFERENCE # Expected output: Your repo build image
   ```

### Deploying to Confidential Space

Run the following command:

```bash
gcloud compute instances create $INSTANCE_NAME \
  --project=verifiable-ai-hackathon \
  --zone=us-east5-b \
  --machine-type=n2d-standard-2 \
  --network-interface=network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_ONLY,subnet=default \
  --metadata=tee-image-reference=$TEE_IMAGE_REFERENCE,\
tee-container-log-redirect=true,\
tee-env-GEMINI_API_KEY=$GEMINI_API_KEY,\
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=confidential-sa@verifiable-ai-hackathon.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --min-cpu-platform="AMD Milan" \
  --tags=flare-ai,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=$INSTANCE_NAME,\
image=projects/confidential-space-images/global/images/confidential-space-debug-250100,\
mode=rw,\
size=11,\
type=pd-standard \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --reservation-affinity=any \
  --confidential-compute-type=SEV
```

#### Post-deployment

1. After deployment, you should see an output similar to:

   ```plaintext
   NAME          ZONE           MACHINE_TYPE    PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
   rag-team1   us-central1-b  n2d-standard-2               10.128.0.18  34.41.127.200  RUNNING
   ```

2. It may take a few minutes for Confidential Space to complete startup checks. You can monitor progress via the [GCP Console](https://console.cloud.google.com/welcome?project=verifiable-ai-hackathon) logs.
   Click on **Compute Engine** → **VM Instances** (in the sidebar) → **Select your instance** → **Serial port 1 (console)**.

   When you see a message like:

   ```plaintext
   INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
   ```

   the container is ready. Navigate to the external IP of the instance (visible in the **VM Instances** page) to access the Chat UI.

### 🔧 Troubleshooting

If you encounter issues, follow these steps:

1. **Check Logs:**

   ```bash
   gcloud compute instances get-serial-port-output $INSTANCE_NAME --project=verifiable-ai-hackathon
   ```

2. **Verify API Key(s):**
   Ensure that all API Keys are set correctly (e.g. `GEMINI_API_KEY`).

3. **Check Firewall Settings:**
   Confirm that your instance is publicly accessible on port `80`.

## 💡 Next Steps

Design and implement a knowledge ingestion pipeline, with a demonstration interface showing practical applications for developers and users.

_N.B._ Other vector databases can be used, provided they run within the same Docker container as the RAG system, since the deployment will occur in a TEE.

- **Enhanced Data Ingestion & Indexing**: Explore more sophisticated data structures for improved indexing and retrieval, and expand beyond a CSV format to include additional data sources (_e.g._, Flare's GitHub, blogs, documentation). BigQuery integration would be desirable.
- **Intelligent Query & Data Processing**: Use recommended AI models to refine the data processing pipeline, including pre-processing steps that optimize and clean incoming data, ensuring higher-quality context retrieval. (_e.g._ Use an LLM to reformulate or expand user queries before passing them to the retriever, improving the precision and recall of the semantic search.)
- **Advanced Context Management**: Develop an intelligent context management system that:
  - Implements Dynamic Relevance Scoring to rank documents by their contextual importance.
  - Optimizes the Context Window to balance the amount of information sent to LLMs.
  - Includes Source Verification Mechanisms to assess and validate the reliability of the data sources.
- **Improved Retrieval & Response Pipelines**: Integrate hybrid search techniques (combining semantic and keyword-based methods) for better retrieval, and implement completion checks to verify that the responder's output is complete and accurate (potentially allow an iterative feedback loop for refining the final answer).
