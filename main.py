#!/usr/bin/env python3
"""
Ultimate Focus Stacking with Apple and Adobe - Main Entry Point

This is the main entry point for the focus stacking workflow.
It maintains compatibility with the existing StackDealer.app while
working with the new organized folder structure.
"""

import sys
import os

# Import and run the main workflow
from src.runner import main

if __name__ == "__main__":
    main()
