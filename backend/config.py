"""Configurações de conexão com o Supabase."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def _get_env(name: str) -> str:
    value: Optional[str] = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variável de ambiente obrigatória ausente: {name}. Defina-a no ambiente ou em um arquivo .env."
        )
    return value


@lru_cache
def get_supabase_client() -> Client:
    """Retorna uma instância única do cliente Supabase.

    Procura primeiro a chave de serviço (SUPABASE_SERVICE_ROLE_KEY) para permitir operações de escrita.
    Caso não exista, usa SUPABASE_ANON_KEY.
    """

    url = _get_env("SUPABASE_URL")
    api_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not api_key:
        raise RuntimeError(
            "Defina SUPABASE_SERVICE_ROLE_KEY (recomendado) ou SUPABASE_ANON_KEY para conectar ao Supabase."
        )

    return create_client(url, api_key)

