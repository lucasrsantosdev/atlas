from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class WebClientError(RuntimeError):
    """Erro de acesso HTTP do Atlas."""


@dataclass(frozen=True)
class WebResponse:
    url: str
    status_code: int
    content_type: str
    body: bytes


class WebClient:
    """
    Cliente HTTP mínimo e substituível do Atlas.

    Não pertence ao modelo.
    Não executa JavaScript.
    Não mantém sessão.
    """

    def __init__(
        self,
        timeout_seconds: int = 15,
        user_agent: str = "ATLAS.IA/0.1",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def get(
        self,
        url: str,
    ) -> WebResponse:
        clean_url = url.strip()

        if not clean_url:
            raise ValueError(
                "URL não pode estar vazia."
            )

        if not clean_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "Atlas aceita apenas URLs HTTP/HTTPS."
            )

        request = Request(
            clean_url,
            method="GET",
            headers={
                "User-Agent": self.user_agent,
                "Accept": (
                    "text/html,"
                    "application/xml,"
                    "application/rss+xml,"
                    "application/json"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                body = response.read()

                return WebResponse(
                    url=response.geturl(),
                    status_code=response.status,
                    content_type=response.headers.get(
                        "Content-Type",
                        "",
                    ),
                    body=body,
                )

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise WebClientError(
                f"Falha ao acessar '{clean_url}': {exc}"
            ) from exc
