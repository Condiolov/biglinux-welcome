import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import os

class BrowserWidget(Gtk.Box):
    """
    A custom widget to display a browser, indicating its installation
    and default status, and handling clicks to install/set as default.
    """
    def __init__(self, browser_data, app_path, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6, **kwargs)
        self.browser_data = browser_data
        self.app_path = app_path
        self.set_tooltip_text(browser_data['label'])

        self.button = Gtk.Button()
        self.button.set_has_frame(False)
        self.button.add_css_class("flat")
        # The click signal will be connected by the parent page

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.button.set_child(content_box)

        # Icon - Load from our local path first
        icon_path = os.path.join(self.app_path, "image", "browsers", f"{browser_data['icon']}.svg")
        self.icon = Gtk.Image.new_from_file(icon_path)
        # Fallback in case file doesn't exist, though it should.
        if not os.path.exists(icon_path):
            self.icon = Gtk.Image.new_from_icon_name(browser_data['icon'])
        self.icon.set_pixel_size(64)

        # Checkmark Overlay
        self.check_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        self.check_icon.add_css_class("success") # For green color styling

        self.overlay = Gtk.Overlay()
        self.overlay.set_child(self.icon)
        self.overlay.add_overlay(self.check_icon)
        self.overlay.set_measure_overlay(self.check_icon, True)
        # Align checkmark to the bottom right
        self.check_icon.set_halign(Gtk.Align.END)
        self.check_icon.set_valign(Gtk.Align.END)

        content_box.append(self.overlay)

        # Label
        label_widget = Gtk.Label(label=browser_data['label'])
        label_widget.set_wrap(True)
        content_box.append(label_widget)

        self.append(self.button)
        self.set_installed(False) # Default state
        self.set_default(False)   # Default state

    def set_installed(self, is_installed):
        """Sets the visual state to installed or not installed."""
        if is_installed:
            self.remove_css_class("is-not-installed")
        else:
            self.add_css_class("is-not-installed")

    def set_default(self, is_default):
        """Shows or hides the default checkmark."""
        self.check_icon.set_visible(is_default)
