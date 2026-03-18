
# Реализуйте здесь простую машину состояний (State Machine).
# Функция должна принимать текущее состояние и событие,
# и возвращать следующее состояние.

def next_state(state: str, event: str) -> str:
    transitions = {
        "NEW": {
            "PAY_OK": "PAID",
            "PAY_FAIL": "CANCELLED",
        },
        "PAID": {
            "DELIVERY_SUCCESS": "DONE",
            "DELIVERY_FAILURE": "CANCELLED",
            "CANCELED_BY_USER": "CANCELLED"
        },
        "DONE": {},
        "CANCELLED": {}        
    }
    return transitions.get(state, {}).get(event)
