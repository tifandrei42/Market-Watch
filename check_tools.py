try:
    from crewai_tools import BraveSearchTool
    print("Found BraveSearchTool in crewai_tools")
except ImportError:
    print("BraveSearchTool NOT in crewai_tools")

try:
    from langchain_community.tools import BraveSearch
    print("Found BraveSearch in langchain_community.tools")
except ImportError:
    print("BraveSearch NOT in langchain_community.tools")
