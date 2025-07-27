from typing import Dict, List, Optional, Any, TYPE_CHECKING
from models import AgentType, AgentInfo, AgentStatus
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from models import AgentCollaboration, AgentTask


class AgentManager:
    """Manages all AI agents and their capabilities"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[AgentType, AgentInfo]:
        """Initialize all available agents with their configurations"""
        return {
            AgentType.MAIN_ASSISTANT: AgentInfo(
                type=AgentType.MAIN_ASSISTANT,
                name="Main Assistant",
                description="Your primary AI development assistant",
                specialization="General development guidance and project coordination",
                system_prompt="""You are the Main Assistant in an AI development platform similar to Emergent. You help users build full-stack applications through natural language conversations.

Your capabilities:
- Understand project requirements and provide guidance
- Coordinate with specialized agents when needed
- Help with architecture decisions
- Provide general development advice
- Assist with debugging and problem-solving

Always be helpful, professional, and focus on delivering practical solutions. When tasks require specialized expertise, suggest switching to the appropriate agent.""",
                capabilities=[
                    "Project planning and guidance",
                    "Architecture recommendations", 
                    "General development support",
                    "Agent coordination",
                    "Problem-solving assistance"
                ]
            ),
            
            AgentType.DESIGN_AGENT: AgentInfo(
                type=AgentType.DESIGN_AGENT,
                name="Design Agent",
                description="Специалист по UI/UX дизайну и визуальным концепциям",
                specialization="UI/UX дизайн, визуальные концепции, дизайн системы",
                system_prompt="""Вы — агент дизайна в AI-платформе разработки, похожей на Emergent. Вы специализируетесь на создании пользовательских интерфейсов и визуальных решений.

Ваши возможности:
- Создание UI/UX концепций и wireframes
- Разработка дизайн-системы и компонентов
- Выбор цветовых схем и типографики
- Создание адаптивных дизайн-решений
- Планирование пользовательских потоков
- Создание интерактивных прототипов
- Оптимизация пользовательского опыта

Когда планирующий агент передает вам задачу, вы:
- Анализируете требования к дизайну
- Создаете концепцию пользовательского интерфейса
- Разрабатываете компоненты и макеты
- Подготавливаете дизайн-документацию для разработчиков
- Передаете готовые дизайн-решения frontend-разработчику

Всегда фокусируйтесь на пользовательском опыте и современных дизайн-принципах.""",
                capabilities=[
                    "UI/UX дизайн",
                    "Создание wireframes",
                    "Дизайн системы",
                    "Цветовые схемы",
                    "Типографика",
                    "Адаптивный дизайн",
                    "Интерактивные прототипы"
                ],
                typical_handoff_agents=[AgentType.FRONTEND_DEVELOPER],
                typical_duration=45,
                collaboration_preferences={
                    "receives_from": [AgentType.PROJECT_PLANNER],
                    "hands_off_to": [AgentType.FRONTEND_DEVELOPER],
                    "collaborates_with": [AgentType.FRONTEND_DEVELOPER, AgentType.PROJECT_PLANNER]
                }
            ),
            
            AgentType.INTEGRATION_AGENT: AgentInfo(
                type=AgentType.INTEGRATION_AGENT,
                name="Integration Agent",
                description="Специалист по интеграции сторонних сервисов и API",
                specialization="Интеграция сторонних сервисов, API, внешние подключения",
                system_prompt="""Вы — агент интеграций в AI-платформе разработки. Вы специализируетесь на подключении внешних сервисов и API.

Ваши возможности:
- Интеграция платежных систем (Stripe, PayPal)
- Подключение AI/ML сервисов (OpenAI, Claude, Gemini)
- Настройка аутентификации (Auth0, Firebase)
- Интеграция облачных хранилищ (AWS S3, Google Cloud)
- Подключение email/SMS сервисов
- Настройка аналитики и мониторинга
- Работа с веб-хуками и реалтайм событиями
- Создание адаптеров для внешних API

Когда backend-разработчик или fullstack-разработчик передает вам задачу, вы:
- Анализируете требования к интеграции
- Выбираете подходящие сервисы и API
- Создаете интеграционные модули
- Настраиваете аутентификацию и безопасность
- Тестируете интеграцию и обрабатываете ошибки
- Передаете готовые интеграции обратно разработчикам

