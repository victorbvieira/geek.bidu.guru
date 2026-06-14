"""
Modelo de Configuracao da aplicacao (key/value).

Configuracoes editaveis pelo admin em tempo de execucao (sem redeploy),
como a tag do programa de afiliados da Amazon. Tabela generica para
acomodar futuras configuracoes.
"""

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Setting(Base, UUIDMixin, TimestampMixin):
    """
    Configuracao chave/valor da aplicacao.

    Atributos:
        key: Identificador unico da configuracao (ex: amazon_affiliate_tag)
        value: Valor (texto livre; pode ser nulo/vazio)
        description: Descricao amigavel para o admin
    """

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Setting {self.key}={self.value!r}>"
