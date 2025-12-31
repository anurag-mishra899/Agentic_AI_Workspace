"""
LinkedIn Job Hunter Agent

An agentic workflow using:
- deepagents from LangChain for agent orchestration with planning capabilities
- Playwright MCP server for browser automation
- FilesystemBackend to offload context to disk and manage memory
- Custom middleware to handle console noise and truncate redundant context

Usage:
    python linkedin_job_hunter.py

    # Or with custom job search:
    python linkedin_job_hunter.py --job-title "Machine Learning Engineer" --num-jobs 10
"""

import sys
import os
import asyncio
import argparse
from typing import Any
from datetime import datetime

# Setup path for custom utilities
LLM_UTILS_PATH = "/Users/anuragmishra/Documents/AI Workspace/"
sys.path.insert(0, LLM_UTILS_PATH)

# LangChain and deepagents imports
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ContextEditingMiddleware,
    ClearToolUsesEdit,
)
from langgraph.runtime import Runtime

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

# LangChain tools for file operations
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import base64
from PIL import Image
import io

# LLM configuration (all LLM initialization in models_config.py)
from llm_utils.models_config import openai_llm, vision_llm


# =============================================================================
# Configuration
# =============================================================================

# Directory to store agent filesystem data
AGENT_WORKSPACE_DIR = "/Users/anuragmishra/Documents/AI Workspace/web_agent/agent_workspace"


# =============================================================================
# Custom Tools for File Operations
# =============================================================================

@tool
def save_job_results(content: str, filename: str = "job_results.md") -> str:
    """
    Save job search results to a file in the workspace directory.

    Args:
        content: The content to save (markdown formatted job listings)
        filename: Name of the file to save (default: job_results.md)

    Returns:
        Success message with file path
    """
    os.makedirs(AGENT_WORKSPACE_DIR, exist_ok=True)
    filepath = os.path.join(AGENT_WORKSPACE_DIR, filename)

    # Add timestamp header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_content = f"# LinkedIn Job Search Results\n\nGenerated: {timestamp}\n\n{content}"

    with open(filepath, 'w') as f:
        f.write(full_content)

    return f"Successfully saved results to: {filepath}"


def resize_image_base64(base64_data: str, max_width: int = 1200, quality: int = 85) -> str:
    """
    Resize a base64 image to reduce payload size while maintaining readability.

    Args:
        base64_data: Base64 encoded image
        max_width: Maximum width to resize to
        quality: JPEG quality (1-100)

    Returns:
        Resized base64 image
    """
    try:
        # Decode base64 to image
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))

        # Calculate new dimensions maintaining aspect ratio
        width, height = image.size
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for JPEG)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        # Save to bytes as JPEG (smaller than PNG)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)

        # Encode back to base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Warning: Could not resize image: {e}")
        return base64_data  # Return original if resize fails


# Global variable to store the last screenshot path
LAST_SCREENSHOT_PATH = os.path.join(AGENT_WORKSPACE_DIR, "current_screenshot.png")


def save_screenshot_to_file(base64_data: str) -> str:
    """Save base64 screenshot to file and return path."""
    # Clean up base64 string if it has data URI prefix
    if "," in base64_data:
        base64_data = base64_data.split(",")[1]

    os.makedirs(AGENT_WORKSPACE_DIR, exist_ok=True)
    with open(LAST_SCREENSHOT_PATH, "wb") as f:
        f.write(base64.b64decode(base64_data))
    print(f"Screenshot saved to: {LAST_SCREENSHOT_PATH}")
    return LAST_SCREENSHOT_PATH


