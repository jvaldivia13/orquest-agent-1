# Diagrama de Orquestacion de Agentes

Este diagrama representa el flujo implementado en `graph/support_graph.py` para procesar solicitudes de soporte TI.

```mermaid
flowchart TD
    User[Usuario / Frontend / CLI] --> API[FastAPI / app.main]
    API --> Init[initialize_request<br/>Genera request_id]

    Init --> Classifier[Agente Clasificador<br/>classifier_agent.py]
    Classifier <-->|LLM si hay API key<br/>fallback local si falla| DeepSeek[DeepSeek API<br/>LangChain]
    Classifier --> Knowledge[Agente de Conocimiento<br/>knowledge_agent.py]

    Knowledge --> KB[(Base de conocimiento local<br/>data/knowledge_base.json)]
    KB --> Knowledge
    Knowledge --> Resolver[Agente Resolutor<br/>resolver_agent.py]
    Resolver <-->|LLM opcional<br/>fallback reglas| DeepSeek

    Resolver --> Decision{Decision de resolucion}
    Decision -->|Solicitud ambigua<br/>needs_more_info=true| Response[Agente de Respuesta<br/>response_agent.py]
    Decision -->|Solucion conocida<br/>sin ticket| Response
    Decision -->|Prioridad alta, seguridad<br/>o sin solucion conocida| Ticketing[Agente de Ticketing<br/>ticketing_agent.py]

    Ticketing --> Tickets[(Tickets simulados locales<br/>data/tickets.jsonl)]
    Tickets --> Ticketing
    Ticketing --> Response

    Response <-->|LLM opcional<br/>fallback plantilla| DeepSeek
    Response --> Validator[Agente Validador<br/>validator_agent.py]
    Validator <-->|LLM opcional<br/>fallback reglas| DeepSeek
    Validator --> ValidDecision{Respuesta valida?}
    ValidDecision -->|No, con reintentos disponibles| Response
    ValidDecision -->|Si, o maximo de reintentos| Logger[log_interaction<br/>logging_tools.py]

    Logger --> Logs[(Log local seguro<br/>logs/interactions.jsonl)]
    Logger --> End[Respuesta final]
    End --> User
```

## Responsabilidades por Nodo

| Nodo | Responsabilidad | Archivo |
| --- | --- | --- |
| `initialize_request` | Crea un `request_id` unico si la solicitud no lo trae. | `graph/support_graph.py` |
| `classifier` | Clasifica la solicitud y asigna categoria/prioridad usando DeepSeek o fallback local. | `agents/classifier_agent.py` |
| `knowledge` | Busca articulos y una posible solucion en la base de conocimiento local. | `agents/knowledge_agent.py` |
| `resolver` | Decide si responder, pedir mas informacion o crear un ticket usando DeepSeek cuando esta disponible o reglas locales como fallback. | `agents/resolver_agent.py` |
| `ticketing` | Crea un ticket simulado en almacenamiento local. | `agents/ticketing_agent.py` |
| `response` | Construye la respuesta que recibira el usuario usando DeepSeek cuando esta disponible o una plantilla local como fallback. | `agents/response_agent.py` |
| `validator` | Valida claridad, coherencia y seguridad usando DeepSeek cuando esta disponible o reglas locales como fallback. | `agents/validator_agent.py` |
| `log_interaction` | Registra la interaccion sin guardar el mensaje crudo del usuario. | `tools/logging_tools.py` |

## Reglas de Enrutamiento

```mermaid
flowchart LR
    Resolver[resolver] --> MoreInfo{needs_more_info?}
    MoreInfo -->|Si| Response[response]
    MoreInfo -->|No| TicketCheck{requires_ticket?}
    TicketCheck -->|Si| Ticketing[ticketing]
    TicketCheck -->|No| Response
    Ticketing --> Response

    Validator[validator] --> Status{validation_status?}
    Status -->|Si| Log[log_interaction]
    Status -->|No| Retries{validation_retry_count >= max_validation_retries?}
    Retries -->|Si| Log
    Retries -->|No| Response
```
