class Wy_Widget(QWidget):
    def __init__(self):
        super().__init__()
        
        # базовые установки
        self.setWindowTitle("Виджет")
        self.setGeometry(600, 300, 360, 150)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
        # макет
        layout = QVBoxLayout(self)

        btn_layers = QPushButton("Показать названия слоев")
        btn_extent = QPushButton("Создать слой экстента экрана")
        btn_layout = QPushButton("Слой + Макет с картой (красный)")

        layout.addWidget(btn_layers)
        layout.addWidget(btn_extent)
        layout.addWidget(btn_layout)
        self.setLayout(layout)
    
        # действия
        btn_layers.clicked.connect(self.show_layer_names)
        btn_extent.clicked.connect(self.create_extent_layer)
        btn_layout.clicked.connect(self.create_layout_with_extent)

        self.show()
        
    def show_layer_names(self):
        layers = QgsProject.instance().mapLayers().values()
        names = [layer.name() for layer in layers]
        msg = '\n'.join(names) if names else "Нет слоев"
        QMessageBox.information(self, "Слои в проекте", msg)
        
    def create_extent_layer(self):
        extent = iface.mapCanvas().extent()
        crs = iface.mapCanvas().mapSettings().destinationCrs()
        layer = QgsVectorLayer(f'Polygon?crs={crs.authid()}', 'Охват_экрана', 'memory')
        pr = layer.dataProvider()
        pr.addAttributes([QgsField('id', QVariant.Int)])
        layer.updateFields()
        
        # полигон по углам экрана
        points = [
            QgsPointXY(extent.xMinimum(), extent.yMinimum()),
            QgsPointXY(extent.xMinimum(), extent.yMaximum()),
            QgsPointXY(extent.xMaximum(), extent.yMaximum()),
            QgsPointXY(extent.xMaximum(), extent.yMinimum()),
            QgsPointXY(extent.xMinimum(), extent.yMinimum())
        ]
        polygon = QgsGeometry.fromPolygonXY([points])
        feat = QgsFeature()
        feat.setGeometry(polygon)
        feat.setAttributes([1])
        pr.addFeatures([feat])
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)
        QMessageBox.information(self, "Готово", "Создан слой охвата экрана!")
        
    def create_layout_with_extent(self):
        # Слои проекта могут обновляться — создаём слой экстента заново
        extent = iface.mapCanvas().extent()
        crs = iface.mapCanvas().mapSettings().destinationCrs()
        layer = QgsVectorLayer(f'Polygon?crs={crs.authid()}', 'Охват_экрана_макет', 'memory')
        pr = layer.dataProvider()
        pr.addAttributes([QgsField('id', QVariant.Int)])
        layer.updateFields()
        points = [
            QgsPointXY(extent.xMinimum(), extent.yMinimum()),
            QgsPointXY(extent.xMinimum(), extent.yMaximum()),
            QgsPointXY(extent.xMaximum(), extent.yMaximum()),
            QgsPointXY(extent.xMaximum(), extent.yMinimum()),
            QgsPointXY(extent.xMinimum(), extent.yMinimum())
        ]
        polygon = QgsGeometry.fromPolygonXY([points])
        feat = QgsFeature()
        feat.setGeometry(polygon)
        feat.setAttributes([1])
        pr.addFeatures([feat])
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

        # Закрашиваем полигон в красный цвет
        symbol = layer.renderer().symbol()
        symbol.setColor(QColor('red'))
        layer.triggerRepaint()

        # Создаем макет
        project = QgsProject.instance()
        manager = project.layoutManager()
        name_layout = "Макет_экстента"
        for layout in manager.printLayouts():
            if layout.name() == name_layout:
                manager.removeLayout(layout)
        layout_print = QgsPrintLayout(project)
        layout_print.initializeDefaults()
        layout_print.setName(name_layout)
        manager.addLayout(layout_print)

        # Карта
        map_item = QgsLayoutItemMap(layout_print)
        map_item.setRect(20, 20, 180, 180)
        map_item.setLayers([layer])
        layout_print.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters), page=0)
        map_item.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))
        map_item.zoomToExtent(layer.extent())
        QMessageBox.information(self, "Готово", "Слой + макет с картой создан!")


widget = Wy_Widget()