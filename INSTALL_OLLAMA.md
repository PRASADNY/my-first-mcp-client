# How to Install and Use Ollama on Windows

## Step 1: Install Ollama

1. **Download Ollama for Windows:**
   - Go to: https://ollama.com/download
   - Download the Windows installer (`.exe` file)
   - Run the installer and follow the installation wizard
   - Ollama will be installed and added to your system PATH

2. **Verify Installation:**
   - Open a new PowerShell or Command Prompt window
   - Run: `ollama --version`
   - You should see the version number if installed correctly

## Step 2: Pull the Llama 3.2 Model

Once Ollama is installed, run:

```powershell
ollama pull llama3.2
```

This will download the Llama 3.2 model (approximately 2GB). The download may take a few minutes depending on your internet connection.

## Step 3: Verify the Model is Installed

After pulling, verify it's available:

```powershell
ollama list
```

This will show all installed models.

## Alternative: Other Model Options

If you want a different size or variant:

- **Smaller model (1B):** `ollama pull llama3.2:1b`
- **Larger model with vision:** `ollama pull llama3.2-vision:11b`
- **Other models:** `ollama pull mistral`, `ollama pull phi3`, etc.

## Troubleshooting

- **"ollama is not recognized"**: Make sure Ollama is installed and restart your terminal/PowerShell
- **Download is slow**: This is normal, models are large files (2-4GB typically)
- **Connection errors**: Check your internet connection

## Next Steps

After installing Ollama and pulling the model, you can:
1. Test it: `ollama run llama3.2`
2. Use it with your MCP client (which is already configured to use Ollama)

