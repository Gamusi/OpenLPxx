# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
This module contains tests for the settings tab for the Presentations plugin.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from PyQt5 import QtCore, QtTest, QtWidgets

from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.presentations.lib.presentationtab import PresentationTab

__default_settings__ = {
    'presentations/powerpoint slide click advance': QtCore.Qt.Unchecked,
    'presentations/powerpoint control window': QtCore.Qt.Unchecked,
    'presentations/impress use display setting': QtCore.Qt.Unchecked
}


def Mocked_Controllers(impress_available, powerpoint_available):
    impress_controller = MagicMock()
    impress_controller.name = 'Impress'
    impress_controller.display_name = 'Impress'
    impress_controller.is_available.return_value = impress_available
    powerpoint_controller = MagicMock()
    powerpoint_controller.name = 'Powerpoint'
    powerpoint_controller.display_name = 'Powerpoint'
    powerpoint_controller.is_available.return_value = powerpoint_available
    return {'Impress': impress_controller, 'Powerpoint': powerpoint_controller}


def test_check_boxes(settings):
    """
    Test check box options are correctly saved
    """
    # GIVEN: A presentations tab fixture
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    form = PresentationTab(None, 'Presentations', None, Mocked_Controllers(True, True), None)

    # WHEN: The presentations tab checkboxes are checked and the form saved
    QtTest.QTest.mouseClick(form.ppt_slide_click_check_box, QtCore.Qt.LeftButton)
    QtTest.QTest.mouseClick(form.ppt_window_check_box, QtCore.Qt.LeftButton)
    QtTest.QTest.mouseClick(form.odp_display_check_box, QtCore.Qt.LeftButton)
    form.activated = True
    form.save()
    # THEN: The updated values should be stored in the settings
    assert form.settings.value('presentations/powerpoint slide click advance') == QtCore.Qt.Checked
    assert form.settings.value('presentations/powerpoint control window') == QtCore.Qt.Checked
    assert form.settings.value('presentations/impress use display setting') == QtCore.Qt.Checked


def test_check_boxes_when_controllers_unavailable(settings):
    """
    Test settings related check box options are unchanged when controllers aren't available
    """
    # GIVEN: A presentations tab fixture
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    form = PresentationTab(None, 'Presentations', None, Mocked_Controllers(False, False), None)

    # WHEN: The presentations tab checkboxes are checked and the form saved
    QtTest.QTest.mouseClick(form.ppt_slide_click_check_box, QtCore.Qt.LeftButton)
    QtTest.QTest.mouseClick(form.ppt_window_check_box, QtCore.Qt.LeftButton)
    QtTest.QTest.mouseClick(form.odp_display_check_box, QtCore.Qt.LeftButton)
    form.activated = True
    form.save()
    # THEN: The updated values should be unchanged
    assert form.settings.value('presentations/powerpoint slide click advance') == QtCore.Qt.Unchecked
    assert form.settings.value('presentations/powerpoint control window') == QtCore.Qt.Unchecked
    assert form.settings.value('presentations/impress use display setting') == QtCore.Qt.Unchecked


class TestPresentationTabPowerPointProbe(unittest.TestCase):
    """Focused regression tests for skipping disabled PowerPoint startup probes."""

    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        Registry.create()
        Settings.setDefaultFormat(Settings.IniFormat)
        Settings.set_filename(Path(self.tmp.name) / 'test.ini')
        self.settings = Settings()
        self.settings.extend_default_settings({
            **__default_settings__,
            'presentations/Powerpoint': QtCore.Qt.Checked,
            'presentations/Impress': QtCore.Qt.Checked,
            'presentations/override app': QtCore.Qt.Unchecked,
        })
        Registry().register('settings', self.settings)
        Registry().register('settings_form', MagicMock())

    def tearDown(self):
        self.tmp.cleanup()

    def test_skips_powerpoint_probe_when_disabled_and_keeps_checkbox_accessible(self):
        self.settings.setValue('presentations/Powerpoint', QtCore.Qt.Unchecked)
        controllers = Mocked_Controllers(True, True)
        form = PresentationTab(None, 'Presentations', 'Presentations', controllers, None)

        controllers['Powerpoint'].is_available.assert_not_called()
        controllers['Impress'].is_available.assert_called_once()
        ppt_box = form.presenter_check_boxes['Powerpoint']
        self.assertTrue(ppt_box.isEnabled())
        self.assertFalse(ppt_box.isChecked())
        self.assertFalse(form.ppt_slide_click_check_box.isEnabled())

    def test_probes_powerpoint_when_enabled(self):
        self.settings.setValue('presentations/Powerpoint', QtCore.Qt.Checked)
        controllers = Mocked_Controllers(True, True)
        form = PresentationTab(None, 'Presentations', 'Presentations', controllers, None)

        controllers['Powerpoint'].is_available.assert_called_once()
        controllers['Impress'].is_available.assert_called_once()
        self.assertTrue(form.presenter_check_boxes['Powerpoint'].isChecked())
        self.assertTrue(form.ppt_slide_click_check_box.isEnabled())

    def test_skips_impress_probe_when_disabled_and_keeps_checkbox_accessible(self):
        self.settings.setValue('presentations/Impress', QtCore.Qt.Unchecked)
        controllers = Mocked_Controllers(True, True)
        form = PresentationTab(None, 'Presentations', 'Presentations', controllers, None)

        controllers['Impress'].is_available.assert_not_called()
        controllers['Powerpoint'].is_available.assert_called_once()
        impress_box = form.presenter_check_boxes['Impress']
        self.assertTrue(impress_box.isEnabled())
        self.assertFalse(impress_box.isChecked())
        self.assertFalse(form.odp_display_check_box.isEnabled())

    def test_probes_impress_when_enabled(self):
        self.settings.setValue('presentations/Impress', QtCore.Qt.Checked)
        controllers = Mocked_Controllers(True, True)
        form = PresentationTab(None, 'Presentations', 'Presentations', controllers, None)

        controllers['Impress'].is_available.assert_called_once()
        self.assertTrue(form.presenter_check_boxes['Impress'].isChecked())
        self.assertTrue(form.odp_display_check_box.isEnabled())

    def test_neither_probed_when_both_disabled_and_both_remain_configurable(self):
        self.settings.setValue('presentations/Powerpoint', QtCore.Qt.Unchecked)
        self.settings.setValue('presentations/Impress', QtCore.Qt.Unchecked)
        controllers = Mocked_Controllers(True, True)
        form = PresentationTab(None, 'Presentations', 'Presentations', controllers, None)

        controllers['Powerpoint'].is_available.assert_not_called()
        controllers['Impress'].is_available.assert_not_called()
        self.assertTrue(form.presenter_check_boxes['Powerpoint'].isEnabled())
        self.assertTrue(form.presenter_check_boxes['Impress'].isEnabled())
        form.presenter_check_boxes['Impress'].setChecked(True)
        self.assertTrue(form.presenter_check_boxes['Impress'].isChecked())
