from .models import RouteResult
from .service import RoutingService


def route(query: str) -> RouteResult:
    return RoutingService.classify(query)