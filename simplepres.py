from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QColorDialog, QFileDialog, QGraphicsView,  
                               QGraphicsScene, QGraphicsItem, QMessageBox)
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtPdf import QPdfDocument

import argparse
import os
import sys

DEFAULT_COLOR = Qt.black
DEFAULT_THICKNESS = 2


class MyItem(QGraphicsItem):
    def __init__(self, pos, color, thickness):
        super().__init__()
        self.path = QPainterPath(pos)
        self.color = color
        self.thickness = thickness

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        painter.setPen(QPen(self.color, self.thickness))
        painter.drawPath(self.path)

    def mousePressEvent(self, event):
        print('mpe')
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        print('mme')
        self.setPos(self.pos() + event.scenePos() - event.lastScenePos())

    def mouseReleaseEvent(self, event):
        print('mre')
        self.setCursor(Qt.ArrowCursor)

    def lineTo(self, point):
        self.path.lineTo(point)
        self.update()

    def moveTo(self, point):
        self.path.moveTo(point)
        #self.update()     

# class to hold page and lines
class Page:
    def __init__(self, document, parent, page_num, paths=None):
        self.document = document
        self.parent = parent
        self.page_num = page_num
        self.paths = paths
        
    def render(self, event=None, size=None):
        if event is not None:
            size = event.size()
        image = self.document.render(self.page_num, size)
        return image

