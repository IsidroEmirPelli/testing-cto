from src.application.dto.source_dto import CreateSourceDTO, SourceDTO
from src.domain.entities.source import Source
from src.domain.repositories.source_repository import SourceRepository


class RegisterSourceUseCase:

    def __init__(self, source_repository: SourceRepository):
        self._source_repository = source_repository

    async def execute(self, dto: CreateSourceDTO) -> SourceDTO:
        existing_source = await self._source_repository.get_by_nombre(
            dto.source_type.nombre
        )
        if existing_source:
            raise ValueError(f"Source {dto.source_type.nombre} already exists")

        source = Source.create(source_type=dto.source_type)
        created_source = await self._source_repository.create(source)

        return self._to_dto(created_source)

    @staticmethod
    def _to_dto(source: Source) -> SourceDTO:
        return SourceDTO(
            id=source.id,
            source_type=source.source_type,
            nombre=source.nombre,
            dominio=source.dominio,
            pais=source.pais,
            activo=source.activo,
            created_at=source.created_at,
            updated_at=source.updated_at,
        )
