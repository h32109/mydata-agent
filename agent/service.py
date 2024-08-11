import asyncio


class ServiceBase:
    def configuration(self, config):
        raise NotImplementedError


class ServiceManager:
    __services = {}

    @classmethod
    def add_service(mgr, svc):
        service_name = svc.__class__.__name__
        setattr(mgr, service_name, svc)
        mgr.__services[service_name] = svc
        return svc

    @classmethod
    async def init(mgr, config):
        tasks = []
        for svc in mgr.__services.values():
            config_method = getattr(svc, 'configuration', None)
            if callable(config_method):
                if asyncio.iscoroutinefunction(config_method):
                    tasks.append(config_method(config))
                else:
                    loop = asyncio.get_running_loop()
                    tasks.append(loop.run_in_executor(None, config_method, config))
        if tasks:
            await asyncio.gather(*tasks)

    @classmethod
    def get(mgr, service_name):
        return mgr.__services[service_name]
