# FastAPI Multi-Agent System - Interface Definitions

## Table of Contents

1. [API Interface Definitions](#api-interface-definitions)
2. [Agent Interface Definitions](#agent-interface-definitions)
3. [Service Interface Definitions](#service-interface-definitions)
4. [Communication Interface Definitions](#communication-interface-definitions)
5. [Data Model Interfaces](#data-model-interfaces)
6. [Plugin Interface Definitions](#plugin-interface-definitions)
7. [Configuration Interface Definitions](#configuration-interface-definitions)
8. [Monitoring Interface Definitions](#monitoring-interface-definitions)

## API Interface Definitions

### 1. Agent Management API

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"

class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent"""
    agent_type: str = Field(..., description="Type of agent to create")
    name: str = Field(..., description="Human-readable name for the agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Agent tags for categorization")

class AgentResponse(BaseModel):
    """Response model for agent information"""
    id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent")
    name: str = Field(..., description="Agent name")
    status: AgentStatus = Field(..., description="Current agent status")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    config: Dict[str, Any] = Field(..., description="Agent configuration")
    tags: Optional[Dict[str, str]] = Field(None, description="Agent tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class MessageRequest(BaseModel):
    """Request model for sending messages to agents"""
    payload: Dict[str, Any] = Field(..., description="Message payload")
    priority: Optional[int] = Field(1, description="Message priority (1-10)")
    timeout: Optional[int] = Field(30, description="Message timeout in seconds")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")

# Agent Management Router
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentCreateRequest) -> AgentResponse:
    """Create a new agent instance"""
    pass

@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    agent_type: Optional[str] = None,
    status: Optional[AgentStatus] = None,
    limit: int = 100,
    offset: int = 0
) -> List[AgentResponse]:
    """List agents with optional filtering"""
    pass

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get specific agent details"""
    pass

@router.post("/{agent_id}/message")
async def send_message_to_agent(agent_id: str, request: MessageRequest):
    """Send message to specific agent"""
    pass
```

### 2. Workflow Management API

```python
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStep(BaseModel):
    """Individual workflow step definition"""
    id: str = Field(..., description="Step identifier")
    agent_type: str = Field(..., description="Required agent type")
    action: str = Field(..., description="Action to perform")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Step inputs")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies")
    timeout: Optional[int] = Field(300, description="Step timeout in seconds")

class WorkflowCreateRequest(BaseModel):
    """Request model for creating workflows"""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")

class WorkflowResponse(BaseModel):
    """Response model for workflow information"""
    id: str = Field(..., description="Workflow identifier")
    name: str = Field(..., description="Workflow name")
    status: WorkflowStatus = Field(..., description="Current status")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    created_at: datetime = Field(..., description="Creation timestamp")

# Workflow Management Router
workflow_router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

@workflow_router.post("/", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest) -> WorkflowResponse:
    """Create a new workflow"""
    pass

@workflow_router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, inputs: Dict[str, Any] = None):
    """Execute a workflow"""
    pass
```

## Agent Interface Definitions

### 1. Base Agent Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio

class AgentMessage(BaseModel):
    """Standard message format for agent communication"""
    id: str = Field(..., description="Message identifier")
    sender_id: str = Field(..., description="Sender agent ID")
    receiver_id: str = Field(..., description="Receiver agent ID")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(..., description="Message timestamp")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")

class AgentInterface(ABC):
    """Base interface for all agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.IDLE
        self.capabilities: List[str] = []
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources and connections"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        pass
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and return response"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status"""
        pass
    
    async def start(self) -> None:
        """Start the agent"""
        await self.initialize()
        self.status = AgentStatus.IDLE
    
    async def stop(self) -> None:
        """Stop the agent gracefully"""
        self.status = AgentStatus.STOPPED
        await self.cleanup()
```

### 2. Specialized Agent Interfaces

```python
class DataAgentInterface(AgentInterface):
    """Interface for data processing agents"""
    
    @abstractmethod
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data format and content"""
        pass

class DecisionAgentInterface(AgentInterface):
    """Interface for decision-making agents"""
    
    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision based on context"""
        pass
    
    @abstractmethod
    async def evaluate_options(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate and rank available options"""
        pass

class CoordinatorAgentInterface(AgentInterface):
    """Interface for coordination agents"""
    
    @abstractmethod
    async def coordinate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Coordinate workflow execution"""
        pass
    
    @abstractmethod
    async def assign_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Assign tasks to available agents"""
        pass
```

## Service Interface Definitions

### 1. Agent Registry Interface

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class AgentRegistryInterface(Protocol):
    """Interface for agent registry service"""
    
    async def register_agent(self, agent: AgentInterface) -> str:
        """Register a new agent and return agent ID"""
        ...
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        ...
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInterface]:
        """Get agent by ID"""
        ...
    
    async def list_agents(
        self,
        agent_type: Optional[str] = None,
        status: Optional[AgentStatus] = None
    ) -> List[AgentInterface]:
        """List agents with optional filtering"""
        ...
    
    async def find_agents_by_capability(self, capability: str) -> List[AgentInterface]:
        """Find agents with specific capability"""
        ...
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update agent status"""
        ...
```

### 2. Communication Handler Interface

```python
@runtime_checkable
class CommunicationHandlerInterface(Protocol):
    """Interface for communication handler service"""
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize communication handler"""
        ...
    
    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message: Dict[str, Any]
    ) -> str:
        """Send message between agents"""
        ...
    
    async def broadcast_message(
        self,
        sender_id: str,
        message: Dict[str, Any]
    ) -> List[str]:
        """Broadcast message to multiple agents"""
        ...
    
    async def subscribe_to_messages(self, agent_id: str, handler: callable) -> None:
        """Subscribe agent to receive messages"""
        ...
```

### 3. Workflow Service Interface

```python
@runtime_checkable
class WorkflowServiceInterface(Protocol):
    """Interface for workflow service"""
    
    async def create_workflow(self, definition: Dict[str, Any]) -> str:
        """Create new workflow and return workflow ID"""
        ...
    
    async def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> str:
        """Execute workflow and return execution ID"""
        ...
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition"""
        ...
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        ...
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running workflow execution"""
        ...
```

## Communication Interface Definitions

### 1. Message Transport Interface

```python
@runtime_checkable
class MessageTransportInterface(Protocol):
    """Interface for message transport implementations"""
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize transport connection"""
        ...
    
    async def publish(self, topic: str, message: bytes) -> str:
        """Publish message to topic"""
        ...
    
    async def subscribe(self, topic: str, handler: callable) -> str:
        """Subscribe to topic with message handler"""
        ...
    
    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from topic"""
        ...
```

### 2. Event Bus Interface

```python
class EventType(str, Enum):
    """System event types"""
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    MESSAGE_SENT = "message_sent"

class SystemEvent(BaseModel):
    """System event model"""
    id: str = Field(..., description="Event identifier")
    type: EventType = Field(..., description="Event type")
    source: str = Field(..., description="Event source")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")

@runtime_checkable
class EventBusInterface(Protocol):
    """Interface for event bus service"""
    
    async def publish_event(self, event: SystemEvent) -> None:
        """Publish system event"""
        ...
    
    async def subscribe_to_events(self, event_types: List[EventType], handler: callable) -> str:
        """Subscribe to specific event types"""
        ...
```

## Data Model Interfaces

### 1. Storage Interface

```python
@runtime_checkable
class StorageInterface(Protocol):
    """Interface for data storage operations"""
    
    async def create(self, table: str, data: Dict[str, Any]) -> str:
        """Create new record and return ID"""
        ...
    
    async def read(self, table: str, id: str) -> Optional[Dict[str, Any]]:
        """Read record by ID"""
        ...
    
    async def update(self, table: str, id: str, data: Dict[str, Any]) -> bool:
        """Update existing record"""
        ...
    
    async def delete(self, table: str, id: str) -> bool:
        """Delete record by ID"""
        ...
    
    async def query(
        self,
        table: str,
        filters: Dict[str, Any] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query records with filters"""
        ...
```

### 2. Cache Interface

```python
@runtime_checkable
class CacheInterface(Protocol):
    """Interface for cache operations"""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        ...
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set key-value pair with optional TTL"""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete key"""
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        ...
```

## Plugin Interface Definitions

### 1. Plugin Base Interface

```python
@runtime_checkable
class PluginInterface(Protocol):
    """Base interface for all plugins"""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        ...
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration"""
        ...
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        ...
    
    def get_capabilities(self) -> List[str]:
        """Return plugin capabilities"""
        ...

class PluginMetadata(BaseModel):
    """Plugin metadata model"""
    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    capabilities: List[str] = Field(default_factory=list, description="Plugin capabilities")
```

### 2. Agent Plugin Interface

```python
@runtime_checkable
class AgentPluginInterface(PluginInterface):
    """Interface for agent plugins"""
    
    def create_agent(self, agent_id: str, config: Dict[str, Any]) -> AgentInterface:
        """Create agent instance"""
        ...
    
    def get_agent_type(self) -> str:
        """Return agent type identifier"""
        ...
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default agent configuration"""
        ...
```

## Configuration Interface Definitions

```python
@runtime_checkable
class ConfigurationManagerInterface(Protocol):
    """Interface for configuration management"""
    
    async def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from various sources"""
        ...
    
    async def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        ...
    
    async def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        ...
    
    async def reload_config(self) -> None:
        """Reload configuration from sources"""
        ...
```

## Monitoring Interface Definitions

```python
@runtime_checkable
class MetricsInterface(Protocol):
    """Interface for metrics collection"""
    
    def counter(self, name: str, labels: Dict[str, str] = None):
        """Create or get counter metric"""
        ...
    
    def gauge(self, name: str, labels: Dict[str, str] = None):
        """Create or get gauge metric"""
        ...
    
    def histogram(self, name: str, labels: Dict[str, str] = None):
        """Create or get histogram metric"""
        ...
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect all metrics"""
        ...

@runtime_checkable
class HealthCheckInterface(Protocol):
    """Interface for health checking"""
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform health check"""
        ...
    
    async def check_readiness(self) -> bool:
        """Check if service is ready"""
        ...
    
    async def check_liveness(self) -> bool:
        """Check if service is alive"""
        ...
```

These interface definitions provide clear contracts for all components in the FastAPI multi-agent system, ensuring consistent implementation across the entire architecture.