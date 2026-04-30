import os
from huggingface_hub import HfApi, login
from dotenv import load_dotenv

# Load local environment variables
load_dotenv(override=True)

def deploy():
    print("🚀 Starting ParamMem Deployment to Hugging Face Spaces...")
    
    # 1. Configuration
    # You can set these in your .env or the script will ask
    hf_token = os.getenv("HF_TOKEN")
    space_name = os.getenv("HF_SPACE_NAME") # Format: "username/space-name"
    
    if not hf_token:
        hf_token = input("🔑 Enter your Hugging Face Write Token: ").strip()
    
    if not space_name:
        space_name = input("📁 Enter target Space name (e.g., username/param-mem): ").strip()

    # 2. Login
    try:
        login(token=hf_token)
        api = HfApi()
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # 3. Create Space if it doesn't exist
    print(f"🔨 Ensuring Space '{space_name}' exists...")
    try:
        api.create_repo(
            repo_id=space_name,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True
        )
    except Exception as e:
        print(f"⚠️ Note: {e}")

    # 4. Upload Files
    print(f"📤 Uploading project folder to {space_name}...")
    # We ignore files specified in .gitignore automatically if we use upload_folder
    # but we'll be explicit here to avoid uploading huge local models
    try:
        api.upload_folder(
            folder_path=".",
            repo_id=space_name,
            repo_type="space",
            ignore_patterns=[
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/param_mem_lora/**",
                "**/chroma_db/**",
                ".env",
                ".git/**"
            ]
        )
        print("✅ Upload Complete!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return

    # 5. Reminder for Secrets
    print("\n" + "="*50)
    print("✨ DEPLOYMENT TRIGGERED!")
    print(f"🌍 Your Space: https://huggingface.co/spaces/{space_name}")
    print("\n⚠️ IMPORTANT: Don't forget to set your Secrets in the Space Settings:")
    print("   1. GROQ_API_KEY")
    print("   2. MODEL_PROVIDER = groq")
    print("   3. GROQ_MODEL = openai/gpt-oss-20b")
    print("="*50)

if __name__ == "__main__":
    deploy()
