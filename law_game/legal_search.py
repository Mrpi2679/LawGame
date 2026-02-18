import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import quote

class LegalSearchAgent:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def search_duckduckgo(self, query, num_results=5):
        """Search DuckDuckGo HTML version"""
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')
            
            results = []
            for result in soup.find_all('a', class_='result__a'):
                title = result.get_text(strip=True)
                href = result.get('href', '')
                
                # Extract actual URL from DuckDuckGo redirect
                actual_url = href
                if 'uddg=' in href:
                    from urllib.parse import unquote, parse_qs
                    try:
                        params = parse_qs(href.split('?')[1])
                        if 'uddg' in params:
                            actual_url = params['uddg'][0]
                    except:
                        pass
                
                if title and actual_url:
                    results.append({'title': title, 'url': actual_url})
            
            return results[:num_results]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def scrape_text(self, url):
        """Get clean text from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
                tag.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean: remove extra whitespace, ads, navigation
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                # Skip short lines (likely nav/ad)
                if len(line) > 30:
                    # Remove special chars but keep punctuation
                    line = re.sub(r'[^\w\s\.,;:!?\'\"-]', '', line)
                    if line:
                        lines.append(line)
            
            # Join and limit
            clean_text = '\n'.join(lines)
            return clean_text[:2500]
        except Exception as e:
            print(f"Scraping error: {e}")
            return ""
    
    def query_llama(self, prompt):
        """Query LLaMA via Ollama"""
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={"model": "llama2", "prompt": prompt, "stream": False},
                timeout=180
            )
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None
    
    def process(self, user_scenario):
        """Main flow: Search → Scrape → LLM → Response"""
        
        # Step 1: DuckDuckGo search
        results = self.search_duckduckgo(user_scenario)
        
        if not results:
            return {'success': False, 'error': 'No search results found'}
        
        # Step 2: Scrape top result
        scraped_text = self.scrape_text(results[0]['url'])
        
        if not scraped_text:
            return {'success': False, 'error': 'Could not extract content'}
        
        # Step 3: Build prompt
        prompt = f"""You are a legal education assistant. Based on this web content about a user's legal situation, provide helpful guidance.

USER SITUATION: {user_scenario}

WEB CONTENT:
{scraped_text[:2000]}

Respond in this format:
1. SITUATION SUMMARY: (1-2 lines)
2. LEGAL AREA: (type of law)
3. YOUR OPTIONS:
   A) [Best action]
   B) [Alternative action]  
   C) [What NOT to do]
4. KEY TAKEAWAY: (one practical tip)
5. DISCLAIMER: Educational purpose only."""

        # Step 4: Query LLaMA
        llm_response = self.query_llama(prompt)
        
        if llm_response:
            return {
                'success': True,
                'response': llm_response,
                'source_title': results[0]['title']
            }
        
        # Fallback if no LLM
        return {
            'success': False,
            'error': 'LLM not available',
            'raw_content': scraped_text[:1000]
        }


def search_legal_info(scenario):
    """Simple function for Flask integration"""
    agent = LegalSearchAgent()
    return agent.process(scenario)


if __name__ == "__main__":
    agent = LegalSearchAgent()
    result = agent.process("employer not paying salary what legal rights do I have")
    print(json.dumps(result, indent=2))
