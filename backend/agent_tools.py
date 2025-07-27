"""
Agent Tools Manager - Система инструментов для агентов
Предоставляет агентам доступ ко всем инструментам, как у главного AI помощника
"""

import os
import json
import asyncio
import subprocess
import glob
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import aiofiles
import aiohttp
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import base64
from PIL import Image
import io

class AgentToolsManager:
    """Менеджер инструментов для агентов - предоставляет все возможности главного AI"""
    
    def __init__(self, workspace_path: str = "/app"):
        self.workspace_path = workspace_path
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    # ============= ФАЙЛОВЫЕ ОПЕРАЦИИ =============
    
    async def view_file(self, path: str, view_range: Optional[List[int]] = None) -> Dict[str, Any]:
        """Просмотр содержимого файла"""
        try:
            full_path = os.path.join(self.workspace_path, path.lstrip('/'))
            
            if os.path.isdir(full_path):
                # Показать содержимое директории
                items = []
                for item in sorted(os.listdir(full_path)):
                    item_path = os.path.join(full_path, item)
                    is_dir = os.path.isdir(item_path)
                    items.append(f"{'[DIR]' if is_dir else '[FILE]'} {item}")
                
                return {
                    "success": True,
                    "type": "directory",
                    "path": path,
                    "content": "\n".join(items)
                }
            
            # Читать файл
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            lines = content.split('\n')
            
            if view_range:
                start_line = max(1, view_range[0]) - 1  # Convert to 0-based
                end_line = len(lines) if view_range[1] == -1 else min(len(lines), view_range[1])
                lines = lines[start_line:end_line]
                content = '\n'.join(f"{i + start_line + 1}|{line}" for i, line in enumerate(lines))
            else:
                content = '\n'.join(f"{i + 1}|{line}" for i, line in enumerate(lines))
            
            return {
                "success": True,
                "type": "file",
                "path": path,
                "content": content,
                "total_lines": len(lines)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": path
            }
    
    async def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Создание нового файла"""
        try:
            full_path = os.path.join(self.workspace_path, path.lstrip('/'))
            
            # Создать директории если нужно
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "success": True,
                "path": path,
                "message": f"File created: {path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": path
            }
    
    async def search_replace(self, path: str, old_str: str, new_str: str = "") -> Dict[str, Any]:
        """Поиск и замена в файле"""
        try:
            full_path = os.path.join(self.workspace_path, path.lstrip('/'))
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if old_str not in content:
                return {
                    "success": False,
                    "error": f"String not found: {old_str[:50]}...",
                    "path": path
                }
            
            new_content = content.replace(old_str, new_str)
            
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(new_content)
            
            return {
                "success": True,
                "path": path,
                "message": f"Replaced text in {path}",
                "changes": len(content) - len(new_content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": path
            }
    
    async def bulk_file_writer(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """Массовое создание файлов"""
        results = []
        
        for file_info in files:
            path = file_info.get('path')
            content = file_info.get('content', '')
            
            result = await self.create_file(path, content)
            results.append({
                "path": path,
                "success": result["success"],
                "error": result.get("error")
            })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": success_count == len(files),
            "total_files": len(files),
            "successful": success_count,
            "failed": len(files) - success_count,
            "results": results
        }
    
    # ============= СИСТЕМНЫЕ КОМАНДЫ =============
    
    async def execute_bash(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Выполнение bash команд"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.workspace_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                return {
                    "success": process.returncode == 0,
                    "command": command,
                    "returncode": process.returncode,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8')
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "command": command,
                    "error": f"Command timed out after {timeout} seconds"
                }
                
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e)
            }
    
    # ============= ПОИСК И НАВИГАЦИЯ =============
    
    async def glob_tool(self, pattern: str, max_results: int = 30) -> Dict[str, Any]:
        """Поиск файлов по паттерну"""
        try:
            search_path = os.path.join(self.workspace_path, pattern)
            matches = glob.glob(search_path, recursive=True)
            
            # Ограничить результаты
            matches = matches[:max_results]
            
            # Сделать пути относительными
            relative_matches = []
            for match in matches:
                rel_path = os.path.relpath(match, self.workspace_path)
                relative_matches.append(rel_path)
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": relative_matches,
                "total_found": len(matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "pattern": pattern,
                "error": str(e)
            }
    
    async def grep_tool(self, pattern: str, path: str = ".", include: Optional[str] = None) -> Dict[str, Any]:
        """Поиск по содержимому файлов"""
        try:
            command = f"grep -r -n '{pattern}' {path}"
            
            if include:
                command += f" --include='{include}'"
            
            result = await self.execute_bash(command)
            
            matches = []
            if result["success"] and result["stdout"]:
                for line in result["stdout"].strip().split('\n'):
                    if ':' in line:
                        file_path, line_num, content = line.split(':', 2)
                        matches.append({
                            "file": file_path,
                            "line": int(line_num),
                            "content": content.strip()
                        })
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "total_found": len(matches)
            }
            
        except Exception as e:
            return {
                "success": False,
                "pattern": pattern,
                "error": str(e)
            }
    
    # ============= ВЕБ И AI ИНСТРУМЕНТЫ =============
    
    async def web_search_tool(self, query: str, search_context_size: str = "medium") -> Dict[str, Any]:
        """Поиск в интернете с помощью DuckDuckGo"""
        try:
            # Используем DuckDuckGo для поиска (не требует API ключи)
            search_url = "https://duckduckgo.com/html/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            params = {
                'q': query,
                'o': 'json'
            }
            
            # Use the context manager's session if available, otherwise create a new one
            if self.session:
                async with self.session.get(search_url, params=params, headers=headers) as response:
                    html = await response.text()
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    results = []
                    
                    for result in soup.find_all('div', class_='result')[:10]:  # Первые 10 результатов
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet
                            })
                    
                    return {
                        "success": True,
                        "query": query,
                        "results": results,
                        "total_found": len(results)
                    }
            else:
                # Fallback to creating own session if context manager not used
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, params=params, headers=headers) as response:
                        html = await response.text()
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        
                        for result in soup.find_all('div', class_='result')[:10]:  # Первые 10 результатов
                            title_elem = result.find('a', class_='result__a')
                            snippet_elem = result.find('a', class_='result__snippet')
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                url = title_elem.get('href', '')
                                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                                
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet
                                })
                        
                        return {
                            "success": True,
                            "query": query,
                            "results": results,
                            "total_found": len(results)
                        }
                    
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    async def crawl_tool(self, url: str, extraction_method: str = "scrape", question: str = "text") -> Dict[str, Any]:
        """Скрапинг веб-страниц"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Use the context manager's session if available, otherwise create a new one
            session_to_use = self.session if self.session else aiohttp.ClientSession()
            
            if self.session:
                async with self.session.get(url, headers=headers, timeout=30) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "url": url,
                            "error": f"HTTP {response.status}: {response.reason}"
                        }
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Удалить скрипты и стили
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Извлечь текст в зависимости от вопроса
                    if "title" in question.lower():
                        content = soup.title.string if soup.title else "No title found"
                    elif "links" in question.lower():
                        links = [{"text": a.get_text(strip=True), "href": a.get('href')} 
                                for a in soup.find_all('a', href=True)]
                        content = json.dumps(links, indent=2, ensure_ascii=False)
                    elif "images" in question.lower():
                        images = [{"alt": img.get('alt', ''), "src": img.get('src')} 
                                 for img in soup.find_all('img', src=True)]
                        content = json.dumps(images, indent=2, ensure_ascii=False)
                    else:
                        # Извлечь основной текст
                        content = soup.get_text()
                        # Очистить лишние пробелы
                        lines = (line.strip() for line in content.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Ограничить размер для больших страниц
                        if len(content) > 5000:
                            content = content[:5000] + "... (content truncated)"
                    
                    return {
                        "success": True,
                        "url": url,
                        "content": content,
                        "title": soup.title.string if soup.title else "",
                        "extraction_method": extraction_method
                    }
            else:
                # Fallback to creating own session if context manager not used
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=30) as response:
                        if response.status != 200:
                            return {
                                "success": False,
                                "url": url,
                                "error": f"HTTP {response.status}: {response.reason}"
                            }
                        
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Удалить скрипты и стили
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Извлечь текст в зависимости от вопроса
                        if "title" in question.lower():
                            content = soup.title.string if soup.title else "No title found"
                        elif "links" in question.lower():
                            links = [{"text": a.get_text(strip=True), "href": a.get('href')} 
                                    for a in soup.find_all('a', href=True)]
                            content = json.dumps(links, indent=2, ensure_ascii=False)
                        elif "images" in question.lower():
                            images = [{"alt": img.get('alt', ''), "src": img.get('src')} 
                                     for img in soup.find_all('img', src=True)]
                            content = json.dumps(images, indent=2, ensure_ascii=False)
                        else:
                            # Извлечь основной текст
                            content = soup.get_text()
                            # Очистить лишние пробелы
                            lines = (line.strip() for line in content.splitlines())
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            content = ' '.join(chunk for chunk in chunks if chunk)
                            
                            # Ограничить размер для больших страниц
                            if len(content) > 5000:
                                content = content[:5000] + "... (content truncated)"
                        
                        return {
                            "success": True,
                            "url": url,
                            "content": content,
                            "title": soup.title.string if soup.title else "",
                            "extraction_method": extraction_method
                        }
                    
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def screenshot_tool(self, page_url: str, script: str = None) -> Dict[str, Any]:
        """Создание скриншотов веб-страниц (заглушка)"""
        # Это требует Playwright или Selenium, которые сложны в асинхронном контексте
        # Для демо возвращаем заглушку
        return {
            "success": True,
            "page_url": page_url,
            "message": "Screenshot functionality would be implemented with Playwright",
            "note": "This is a mock implementation. In production, use Playwright for screenshots."
        }
    
    async def vision_expert_agent(self, task: str) -> Dict[str, Any]:
        """Работа с изображениями"""
        try:
            # Простая генерация placeholder изображения
            img = Image.new('RGB', (800, 600), color='lightblue')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Конвертируем в base64
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "task": task,
                "image_data": f"data:image/png;base64,{img_base64}",
                "summary": f"Generated placeholder image for task: {task}",
                "image_urls": [f"data:image/png;base64,{img_base64}"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "task": task,
                "error": str(e)
            }
    
    async def integration_playbook_expert(self, integration: str, constraints: str = "") -> Dict[str, Any]:
        """Генерация playbook для интеграций"""
        
        playbooks = {
            "stripe": {
                "title": "Stripe Payment Integration",
                "steps": [
                    "1. Install stripe library: pip install stripe",
                    "2. Get API keys from Stripe Dashboard",
                    "3. Create payment intent endpoint",
                    "4. Implement frontend payment form",
                    "5. Handle webhooks for payment confirmation"
                ],
                "code_example": """
import stripe
stripe.api_key = "sk_test_..."

# Create payment intent
intent = stripe.PaymentIntent.create(
    amount=2000,  # $20.00
    currency='usd',
)
                """,
                "required_keys": ["STRIPE_PUBLISHABLE_KEY", "STRIPE_SECRET_KEY"]
            },
            "openai": {
                "title": "OpenAI API Integration", 
                "steps": [
                    "1. Install openai library: pip install openai",
                    "2. Get API key from OpenAI Dashboard",
                    "3. Initialize client with API key",
                    "4. Create chat completion requests",
                    "5. Handle responses and errors"
                ],
                "code_example": """
from openai import OpenAI
client = OpenAI(api_key="sk-...")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
                """,
                "required_keys": ["OPENAI_API_KEY"]
            },
            "gemini": {
                "title": "Google Gemini API Integration",
                "steps": [
                    "1. Install google-generativeai: pip install google-generativeai",
                    "2. Get API key from Google AI Studio",
                    "3. Configure the model",
                    "4. Generate content with prompts",
                    "5. Handle streaming responses"
                ],
                "code_example": """
import google.generativeai as genai
genai.configure(api_key="AIza...")

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello!")
                """,
                "required_keys": ["GOOGLE_API_KEY"]
            }
        }
        
        playbook = playbooks.get(integration.lower(), {
            "title": f"Integration for {integration}",
            "steps": [f"1. Research {integration} API documentation",
                     f"2. Install required libraries for {integration}",
                     f"3. Implement authentication",
                     f"4. Create API client",
                     f"5. Test integration"],
            "code_example": f"# Code example for {integration} would go here",
            "required_keys": [f"{integration.upper()}_API_KEY"]
        })
        
        return {
            "success": True,
            "integration": integration,
            "constraints": constraints,
            "playbook": playbook,
            "verification": "VERIFIED" if integration.lower() in playbooks else "UNVERIFIED"
        }
        
    async def get_assets_tool(self) -> Dict[str, Any]:
        """Получение загруженных активов"""
        try:
            assets_dir = os.path.join(self.workspace_path, "assets")
            if not os.path.exists(assets_dir):
                return {
                    "success": True,
                    "assets": [],
                    "message": "No assets directory found"
                }
            
            assets = []
            for filename in os.listdir(assets_dir):
                file_path = os.path.join(assets_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    assets.append({
                        "filename": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return {
                "success": True,
                "assets": assets,
                "total": len(assets)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============= СОСТОЯНИЕ И КОНТЕКСТ =============
    
    async def save_agent_state(self, agent_type: str, session_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранение состояния агента"""
        try:
            state_dir = os.path.join(self.workspace_path, ".agent_states")
            os.makedirs(state_dir, exist_ok=True)
            
            state_file = os.path.join(state_dir, f"{session_id}_{agent_type}.json")
            
            state_data = {
                "agent_type": agent_type,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "state": state
            }
            
            async with aiofiles.open(state_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(state_data, indent=2, ensure_ascii=False))
            
            return {
                "success": True,
                "agent_type": agent_type,
                "session_id": session_id,
                "message": "Agent state saved"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def load_agent_state(self, agent_type: str, session_id: str) -> Dict[str, Any]:
        """Загрузка состояния агента"""
        try:
            state_file = os.path.join(self.workspace_path, ".agent_states", f"{session_id}_{agent_type}.json")
            
            if not os.path.exists(state_file):
                return {
                    "success": False,
                    "error": "State not found"
                }
            
            async with aiofiles.open(state_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                state_data = json.loads(content)
            
            return {
                "success": True,
                "agent_type": agent_type,
                "session_id": session_id,
                "state": state_data["state"],
                "timestamp": state_data["timestamp"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handoff_to_agent(self, from_agent: str, to_agent: str, session_id: str, 
                              context: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Передача управления другому агенту"""
        try:
            handoff_data = {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context,
                "message": message
            }
            
            # Сохранить информацию о передаче
            handoff_dir = os.path.join(self.workspace_path, ".agent_handoffs")
            os.makedirs(handoff_dir, exist_ok=True)
            
            handoff_file = os.path.join(handoff_dir, f"{session_id}_handoffs.json")
            
            # Загрузить существующие передачи
            handoffs = []
            if os.path.exists(handoff_file):
                async with aiofiles.open(handoff_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    handoffs = json.loads(content)
            
            # Добавить новую передачу
            handoffs.append(handoff_data)
            
            # Сохранить обновленный список
            async with aiofiles.open(handoff_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(handoffs, indent=2, ensure_ascii=False))
            
            return {
                "success": True,
                "handoff_id": len(handoffs),
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": "Handoff completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }