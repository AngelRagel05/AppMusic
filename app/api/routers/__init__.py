from fastapi import APIRouter

from app.api.routers.comparisonRouter import router as comparisonRouter
from app.api.routers.downloadRouter import router as downloadRouter
from app.api.routers.ignoredTermRouter import router as ignoredTermRouter
from app.api.routers.libraryRouter import router as libraryRouter
from app.api.routers.playlistRouter import router as playlistRouter
from app.api.routers.songRouter import router as songRouter
from app.api.routers.systemRouter import router as systemRouter
from app.api.routers.taskRouter import router as taskRouter

apiRouter = APIRouter()
apiRouter.include_router(systemRouter)
apiRouter.include_router(taskRouter)
apiRouter.include_router(libraryRouter)
apiRouter.include_router(playlistRouter)
apiRouter.include_router(comparisonRouter)
apiRouter.include_router(ignoredTermRouter)
apiRouter.include_router(songRouter)
apiRouter.include_router(downloadRouter)

__all__ = ["apiRouter"]
