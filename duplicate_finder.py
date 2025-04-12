#!/usr/bin/env python3
"""
duplicate_finder.py - Find duplicate files in specified directories

This script scans directories for duplicate files by comparing file sizes
and then file hashes. This two-step approach makes the scanning process
much more efficient than hashing all files. It can also generate a file
containing paths of duplicates that could be deleted.
"""

import os
import sys
import hashlib
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import time

# Define excluded directories and files
EXCLUDED_DIRS = {
    # System directories
    '/System',
    '/Library',
    '/private',
    '/dev',
    '/Volumes',
    '/Network',
    '/cores',
    '/opt',
    '/sbin',
    '/usr',
    '/bin',
    '/etc',
    '/var',
    # Hidden directories
    '.*',
    # Common application directories
    'node_modules',
    'venv',
    '.venv',
    'env',
    '.env',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    '.idea',
    '.vscode',
    'build',
    'dist',
    'target',
    # Cache directories
    'cache',
    '.cache',
    'tmp',
    'temp',
    # Backup directories
    'backup',
    'backups',
    '.backup',
    '.backups',
}

EXCLUDED_FILES = {
    # System files
    '.DS_Store',
    '.localized',
    '.Trash',
    '.Trashes',
    '.Spotlight-V100',
    '.fseventsd',
    '.TemporaryItems',
    '.DocumentRevisions-V100',
    '.PKInstallSandboxManager',
    '.CFUserTextEncoding',
    '.hotfiles.btree',
    '.vol',
    # Configuration files
    '.config',
    '.profile',
    '.bashrc',
    '.bash_profile',
    '.zshrc',
    '.zprofile',
    '.ssh',
    '.gnupg',
    '.pki',
    # Cache files
    '.cache',
    '.npm',
    '.pip',
    '.m2',
    '.gradle',
    '.ivy2',
    '.sbt',
    # Database files
    '.sqlite',
    '.db',
    '.sqlite3',
    '.db3',
    # Temporary files
    '.tmp',
    '.temp',
    '.swp',
    '.swo',
    '.bak',
    '.backup',
    # Virtual environment files
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.exe',
    '.dylib',
    '.bundle',
}

def should_exclude(path: str) -> bool:
    """
    Check if a path should be excluded from scanning.
    
    Args:
        path: The path to check
    
    Returns:
        True if the path should be excluded, False otherwise
    """
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    print(f"\nChecking path: {abs_path}")
    
    # Check if path is in excluded directories
    for excluded_dir in EXCLUDED_DIRS:
        if excluded_dir.startswith('.'):
            # Handle hidden directories
            if os.path.basename(abs_path).startswith(excluded_dir[1:]):
                print(f"Excluded: Hidden directory match - {excluded_dir}")
                return True
        elif excluded_dir in abs_path.split(os.sep):  # Only match complete directory names
            print(f"Excluded: Directory match - {excluded_dir}")
            return True
    
    # Check if file is in excluded files
    filename = os.path.basename(abs_path)
    for excluded_file in EXCLUDED_FILES:
        if excluded_file.startswith('.'):
            # Handle hidden files
            if filename.startswith(excluded_file[1:]):
                print(f"Excluded: Hidden file match - {excluded_file}")
                return True
        elif filename.endswith(excluded_file):
            print(f"Excluded: File extension match - {excluded_file}")
            return True
    
    print("Not excluded")
    return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Find duplicate files across directories'
    )
    parser.add_argument(
        'directories', 
        nargs='+', 
        help='Directories to scan for duplicates'
    )
    parser.add_argument(
        '-r', '--recursive', 
        action='store_true', 
        help='Scan directories recursively'
    )
    parser.add_argument(
        '--hash-algorithm', 
        choices=['md5', 'sha1', 'sha256'], 
        default='md5',
        help='Hash algorithm to use (default: md5)'
    )
    parser.add_argument(
        '-o', '--output-file',
        help='Write paths of duplicate files (candidates for deletion) to specified file'
    )
    return parser.parse_args()

def get_file_hash(file_path: str, hash_algorithm: str = 'md5', chunk_size: int = 8192) -> str:
    """
    Calculate the hash of a file by reading it in chunks.
    
    Args:
        file_path: Path to the file
        hash_algorithm: The hash algorithm to use (md5, sha1, sha256)
        chunk_size: Size of chunks to read at a time
    
    Returns:
        The hash digest as a string
    """
    algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }
    
    if hash_algorithm not in algorithms:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")
    
    hash_obj = algorithms[hash_algorithm]()
    
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return None

def get_file_metadata(file_path: str) -> Tuple[str, int, datetime]:
    """
    Get file metadata including path, size, and modification date.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Tuple of (file_path, size, modification_time)
    """
    try:
        stat_info = os.stat(file_path)
        return (
            file_path,
            stat_info.st_size,
            datetime.fromtimestamp(stat_info.st_mtime)
        )
    except (IOError, OSError) as e:
        print(f"Error getting metadata for {file_path}: {e}", file=sys.stderr)
        return None