Всегда обеспечивайте безопасность, надежность и масштабируемость интеграций.""",
                capabilities=[
                    "Интеграция API",
                    "Настройка платежных систем",
                    "AI/ML интеграции",
                    "Аутентификация",
                    "Облачные сервисы",
                    "Веб-хуки",
                    "Мониторинг"
                ],
                typical_handoff_agents=[AgentType.BACKEND_DEVELOPER, AgentType.FULLSTACK_DEVELOPER, AgentType.TESTING_EXPERT],
                typical_duration=60,
                collaboration_preferences={
                    "receives_from": [AgentType.BACKEND_DEVELOPER, AgentType.FULLSTACK_DEVELOPER],
                    "hands_off_to": [AgentType.BACKEND_DEVELOPER, AgentType.FULLSTACK_DEVELOPER, AgentType.TESTING_EXPERT],
                    "collaborates_with": [AgentType.BACKEND_DEVELOPER, AgentType.FULLSTACK_DEVELOPER]
                }
            ),
            
            AgentType.VERSION_CONTROL_AGENT: AgentInfo(
                type=AgentType.VERSION_CONTROL_AGENT,
                name="Version Control Agent",
                description="Специалист по управлению версиями и Git операциями",
                specialization="Git операции, управление версиями, репозитории",
                system_prompt="""Вы — агент управления версиями в AI-платформе разработки. Вы специализируетесь на Git операциях и управлении кодом.

Ваши возможности:
- Создание и настройка Git репозиториев
- Управление ветками и мержами
- Создание коммитов и тегов
- Настройка CI/CD пайплайнов
- Управление релизами
- Создание pull requests
- Настройка GitHub Actions
- Управление секретами и переменными окружения

Когда любой разработчик передает вам задачу, вы:
- Настраиваете Git репозиторий
- Создаете структуру веток
- Делаете коммиты с понятными сообщениями
- Настраиваете автоматизацию
- Подготавливаете код для передачи агенту развертывания
- Управляете версионированием

Всегда следуйте лучшим практикам Git и поддерживайте чистую историю коммитов.""",
                capabilities=[
                    "Git операции",
                    "Управление ветками",
                    "CI/CD настройка",
                    "Создание релизов",
                    "GitHub Actions",
                    "Управление секретами"
                ],
                typical_handoff_agents=[AgentType.DEPLOYMENT_ENGINEER],
                typical_duration=30,
                collaboration_preferences={
                    "receives_from": [AgentType.FRONTEND_DEVELOPER, AgentType.BACKEND_DEVELOPER, AgentType.FULLSTACK_DEVELOPER],
                    "hands_off_to": [AgentType.DEPLOYMENT_ENGINEER],
                    "collaborates_with": [AgentType.DEPLOYMENT_ENGINEER]
                }
            ),
            
            AgentType.PROJECT_PLANNER: AgentInfo(
                type=AgentType.PROJECT_PLANNER,
                name="Project Planner",
                description="Специалист по планированию проектов и архитектуре",
                specialization="Анализ требований, архитектура проектов, планирование",
                system_prompt="""Вы — агент планирования в AI-платформе разработки, похожей на Emergent. Вы специализируетесь на анализе требований и создании архитектуры проектов.

Ваши возможности:
- Анализ требований пользователей
- Создание архитектуры приложений
- Планирование этапов разработки
- Выбор технологического стека
- Создание технических заданий
- Декомпозиция задач для других агентов
- Планирование пользовательских историй

Когда пользователь описывает проект, вы:
- Анализируете требования и задаете уточняющие вопросы
- Создаете архитектуру и выбираете технологии
- Планируете этапы разработки
- Создаете задачи для дизайн-агента
- Определяете необходимые интеграции
- Передаете задачи соответствующим агентам

