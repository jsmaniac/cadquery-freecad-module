# -*- coding: utf-8 -*-
"""
This package contains the python code editor widget
"""
import sys
from pyqode.core.api import ColorScheme
from pyqode.python.backend import server
from pyqode.qt import QtCore, QtGui
from pyqode.core import api
from pyqode.core import modes
from pyqode.core import panels
from pyqode.python import managers as pymanagers
from pyqode.python import modes as pymodes
from pyqode.python import panels as pypanels
from pyqode.python.folding import PythonFoldDetector


class PyCodeEditBase(api.CodeEdit):
    """
    Base class for creating a python code editor widget. The base class
    takes care of setting up the syntax highlighter.

    .. note:: This code editor widget use PEP 0263 to detect file encoding.
              If the opened file does not respects the PEP 0263,
              :py:func:`locale.getpreferredencoding` is used as the default
              encoding.
    """

    def __init__(self, parent=None, create_default_actions=True,
                 color_scheme='qt'):
        super(PyCodeEditBase, self).__init__(parent, create_default_actions)
        self.file = pymanagers.PyFileManager(self)

    def setPlainText(self, txt, mimetype='text/x-python', encoding='utf-8'):
        """
        Extends QCodeEdit.setPlainText to allow user to setPlainText without
        mimetype (since the python syntax highlighter does not use it).
        """
        self.syntax_highlighter.docstrings[:] = []
        self.syntax_highlighter.import_statements[:] = []
        super(PyCodeEditBase, self).setPlainText(txt, mimetype, encoding)


class PyCodeEdit(PyCodeEditBase):
    """
    Extends PyCodeEditBase with a set of hardcoded modes and panels specifics
    to a python code editor widget.
    """
    DARK_STYLE = 0
    LIGHT_STYLE = 1

    mimetypes = ['text/x-python']

    def __init__(self, parent=None, server_script=server.__file__,
                 interpreter=sys.executable, args=None,
                 create_default_actions=True, color_scheme='qt'):
        super(PyCodeEdit, self).__init__(
            parent=parent, create_default_actions=create_default_actions,
            color_scheme=color_scheme)
        self.backend.start(server_script, interpreter, args)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("pyQode - Python Editor")

        # install those modes first as they are required by other modes/panels
        self.modes.append(pymodes.DocumentAnalyserMode())

        # panels
        self.panels.append(panels.FoldingPanel())
        self.panels.append(panels.LineNumberPanel())
        self.panels.append(panels.CheckerPanel())
        self.panels.append(panels.GlobalCheckerPanel(),
                           panels.GlobalCheckerPanel.Position.RIGHT)
        self.panels.append(panels.SearchAndReplacePanel(),
                           panels.SearchAndReplacePanel.Position.BOTTOM)
        self.panels.append(panels.EncodingPanel(), api.Panel.Position.TOP)
        self.add_separator()
        self.panels.append(pypanels.QuickDocPanel(), api.Panel.Position.BOTTOM)

        # modes
        # generic
        self.modes.append(modes.CaretLineHighlighterMode())
        self.modes.append(modes.FileWatcherMode())
        self.modes.append(modes.RightMarginMode())
        self.modes.append(modes.ZoomMode())
        self.modes.append(modes.SymbolMatcherMode())
        self.modes.append(modes.CodeCompletionMode())
        self.modes.append(modes.OccurrencesHighlighterMode())
        self.modes.append(modes.SmartBackSpaceMode())
        self.modes.append(modes.ExtendedSelectionMode())
        # python specifics
        self.modes.append(pymodes.PyAutoIndentMode())
        self.modes.append(pymodes.PyAutoCompleteMode())
        self.modes.append(pymodes.FrostedCheckerMode())
        self.modes.append(pymodes.PEP8CheckerMode())
        self.modes.append(pymodes.CalltipsMode())
        self.modes.append(pymodes.PyIndenterMode())
        self.modes.append(pymodes.GoToAssignmentsMode())
        self.modes.append(pymodes.CommentsMode())
        self.modes.append(pymodes.PythonSH(
            self.document(), color_scheme=ColorScheme(color_scheme)))
        self.syntax_highlighter.fold_detector = PythonFoldDetector()

    def clone(self):
        clone = self.__class__(
            parent=self.parent(), server_script=self.backend.server_script,
            interpreter=self.backend.interpreter, args=self.backend.args,
            color_scheme=self.syntax_highlighter.color_scheme.name)
        return clone

    def __repr__(self):
        return 'PyCodeEdit(path=%r)' % self.file.path