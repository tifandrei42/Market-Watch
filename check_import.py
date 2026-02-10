try:
    from crewai.tools import BaseTool
    print("Found BaseTool in crewai.tools")
except ImportError:
    print("Not in crewai.tools")

try:
    from crewai_tools import BaseTool
    print("Found BaseTool in crewai_tools")
except ImportError:
    print("Not in crewai_tools")