class MyGraphicsView(QGraphicsView):
    def __init__(self, scene, pdf_filename):
        super().__init__(scene)
        self.dragged_item = None
        self.path = None
        self.d_pressed = False
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        pdf_document = QPdfDocument()
        pdf_document.load(pdf_filename)
        self.page_number = 0
        self.page_count = pdf_document.pageCount()
        self.page = Page(pdf_document, self, self.page_number)
        # track items for each page in a dictionary page_num: [items]
        self.page_items = {}

        self.updateBackground()

    # remove all paths from the scene
    def clear_paths(self):
        #self.scene().clear()
        for item in self.scene().items():
        #    if isinstance(item, MyItem):
                self.scene().removeItem(item)

    # save page items
    def save_page_items(self):
        self.page_items[self.page_number] = self.scene().items()

    # load page items
    def load_page_items(self):

        if self.page_number in self.page_items:
            for item in self.page_items[self.page_number]:
                self.scene().addItem(item)

    def next_page(self):
        if self.page_number < self.page_count - 1:
            # save current page items
            self.save_page_items()
            self.clear_paths()
            self.page_number += 1
            self.page = Page(self.page.document, self, self.page_number)
            self.updateBackground()
            # update page items
            self.load_page_items()

    def prev_page(self):
        if self.page_number > 0:
            self.save_page_items()
            self.clear_paths()
            self.page_number -= 1
            self.page = Page(self.page.document, self, self.page_number)
            self.updateBackground()
            self.load_page_items()

    def updateBackground(self):
        pixmap = QPixmap(self.page.render(size=self.size()))
        brush = QBrush(pixmap)
        #brush.setAlignment(Qt.AlignCenter)
        self.scene().setBackgroundBrush(brush)
        self.scene().setSceneRect(0,0, pixmap.width(), pixmap.height())

    def resizeEvent(self, event):
        print('resizeEvent')
        self.updateBackground()
        # scale page items to fit the new size
        #self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        #super().resizeEvent(event)

    def mousePressEvent(self, event):
        # Check if the user has clicked on an item
        pos = event.position()
        x = pos.x()
        y = pos.y()
        item = self.itemAt(x,y)
        if item:
            self.dragged_item = item
            return super().mousePressEvent(event)
            # select the item and draw bounding box
            item.setSelected(True)
            print(f'dragging item {pos}')
            # If an item was clicked, start dragging it
            self.dragged_item.setCursor(Qt.ClosedHandCursor)
        else:
            if self.dragged_item:
                self.dragged_item.setSelected(False)
            self.dragged_item = None
            print(f'drawing line {pos}')
            # If no item was clicked, start drawing a line
            start = self.mapToScene(x, y)#event.position())
            ##self.path = QPainterPath(start)
            self.path = MyItem(start, DEFAULT_COLOR, DEFAULT_THICKNESS)
            #self.path.moveTo(start)
            ##self.prev_path = self.scene().addPath(self.path)
            self.prev_path = self.scene().addItem(self.path)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        #print(f'pos: {pos} scene_pos: {scene_pos}', end='--')    
        # if button is pressed
        # if d is pressed delete item under mouse
        if self.d_pressed:
            pos = event.position()
            x = pos.x()
            y = pos.y()
            scene_pos= self.mapToScene(x, y)

            self.d_pressed = False
            item = self.itemAt(x, y)
            if item:
                self.scene().removeItem(item)
                #self.viewport().update()
            return super().mouseMoveEvent(event)
        if (event.buttons() == Qt.LeftButton):
            pos = event.position()
            x = pos.x()
            y = pos.y()
            scene_pos= self.mapToScene(x, y)

            if hasattr(self, 'dragged_item') and self.dragged_item:
                return super().mouseMoveEvent(event)
                # If an item is being dragged, update its position
                cur_pos = self.dragged_item.pos()
                delta = scene_pos - cur_pos
                self.dragged_item.setPos(cur_pos+delta) #self.dragged_item.pos() + pos )#- event.lastScenePos())

            elif self.path:
                # If no item is being dragged, continue drawing the line
                #end = self.mapToScene(pos)
                #self.path.lineTo(end)
                self.path.lineTo(scene_pos)
                # Can I get around adding a new path each time?
                if self.prev_path:
                    self.scene().removeItem(self.prev_path)
                ##self.prev_path = self.scene().addPath(self.path)
                self.prev_path = self.scene().addItem(self.path)
                ##self.prev_path = self.scene().addItem(LineItem(self.path, DEFAULT_COLOR, DEFAULT_THICKNESS))
                print(f'len items {len(self.scene().items())}')
                self.update()
                #self.path.update()
                
                #self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        print('mouseReleaseEvent')
        if self.dragged_item:
            return super().mouseReleaseEvent(event)
            # If an item was being dragged, leave it selected
            self.dragged_item.setSelected(True)
            self.dragged_item.setCursor(Qt.ArrowCursor)
        else:
            self.path = None
            #self.update()
            # If no item was being dragged, finish drawing the line
        super().mouseReleaseEvent(event)  

    # quit when q is pressed
    def keyPressEvent(self, event):      
        if event.key() == Qt.Key_Q:
            self.close()
        # change thickness of line when +/- is pressed
        elif event.key() == Qt.Key_Plus and self.dragged_item:
            self.dragged_item.thickness += 1
            self.viewport().update()   
        elif event.key() == Qt.Key_Minus:
            self.dragged_item.thickness -= 1
            self.viewport().update()   
        # delete item when d is pressed
        elif event.key() == Qt.Key_D:
            self.d_pressed = True
            self.scene().removeItem(self.dragged_item)
            self.viewport().update()
            print(f'items {len(self.scene().items())}')
        # show a color selector dialog when c is pressed
        elif event.key() == Qt.Key_C:
            color = QColorDialog.getColor()
            if color.isValid():
                self.dragged_item.color = color
                self.viewport().update()
        # show next page when n is pressed or right arrow
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_N:
            self.next_page()
        # show previous page when p is pressed or left arrow
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_P:
            self.prev_page()
        # show a help dialog when h is pressed
        elif event.key() == Qt.Key_H:
            self.help_dialog()

    # reset d_pressed when key is released
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_D:
            self.d_pressed = False

    def help_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Help")
        msg.setInformativeText("""q: quit
c: change color
+/-: change line thickness
d: delete item under mouse
n: next page
p: previous page
h: help
        """)
        msg.setWindowTitle("Help")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()




def main(args):
    # use argparse to get the pdf filename
    parser = argparse.ArgumentParser()
    # make pdf_filename optional

    parser.add_argument('pdf_filename', help='pdf filename', nargs='?')
    args = parser.parse_args()
    if args.pdf_filename and os.path.exists(args.pdf_filename):
        filename = args.pdf_filename
    else:
        filename = None

    app = QApplication(sys.argv)
    # open pdf file dialog if no filename is given
    if not filename:
        filename, _ = QFileDialog.getOpenFileName(None, 'Open PDF', '', 'PDF files (*.pdf)')
        if not filename:
            sys.exit(0)

    scene = QGraphicsScene()
    #filename = '/tmp/ai4devs2023.pdf'
    view = MyGraphicsView(scene, pdf_filename=filename)

    view.show()
    view.resize(600, 899)
    sys.exit(app.exec())

if __name__ == '__main__':
    main(sys.argv)