@tool
def analyze_saved_screenshot(num_jobs: int = 10) -> str:
    """
    Analyze the most recently saved screenshot using Vision AI.

    IMPORTANT: Call this AFTER browser_screenshot has been called.
    The screenshot is automatically saved to a file by the system.

    Args:
        num_jobs: Maximum number of jobs to extract (default: 10)

    Returns:
        Extracted job listings in markdown format
    """
    # Check if screenshot file exists
    if not os.path.exists(LAST_SCREENSHOT_PATH):
        return "Error: No screenshot found. Please call browser_screenshot first."

    print(f"Reading screenshot from: {LAST_SCREENSHOT_PATH}")

    # Read and resize the image
    try:
        with open(LAST_SCREENSHOT_PATH, "rb") as f:
            image_data = f.read()

        # Convert to base64
        screenshot_base64 = base64.b64encode(image_data).decode('utf-8')

        # Resize image to reduce payload size
        print("Resizing screenshot for API call...")
        resized_base64 = resize_image_base64(screenshot_base64, max_width=1400, quality=85)
        original_size = len(screenshot_base64)
        new_size = len(resized_base64)
        print(f"Image size reduced from {original_size:,} to {new_size:,} bytes ({100*new_size/original_size:.1f}%)")

    except Exception as e:
        return f"Error reading screenshot: {str(e)}"

    extraction_prompt = f"""Analyze this LinkedIn job search results screenshot.

Extract ALL visible job listings from the LEFT PANEL (the job cards list).

For EACH job card visible, extract:
1. Job Title
2. Company Name
3. Location (City, State, Country)
4. Work Type (On-site, Remote, Hybrid) if shown
5. Time Posted (e.g., "1 week ago", "3 days ago")

Format your response as a numbered markdown list:

1. **[Job Title]** - [Company] - [Location] ([Work Type]) - [Time Posted]
2. **[Job Title]** - [Company] - [Location] ([Work Type]) - [Time Posted]
...

Extract up to {num_jobs} jobs. Include ALL jobs you can see in the left panel.
If any field is not visible, write "N/A".

IMPORTANT: Count carefully and list EVERY job card you see in the left panel."""

    try:
        print("Sending screenshot to Vision AI for analysis...")
        message = HumanMessage(
            content=[
                {"type": "text", "text": extraction_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{resized_base64}"},
                },
            ],
        )

        response = vision_llm.invoke([message])
        print("Vision AI analysis complete!")
        return response.content
    except Exception as e:
        return f"Error analyzing screenshot: {str(e)}"


# =============================================================================
# Middleware Classes (Simplified - matching working notebook)
# =============================================================================

class ScreenshotInterceptMiddleware(AgentMiddleware):
    """
    Middleware that intercepts screenshot base64 data, saves it to a file,
    and replaces the large base64 with a small placeholder to avoid context bloat.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def _is_base64_image(self, content: str) -> bool:
        """Check if content looks like base64 image data."""
        if not isinstance(content, str):
            return False
        # Base64 images are very long and contain specific patterns
        if len(content) > 10000:
            # Check for common base64 image prefixes or raw base64
            if content.startswith('data:image') or content.startswith('iVBOR') or content.startswith('/9j/'):
                return True
            # Check if it looks like base64 (mostly alphanumeric)
            sample = content[:1000].replace('\n', '').replace('\r', '')
            alphanumeric_ratio = sum(c.isalnum() or c in '+/=' for c in sample) / len(sample) if sample else 0
            if alphanumeric_ratio > 0.95 and len(content) > 50000:
                return True
        return False

    def _save_and_replace_screenshot(self, content: str) -> str:
        """Save screenshot to file and return placeholder text."""
        try:
            save_screenshot_to_file(content)
            return f"[Screenshot saved to {LAST_SCREENSHOT_PATH}. Call analyze_saved_screenshot() to extract job listings.]"
        except Exception as e:
            print(f"Warning: Could not save screenshot: {e}")
            return "[Screenshot captured but could not be saved. Try again.]"

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Intercept messages before they go to the model, save screenshots to files."""
        for msg in state['messages']:
            try:
                content = msg.content if hasattr(msg, 'content') else msg.get('content')
            except Exception:
                continue

            # Handle string content (raw base64)
            if isinstance(content, str) and self._is_base64_image(content):
                replacement = self._save_and_replace_screenshot(content)
                try:
                    msg.content = replacement
                except Exception:
                    try:
                        msg['content'] = replacement
                    except Exception:
                        pass
                if self.verbose:
                    print("Intercepted screenshot data, saved to file")

            # Handle list content (tool results with text field)
            elif isinstance(content, list):
                new_content = []
                for elem in content:
                    if isinstance(elem, str) and self._is_base64_image(elem):
                        new_content.append(self._save_and_replace_screenshot(elem))
                        if self.verbose:
                            print("Intercepted screenshot data in list, saved to file")
                    elif isinstance(elem, dict):
                        text = elem.get('text', '')
                        if isinstance(text, str) and self._is_base64_image(text):
                            new_elem = dict(elem)
                            new_elem['text'] = self._save_and_replace_screenshot(text)
                            new_content.append(new_elem)
                            if self.verbose:
                                print("Intercepted screenshot data in dict, saved to file")
                        else:
                            new_content.append(elem)
                    else:
                        new_content.append(elem)
                try:
                    msg.content = new_content
                except Exception:
                    try:
                        msg['content'] = new_content
                    except Exception:
                        pass

        return None


