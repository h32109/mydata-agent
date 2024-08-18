from agent.context.langchain_ctx.store_prod import StoreProd


class PluginBase:

    def __init__(self,
                 prod: StoreProd,
                 *args,
                 **kwargs):
        self.prod: StoreProd = prod