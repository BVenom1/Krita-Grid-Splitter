from krita import DockWidgetFactory, DockWidgetFactoryBase
from .grid_splitter import GridSplitter

DOCKER_ID = 'template_docker'
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        GridSplitter)

instance.addDockWidgetFactory(dock_widget_factory)