class LoggingMiddleware(AgentMiddleware):
    """
    Middleware for logging and truncating long content.
    """

    def __init__(self, max_content_length: int = 2000, verbose: bool = True):
        self.max_content_length = max_content_length
        self.verbose = verbose
        self.call_count = 0

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        self.call_count += 1

        for msg in state['messages']:
            try:
                content = msg.content if hasattr(msg, 'content') else msg.get('content')
            except Exception:
                continue

            # Truncate string content
            if isinstance(content, str) and len(content) > self.max_content_length:
                truncated = content[:self.max_content_length] + f"\n... [TRUNCATED {len(content) - self.max_content_length} chars]"
                try:
                    msg.content = truncated
                except Exception:
                    try:
                        msg['content'] = truncated
                    except Exception:
                        pass

            # Truncate list content
            elif isinstance(content, list):
                new_content = []
                for elem in content:
                    if isinstance(elem, str):
                        if len(elem) > self.max_content_length:
                            new_content.append(elem[:self.max_content_length] + "... [TRUNCATED]")
                        else:
                            new_content.append(elem)
                    elif isinstance(elem, dict) and isinstance(elem.get('text'), str):
                        text = elem['text']
                        if len(text) > self.max_content_length:
                            new_elem = dict(elem)
                            new_elem['text'] = text[:self.max_content_length] + "... [TRUNCATED]"
                            new_content.append(new_elem)
                        else:
                            new_content.append(elem)
                    else:
                        new_content.append(elem)
                try:
                    msg.content = new_content
                except Exception:
                    try:
                        msg['content'] = new_content
                    except Exception:
                        pass

        if self.verbose:
            print(f"\n[Call #{self.call_count}] Processing {len(state['messages'])} messages")

        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if not self.verbose:
            return None

        try:
            last_msg = state['messages'][-1]
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                tool_names = [tc.get('name', 'unknown') for tc in last_msg.tool_calls]
                print(f"Tools called: {tool_names}")
            elif hasattr(last_msg, 'content') and last_msg.content:
                preview = str(last_msg.content)[:150]
                print(f"Response: {preview}...")
        except Exception as e:
            print(f"Error in after_model: {e}")

        return None


# =============================================================================
# Agent System Prompt
# =============================================================================

AGENT_SYSTEM_PROMPT = """
You are an expert web automation agent specialized in job hunting on LinkedIn.

## Your Capabilities:
- Navigate websites using browser tools
- Take screenshots and analyze them with Vision AI
- Extract job listings from visual screenshots
- Save results to files

## CRITICAL TOOL DISTINCTION:
- `browser_screenshot` = Takes a visual screenshot (USE THIS!)
- `browser_snapshot` = Takes accessibility tree dump (DO NOT USE - saves to wrong directory)

ALWAYS use `browser_screenshot`, NEVER use `browser_snapshot`!

## SCREENSHOT-BASED EXTRACTION WORKFLOW:
1. Navigate to linkedin.com/jobs/
2. Wait for page to load
3. Type job title in search and press Enter
4. Wait for results to load
5. **USE `browser_screenshot`** (NOT browser_snapshot!)
6. **CALL `analyze_saved_screenshot()`** - screenshot is auto-saved!
7. Save the results using `save_job_results`

## Tool Usage:

### Browser Tools:
- `browser_navigate` - Go to https://www.linkedin.com/jobs/
- `browser_wait_for` - Wait for content: use time=5 for initial load
- `browser_type` - Type in input fields (find by selector or element)
- `browser_press_key` - Press "Enter" to submit search
- `browser_click` - Click elements
- `browser_screenshot` - **USE THIS** - Takes visual screenshot, auto-saved by system

### Analysis Tools:
- `analyze_saved_screenshot` - Analyzes the last screenshot. Call with: analyze_saved_screenshot() or analyze_saved_screenshot(num_jobs=10)

### File Tools:
- `save_job_results` - Save extracted job list to markdown file

## IMPORTANT - The Two-Step Process:
1. Call `browser_screenshot` (NOT browser_snapshot!) - screenshot auto-saved
2. Call `analyze_saved_screenshot()` - reads saved file, analyzes with Vision AI

## DO NOT USE:
- `browser_snapshot` - Saves to /tmp/ directory, causes file not found errors
- `browser_evaluate` - JavaScript selectors return empty results
- Do NOT pass base64 data to analyze_saved_screenshot

## WORKFLOW FOR SEARCH:
To search on LinkedIn without needing to identify the search box:
1. Navigate to: https://www.linkedin.com/jobs/search/?keywords=YOUR_JOB_TITLE
   (URL-encode spaces as %20)
2. Wait for results
3. Take screenshot with browser_screenshot
4. Analyze with analyze_saved_screenshot()
"""


# =============================================================================
# Main Agent Functions
# =============================================================================

def create_job_search_task(job_title: str, num_jobs: int = 10) -> str:
    """Create a job search task prompt."""
    # URL-encode the job title for direct navigation
    encoded_title = job_title.replace(' ', '%20')

    return f"""
Search for '{job_title}' jobs on LinkedIn and extract job listings.

## Step-by-step instructions:

### Phase 1: Navigate Directly to Search Results
1. Navigate directly to the search URL:
   browser_navigate(url="https://www.linkedin.com/jobs/search/?keywords={encoded_title}")
2. Wait 5 seconds for results to load: browser_wait_for(time=5)

### Phase 2: Capture Screenshot (USE browser_screenshot!)
3. Call browser_screenshot to capture the page
   - USE `browser_screenshot` (NOT browser_snapshot!)
   - browser_snapshot saves to /tmp/ and causes errors
   - browser_screenshot returns image data that is auto-saved
4. The screenshot is AUTOMATICALLY saved by the system

### Phase 3: Extract Jobs Using Vision AI
5. Call analyze_saved_screenshot(num_jobs={num_jobs})
   - Just call it with num_jobs, no screenshot data needed
   - It reads from the auto-saved file
6. The Vision AI will extract ALL visible jobs from the screenshot

### Phase 4: Save and Report
7. Call save_job_results with the extracted job list
8. Report the complete job list in your response

## CRITICAL REMINDERS:
- Use `browser_screenshot` NOT `browser_snapshot`
- Navigate directly to search URL to skip finding the search box
- analyze_saved_screenshot reads from file - no data to pass

## Expected Output:
A numbered list of {num_jobs} jobs with: Title, Company, Location, Work Type, Time Posted
"""