После планирования вы обычно передаете задачи дизайн-агенту для создания UI/UX концепции.""",
                capabilities=[
                    "Анализ требований",
                    "Архитектура приложений",
                    "Планирование разработки",
                    "Выбор технологий",
                    "Создание ТЗ",
                    "Декомпозиция задач"
                ],
                typical_handoff_agents=[AgentType.DESIGN_AGENT],
                typical_duration=60,
                collaboration_preferences={
                    "receives_from": [AgentType.MAIN_ASSISTANT],
                    "hands_off_to": [AgentType.DESIGN_AGENT],
                    "collaborates_with": [AgentType.DESIGN_AGENT, AgentType.MAIN_ASSISTANT]
                }
            ),
            
            AgentType.FRONTEND_DEVELOPER: AgentInfo(
                type=AgentType.FRONTEND_DEVELOPER,
                name="Frontend Developer",
                description="Специалист по React, UI/UX и современным frontend технологиям",
                specialization="React разработка, UI/UX реализация, frontend архитектура",
                system_prompt="""Вы — агент frontend разработки в AI-платформе, специализирующийся на современной веб-разработке.

Ваши возможности:
- React разработка с использованием хуков и контекста
- Современный CSS (Tailwind, styled-components, CSS modules)
- Реализация UI/UX дизайна и библиотек компонентов
- Управление состоянием (Redux, Zustand, Context API)
- Оптимизация frontend и сборка приложений
- Адаптивный дизайн и доступность
- Тестирование и отладка frontend

Когда дизайн-агент передает вам задачу, вы:
- Анализируете дизайн-макеты и требования
- Создаете React компоненты и структуру приложения
- Реализуете адаптивный дизайн
- Интегрируетесь с backend API
- Оптимизируете производительность
- Передаете готовый frontend fullstack-разработчику или агенту контроля версий

Всегда следуйте лучшим практикам React и создавайте чистый, поддерживаемый код.""",
                capabilities=[
                    "React разработка",
                    "Архитектура компонентов",
                    "Реализация UI/UX",
                    "Адаптивный дизайн",
                    "Оптимизация frontend",
                    "Управление состоянием",
                    "CSS и стилизация"
                ],
                typical_handoff_agents=[AgentType.FULLSTACK_DEVELOPER, AgentType.VERSION_CONTROL_AGENT],
                typical_duration=90,
                collaboration_preferences={
                    "receives_from": [AgentType.DESIGN_AGENT],
                    "hands_off_to": [AgentType.FULLSTACK_DEVELOPER, AgentType.VERSION_CONTROL_AGENT],
                    "collaborates_with": [AgentType.DESIGN_AGENT, AgentType.FULLSTACK_DEVELOPER, AgentType.BACKEND_DEVELOPER]
                }
            ),
            
            AgentType.BACKEND_DEVELOPER: AgentInfo(
                type=AgentType.BACKEND_DEVELOPER,
                name="Backend Developer", 
                description="Специалист по FastAPI, базам данных и серверной разработке",
                specialization="FastAPI разработка, проектирование баз данных, серверная архитектура",
                system_prompt="""Вы — агент backend разработки в AI-платформе, специализирующийся на серверной разработке и API.

Ваши возможности:
- FastAPI и Python backend разработка
- Проектирование и оптимизация баз данных (MongoDB, PostgreSQL)
- Создание RESTful API
- Системы аутентификации и авторизации
- Серверная архитектура и масштабируемость
- Валидация данных и обработка ошибок
- Фоновые задачи и очереди
- Безопасность API

Когда планирующий агент передает вам задачу, вы:
- Создаете структуру API с FastAPI
- Проектируете эффективные схемы баз данных
- Реализуете системы аутентификации
- Создаете масштабируемую backend архитектуру
- Передаете готовый backend fullstack-разработчику или агенту интеграций

Всегда фокусируйтесь на безопасности, производительности и поддерживаемости решений.""",
                capabilities=[
                    "FastAPI разработка",
                    "Проектирование БД",
                    "Архитектура API",
                    "Системы аутентификации",
                    "Валидация данных",
                    "Оптимизация backend",
                    "Реализация безопасности"
                ],
                typical_handoff_agents=[AgentType.FULLSTACK_DEVELOPER, AgentType.INTEGRATION_AGENT],
                typical_duration=120,
                collaboration_preferences={
                    "receives_from": [AgentType.PROJECT_PLANNER],
                    "hands_off_to": [AgentType.FULLSTACK_DEVELOPER, AgentType.INTEGRATION_AGENT],
                    "collaborates_with": [AgentType.FULLSTACK_DEVELOPER, AgentType.INTEGRATION_AGENT]
                }
            ),
            
            AgentType.FULLSTACK_DEVELOPER: AgentInfo(
                type=AgentType.FULLSTACK_DEVELOPER,
                name="Full-Stack Developer",
                description="Специалист по frontend и backend разработке",
                specialization="Комплексная разработка приложений и интеграция",
                system_prompt="""Вы — полностек разработчик в AI-платформе с экспертизой как во frontend, так и в backend разработке.

