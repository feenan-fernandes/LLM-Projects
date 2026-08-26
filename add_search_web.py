import re

with open('swarm-ide/backend/loop/action_parser.py', 'r', encoding='utf-8') as f:
    action_parser = f.read()

if 'search_web' not in action_parser:
    search_web_xml = '''
<search_web>
  <query>The query to search the internet for</query>
</search_web>
'''
    action_parser = action_parser.replace('<execute_bash>', search_web_xml.strip() + '\\n\\n<execute_bash>')
    
    # Add to REGEX
    search_web_regex = '''
    search_web = re.search(r'<search_web>.*?<query>(.*?)</query>.*?</search_web>', text, re.DOTALL | re.IGNORECASE)
    if search_web: return {"action": "search_web", "query": search_web.group(1).strip()}
'''
    action_parser = action_parser.replace('execute_bash = re.search', search_web_regex.strip() + '\\n    execute_bash = re.search')
    
    with open('swarm-ide/backend/loop/action_parser.py', 'w', encoding='utf-8') as f:
        f.write(action_parser)

with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    builder_loop = f.read()

if 'elif action_type == "search_web":' not in builder_loop:
    search_web_logic = '''
            elif action_type == "search_web":
                query = args.get("query", "")
                try:
                    from duckduckgo_search import DDGS
                    results = DDGS().text(query, max_results=3)
                    if results:
                        observation = "Search Results:\\n"
                        for r in results:
                            observation += f"- [{{r.get('title')}}]({{r.get('href')}})\\n{{r.get('body')}}\\n\\n"
                    else:
                        observation = "No results found for query."
                except Exception as e:
                    observation = f"Web search failed: {e}"
'''
    builder_loop = builder_loop.replace('elif action_type == "execute_bash":', search_web_logic.strip() + '\\n\\n            elif action_type == "execute_bash":')
    
    with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
        f.write(builder_loop)

print("Added search_web action.")