async def run_job_hunter_agent(
    job_title: str = "Generative AI Architect",
    num_jobs: int = 5,
    verbose: bool = True,
    headless: bool = False,
) -> str | None:
    """
    Main function to run the LinkedIn job hunter agent.

    Args:
        job_title: Job title to search for
        num_jobs: Number of job postings to extract
        verbose: Enable verbose logging
        headless: Run browser in headless mode

    Returns:
        Final agent response or None if failed
    """

    # Ensure workspace directory exists
    os.makedirs(AGENT_WORKSPACE_DIR, exist_ok=True)

    # Configure server params based on headless setting
    server_args = ["@playwright/mcp@latest"]
    if headless:
        server_args.append("--headless")

    server_params = StdioServerParameters(
        command="npx",
        args=server_args,
    )

    print(f"{'='*60}")
    print(f"LinkedIn Job Hunter Agent")
    print(f"{'='*60}")
    print(f"Job Title: {job_title}")
    print(f"Number of Jobs: {num_jobs}")
    print(f"Workspace: {AGENT_WORKSPACE_DIR}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Headless: {headless}")
    print(f"{'='*60}\n")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP connection
            await session.initialize()

            # Load Playwright browser tools
            playwright_tools = await load_mcp_tools(session)
            print(f"Loaded {len(playwright_tools)} browser tools")
            if verbose:
                print(f"Tools: {[t.name for t in playwright_tools[:5]]}...")

            # Combine browser tools with custom tools (vision analysis + file saving)
            all_tools = playwright_tools + [analyze_saved_screenshot, save_job_results]
            print(f"Total tools available: {len(all_tools)}")
            print(f"Custom tools: analyze_saved_screenshot, save_job_results")

            # Create the deep agent with optimized configuration
            # Using virtual_mode=True to match working notebook
            agent = create_deep_agent(
                model=openai_llm,
                tools=all_tools,
                system_prompt=AGENT_SYSTEM_PROMPT,

                # FilesystemBackend: virtual_mode=True keeps files in memory (like working notebook)
                backend=FilesystemBackend(
                    root_dir=AGENT_WORKSPACE_DIR,
                    virtual_mode=True
                ),

                # Middleware stack for context management
                # Note: Screenshots are large base64 strings, so we need higher limits
                middleware=[
                    # FIRST: Intercept screenshots and save to file (prevents context bloat)
                    ScreenshotInterceptMiddleware(verbose=verbose),
                    # THEN: Truncate any remaining long content
                    LoggingMiddleware(max_content_length=4000, verbose=verbose),
                    ContextEditingMiddleware(
                        edits=[
                            ClearToolUsesEdit(
                                trigger=5000,
                                keep=5,
                                clear_tool_inputs=False,
                                exclude_tools=["analyze_saved_screenshot"],
                                placeholder="[cleared]"
                            ),
                        ],
                    ),
                ],
            )

            print("\nAgent created. Starting execution...\n")

            # Create task
            task = create_job_search_task(job_title, num_jobs)

            # Run the agent with streaming
            final_response = None
            async for chunk in agent.astream(
                {"messages": [{"role": "user", "content": task}]},
                stream_mode="values"
            ):
                latest_message = chunk["messages"][-1]

                # Display progress
                if hasattr(latest_message, 'content') and latest_message.content:
                    if not hasattr(latest_message, 'tool_calls') or not latest_message.tool_calls:
                        final_response = latest_message.content
                        print(f"\n--- Agent Response ---")
                        # Show more of the response for debugging
                        print(latest_message.content[:2000])
                        if len(latest_message.content) > 2000:
                            print("...")

                elif hasattr(latest_message, 'tool_calls') and latest_message.tool_calls:
                    for tc in latest_message.tool_calls:
                        print(f"Executing: {tc.get('name', 'unknown')}")

            print(f"\n{'='*60}")
            print("Agent execution completed.")
            print(f"Check workspace for saved files: {AGENT_WORKSPACE_DIR}")

            return final_response


def list_workspace_files(directory: str) -> None:
    """Recursively list all files in the workspace."""
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    print(f"\nFiles in agent workspace:")
    print("=" * 40)

    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            print(f'{subindent}{file} ({size} bytes)')


def read_summary() -> None:
    """Read and display the job search summary if it exists."""
    summary_path = os.path.join(AGENT_WORKSPACE_DIR, "data", "summary.md")
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            print("\nJob Search Summary:")
            print("=" * 40)
            print(f.read())
    else:
        print("\nNo summary file found yet.")


# =============================================================================
# CLI Entry Point
# =============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="LinkedIn Job Hunter Agent - Automated job search using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linkedin_job_hunter.py
  python linkedin_job_hunter.py --job-title "Machine Learning Engineer"
  python linkedin_job_hunter.py --job-title "Data Scientist" --num-jobs 10 --headless
  python linkedin_job_hunter.py --list-files
  python linkedin_job_hunter.py --show-summary
        """
    )

    parser.add_argument(
        "--job-title", "-j",
        type=str,
        default="Generative AI Architect",
        help="Job title to search for (default: 'Generative AI Architect')"
    )

    parser.add_argument(
        "--num-jobs", "-n",
        type=int,
        default=5,
        help="Number of job postings to extract (default: 5)"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce verbose output"
    )

    parser.add_argument(
        "--list-files", "-l",
        action="store_true",
        help="List files in agent workspace and exit"
    )

    parser.add_argument(
        "--show-summary", "-s",
        action="store_true",
        help="Show job search summary and exit"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Handle utility commands
    if args.list_files:
        list_workspace_files(AGENT_WORKSPACE_DIR)
        return

    if args.show_summary:
        read_summary()
        return

    # Run the agent
    try:
        result = asyncio.run(
            run_job_hunter_agent(
                job_title=args.job_title,
                num_jobs=args.num_jobs,
                verbose=not args.quiet,
                headless=args.headless,
            )
        )

        # Show workspace files after completion
        list_workspace_files(AGENT_WORKSPACE_DIR)

        # Show summary if available
        read_summary()

    except KeyboardInterrupt:
        print("\n\nAgent interrupted by user.")
    except Exception as e:
        print(f"\nError running agent: {e}")
        raise


if __name__ == "__main__":
    main()