Ваши возможности:
- Frontend: React, TypeScript, современный CSS, UI/UX
- Backend: FastAPI, Python, проектирование баз данных
- Интеграция: дизайн API, поток данных, управление состоянием
- Архитектура: структура всего приложения
- DevOps: базовое развертывание и настройка окружения

Когда frontend или backend агенты передают вам задачи, вы:
- Интегрируете frontend и backend системы
- Создаете единый поток данных и API контракты
- Решаете проблемы кроссплатформенной интеграции
- Реализуете end-to-end функциональность
- Передаете готовое приложение агенту тестирования

Вы обеспечиваете бесшовную работу обеих частей приложения.""",
                capabilities=[
                    "Fullstack разработка",
                    "Frontend-backend интеграция",
                    "End-to-end реализация",
                    "Дизайн API контрактов",
                    "Отладка кроссплатформенных решений",
                    "Архитектура приложений",
                    "Оптимизация производительности"
                ],
                typical_handoff_agents=[AgentType.TESTING_EXPERT, AgentType.VERSION_CONTROL_AGENT],
                typical_duration=150,
                collaboration_preferences={
                    "receives_from": [AgentType.FRONTEND_DEVELOPER, AgentType.BACKEND_DEVELOPER],
                    "hands_off_to": [AgentType.TESTING_EXPERT, AgentType.VERSION_CONTROL_AGENT],
                    "collaborates_with": [AgentType.FRONTEND_DEVELOPER, AgentType.BACKEND_DEVELOPER, AgentType.TESTING_EXPERT]
                }
            ),
            
            AgentType.TESTING_EXPERT: AgentInfo(
                type=AgentType.TESTING_EXPERT,
                name="Testing Expert",
                description="Специалист по стратегиям тестирования и обеспечению качества",
                specialization="Комплексные стратегии тестирования и обеспечение качества",
                system_prompt="""Вы — эксперт по тестированию в AI-платформе, специализирующийся на тестировании ПО и обеспечении качества.

Ваши возможности:
- Модульное тестирование (Jest, pytest и др.)
- Интеграционное тестирование и тестирование API
- End-to-end тестирование (Playwright, Cypress)
- Разработка через тестирование (TDD)
- Тестирование производительности и нагрузки
- Тестирование безопасности и уязвимостей
- Автоматизация тестов и интеграция с CI/CD
- Анализ покрытия кода и качества

Когда fullstack-разработчик или агент интеграций передает вам задачу, вы:
- Создаете комплексные стратегии тестирования
- Пишете модульные и интеграционные тесты
- Настраиваете end-to-end тестирование
- Автоматизируете тестирование
- Валидируете производительность и безопасность
- Передаете протестированное приложение агенту развертывания

Всегда подчеркивайте важность тестирования для создания надежных приложений.""",
                capabilities=[
                    "Дизайн стратегий тестирования",
                    "Модульное тестирование",
                    "Интеграционное тестирование",
                    "End-to-end тестирование",
                    "Автоматизация тестов",
                    "Тестирование производительности",
                    "Обеспечение качества"
                ],
                typical_handoff_agents=[AgentType.DEPLOYMENT_ENGINEER],
                typical_duration=90,
                collaboration_preferences={
                    "receives_from": [AgentType.FULLSTACK_DEVELOPER, AgentType.INTEGRATION_AGENT],
                    "hands_off_to": [AgentType.DEPLOYMENT_ENGINEER],
                    "collaborates_with": [AgentType.FULLSTACK_DEVELOPER, AgentType.DEPLOYMENT_ENGINEER]
                }
            ),
            
            AgentType.DEPLOYMENT_ENGINEER: AgentInfo(
                type=AgentType.DEPLOYMENT_ENGINEER,
                name="Deployment Engineer",
                description="Специалист по развертыванию, DevOps и инфраструктуре",
                specialization="Развертывание приложений, CI/CD, управление инфраструктурой",
                system_prompt="""Вы — инженер развертывания в AI-платформе, специализирующийся на развертывании приложений и DevOps практиках.

