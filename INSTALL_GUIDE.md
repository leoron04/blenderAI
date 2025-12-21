# BlenderAI Installation Guide

> ⚠️ Importante: la cartella dell’addon deve chiamarsi **esattamente `blenderAI`** (niente `-master`, `-1`, ecc.). Se vedi errori tipo `No module named blenderAI-1`, rinomina la cartella e riprova. Vedi anche `INSTALL_FIX_GUIDE.md` per la procedura rapida.

## Installation Methods

### Method 1: ZIP Installation (Recommended)

This is the standard Blender addon installation method.

#### Steps:

1. **Download the ZIP file**
   - Go to: https://github.com/leoron04/blenderAI
   - Click "Code" → "Download ZIP"
   - This downloads `blenderAI-main.zip`

2. **Install in Blender**
   - Open Blender
   - Edit → Preferences → Add-ons
   - Click "Install..." button
   - Select the downloaded `blenderAI-main.zip`
   - Click "Install Add-on from File"
   - Se installi manualmente scompattando, assicurati che la cartella finale si chiami `blenderAI`

3. **Enable the addon**
   - Search for "BlenderAI" in the add-ons search box
   - Click the checkbox to enable it
   - You'll see "BlenderAI" appear in your add-ons list

4. **Configure API Keys**
   - First use of the addon will open settings
   - Add your API key (OpenAI or Google Gemini)
   - Save and the addon is ready!

### Method 2: Manual Folder Installation

For development or advanced users:

1. **Clone the repository**
   ```bash
   git clone https://github.com/leoron04/blenderAI.git
   ```

2. **Copy to Blender addons folder**
   
   **Windows:**
   ```
   C:\Users\YourUsername\AppData\Roaming\Blender Foundation\Blender\4.0\scripts\addons\
   ```
   
   **macOS:**
   ```
   /Users/YourUsername/Library/Application Support/Blender/4.0/scripts/addons/
   ```
   
   **Linux:**
   ```
   ~/.config/blender/4.0/scripts/addons/
   ```

3. **Rename folder** (important!)
   - The addon folder MUST be named `blenderAI` (not `blenderAI-main`)
   - Or rename: `mv blenderAI-main blenderAI`

4. **Restart Blender and enable** the addon

## Configuration

### Setting up API Keys

#### OpenAI (ChatGPT)

1. Go to https://platform.openai.com
2. Create an account and get your API key
3. In Blender, paste the key in BlenderAI panel
4. Select "ChatGPT" as your AI model

#### Google Gemini

1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. In Blender, paste the key in BlenderAI panel
4. Select "Gemini" as your AI model

## Troubleshooting

### Addon doesn't appear in Add-ons list

- Make sure the folder is named `blenderAI` (lowercase)
- Check that all `.py` files are present
- Verify the `__init__.py` file exists
- Restart Blender completely

### "API key not configured" error

- Open BlenderAI panel
- Enter your API key in the text field
- Make sure the key is valid for the selected model
- Check your API plan has available quota

### Scene Analysis not working

- Make sure you have objects in your scene
- Check that the API key is correct
- Try using debug mode to see error messages

## Requirements

- Blender 3.0+
- Python 3.10+
- API key from OpenAI or Google Gemini
- Internet connection for AI queries

## Uninstallation

To remove BlenderAI:

1. Edit → Preferences → Add-ons
2. Search for "BlenderAI"
3. Click the arrow to expand
4. Click "Remove"
5. Restart Blender

## Getting Help

- Read the documentation: https://github.com/leoron04/blenderAI/blob/main/README.md
- Check CONTRIBUTING.md for development help
- Open an issue on GitHub for bug reports
- Visit the repository for latest updates
