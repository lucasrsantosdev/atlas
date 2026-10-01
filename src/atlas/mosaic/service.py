from __future__ import annotations

from atlas.mosaic.models import MosaicRequest, MosaicResult


class MosaicService:
    """
    Serviço principal de orquestração do Mosaic.

    O Mosaic compreende a solicitação do usuário,
    classifica intenção, prepara contexto e retorna
    um resultado estruturado.

    O Mosaic não executa tarefas e não grava
    diretamente memória permanente.
    """

    def analyze(self, request: MosaicRequest) -> MosaicResult:
        raise NotImplementedError(
            "Pipeline de análise do Mosaic v0.1 ainda não implementado."
        )