def scan_directories(directories: List[str], recursive: bool = True) -> List[str]:
    """
    Scan directories and return a list of all file paths.
    
    Args:
        directories: List of directory paths to scan
        recursive: Whether to scan recursively
    
    Returns:
        List of file paths
    """
    file_paths = []
    
    for directory in directories:
        print(f"\nScanning directory: {directory}")
        if not os.path.exists(directory):
            print(f"Warning: Directory does not exist: {directory}", file=sys.stderr)
            continue
            
        if not os.path.isdir(directory):
            print(f"Warning: Not a directory: {directory}", file=sys.stderr)
            continue
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    print(f"\nCurrent directory: {root}")
                    print(f"Found {len(files)} files")
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not should_exclude(file_path):
                            print(f"Adding file: {file_path}")
                            file_paths.append(file_path)
                        else:
                            print(f"Excluded file: {file_path}")
            else:
                for entry in os.scandir(directory):
                    if entry.is_file() and not should_exclude(entry.path):
                        print(f"Adding file: {entry.path}")
                        file_paths.append(entry.path)
                    else:
                        print(f"Excluded file: {entry.path}")
        except (IOError, OSError) as e:
            print(f"Error scanning directory {directory}: {e}", file=sys.stderr)
    
    print(f"\nTotal files found: {len(file_paths)}")
    return file_paths

def find_duplicates(file_paths: List[str], hash_algorithm: str = 'md5') -> Dict[str, List[Tuple[str, int, datetime]]]:
    """
    Find duplicate files by first comparing sizes, then hashing files of the same size.
    
    Args:
        file_paths: List of file paths to check
        hash_algorithm: Hash algorithm to use
    
    Returns:
        Dictionary of hash -> list of file metadata tuples
    """
    # Group files by size first
    files_by_size = defaultdict(list)
    total_files = len(file_paths)
    
    print(f"Step 1: Grouping {total_files} files by size...")
    
    for i, file_path in enumerate(file_paths):
        if i % 100 == 0 or i == total_files - 1:
            sys.stdout.write(f"\rProcessing file {i+1}/{total_files}...")
            sys.stdout.flush()
        
        metadata = get_file_metadata(file_path)
        if metadata:
            files_by_size[metadata[1]].append(metadata)
    
    print("\nStep 2: Calculating hashes for files with matching sizes...")
    
    # Only keep sizes with more than one file
    potential_duplicates = {
        size: files for size, files in files_by_size.items() if len(files) > 1
    }
    
    # Group files by hash
    duplicates = defaultdict(list)
    potential_duplicate_count = sum(len(files) for files in potential_duplicates.values())
    processed = 0
    
    for size, files in potential_duplicates.items():
        for file_metadata in files:
            file_path = file_metadata[0]
            
            processed += 1
            if processed % 10 == 0 or processed == potential_duplicate_count:
                sys.stdout.write(f"\rHashing file {processed}/{potential_duplicate_count}...")
                sys.stdout.flush()
            
            file_hash = get_file_hash(file_path, hash_algorithm)
            if file_hash:
                hash_key = f"{size}_{file_hash}"
                duplicates[hash_key].append(file_metadata)
    
    print("\nFinished hashing files!")
    
    # Only keep groups with more than one file (actual duplicates)
    return {
        hash_key: files for hash_key, files in duplicates.items() if len(files) > 1
    }

def print_duplicates(duplicates: Dict[str, List[Tuple[str, int, datetime]]], output_file: str = None):
    """
    Print information about duplicate files and optionally write duplicate paths to a file.
    
    Args:
        duplicates: Dictionary of hash -> list of file metadata
        output_file: Path to file where duplicate paths should be written (optional)
    """
    if not duplicates:
        print("\nNo duplicate files found.")
        return
    
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_groups = len(duplicates)
    total_wasted_space = sum(
        (len(files) - 1) * files[0][1] for files in duplicates.values()
    )
    
    print(f"\n{'-'*80}")
    print(f"Found {total_duplicates} duplicate files in {total_groups} groups")
    print(f"Wasted disk space: {format_size(total_wasted_space)}")
    print(f"{'-'*80}")
    
    # Create a list to hold all duplicate file paths (excluding the first in each group)
    deletion_candidates = []
    
    for i, (hash_key, files) in enumerate(duplicates.items(), 1):
        size = files[0][1]
        print(f"\nDuplicate Group #{i} - {len(files)} files, {format_size(size)} each:")
        
        # Sort files by modification time (most recent first)
        sorted_files = sorted(files, key=lambda x: x[2], reverse=True)
        
        # Add all but the first file (most recent) to deletion candidates
        if len(sorted_files) > 1:
            for file_path, file_size, mod_time in sorted_files[1:]:
                deletion_candidates.append(file_path)
        
        # Print file information with size in a consistent format
        for file_path, file_size, mod_time in sorted_files:
            print(f"  {file_path} ({format_size(file_size)})")
            print(f"    Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        wasted = (len(files) - 1) * size
        print(f"  Wasted space: {format_size(wasted)}")
    
    # Write duplicate file paths to output file if specified
    if output_file and deletion_candidates:
        try:
            with open(output_file, 'w') as f:
                for file_path in deletion_candidates:
                    # Escape paths for shell command usage by wrapping in quotes and escaping any existing quotes
                    escaped_path = file_path.replace("'", "'\\''")
                    f.write(f"'{escaped_path}'\n")
            print(f"\nWrote {len(deletion_candidates)} file paths to {output_file}")
        except IOError as e:
            print(f"Error writing to output file {output_file}: {e}", file=sys.stderr)

def format_size(size_in_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024 or unit == 'TB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def main():
    """Main function."""
    args = parse_arguments()
    
    start_time = time.time()
    
    print(f"Scanning directories: {', '.join(args.directories)}")
    print(f"Recursive scan: {'Yes' if args.recursive else 'No'}")
    print(f"Hash algorithm: {args.hash_algorithm}")
    print()
    
    file_paths = scan_directories(args.directories, args.recursive)
    
    if not file_paths:
        print("No files found in the specified directories.")
        return
    
    print(f"Found {len(file_paths)} files to check for duplicates.")
    
    duplicates = find_duplicates(file_paths, args.hash_algorithm)
    print_duplicates(duplicates, args.output_file)
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

