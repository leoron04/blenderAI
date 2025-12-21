# BlenderAI Verification Checklist

Use this checklist to verify that the addon is properly installed and functioning.

## Installation Verification

- [ ] Downloaded `blenderAI-main.zip` from GitHub
- [ ] Extracted/installed ZIP in Blender preferences
- [ ] Found "BlenderAI" in Add-ons list
- [ ] Enabled the addon (checkbox is checked)
- [ ] Blender didn't crash during installation
- [ ] No errors in Blender console (Window > Toggle System Console)

## UI Verification

- [ ] BlenderAI panel appears in 3D View sidebar
- [ ] "🤖 BlenderAI Agent" tab visible
- [ ] "⚙️ Advanced Settings" tab visible
- [ ] Panel has proper sections:
  - [ ] AI Agent Configuration
  - [ ] API Key field
  - [ ] Quick Actions buttons
  - [ ] Scene Info
  - [ ] Help & Documentation

## Configuration Verification

- [ ] API Key field accepts text input
- [ ] Can select between ChatGPT and Gemini
- [ ] No errors when changing model selection
- [ ] Can access Advanced Settings panel
- [ ] Debug mode toggle works

## Functionality Verification

- [ ] "Analyze Scene" button responds
- [ ] Scene info updates with object count
- [ ] "Ask Agent" button doesn't cause crashes
- [ ] "Help" button shows information
- [ ] No Python errors in console

## File Structure Verification

Check that all required files exist:

- [ ] `__init__.py` - Addon manifest
- [ ] `operators.py` - Core agent logic
- [ ] `ui.py` - User interface panels
- [ ] `utils.py` - Utility functions
- [ ] `requirements.txt` - Dependencies
- [ ] `README.md` - Documentation
- [ ] `LICENSE` - MIT license
- [ ] `.gitignore` - Git configuration
- [ ] `.env.example` - Configuration template
- [ ] `CONTRIBUTING.md` - Contribution guide
- [ ] `CHANGELOG.md` - Version history
- [ ] `INSTALL_GUIDE.md` - Installation instructions

## Performance Verification

- [ ] UI loads without lag
- [ ] Panel is responsive to clicks
- [ ] No memory leaks (check Task Manager)
- [ ] Smooth scrolling in scene statistics

## API Integration Verification (Optional)

If you have an API key:

- [ ] Enter API key in panel
- [ ] Addon doesn't expose key to console
- [ ] Can communicate with AI service
- [ ] Responses are displayed properly
- [ ] Scene analysis returns expected data

## Troubleshooting

If any verification fails:

1. **Addon doesn't appear in list**
   - Check folder name is `blenderAI` (lowercase)
   - Verify `__init__.py` exists
   - Restart Blender completely

2. **Panel doesn't show**
   - Check that addon is enabled (checkbox)
   - Look in View > Sidebar > BlenderAI tab
   - Try restarting Blender

3. **Buttons don't work**
   - Check Blender console for errors
   - Verify Python 3.10+ installed
   - Try disabling and re-enabling addon

4. **API key errors**
   - Verify API key format
   - Check internet connection
   - Try with different AI model

## System Requirements Verification

- [ ] Blender 3.0+
- [ ] Python 3.10+
- [ ] Windows/macOS/Linux compatible
- [ ] 4GB+ RAM available
- [ ] 50MB+ disk space

## Success Criteria

✅ **Addon is successfully installed if:**

- Appears in Add-ons list
- UI panel displays correctly
- All buttons are clickable
- Scene statistics update properly
- No console errors
- Smooth user experience

✅ **Addon is fully functional if:**

- API key can be configured
- Scene analysis works
- AI model selection works
- Quick actions respond
- Debug mode toggles

## Report Issues

If you find problems:

1. Check this verification guide first
2. Check INSTALL_GUIDE.md troubleshooting
3. Enable debug mode and check console
4. Open an issue on GitHub with:
   - Your Blender version
   - Your Python version
   - Error message from console
   - Steps to reproduce

---

**Last Updated:** 2025-12-21
**BlenderAI Version:** 1.0.0
