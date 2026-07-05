"""Plugin directory for user-defined processors.

Place your custom processor modules here. They will be automatically
discovered by the PluginRegistry.

Usage:
    1. Create a new .py file in this directory
    2. Inherit from videomarker.core.processor.Processor
    3. Decorate with @processor("your_processor_name")
    4. Implement the process() method
"""
