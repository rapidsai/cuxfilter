import inspect
import panel as pn


def get_code(fn, dtype, n):
    result = (
        "".join(
            list(
                map(
                    lambda x: x.replace("    ", "", 1),
                    list(
                        filter(
                            lambda x: x.startswith((" ", "\n")),
                            inspect.getsourcelines(fn)[0],
                        )
                    ),
                )
            )
        )
        .replace("=n", f"={n}")
        .replace("=dtype", f'="{dtype}"')
        .replace("{dtype}", f"{dtype}")
        .replace("return ", "")
        .replace(f'exec(f"import hvplot.{dtype}")', f"import hvplot.{dtype}")
    )

    return pn.widgets.Ace(
        name="code",
        language="python",
        height=360,
        width=800,
        value=result,
        readonly=True,
    )
