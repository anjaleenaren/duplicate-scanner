# Duplicate File Finder

A modern Electron application for finding and managing duplicate files across your system. Built with Python for efficient file processing and Electron for a beautiful cross-platform interface.


https://github.com/user-attachments/assets/9bb34331-e563-4fe0-baf9-19fdb8da9441


## Features

- 🎯 Find duplicate files across multiple directories
- 🔄 Recursive directory scanning
- 🔒 Multiple hash algorithms (MD5, SHA1, SHA256)
- 📊 Visual progress tracking
- 🗑️ Safe file deletion with confirmation
- 📝 Optional duplicate report generation
- 🎨 Modern, responsive UI
- 🖥️ Cross-platform support (Windows, macOS, Linux)

## Installation

### Prerequisites

- Node.js (v14 or later)
- Python 3.7 or later
- npm or yarn

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/duplicate-scanner.git
cd duplicate-scanner
```

2. Install dependencies:
```bash
cd electron-duplicate-finder
npm install
```

3. Build the application:
```bash
npm run dist
```

## Usage

### Running the Application

1. **Development Mode**
```bash
npm start
```

2. **Production Mode**
- Windows: Run the generated .exe file
- macOS: Run the .app file
- Linux: Run the .AppImage or .deb file

### How to Use

1. Click "Browse..." to select one or more directories to scan
2. Choose your preferred hash algorithm:
   - MD5: Fastest but less secure
   - SHA1: Balanced speed and security
   - SHA256: Most secure but slower
3. (Optional) Enter an output file path to save the duplicate report
4. Click "Scan for Duplicates" to start the process
5. Review the results and select files to delete
6. Use "Delete Selected Files" to remove duplicates

## Technical Details

### Algorithm Overview

The application uses a multi-step process to efficiently find duplicate files:

1. **File Collection**
   - Recursively scans selected directories
   - Filters out directories and special files
   - Collects file metadata (size, modification time)

2. **Size-based Pre-filtering**
   - Groups files by size
   - Files with unique sizes are immediately eliminated
   - Only files with matching sizes proceed to hashing

3. **Hashing**
   - Uses the selected hash algorithm (MD5/SHA1/SHA256)
   - Processes files in chunks to handle large files efficiently
   - Implements progress tracking and error handling

4. **Duplicate Detection**
   - Groups files by their hash values
   - Files with identical hashes are marked as duplicates
   - Presents results with file metadata and modification times

### Hash Algorithms

1. **MD5**
   - Fastest algorithm
   - 128-bit hash
   - Suitable for general use
   - Not recommended for security-critical applications

2. **SHA1**
   - Medium speed
   - 160-bit hash
   - Good balance of speed and security
   - Suitable for most use cases

3. **SHA256**
   - Slowest but most secure
   - 256-bit hash
   - Recommended for critical applications
   - Provides highest collision resistance

### Performance Considerations

- The application uses chunked file reading to handle large files
- Progress tracking is implemented for both scanning and hashing
- Memory usage is optimized by processing files in groups
- File operations are performed asynchronously to maintain UI responsiveness

## Development

### Project Structure

```
duplicate-scanner/
├── electron-duplicate-finder/    # Electron application
│   ├── main.js                   # Main process
│   ├── index.html               # Renderer process
│   └── package.json             # Node.js dependencies
├── duplicate_finder.py          # Python core logic
└── test_files/                  # Test data
```

### Building from Source

1. Install development dependencies:
```bash
npm install
```

2. Build the application:
```bash
npm run dist
```

3. Test the application:
```bash
npm start
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the ISC License - see the LICENSE file for details.

## Acknowledgments

- Electron team for the amazing framework
- Python community for robust file handling libraries
- All contributors and users of this project

## Packaging for Distribution

### Prerequisites for Packaging

- Node.js (v14 or later)
- Python 3.7 or later
- npm or yarn
- For Windows: NSIS (for creating installers)
- For macOS: Xcode Command Line Tools
- For Linux: fpm, rpm, dpkg (for creating packages)

### Building Distribution Packages

1. **Install Dependencies**
```bash
cd electron-duplicate-finder
npm install
```

2. **Build for All Platforms**
```bash
npm run dist
```

This will create installers in the `dist` directory:
- Windows: `.exe` installer
- macOS: `.dmg` and `.zip` files
- Linux: `.AppImage` and `.deb` packages

### Platform-Specific Builds

1. **Windows Only**
```bash
npm run dist -- --win
```

2. **macOS Only**
```bash
npm run dist -- --mac
```

3. **Linux Only**
```bash
npm run dist -- --linux
```

### Distribution Files

After building, you'll find the following files in the `dist` directory:

- **Windows**
  - `Duplicate File Finder Setup.exe` - Installer
  - `Duplicate File Finder Setup.exe.blockmap` - Update metadata

- **macOS**
  - `Duplicate File Finder.dmg` - Disk image
  - `Duplicate File Finder.zip` - Compressed archive

- **Linux**
  - `Duplicate File Finder.AppImage` - Portable executable
  - `Duplicate File Finder.deb` - Debian package

### Important Notes for Distribution

1. **Python Dependencies**
   - The Python script is bundled with the application
   - Users don't need to install Python separately
   - The script is placed in the application's resources directory

2. **File Permissions**
   - The application requires read/write permissions for scanning directories
   - On macOS/Linux, users might need to grant permissions manually
   - On Windows, the installer handles permission requests

3. **Updates**
   - The application includes auto-update capabilities
   - Updates are handled through the electron-builder auto-update feature
   - Users will be notified when new versions are available

4. **Security Considerations**
   - The application runs with the user's permissions
   - File deletion requires explicit user confirmation
   - All operations are logged for transparency 
