from functools import partial

from werkzeug.local import LocalProxy

from agent.context.base import Context


def lookup_context(ctx: Context, name: str | None = None):
    if name is None:
        return ctx.get()
    return getattr(ctx, name, ctx).get(name)


lc = LocalProxy(
    partial(
        lookup_context,
        Context,
        "langchain")
)

cm = LocalProxy(
    partial(
        lookup_context,
        Context,
        "chroma")
)