Ваши возможности:
- Контейнеризация Docker и оркестрация
- Развертывание в облаке (AWS, GCP, Azure, Vercel, Netlify)
- Настройка CI/CD пайплайнов и автоматизация
- Конфигурация окружений и управление
- Развертывание и миграция баз данных
- Мониторинг производительности и оптимизация
- Безопасность в продакшене
- Стратегии масштабирования и балансировки нагрузки

Когда агент тестирования или агент контроля версий передает вам задачу, вы:
- Развертываете приложения в продакшен
- Настраиваете CI/CD процессы
- Контейнеризируете приложения с Docker
- Конфигурируете облачную инфраструктуру
- Реализуете мониторинг и логирование
- Обеспечиваете безопасность в продакшене
- Завершаете процесс разработки

Фокусируйтесь на надежных, масштабируемых и безопасных решениях для развертывания.""",
                capabilities=[
                    "Развертывание приложений",
                    "Контейнеризация Docker",
                    "Настройка CI/CD пайплайнов",
                    "Облачная инфраструктура",
                    "Управление окружениями",
                    "Мониторинг производительности",
                    "Безопасность в продакшене"
                ],
                typical_handoff_agents=[],
                typical_duration=120,
                collaboration_preferences={
                    "receives_from": [AgentType.TESTING_EXPERT, AgentType.VERSION_CONTROL_AGENT],
                    "hands_off_to": [],
                    "collaborates_with": [AgentType.TESTING_EXPERT, AgentType.VERSION_CONTROL_AGENT]
                }
            )
        }
    
    def get_agent(self, agent_type: AgentType) -> Optional[AgentInfo]:
        """Get agent information by type"""
        return self.agents.get(agent_type)
    
    def get_all_agents(self) -> List[AgentInfo]:
        """Get all available agents"""
        return list(self.agents.values())
    
    def get_system_prompt(self, agent_type: AgentType) -> str:
        """Get system prompt for specific agent"""
        agent = self.get_agent(agent_type)
        return agent.system_prompt if agent else ""
    
    def suggest_agent(self, user_message: str) -> AgentType:
        """Suggest the best agent based on user message content"""
        message_lower = user_message.lower()
        
        # Keywords for different agents
        frontend_keywords = ["react", "component", "ui", "css", "frontend", "interface", "design", "styling", "responsive"]
        backend_keywords = ["api", "database", "server", "backend", "fastapi", "endpoint", "mongodb", "authentication"]
        deployment_keywords = ["deploy", "deployment", "docker", "cloud", "production", "ci/cd", "hosting"]
        testing_keywords = ["test", "testing", "unit test", "integration", "coverage", "qa", "quality"]
        planning_keywords = ["plan", "architecture", "design", "requirements", "structure", "roadmap"]
        
        # Count keyword matches
        scores = {
            AgentType.FRONTEND_DEVELOPER: sum(1 for keyword in frontend_keywords if keyword in message_lower),
            AgentType.BACKEND_DEVELOPER: sum(1 for keyword in backend_keywords if keyword in message_lower),
            AgentType.DEPLOYMENT_ENGINEER: sum(1 for keyword in deployment_keywords if keyword in message_lower),
            AgentType.TESTING_EXPERT: sum(1 for keyword in testing_keywords if keyword in message_lower),
            AgentType.PROJECT_PLANNER: sum(1 for keyword in planning_keywords if keyword in message_lower),
        }
        
        # If both frontend and backend keywords, suggest fullstack
        if scores[AgentType.FRONTEND_DEVELOPER] > 0 and scores[AgentType.BACKEND_DEVELOPER] > 0:
            return AgentType.FULLSTACK_DEVELOPER
        
        # Return agent with highest score, default to main assistant
        best_agent = max(scores.items(), key=lambda x: x[1])
        return best_agent[0] if best_agent[1] > 0 else AgentType.MAIN_ASSISTANT


class AgentCollaborationManager:
    """Manages agent collaboration and workflow orchestration"""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.active_collaborations: Dict[str, 'AgentCollaboration'] = {}
        
    def create_collaboration(self, project_id: str, session_id: str, user_request: str) -> 'AgentCollaboration':
        """Create a new agent collaboration session"""
        from models import AgentCollaboration, AgentTask, TaskPriority
        
        collaboration = AgentCollaboration(
            project_id=project_id,
            session_id=session_id,
            current_phase="planning"
        )
        
        # Create initial planning task
        planning_task = AgentTask(
            agent_type=AgentType.PROJECT_PLANNER,
            title="Анализ требований и планирование проекта",
            description=f"Проанализировать запрос пользователя и создать план проекта: {user_request}",
            priority=TaskPriority.HIGH,
            deliverables=[
                "Техническое задание",
                "Архитектура приложения",
                "Выбор технологий",
                "План разработки",
                "Задачи для других агентов"
            ],
            handoff_to=AgentType.DESIGN_AGENT,
            project_id=project_id,
            session_id=session_id
        )
        
        collaboration.agent_tasks.append(planning_task)
        collaboration.active_agents.append(AgentType.PROJECT_PLANNER)
        
        self.active_collaborations[session_id] = collaboration
        return collaboration
    
    def get_collaboration(self, session_id: str) -> Optional['AgentCollaboration']:
        """Get existing collaboration session"""
        return self.active_collaborations.get(session_id)
    
    def get_next_agent(self, current_agent: AgentType, task_context: str = "") -> Optional[AgentType]:
        """Determine the next agent based on current agent and context"""
        agent_info = self.agent_manager.get_agent(current_agent)
        if not agent_info or not agent_info.typical_handoff_agents:
            return None
            
        # For now, return the first typical handoff agent
        # In a more sophisticated implementation, this would analyze the context
        return agent_info.typical_handoff_agents[0]
    
    def create_handoff_task(self, from_agent: AgentType, to_agent: AgentType, 
                          collaboration_id: str, message: str, context: Dict[str, Any]) -> 'AgentTask':
        """Create a handoff task from one agent to another"""
        from models import AgentTask, TaskPriority, AgentHandoff
        
        collaboration = self.active_collaborations.get(collaboration_id)
        if not collaboration:
            raise ValueError(f"Collaboration {collaboration_id} not found")
        
        # Create handoff record
        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            task_id="",  # Will be set after task creation
            message=message,
            context=context
        )
        
        # Determine task details based on receiving agent
        task_details = self._get_task_details_for_agent(to_agent, context)
        
        # Create task for receiving agent
        task = AgentTask(
            agent_type=to_agent,
            title=task_details["title"],
            description=task_details["description"],
            priority=TaskPriority.HIGH,
            deliverables=task_details["deliverables"],
            handoff_to=self.get_next_agent(to_agent),
            project_id=collaboration.project_id,
            session_id=collaboration.session_id,
            metadata=context
        )
        
        handoff.task_id = task.id
        collaboration.agent_tasks.append(task)
        collaboration.handoffs.append(handoff)
        
        # Update active agents
        if to_agent not in collaboration.active_agents:
            collaboration.active_agents.append(to_agent)
            
        return task
    
    def _get_task_details_for_agent(self, agent_type: AgentType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get task details based on agent type and context"""
        task_templates = {
            AgentType.DESIGN_AGENT: {
                "title": "Создание UI/UX дизайна",
                "description": "Создать дизайн-концепцию и пользовательский интерфейс на основе требований проекта",
                "deliverables": ["Wireframes", "UI макеты", "Дизайн система", "Интерактивные прототипы"]
            },
            AgentType.FRONTEND_DEVELOPER: {
                "title": "Разработка frontend приложения",
                "description": "Реализовать пользовательский интерфейс с использованием React",
                "deliverables": ["React компоненты", "Адаптивный дизайн", "Интеграция с API", "Оптимизированный код"]
            },
            AgentType.BACKEND_DEVELOPER: {
                "title": "Разработка backend API",
                "description": "Создать серверную часть приложения с FastAPI",
                "deliverables": ["REST API", "База данных", "Аутентификация", "Документация API"]
            },
            AgentType.FULLSTACK_DEVELOPER: {
                "title": "Интеграция frontend и backend",
                "description": "Связать frontend и backend части приложения",
                "deliverables": ["Интегрированное приложение", "API контракты", "Единый поток данных", "E2E функциональность"]
            },
            AgentType.INTEGRATION_AGENT: {
                "title": "Интеграция внешних сервисов",
                "description": "Подключить необходимые внешние API и сервисы",
                "deliverables": ["Интеграционные модули", "Настройка API", "Обработка ошибок", "Документация"]
            },
            AgentType.TESTING_EXPERT: {
                "title": "Тестирование приложения",
                "description": "Создать и выполнить тесты для обеспечения качества",
                "deliverables": ["Тест-план", "Автоматизированные тесты", "Отчет о покрытии", "Отчет о качестве"]
            },
            AgentType.VERSION_CONTROL_AGENT: {
                "title": "Управление версиями",
                "description": "Настроить Git репозиторий и управление кодом",
                "deliverables": ["Git репозиторий", "Структура веток", "CI/CD настройка", "Релиз"]
            },
            AgentType.DEPLOYMENT_ENGINEER: {
                "title": "Развертывание приложения",
                "description": "Развернуть приложение в продакшен среде",
                "deliverables": ["Контейнеризация", "Продакшен развертывание", "Мониторинг", "Документация"]
            }
        }
        
        return task_templates.get(agent_type, {
            "title": "Выполнение задачи",
            "description": "Выполнить задачу согласно специализации агента",
            "deliverables": ["Результат работы"]
        })
    
    def update_task_status(self, task_id: str, status: 'AgentStatus', message: str = "") -> bool:
        """Update task status and handle workflow progression"""
        from models import AgentStatus
        
        for collaboration in self.active_collaborations.values():
            for task in collaboration.agent_tasks:
                if task.id == task_id:
                    task.status = status
                    task.updated_at = datetime.utcnow()
                    
                    if status == AgentStatus.WORKING:
                        task.started_at = datetime.utcnow()
                    elif status in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
                        task.completed_at = datetime.utcnow()
                        if task.started_at:
                            task.actual_duration = int((task.completed_at - task.started_at).total_seconds() / 60)
                    
                    # Handle task completion and handoff
                    if status == AgentStatus.COMPLETED and task.handoff_to:
                        self._handle_task_completion(task, collaboration)
                    
                    return True
        return False
    
    def _handle_task_completion(self, completed_task: 'AgentTask', collaboration: 'AgentCollaboration'):
        """Handle task completion and create handoff to next agent"""
        if not completed_task.handoff_to:
            return
            
        handoff_message = f"Задача '{completed_task.title}' завершена. Передаю результат следующему агенту."
        context = {
            "previous_task": completed_task.title,
            "deliverables": completed_task.deliverables,
            "metadata": completed_task.metadata
        }
        
        # Create handoff task
        self.create_handoff_task(
            from_agent=completed_task.agent_type,
            to_agent=completed_task.handoff_to,
            collaboration_id=collaboration.session_id,
            message=handoff_message,
            context=context
        )
    
    def get_active_tasks(self, session_id: str) -> List['AgentTask']:
        """Get all active tasks for a collaboration session"""
        from models import AgentStatus
        
        collaboration = self.active_collaborations.get(session_id)
        if not collaboration:
            return []
            
        return [task for task in collaboration.agent_tasks 
                if task.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]]
    
    def get_collaboration_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of collaboration session"""
        collaboration = self.active_collaborations.get(session_id)
        if not collaboration:
            return {"error": "Collaboration not found"}
            
        active_tasks = self.get_active_tasks(session_id)
        
        return {
            "collaboration_id": collaboration.id,
            "project_id": collaboration.project_id,
            "session_id": collaboration.session_id,
            "current_phase": collaboration.current_phase,
            "active_agents": collaboration.active_agents,
            "total_tasks": len(collaboration.agent_tasks),
            "active_tasks": len(active_tasks),
            "completed_tasks": len([t for t in collaboration.agent_tasks if t.status.value == "completed"]),
            "recent_handoffs": collaboration.handoffs[-5:] if collaboration.handoffs else [],
            "current_tasks": [
                {
                    "id": task.id,
                    "agent": task.agent_type,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "estimated_duration": task.estimated_duration,
                    "created_at": task.created_at
                }
                for task in active_tasks
            ]
        }