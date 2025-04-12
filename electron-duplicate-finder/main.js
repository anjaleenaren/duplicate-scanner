const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object to avoid garbage collection
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    }
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Open DevTools during development (comment out for production)
  //mainWindow.webContents.openDevTools();

  // Handle window being closed
  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

// Create the window when Electron is ready
app.whenReady().then(createWindow);

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// On macOS, recreate window when dock icon is clicked and no windows are open
app.on('activate', function () {
  if (mainWindow === null) createWindow();
});

// Handle directory selection dialog
ipcMain.handle('select-directories', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'multiSelections']
  });
  
  return result.filePaths;
});

// Execute Python script
ipcMain.handle('run-duplicate-finder', async (event, args) => {
  const { directories, recursive, hashAlgorithm, outputFile } = args;
  
  // Get the path to the Python script
  // During development, the script is in the parent directory
  // In production, it will be in extraResources
  let pythonScriptPath;
  
  if (app.isPackaged) {
    pythonScriptPath = path.join(process.resourcesPath, 'duplicate_finder.py');
  } else {
    pythonScriptPath = path.join(app.getAppPath(), '..', 'duplicate_finder.py');
  }
  
  console.log(`Using Python script at: ${pythonScriptPath}`);
  
  // Build command arguments
  let cmdArgs = [...directories];
  if (recursive) cmdArgs.push('-r');
  if (hashAlgorithm) cmdArgs.push('--hash-algorithm', hashAlgorithm);
  if (outputFile) cmdArgs.push('-o', outputFile);
  
  // Determine Python executable (platform-specific)
  const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';
  
  // Spawn Python process
  const pythonProcess = spawn(pythonCommand, [pythonScriptPath, ...cmdArgs]);
  
  let dataString = '';
  
  // Listen for data from the Python script
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    dataString += output;
    
    // Send progress updates to the renderer
    mainWindow.webContents.send('process-update', output);
  });
  
  // Listen for errors
  pythonProcess.stderr.on('data', (data) => {
    const error = data.toString();
    mainWindow.webContents.send('process-error', error);
  });
  
  // Return a promise that resolves when the Python process completes
  return new Promise((resolve, reject) => {
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, data: dataString });
      } else {
        reject({ success: false, error: `Process exited with code ${code}` });
      }
    });
  });
});

// Handle file deletion (for the delete selected duplicates feature)
ipcMain.handle('delete-files', async (event, filePaths) => {
  console.log('Received delete request for files:', filePaths);
  const results = [];
  
  for (const filePath of filePaths) {
    try {
      // Ensure the path is absolute
      const absolutePath = path.resolve(filePath);
      console.log('Attempting to delete:', absolutePath);
      
      // Check if file exists
      if (!fs.existsSync(absolutePath)) {
        throw new Error('File does not exist');
      }
      
      await fs.promises.unlink(absolutePath);
      console.log('Successfully deleted:', absolutePath);
      results.push({ path: filePath, success: true });
    } catch (error) {
      console.error('Error deleting file:', filePath, error);
      results.push({ path: filePath, success: false, error: error.message });
    }
  }
  
  console.log('Delete operation results:', results);
  return results;
});

