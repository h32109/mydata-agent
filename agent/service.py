import typing as t


class ServiceBase:
    def configuration(self, settings):
        raise NotImplementedError


class Service:
    __services: t.Dict[str, ServiceBase] = {}

    @classmethod
    def add_service(cls, service_class: t.Type[ServiceBase]) -> ServiceBase:
        service_name = service_class.__name__
        if service_name in cls.__services:
            return cls.__services[service_name]

        service = service_class()
        setattr(cls, service_name, service)
        cls.__services[service_name] = service
        return service

    @classmethod
    def init(cls, settings):
        for service in cls.__services.values():
            service.configuration(settings)

    @classmethod
    def get(cls, service_name: str) -> ServiceBase:
        try:
            return cls.__services[service_name]
        except KeyError:
            raise ValueError(f"Service '{service_name}' not found.")