import os
import subprocess
import ast
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field


class TestGeneratorToolInput(BaseModel):
    source_file: str = Field(..., description="Path to the source file to generate tests for")
    test_type: str = Field(default="pytest", description="Test framework: 'pytest' or 'jest'")

class TestGeneratorTool(BaseTool):
    name: str = "Test Generator Tool"
    description: str = (
        "Generate unit test files for Python (pytest) or TypeScript/JavaScript (jest) source files. "
        "Analyzes the source code and creates basic test templates."
    )
    args_schema: Type[BaseModel] = TestGeneratorToolInput

    def _run(self, source_file: str, test_type: str = "pytest") -> str:
        try:
            if not os.path.exists(source_file):
                return f"Error: Source file {source_file} not found"

            if test_type == "pytest":
                return self._generate_pytest(source_file)
            elif test_type == "jest":
                return self._generate_jest(source_file)
            else:
                return f"Unsupported test type: {test_type}"

        except Exception as e:
            return f"Error generating tests: {str(e)}"

    def _generate_pytest(self, source_file: str) -> str:
        """Generate pytest test file for Python source"""
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Parse to find classes and functions
        try:
            tree = ast.parse(source_code)
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

            # Generate test file content
            test_content = f'''"""Tests for {os.path.basename(source_file)}"""
import pytest
from {self._get_import_path(source_file)} import *


'''
            # Generate test functions
            for func in functions:
                test_content += f'''def test_{func}():
    """Test {func} function"""
    # TODO: Implement test
    pass


'''

            for cls in classes:
                test_content += f'''class Test{cls}:
    """Test suite for {cls}"""
    
    def test_init(self):
        """Test {cls} initialization"""
        # TODO: Implement test
        pass


'''

            # Determine test file path
            test_file = self._get_test_file_path(source_file)
            
            # Save test file
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)

            return f"Generated pytest file: {test_file}\nFound {len(functions)} functions and {len(classes)} classes"

        except SyntaxError as e:
            return f"Error parsing Python file: {str(e)}"

    def _generate_jest(self, source_file: str) -> str:
        """Generate jest test file for TypeScript/JavaScript"""
        basename = os.path.basename(source_file)
        name_without_ext = os.path.splitext(basename)[0]

        test_content = f'''/**
 * Tests for {basename}
 */

import {{ describe, it, expect }} from '@jest/globals';
// TODO: Import your functions/classes from '{name_without_ext}'

describe('{name_without_ext}', () => {{
  it('should work correctly', () => {{
    // TODO: Implement test
    expect(true).toBe(true);
  }});
}});
'''

        test_file = self._get_test_file_path(source_file, is_typescript=True)
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        return f"Generated jest test file: {test_file}"

    def _get_import_path(self, source_file: str) -> str:
        """Convert file path to Python import path"""
        # Remove .py extension and convert slashes
        import_path = source_file.replace('\\', '/').replace('.py', '').replace('/', '.')
        # Remove leading dots
        import_path = import_path.lstrip('.')
        # Handle src/ prefix
        if 'src.' in import_path:
            import_path = import_path.split('src.')[1]
        return import_path

    def _get_test_file_path(self, source_file: str, is_typescript: bool = False) -> str:
        """Generate test file path"""
        dir_name = os.path.dirname(source_file)
        base_name = os.path.basename(source_file)
        name_without_ext = os.path.splitext(base_name)[0]
        
        if is_typescript:
            ext = '.test.ts' if source_file.endswith('.ts') else '.test.js'
        else:
            ext = '.py'
            name_without_ext = f'test_{name_without_ext}'

        # Place tests in __tests__ subdirectory
        test_dir = os.path.join(dir_name, '__tests__')
        return os.path.join(test_dir, f'{name_without_ext}{ext}')


class PytestRunnerToolInput(BaseModel):
    test_path: str = Field(default=".", description="Path to test file or directory")
    verbose: bool = Field(default=True, description="Run with verbose output")

class PytestRunnerTool(BaseTool):
    name: str = "Pytest Runner Tool"
    description: str = "Execute Python tests using pytest and return results."
    args_schema: Type[BaseModel] = PytestRunnerToolInput

    def _run(self, test_path: str = ".", verbose: bool = True) -> str:
        try:
            cmd = ['pytest', test_path]
            if verbose:
                cmd.append('-v')

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            output = f"Exit Code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            return output

        except FileNotFoundError:
            return "Error: pytest not installed. Run: pip install pytest"
        except Exception as e:
            return f"Error running tests: {str(e)}"


class CodeScannerToolInput(BaseModel):
    directory: str = Field(default=".", description="Directory to scan for TODOs and issues")
    patterns: List[str] = Field(default=["TODO", "FIXME", "BUG"], description="Patterns to search for")

class CodeScannerTool(BaseTool):
    name: str = "Code Scanner Tool"
    description: str = "Scan codebase for TODO comments, FIXME tags, and potential issues."
    args_schema: Type[BaseModel] = CodeScannerToolInput

    def _run(self, directory: str = ".", patterns: List[str] = None) -> str:
        if patterns is None:
            patterns = ["TODO", "FIXME", "BUG"]

        findings = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip node_modules, .venv, __pycache__
                dirs[:] = [d for d in dirs if d not in ['node_modules', '.venv', '__pycache__', '.git']]
                
                for file in files:
                    if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                for pattern in patterns:
                                    if pattern in line:
                                        findings.append({
                                            'file': file_path,
                                            'line': line_num,
                                            'pattern': pattern,
                                            'text': line.strip()
                                        })

            if not findings:
                return "No TODOs or issues found in codebase."

            # Format output
            output = f"Found {len(findings)} items:\n\n"
            for finding in findings[:20]:  # Limit to 20 items
                output += f"[{finding['pattern']}] {finding['file']}:{finding['line']}\n"
                output += f"  {finding['text']}\n\n"

            if len(findings) > 20:
                output += f"\n... and {len(findings) - 20} more items"

            return output

        except Exception as e:
            return f"Error scanning code: {str(e)}"
